#!/usr/bin/env python3
"""
Marpione (marpi1) — Interactive Marp Inline Slide Deck Widget & Sidecar Generator for Antigravity.

Compiles any Marp markdown presentation (single-file or @import manifest deck) into high-DPI
slide images and builds a self-contained <agent-embed> HTML widget with:
  - Left / Right overlay & bottom cursors (1 -> 2 -> 3 ... N) + keyboard shortcuts
  - Color-coded chapter progress scrubber + slide dropdown selector
  - Speaker notes & source file inspector drawer (Notes)
  - "Copy PNG" button (true 1280x720 PNG Blob via offscreen Canvas + ClipboardItem)
  - "Paste to Conversation" button (sends rendered PNG + clickable source link into active
    Antigravity chat via Sidecar bridge, plus clipboard fallback)

Zero mandatory third-party Python dependencies (pure Python 3 stdlib; uses Pillow, cwebp, or
ffmpeg if available to compress inline data URLs to WebP, falling back to PNG).
"""

import argparse
import base64
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


def ensure_node_in_path() -> None:
    """Ensures Node.js / npx / marp binaries from nvm, homebrew, or local bin are in PATH."""
    home = Path.home()
    extra_dirs = []
    nvm_dir = home / ".nvm" / "versions" / "node"
    if nvm_dir.is_dir():
        for v in sorted(nvm_dir.iterdir(), reverse=True):
            b = v / "bin"
            if b.is_dir():
                extra_dirs.append(str(b))
                break
    for cand in [
        home / ".local" / "bin",
        home / "bin",
        Path("/opt/homebrew/bin"),
        Path("/usr/local/bin"),
        Path("/usr/bin"),
    ]:
        if cand.is_dir():
            extra_dirs.append(str(cand))

    current_path = os.environ.get("PATH", "")
    path_parts = current_path.split(":") if current_path else []
    for d in reversed(extra_dirs):
        if d not in path_parts:
            path_parts.insert(0, d)
    os.environ["PATH"] = ":".join(path_parts)


def get_app_data_dir() -> Path:
    """Resolves the Antigravity appDataDir portably across macOS and Linux."""
    if os.environ.get("ANTIGRAVITY_APP_DATA_DIR"):
        return Path(os.environ["ANTIGRAVITY_APP_DATA_DIR"]).expanduser().resolve()
    home = Path.home()
    candidates = [
        home / ".gemini" / "antigravity",
        home / "Library" / "Application Support" / "Antigravity",
        home / ".config" / "Antigravity",
        home / ".local" / "share" / "Antigravity",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def detect_active_session_id(explicit_session_id: str | None = None) -> str:
    """Resolves the active Antigravity conversation ID."""
    if explicit_session_id and explicit_session_id.strip():
        return explicit_session_id.strip()
    if os.environ.get("ANTIGRAVITY_CONVERSATION_ID"):
        return os.environ["ANTIGRAVITY_CONVERSATION_ID"].strip()

    brain_dir = get_app_data_dir() / "brain"
    if not brain_dir.is_dir():
        return "standalone"

    candidates = []
    for entry in brain_dir.iterdir():
        if not entry.is_dir() or entry.name.startswith(".") or entry.name == "tempmediaStorage":
            continue
        transcript = entry / ".system_generated" / "logs" / "transcript.jsonl"
        target = transcript if transcript.is_file() else entry
        try:
            candidates.append((target.stat().st_mtime, entry.name))
        except OSError:
            continue
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][1]
    return "standalone"


def discover_sidecar_config(session_id: str) -> dict:
    """
    Discovers the active Antigravity Sidecar port & token from either:
      1. ~/.gemini/antigravity/sidecar_data/marpione/*/logs/sidecar.log (or marpione/logs/sidecar.log)
      2. ~/.gemini/antigravity/sidecar_data/agy-paint-studio/studio/logs/sidecar.log
      3. Any other active sidecar log under sidecar_data/
    """
    cfg = {
        "baseUrl": "",
        "token": "",
        "conversationId": session_id,
    }
    sidecar_data = get_app_data_dir() / "sidecar_data"
    if not sidecar_data.is_dir():
        return cfg

    log_candidates = list(sidecar_data.glob("marpione/**/sidecar.log")) + list(
        sidecar_data.glob("agy-paint-studio/**/sidecar.log")
    )
    if not log_candidates:
        log_candidates = list(sidecar_data.glob("**/sidecar.log"))

    for log_path in log_candidates:
        if not log_path.is_file():
            continue
        try:
            text = log_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        ports = re.findall(r"127\.0\.0\.1:(\d+)", text)
        if not ports:
            continue
        port = ports[-1]
        base_url = f"http://127.0.0.1:{port}"

        # Try marpione's /api/bridge-config first
        for endpoint in (
            f"{base_url}/api/bridge-config?session_id={session_id}",
            f"{base_url}/api/template?session_id={session_id}",
        ):
            try:
                with urllib.request.urlopen(endpoint, timeout=2.5) as resp:
                    body = resp.read().decode("utf-8", errors="ignore")
                    if endpoint.endswith(f"session_id={session_id}") and "/api/bridge-config" in endpoint:
                        data = json.loads(body)
                        if data.get("baseUrl"):
                            cfg.update(data)
                            cfg["conversationId"] = session_id
                            return cfg
                    m = re.search(r"const cfg = (\{[^;]+\});", body)
                    if m:
                        parsed = json.loads(m.group(1))
                        cfg.update(parsed)
                        cfg["conversationId"] = session_id
                        return cfg
            except Exception:
                continue

    return cfg


def find_slides_root(md_path: Path) -> Path:
    """Finds the presentation slides directory for resolving @import paths and assets."""
    curr = md_path.resolve().parent
    for _ in range(4):
        if (curr / "deck-en").is_dir() or (curr / "deck-it").is_dir() or (curr / "images").exists():
            return curr
        if curr.name == "slides":
            return curr
        if (curr / "slides").is_dir():
            return curr / "slides"
        curr = curr.parent
    return md_path.resolve().parent


def resolve_import_target(raw_target: str, manifest_dir: Path, slides_dir: Path) -> Path | None:
    """Resolves an @import target relative to the manifest directory or slides root."""
    clean = raw_target.strip().strip("'\"")
    if not clean:
        return None
    for base in (manifest_dir, slides_dir, slides_dir / "deck-en", slides_dir / "deck-it"):
        cand = (base / clean).resolve()
        if cand.is_file():
            return cand
    target_name = Path(clean).name
    for folder in ("deck-en", "deck-it"):
        folder_path = slides_dir / folder
        if folder_path.is_dir():
            for root, _, files in os.walk(folder_path):
                if target_name in files:
                    cand = Path(root) / target_name
                    if cand.is_file():
                        return cand
    return None


def compile_manifest_if_needed(md_path: Path, slides_dir: Path, work_dir: Path) -> Path:
    """
    If md_path uses @import directives, compiles it either via ../bin/compile_slides.py
    (if present in the repository) or via Marpione's built-in @import resolver.
    """
    raw_text = md_path.read_text(encoding="utf-8", errors="ignore")
    import_re = re.compile(
        r"""^(?:<!--\s*)?(?:@import|import|\!include)\s+["']?([^"'\s>]+)["']?(?:\s*-->)?""",
        re.IGNORECASE | re.MULTILINE,
    )
    if not import_re.search(raw_text):
        return md_path

    # Check if repo has ../bin/compile_slides.py
    compile_script = slides_dir.parent / "bin" / "compile_slides.py"
    if compile_script.is_file():
        try:
            rel_deck = md_path.resolve().relative_to(slides_dir.resolve())
        except ValueError:
            rel_deck = md_path.resolve()
        try:
            subprocess.run(
                [sys.executable, str(compile_script), "--deck", str(rel_deck)],
                cwd=str(slides_dir),
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            # Determine compiled output filename
            parent_name = md_path.parent.name
            out_candidates = [
                slides_dir / "out" / f"slides-devfest-{parent_name}.md",
                slides_dir / "out" / md_path.name,
                slides_dir / "out" / "slides-en.md",
            ]
            for c in out_candidates:
                if c.is_file():
                    return c
        except Exception as e:
            print(f"[marpione] Note: compile_slides.py fallback to built-in resolver ({e})", file=sys.stderr)

    # Built-in @import resolver
    manifest_dir = md_path.resolve().parent
    compiled_chunks = []
    header_added = False

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//")):
            continue
        m = import_re.match(stripped)
        if m:
            target = m.group(1)
            resolved = resolve_import_target(target, manifest_dir, slides_dir)
            if not resolved:
                continue
            chunk = resolved.read_text(encoding="utf-8", errors="ignore").strip()
            try:
                rel_source = str(resolved.relative_to(slides_dir))
            except ValueError:
                rel_source = resolved.name

            if "000_header" in resolved.name and not header_added:
                compiled_chunks.append(chunk)
                header_added = True
            else:
                # Strip secondary frontmatter if present
                chunk = re.sub(r"^---\s*\nmarp:\s*true.*?\n---\s*\n?", "", chunk, flags=re.DOTALL)
                watermark = f'\n\n<div class="slide-watermark"><tt>📄 {rel_source}</tt></div>'
                compiled_chunks.append(chunk + watermark)

    if not compiled_chunks:
        return md_path

    header_part = compiled_chunks[0] if header_added else "---\nmarp: true\ntheme: default\npaginate: true\n---"
    body_parts = compiled_chunks[1:] if header_added else compiled_chunks
    combined = header_part.rstrip() + "\n\n" + "\n\n---\n\n".join(body_parts) + "\n"

    out_md = work_dir / f"compiled_{md_path.stem}.md"
    out_md.write_text(combined, encoding="utf-8")
    return out_md


def render_marp_to_pngs(compiled_md: Path, slides_dir: Path) -> list[Path]:
    """Renders a compiled Marp markdown file into slide.001.png .. slide.NNN.png with caching."""
    content_bytes = compiled_md.read_bytes()
    digest = hashlib.sha256(content_bytes).hexdigest()[:16]
    cache_dir = Path(tempfile.gettempdir()) / "marpione_cache" / f"{compiled_md.stem}_{digest}"
    cache_dir.mkdir(parents=True, exist_ok=True)

    cached_pngs = sorted(cache_dir.glob("slide.*.png"))
    if cached_pngs:
        return cached_pngs

    # Symlink asset folders into cache_dir so relative image paths resolve
    for asset_name in ("images", "assets", "presentation", "public", "deck-en", "deck-it"):
        src_asset = slides_dir / asset_name
        dst_asset = cache_dir / asset_name
        if src_asset.exists() and not dst_asset.exists():
            try:
                dst_asset.symlink_to(src_asset.resolve())
            except OSError:
                pass

    local_md = cache_dir / compiled_md.name
    if local_md.resolve() != compiled_md.resolve():
        shutil.copy2(compiled_md, local_md)

    out_pattern = cache_dir / "slide.png"
    cmd = [
        "npx",
        "--yes",
        "@marp-team/marp-cli",
        "--html",
        "--allow-local-files",
        "--images",
        "png",
        "--image-scale",
        "1",
        str(local_md),
        "-o",
        str(out_pattern),
    ]
    subprocess.run(cmd, cwd=str(cache_dir), check=True)
    rendered = sorted(cache_dir.glob("slide.*.png"))
    if not rendered and out_pattern.is_file():
        single = cache_dir / "slide.001.png"
        out_pattern.rename(single)
        rendered = [single]
    return rendered


def encode_image_as_data_url(png_path: Path, quality: int = 82) -> str:
    """
    Converts a slide PNG to a compact WebP data URL using Pillow, cwebp, or ffmpeg,
    falling back to PNG base64 if none are installed.
    """
    # 1. Try Pillow
    try:
        from PIL import Image  # type: ignore

        im = Image.open(png_path)
        buf = io.BytesIO()
        im.save(buf, format="WEBP", quality=quality)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return f"data:image/webp;base64,{b64}"
    except Exception:
        pass

    # 2. Try cwebp CLI
    cwebp_bin = shutil.which("cwebp")
    if cwebp_bin:
        try:
            with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmp_w:
                tmp_webp = Path(tmp_w.name)
            subprocess.run(
                [cwebp_bin, "-q", str(quality), "-quiet", str(png_path), "-o", str(tmp_webp)],
                check=True,
                timeout=10,
            )
            b64 = base64.b64encode(tmp_webp.read_bytes()).decode("ascii")
            tmp_webp.unlink(missing_ok=True)
            return f"data:image/webp;base64,{b64}"
        except Exception:
            pass

    # 3. Fallback to raw PNG base64
    b64 = base64.b64encode(png_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def build_slides_payload(
    compiled_md: Path,
    png_files: list[Path],
    slides_dir: Path,
    brain_slides_dir: Path | None = None,
    quality: int = 82,
) -> list[dict]:
    """Pairs rendered PNGs with parsed Markdown sections, titles, chapters, and speaker notes."""
    if brain_slides_dir:
        brain_slides_dir.mkdir(parents=True, exist_ok=True)

    raw_sections: list[str] = []
    if compiled_md.is_file():
        md_text = compiled_md.read_text(encoding="utf-8", errors="ignore")
        m = re.match(r"^---\n.*?\n---\n", md_text, re.DOTALL)
        body = md_text[m.end() :] if m else md_text
        raw_sections = re.split(r"(?m)^---\s*$", body)

    while len(raw_sections) < len(png_files):
        raw_sections.append("")

    slides_data = []
    for idx, png_path in enumerate(png_files, 1):
        sec = raw_sections[idx - 1] if idx - 1 < len(raw_sections) else ""

        if brain_slides_dir:
            dest_png = brain_slides_dir / f"slide.{idx:03d}.png"
            if dest_png.resolve() != png_path.resolve():
                shutil.copy2(png_path, dest_png)
        else:
            dest_png = png_path.resolve()

        wm_matches = re.findall(r"(?:deck-(?:en|it)/[^\s<\"']+\.md|[^\s<\"'/]+\.md)", sec)
        source_rel = wm_matches[-1] if wm_matches else f"slide_{idx:03d}.md"
        cand_abs = (slides_dir / source_rel).resolve()
        source_abs = str(cand_abs if cand_abs.is_file() else compiled_md.resolve())

        if "part1" in source_rel:
            part = "Part 1 · Story"
            part_idx = 1
        elif "part2" in source_rel:
            part = "Part 2 · Tech & Agents"
            part_idx = 2
        elif "part3" in source_rel:
            part = "Part 3 · Ecosystem & CTA"
            part_idx = 3
        elif "part4" in source_rel or "appendix" in source_rel:
            part = "Part 4 · Appendix"
            part_idx = 4
        else:
            part = "Slides"
            part_idx = 1

        headings = re.findall(r"(?m)^#{1,3}\s+(.+)$", sec)
        clean_title = ""
        if headings:
            raw_h = re.sub(r"<[^>]+>", "", headings[0])
            clean_title = raw_h.replace("&bull;", "·").replace("`", "").strip()
        if not clean_title:
            stem = Path(source_rel).stem
            stem = re.sub(r"^\d+[a-z]?_", "", stem)
            stem = re.sub(r"\.[a-z0-9_-]+$", "", stem)
            clean_title = stem.replace("_", " ").title() or f"Slide {idx}"

        comments = re.findall(r"<!--(.*?)-->", sec, re.DOTALL)
        notes_list = []
        for c in comments:
            c_strip = c.strip()
            if not c_strip:
                continue
            if re.match(
                r"^(_class|_paginate|_backgroundColor|_color|_header|_footer|skip|marp):",
                c_strip,
                re.IGNORECASE,
            ):
                continue
            notes_list.append(c_strip)
        speaker_notes = "\n\n".join(notes_list)

        slides_data.append(
            {
                "num": idx,
                "title": clean_title,
                "sourceRel": source_rel,
                "sourceName": Path(source_rel).name,
                "sourceAbs": source_abs,
                "part": part,
                "partIdx": part_idx,
                "notes": speaker_notes,
                "pngPath": str(dest_png),
                "dataUrl": encode_image_as_data_url(png_path, quality=quality),
            }
        )

    return slides_data


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>__DECK_TITLE__ — Marpione Slide Viewer</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    * { box-sizing: border-box; }
    .slide-stage {
      aspect-ratio: 16 / 9;
      max-height: 310px;
      width: auto;
      margin: 0 auto;
    }
    @media (min-height: 620px) {
      .slide-stage {
        max-height: calc(100vh - 190px);
        width: 100%;
      }
    }
    .nav-cursor {
      opacity: 0.75;
      transition: opacity 0.15s ease, transform 0.15s ease, background-color 0.15s ease;
    }
    .slide-stage:hover .nav-cursor {
      opacity: 1;
    }
    .nav-cursor:hover:not(:disabled) {
      transform: scale(1.08);
    }
    .nav-cursor:disabled {
      opacity: 0.25 !important;
      cursor: not-allowed;
    }
    .notes-scroll::-webkit-scrollbar { width: 5px; }
    .notes-scroll::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.4); border-radius: 4px; }
  </style>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-2 select-none">
  <div class="bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)] rounded-xl p-3 shadow-sm flex flex-col gap-2">
    
    <!-- Top Header Bar -->
    <div class="flex items-center justify-between gap-2 flex-wrap">
      <div class="flex items-center gap-2 min-w-0">
        <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-semibold bg-[var(--secondary)] text-[var(--secondary-foreground)] border border-[var(--border)] shrink-0">
          🎭 __DECK_TITLE__
        </span>
        <select id="slide-select" aria-label="Select slide"
          class="bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] rounded-lg px-2 py-1 text-xs font-medium truncate max-w-[260px] sm:max-w-[340px] focus:outline-none focus:ring-1 focus:ring-[var(--primary)] cursor-pointer">
        </select>
      </div>

      <div class="flex items-center gap-1.5 shrink-0">
        <span id="part-badge" class="hidden sm:inline-block px-2 py-0.5 rounded text-xs font-medium bg-[var(--background)] text-[var(--muted-foreground)] border border-[var(--border)]">
          Slides
        </span>
        <button id="btn-notes" type="button" title="Toggle Speaker Notes (N)"
          class="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--secondary)] transition cursor-pointer">
          <span>📝</span>
          <span id="notes-label">Notes</span>
        </button>
      </div>
    </div>

    <!-- Main 16:9 Slide Stage with Left/Right Overlay Cursors -->
    <div class="relative w-full bg-black/90 rounded-lg overflow-hidden border border-[var(--border)] flex items-center justify-center">
      <div class="slide-stage relative flex items-center justify-center w-full overflow-hidden">
        <img id="slide-img" src="" alt="Marp Slide" class="w-full h-full object-contain block select-none" draggable="false" />

        <!-- Floating Left Cursor (<) -->
        <button id="stage-prev" type="button" title="Previous Slide (←)" aria-label="Previous Slide"
          class="nav-cursor absolute left-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-black/65 hover:bg-black/85 text-white border border-white/20 flex items-center justify-center shadow-lg cursor-pointer z-10">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <!-- Floating Right Cursor (>) -->
        <button id="stage-next" type="button" title="Next Slide (→)" aria-label="Next Slide"
          class="nav-cursor absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-black/65 hover:bg-black/85 text-white border border-white/20 flex items-center justify-center shadow-lg cursor-pointer z-10">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <!-- Top-Right Slide Number Badge Overlay -->
        <div class="absolute top-2 right-2 px-2 py-0.5 rounded-md bg-black/70 text-white text-xs font-mono border border-white/15 pointer-events-none">
          <span id="stage-counter">1 / 1</span>
        </div>

        <!-- Speaker Notes Overlay Drawer -->
        <div id="notes-drawer" class="hidden absolute inset-x-0 bottom-0 max-h-[68%] bg-black/90 backdrop-blur-md text-white border-t border-white/20 p-3 z-20 flex flex-col gap-1.5">
          <div class="flex items-center justify-between border-b border-white/15 pb-1">
            <span id="notes-title" class="text-xs font-semibold text-sky-300 truncate">Speaker Notes</span>
            <button id="notes-close" type="button" class="text-xs text-white/70 hover:text-white px-1.5 py-0.5 rounded bg-white/10 cursor-pointer">✕ Close</button>
          </div>
          <div id="notes-content" class="notes-scroll overflow-y-auto text-xs leading-relaxed text-slate-200 whitespace-pre-wrap select-text pr-1"></div>
        </div>

        <!-- Toast Feedback Banner -->
        <div id="toast-banner" class="hidden absolute top-2 left-1/2 -translate-x-1/2 px-3 py-1.5 rounded-lg bg-emerald-600/95 text-white text-xs font-semibold shadow-lg border border-emerald-400/40 z-30 transition-all">
          Copied!
        </div>
      </div>
    </div>

    <!-- Interactive Chapter Scrubber Bar -->
    <div id="scrubber-bar" class="w-full h-2.5 rounded-full bg-[var(--background)] border border-[var(--border)] overflow-hidden flex gap-[1px] p-[1px] cursor-pointer" title="Click to jump to any slide">
    </div>

    <!-- Bottom Controls: Left/Right Cursors + Copy PNG + Paste to Conversation -->
    <div class="flex items-center justify-between gap-2 flex-wrap pt-0.5">
      <div class="flex items-center gap-1">
        <button id="btn-first" type="button" title="First Slide (Home)"
          class="px-2 py-1 rounded-lg text-xs font-medium bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--secondary)] disabled:opacity-40 cursor-pointer">
          ⏮
        </button>
        <button id="btn-prev" type="button" title="Previous Slide (←)"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--secondary)] disabled:opacity-40 cursor-pointer">
          ◀ Prev
        </button>
        <div class="px-2 py-1 rounded-lg text-xs font-mono font-semibold bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] min-w-[64px] text-center">
          <span id="bottom-counter">1 / 1</span>
        </div>
        <button id="btn-next" type="button" title="Next Slide (→)"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--secondary)] disabled:opacity-40 cursor-pointer">
          Next ▶
        </button>
        <button id="btn-last" type="button" title="Last Slide (End)"
          class="px-2 py-1 rounded-lg text-xs font-medium bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)] hover:bg-[var(--secondary)] disabled:opacity-40 cursor-pointer">
          ⏭
        </button>
      </div>

      <div class="flex items-center gap-1.5 flex-wrap flex-1 justify-end">
        <input id="chat-note-input" type="text" placeholder="Optional note for chat..."
          class="bg-[var(--background)] text-[var(--foreground)] placeholder-[var(--muted-foreground)] border border-[var(--border)] rounded-lg px-2.5 py-1 text-xs w-36 sm:w-44 focus:outline-none focus:ring-1 focus:ring-[var(--primary)]" />

        <button id="btn-copy-png" type="button" title="Copy rendered slide as PNG image to clipboard (then ⌘V in chat)"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-[var(--secondary)] text-[var(--secondary-foreground)] border border-[var(--border)] hover:opacity-90 active:scale-95 transition cursor-pointer">
          <span>📋</span>
          <span id="copy-btn-text">Copy PNG</span>
        </button>

        <button id="btn-paste-convo" type="button" title="Send rendered PNG + slide reference directly into the current Antigravity conversation"
          class="inline-flex items-center gap-1 px-3 py-1 rounded-lg text-xs font-semibold bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 active:scale-95 transition shadow-sm cursor-pointer">
          <span>💬</span>
          <span id="paste-btn-text">Paste to Conversation</span>
        </button>
      </div>
    </div>

  </div>

  <canvas id="png-canvas" width="1280" height="720" class="hidden"></canvas>

  <script>
    const SIDECAR_CFG = __SIDECAR_CFG_JSON__;
    const SLIDES = __SLIDES_JSON__;
    const DECK_TITLE = __DECK_TITLE_JSON__;

    let currentIdx = 0;
    let notesOpen = false;
    let toastTimer = null;

    const slideImg = document.getElementById('slide-img');
    const slideSelect = document.getElementById('slide-select');
    const partBadge = document.getElementById('part-badge');
    const stageCounter = document.getElementById('stage-counter');
    const bottomCounter = document.getElementById('bottom-counter');
    const stagePrev = document.getElementById('stage-prev');
    const stageNext = document.getElementById('stage-next');
    const btnFirst = document.getElementById('btn-first');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnLast = document.getElementById('btn-last');
    const btnNotes = document.getElementById('btn-notes');
    const notesDrawer = document.getElementById('notes-drawer');
    const notesTitle = document.getElementById('notes-title');
    const notesContent = document.getElementById('notes-content');
    const notesClose = document.getElementById('notes-close');
    const scrubberBar = document.getElementById('scrubber-bar');
    const btnCopyPng = document.getElementById('btn-copy-png');
    const copyBtnText = document.getElementById('copy-btn-text');
    const btnPasteConvo = document.getElementById('btn-paste-convo');
    const pasteBtnText = document.getElementById('paste-btn-text');
    const chatNoteInput = document.getElementById('chat-note-input');
    const toastBanner = document.getElementById('toast-banner');
    const pngCanvas = document.getElementById('png-canvas');

    function showToast(msg, isError = false) {
      if (toastTimer) clearTimeout(toastTimer);
      toastBanner.textContent = msg;
      toastBanner.className = `absolute top-2 left-1/2 -translate-x-1/2 px-3 py-1.5 rounded-lg text-white text-xs font-semibold shadow-lg border z-30 transition-all ${
        isError ? 'bg-rose-600/95 border-rose-400/40' : 'bg-emerald-600/95 border-emerald-400/40'
      }`;
      toastBanner.classList.remove('hidden');
      toastTimer = setTimeout(() => {
        toastBanner.classList.add('hidden');
      }, 3200);
    }

    function initControls() {
      let currentGroup = null;
      let optGroupEl = null;

      SLIDES.forEach((s, idx) => {
        if (s.part !== currentGroup) {
          currentGroup = s.part;
          optGroupEl = document.createElement('optgroup');
          optGroupEl.label = s.part;
          slideSelect.appendChild(optGroupEl);
        }
        const opt = document.createElement('option');
        opt.value = String(idx);
        opt.textContent = `#${s.num} · ${s.title} (${s.sourceName})`;
        optGroupEl.appendChild(opt);

        const seg = document.createElement('div');
        seg.dataset.idx = String(idx);
        seg.title = `Slide ${s.num}: ${s.title}\n${s.sourceRel}`;
        seg.className = 'h-full flex-1 transition-all duration-150 rounded-[1px]';
        seg.addEventListener('click', () => goToSlide(idx));
        scrubberBar.appendChild(seg);
      });
    }

    function updateScrubber() {
      const children = scrubberBar.children;
      const partColors = {
        1: 'bg-sky-500/45',
        2: 'bg-indigo-500/45',
        3: 'bg-amber-500/45',
        4: 'bg-emerald-500/45',
      };
      const activeColors = {
        1: 'bg-sky-400 ring-1 ring-white',
        2: 'bg-indigo-400 ring-1 ring-white',
        3: 'bg-amber-400 ring-1 ring-white',
        4: 'bg-emerald-400 ring-1 ring-white',
      };
      for (let i = 0; i < children.length; i++) {
        const pIdx = SLIDES[i].partIdx || 1;
        children[i].className = `h-full flex-1 transition-all duration-150 rounded-[1px] ${
          i === currentIdx ? activeColors[pIdx] : partColors[pIdx] + ' hover:opacity-80'
        }`;
      }
    }

    function goToSlide(idx) {
      if (idx < 0 || idx >= SLIDES.length) return;
      currentIdx = idx;
      const s = SLIDES[currentIdx];

      slideImg.src = s.dataUrl;
      slideSelect.value = String(currentIdx);
      partBadge.textContent = s.part;

      const countStr = `${s.num} / ${SLIDES.length}`;
      stageCounter.textContent = countStr;
      bottomCounter.textContent = countStr;

      const isFirst = currentIdx === 0;
      const isLast = currentIdx === SLIDES.length - 1;
      stagePrev.disabled = isFirst;
      btnPrev.disabled = isFirst;
      btnFirst.disabled = isFirst;
      stageNext.disabled = isLast;
      btnNext.disabled = isLast;
      btnLast.disabled = isLast;

      notesTitle.textContent = `📄 ${s.sourceRel}`;
      notesContent.textContent = s.notes ? s.notes : '(No speaker notes on this slide.)';
      const hasNotes = Boolean(s.notes && s.notes.trim());
      document.getElementById('notes-label').textContent = hasNotes ? 'Notes •' : 'Notes';

      updateScrubber();
    }

    function renderCurrentSlideToPng() {
      return new Promise((resolve, reject) => {
        const s = SLIDES[currentIdx];
        const img = new Image();
        img.onload = () => {
          const ctx = pngCanvas.getContext('2d');
          ctx.clearRect(0, 0, pngCanvas.width, pngCanvas.height);
          ctx.drawImage(img, 0, 0, pngCanvas.width, pngCanvas.height);
          const pngDataUrl = pngCanvas.toDataURL('image/png');
          pngCanvas.toBlob((blob) => {
            if (!blob) return reject(new Error('Canvas toBlob failed'));
            resolve({ blob, pngDataUrl, slide: s });
          }, 'image/png');
        };
        img.onerror = () => reject(new Error('Failed to decode slide image'));
        img.src = s.dataUrl;
      });
    }

    async function handleCopyPng() {
      const origLabel = copyBtnText.textContent;
      copyBtnText.textContent = 'Copying...';
      try {
        const { blob, pngDataUrl, slide } = await renderCurrentSlideToPng();
        let copiedImage = false;

        if (navigator.clipboard && window.ClipboardItem) {
          try {
            await navigator.clipboard.write([
              new ClipboardItem({ 'image/png': blob })
            ]);
            copiedImage = true;
          } catch (clipErr) {
            console.warn('ClipboardItem image/png write failed:', clipErr);
          }
        }

        if (copiedImage) {
          copyBtnText.textContent = '✓ Copied PNG!';
          showToast(`✅ Slide #${slide.num} PNG copied to clipboard! Press ⌘V in chat.`);
        } else {
          const mdSnippet = `![Slide ${slide.num} - ${slide.title}](${slide.pngPath})`;
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(mdSnippet);
          }
          const a = document.createElement('a');
          a.href = pngDataUrl;
          a.download = `slide-${String(slide.num).padStart(3, '0')}.png`;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          copyBtnText.textContent = '✓ Saved PNG!';
          showToast(`📥 Downloaded PNG & copied path for Slide #${slide.num}`);
        }
      } catch (err) {
        console.error('Copy PNG error:', err);
        showToast(`❌ Could not copy PNG: ${err.message}`, true);
      } finally {
        setTimeout(() => { copyBtnText.textContent = origLabel; }, 2000);
      }
    }

    function sidecarFetch(path, options = {}) {
      const headers = new Headers(options.headers || {});
      headers.set('Content-Type', 'application/json');
      if (SIDECAR_CFG.token) {
        headers.set('X-Sidecar-Token', SIDECAR_CFG.token);
      }
      const targetUrl = path.startsWith('http')
        ? path
        : SIDECAR_CFG.baseUrl.replace(/\/+$/, '') + (path.startsWith('/') ? path : '/' + path);
      return fetch(targetUrl, { ...options, headers });
    }

    async function resolveProjectId(convId) {
      if (!convId || !SIDECAR_CFG.baseUrl) return '';
      try {
        const res = await sidecarFetch('/_sidecar/get-conversation-metadata', {
          method: 'POST',
          body: JSON.stringify({ conversationId: convId })
        });
        if (!res.ok) return '';
        const data = await res.json();
        const metaEvent = data && data.response && (data.response.conversationMetadata || data.response.conversation_metadata);
        const meta = metaEvent && metaEvent.metadata;
        return (meta && (meta.projectId || meta.project_id)) || '';
      } catch {
        return '';
      }
    }

    async function handlePasteToConvo() {
      const origLabel = pasteBtnText.textContent;
      pasteBtnText.textContent = 'Sending...';
      btnPasteConvo.disabled = true;

      try {
        const { blob, slide } = await renderCurrentSlideToPng();
        const userNote = chatNoteInput.value.trim();

        if (navigator.clipboard && window.ClipboardItem) {
          try {
            await navigator.clipboard.write([
              new ClipboardItem({ 'image/png': blob })
            ]);
          } catch {}
        }

        const lines = [
          `![Slide ${slide.num} — ${slide.title}](${slide.pngPath})`,
          ``,
          `**🎭 ${DECK_TITLE} · Slide #${slide.num} / ${SLIDES.length}**: *${slide.title}*`,
          `- **Source file**: [\`${slide.sourceRel}\`](file://${slide.sourceAbs})`,
        ];
        if (userNote) {
          lines.push(`- **Note**: ${userNote}`);
        }
        const messageContent = lines.join('\n');

        let sentViaSidecar = false;
        if (window.antigravity && typeof window.antigravity.sendMessage === 'function' && SIDECAR_CFG.conversationId) {
          try {
            await window.antigravity.sendMessage(SIDECAR_CFG.conversationId, messageContent);
            sentViaSidecar = true;
          } catch {}
        }

        if (!sentViaSidecar && SIDECAR_CFG.baseUrl && SIDECAR_CFG.conversationId) {
          try {
            const projectId = await resolveProjectId(SIDECAR_CFG.conversationId);
            const res = await sidecarFetch('/_sidecar/send-message', {
              method: 'POST',
              body: JSON.stringify({
                conversationId: SIDECAR_CFG.conversationId,
                message: messageContent,
                projectId
              })
            });
            if (res.ok) {
              sentViaSidecar = true;
            }
          } catch (sidecarErr) {
            console.warn('Sidecar send-message failed:', sidecarErr);
          }
        }

        if (sentViaSidecar) {
          pasteBtnText.textContent = '✓ Sent to Chat!';
          chatNoteInput.value = '';
          showToast(`🚀 Slide #${slide.num} posted directly into the conversation!`);
        } else {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(messageContent);
          }
          pasteBtnText.textContent = '✓ Copied for Chat!';
          showToast(`📋 Slide #${slide.num} copied! Press ⌘V in the chat box below.`);
        }
      } catch (err) {
        console.error('Paste to conversation failed:', err);
        showToast(`❌ Failed: ${err.message}`, true);
      } finally {
        btnPasteConvo.disabled = false;
        setTimeout(() => { pasteBtnText.textContent = origLabel; }, 2200);
      }
    }

    stagePrev.addEventListener('click', () => goToSlide(currentIdx - 1));
    stageNext.addEventListener('click', () => goToSlide(currentIdx + 1));
    btnPrev.addEventListener('click', () => goToSlide(currentIdx - 1));
    btnNext.addEventListener('click', () => goToSlide(currentIdx + 1));
    btnFirst.addEventListener('click', () => goToSlide(0));
    btnLast.addEventListener('click', () => goToSlide(SLIDES.length - 1));

    slideSelect.addEventListener('change', (e) => {
      goToSlide(Number(e.target.value));
    });

    btnNotes.addEventListener('click', () => {
      notesOpen = !notesOpen;
      notesDrawer.classList.toggle('hidden', !notesOpen);
    });
    notesClose.addEventListener('click', () => {
      notesOpen = false;
      notesDrawer.classList.add('hidden');
    });

    btnCopyPng.addEventListener('click', handleCopyPng);
    btnPasteConvo.addEventListener('click', handlePasteToConvo);

    chatNoteInput.addEventListener('keydown', (e) => {
      e.stopPropagation();
      if (e.key === 'Enter') {
        e.preventDefault();
        handlePasteToConvo();
      }
    });

    window.addEventListener('keydown', (e) => {
      if (document.activeElement === chatNoteInput) return;
      if (e.key === 'ArrowLeft' || e.key === 'k' || e.key === 'K') {
        e.preventDefault();
        goToSlide(currentIdx - 1);
      } else if (e.key === 'ArrowRight' || e.key === 'j' || e.key === 'J' || e.key === ' ') {
        e.preventDefault();
        goToSlide(currentIdx + 1);
      } else if (e.key === 'Home') {
        e.preventDefault();
        goToSlide(0);
      } else if (e.key === 'End') {
        e.preventDefault();
        goToSlide(SLIDES.length - 1);
      } else if (e.key === 'n' || e.key === 'N') {
        e.preventDefault();
        notesOpen = !notesOpen;
        notesDrawer.classList.toggle('hidden', !notesOpen);
      }
    });

    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'theme-change' && event.data.payload && event.data.payload.cssVariables) {
        for (const [k, v] of Object.entries(event.data.payload.cssVariables)) {
          document.documentElement.style.setProperty(k, v);
        }
      }
    });

    initControls();
    goToSlide(__INITIAL_SLIDE_IDX__);
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="marpione",
        description="Marpione (marpi1): Build an interactive Marp inline slide widget (<agent-embed>) or JSON payload.",
    )
    parser.add_argument(
        "target",
        help="Path to a Marp .md file (single deck or @import manifest) or directory of rendered slide.*.png images.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output HTML artifact path (defaults to <brain_dir>/marpione-<slug>.html).",
    )
    parser.add_argument(
        "--session-id",
        help="Antigravity conversation/session ID (auto-detected if omitted).",
    )
    parser.add_argument(
        "--title",
        help="Custom deck display title (auto-inferred from deck path if omitted).",
    )
    parser.add_argument(
        "--slide",
        type=int,
        default=1,
        help="Initial 1-based slide number to display (default: 1).",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=82,
        help="WebP compression quality for inline images (default: 82).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON slide payload to stdout instead of writing an HTML file (used by the Aux Pane sidecar).",
    )
    args = parser.parse_args()

    ensure_node_in_path()
    target_path = Path(args.target).expanduser().resolve()
    if not target_path.exists():
        print(f"❌ Error: Target not found: {target_path}", file=sys.stderr)
        sys.exit(1)

    session_id = detect_active_session_id(args.session_id)
    app_data_dir = get_app_data_dir()
    brain_dir = app_data_dir / "brain" / session_id
    if not brain_dir.is_dir():
        brain_dir = Path(tempfile.gettempdir()) / f"marpione_{session_id}"
        brain_dir.mkdir(parents=True, exist_ok=True)

    if target_path.is_dir():
        slug = target_path.name
        slides_dir = target_path
        compiled_md = target_path / "slides.md"
        png_files = sorted(target_path.glob("slide.*.png"))
        if not png_files:
            print(f"❌ Error: No slide.*.png found in directory {target_path}", file=sys.stderr)
            sys.exit(1)
    else:
        parent_name = target_path.parent.name
        slug = parent_name if target_path.stem == "slides" and parent_name != "slides" else target_path.stem
        slides_dir = find_slides_root(target_path)
        work_dir = Path(tempfile.gettempdir()) / "marpione_work"
        work_dir.mkdir(parents=True, exist_ok=True)
        compiled_md = compile_manifest_if_needed(target_path, slides_dir, work_dir)
        png_files = render_marp_to_pngs(compiled_md, slides_dir)

    deck_title = args.title or slug.replace("_", " ").replace("-", " ").title()
    brain_slides_dir = brain_dir / f"slides_{slug}"

    slides_data = build_slides_payload(
        compiled_md=compiled_md,
        png_files=png_files,
        slides_dir=slides_dir,
        brain_slides_dir=brain_slides_dir,
        quality=args.quality,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "deckTitle": deck_title,
                    "sessionId": session_id,
                    "count": len(slides_data),
                    "slides": slides_data,
                }
            )
        )
        return

    sidecar_cfg = discover_sidecar_config(session_id)
    out_html = Path(args.output).expanduser().resolve() if args.output else (brain_dir / f"marpione-{slug}.html")
    out_html.parent.mkdir(parents=True, exist_ok=True)

    initial_idx = max(0, min(len(slides_data) - 1, args.slide - 1))

    html = (
        HTML_TEMPLATE.replace("__DECK_TITLE__", deck_title)
        .replace("__DECK_TITLE_JSON__", json.dumps(deck_title).replace("</", "<\\/"))
        .replace("__SIDECAR_CFG_JSON__", json.dumps(sidecar_cfg).replace("</", "<\\/"))
        .replace("__SLIDES_JSON__", json.dumps(slides_data).replace("</", "<\\/"))
        .replace("__INITIAL_SLIDE_IDX__", str(initial_idx))
    )

    out_html.write_text(html, encoding="utf-8")
    size_mb = out_html.stat().st_size / (1024 * 1024)
    print(f"✅ Marpione built {len(slides_data)} slides ({size_mb:.2f} MB)")
    print(f"   📄 Artifact: {out_html}")
    print(f"   🖼️  PNG dir:  {brain_slides_dir}")
    print(f'   🔗 Embed:    <agent-embed src="file://{out_html}"></agent-embed>')


if __name__ == "__main__":
    main()
