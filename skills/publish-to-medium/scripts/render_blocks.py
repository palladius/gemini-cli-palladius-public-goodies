#!/usr/bin/env python3
"""Local Offline-Cached Rasterizer for Mermaid Diagrams and LaTeX Math -> High-DPI PNG.

Designed for blog cross-posting targets (Medium, LinkedIn Articles, Dev.to) that do not
natively render ```mermaid fences or LaTeX math ($...$ / $$...$$).

Privacy & Portability Guarantees:
  - Zero diagram or formula source text is ever sent to external APIs (e.g. no mermaid.ink).
  - Mermaid JS is downloaded at most once into `~/.cache/publish-to-medium/mermaid.min.js`
    and executed locally inside headless Chrome/Chromium (`file://`) + cropped via ImageMagick.
  - LaTeX math renders locally via `pdflatex` + `pdftoppm` (300 DPI) when installed, falling
    back to headless Chrome + locally cached KaTeX.
"""
from __future__ import annotations

import hashlib
import html as html_lib
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from pathlib import Path


MERMAID_CDN_URL = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
KATEX_JS_CDN_URL = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"


def cache_dir() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "publish-to-medium"
    base.mkdir(parents=True, exist_ok=True)
    return base


def ensure_cached_asset(filename: str, url: str) -> Path:
    dest = cache_dir() / filename
    if dest.is_file() and dest.stat().st_size > 1024:
        return dest
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (publish-to-medium/1.0)"})
    with urllib.request.urlopen(req, timeout=20.0) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return dest


def find_chrome_binary() -> str | None:
    for cand in (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ):
        found = shutil.which(cand) if not cand.startswith("/") else (cand if os.access(cand, os.X_OK) else None)
        if found:
            return found
    return None


def find_magick_binary() -> list[str] | None:
    if shutil.which("magick"):
        return ["magick"]
    if shutil.which("convert"):
        return ["convert"]
    return None


def trim_and_pad_png(png_path: Path, pad_px: int = 28) -> None:
    magick = find_magick_binary()
    if not magick or not png_path.is_file():
        return
    tmp_out = png_path.with_suffix(".trimmed.png")
    subprocess.run(
        [
            *magick,
            str(png_path),
            "-background",
            "white",
            "-alpha",
            "remove",
            "-alpha",
            "off",
            "-fuzz",
            "2%",
            "-trim",
            "+repage",
            "-bordercolor",
            "white",
            "-border",
            f"{pad_px}x{pad_px}",
            str(tmp_out),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    tmp_out.replace(png_path)


def render_mermaid_to_png(mermaid_code: str, out_png: Path) -> bool:
    """Renders a Mermaid diagram locally to a crisp 2x Retina PNG on white background."""
    chrome = find_chrome_binary()
    if not chrome:
        return False
    out_png.parent.mkdir(parents=True, exist_ok=True)
    mermaid_js = ensure_cached_asset("mermaid.min.js", MERMAID_CDN_URL)

    html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {{
    margin: 0;
    padding: 40px;
    background: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }}
  #container {{
    display: inline-block;
    background: #ffffff;
    padding: 16px;
  }}
</style>
<script src="{mermaid_js.as_uri()}"></script>
</head>
<body>
  <div id="container">
    <pre class="mermaid">{html_lib.escape(mermaid_code.strip())}</pre>
  </div>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'default',
      securityLevel: 'strict',
      flowchart: {{ htmlLabels: true, curve: 'basis' }}
    }});
  </script>
</body>
</html>
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_html = Path(tmpdir) / "diagram.html"
        raw_shot = Path(tmpdir) / "raw.png"
        tmp_html.write_text(html_doc, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--force-device-scale-factor=3",
                "--window-size=2400,2000",
                "--virtual-time-budget=3000",
                f"--screenshot={raw_shot}",
                tmp_html.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        if not raw_shot.is_file():
            return False
        shutil.copy2(raw_shot, out_png)
    trim_and_pad_png(out_png, pad_px=28)
    return out_png.is_file() and out_png.stat().st_size > 500


def render_latex_to_png(latex_expr: str, out_png: Path, display_mode: bool = True) -> bool:
    """Renders a LaTeX math expression locally to a high-DPI PNG on white background."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    clean_expr = latex_expr.strip()
    if not clean_expr:
        return False

    # Engine 1: Native pdflatex + pdftoppm (300 DPI vector-sharp Computer Modern math)
    if shutil.which("pdflatex") and shutil.which("pdftoppm"):
        math_body = f"$\\displaystyle {clean_expr}$" if display_mode else f"${clean_expr}$"
        tex_src = (
            "\\documentclass[border=10pt]{standalone}\n"
            "\\usepackage[utf8]{inputenc}\n"
            "\\usepackage{amsmath,amssymb,amsfonts,bm}\n"
            "\\begin{document}\n"
            f"{math_body}\n"
            "\\end{document}\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "eq.tex"
            pdf_file = Path(tmpdir) / "eq.pdf"
            png_prefix = Path(tmpdir) / "eq_out"
            tex_file.write_text(tex_src, encoding="utf-8")
            res = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "eq.tex"],
                cwd=tmpdir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=20,
            )
            if res.returncode == 0 and pdf_file.is_file():
                subprocess.run(
                    ["pdftoppm", "-png", "-r", "300", "-singlefile", str(pdf_file), str(png_prefix)],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=15,
                )
                gen_png = Path(f"{png_prefix}.png")
                if gen_png.is_file():
                    shutil.copy2(gen_png, out_png)
                    trim_and_pad_png(out_png, pad_px=20)
                    return True

    # Engine 2: Headless Chrome + cached KaTeX fallback
    chrome = find_chrome_binary()
    if not chrome:
        return False
    katex_js = ensure_cached_asset("katex.min.js", KATEX_JS_CDN_URL)
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script src="{katex_js.as_uri()}"></script>
<style>
  html, body {{ margin: 0; padding: 40px; background: #ffffff; }}
  #math {{ display: inline-block; font-size: 28px; color: #111; padding: 12px; background: #fff; }}
</style>
</head>
<body>
  <div id="math"></div>
  <script>
    katex.render({repr(clean_expr)}, document.getElementById('math'), {{
      displayMode: {'true' if display_mode else 'false'},
      throwOnError: false
    }});
  </script>
</body>
</html>
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_html = Path(tmpdir) / "math.html"
        raw_shot = Path(tmpdir) / "raw.png"
        tmp_html.write_text(html_doc, encoding="utf-8")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--force-device-scale-factor=2",
                "--window-size=1400,800",
                "--virtual-time-budget=2000",
                f"--screenshot={raw_shot}",
                tmp_html.as_uri(),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=20,
        )
        if raw_shot.is_file():
            shutil.copy2(raw_shot, out_png)
            trim_and_pad_png(out_png, pad_px=20)
            return True
    return False


def rasterize_markdown_mermaid_and_math(
    md_text: str,
    rendered_dir: Path,
    rel_img_prefix: str = "rendered",
) -> tuple[str, list[Path]]:
    """Replaces ```mermaid blocks and $$...$$ (plus non-trivial inline $...$) math in Markdown
    with standard Markdown image references `![Caption](rendered/...)`, caching by SHA-256 hash
    so unchanged diagrams/equations render in 0ms on rebuilds!
    """
    rendered_dir.mkdir(parents=True, exist_ok=True)
    generated_files: list[Path] = []

    # Protect non-mermaid fenced code blocks and inline code spans first so `$` inside code is untouched!
    protected_blocks: list[str] = []

    def _save_non_mermaid_fence(match: re.Match[str]) -> str:
        lang = (match.group(1) or "").strip().lower()
        if lang == "mermaid":
            return match.group(0)
        protected_blocks.append(match.group(0))
        return f"@@RASTER_PROTECT_BLOCK_{len(protected_blocks) - 1}@@"

    work = re.sub(
        r"^[ \t]*```([a-zA-Z0-9_-]*)\n(.*?)\n[ \t]*```",
        _save_non_mermaid_fence,
        md_text,
        flags=re.MULTILINE | re.DOTALL,
    )

    protected_inline: list[str] = []

    def _save_inline_code(match: re.Match[str]) -> str:
        protected_inline.append(match.group(0))
        return f"@@RASTER_PROTECT_INLINE_{len(protected_inline) - 1}@@"

    work = re.sub(r"`[^`\n]+`", _save_inline_code, work)

    # 1. Rasterize ```mermaid fences
    def _replace_mermaid(match: re.Match[str]) -> str:
        code = match.group(1).strip()
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()[:10]
        fname = f"mermaid_{digest}.png"
        out_png = rendered_dir / fname
        if not out_png.is_file():
            ok = render_mermaid_to_png(code, out_png)
            if not ok:
                return match.group(0)
        generated_files.append(out_png)
        first_line = code.splitlines()[0].strip() if code.splitlines() else "Diagram"
        kind = "Sequence Diagram" if "sequenceDiagram" in first_line else "Architecture Diagram"
        return f"![{kind}]({rel_img_prefix}/{fname})"

    work = re.sub(
        r"^[ \t]*```mermaid[ \t]*\n(.*?)\n[ \t]*```",
        _replace_mermaid,
        work,
        flags=re.MULTILINE | re.DOTALL,
    )

    # 2. Rasterize display math $$...$$
    def _replace_display_math(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        if not expr:
            return match.group(0)
        digest = hashlib.sha256(f"display:{expr}".encode("utf-8")).hexdigest()[:10]
        fname = f"math_{digest}.png"
        out_png = rendered_dir / fname
        if not out_png.is_file():
            ok = render_latex_to_png(expr, out_png, display_mode=True)
            if not ok:
                return match.group(0)
        generated_files.append(out_png)
        short_alt = re.sub(r"\s+", " ", expr)[:80]
        return f"\n\n![Formula: {short_alt}]({rel_img_prefix}/{fname})\n\n"

    work = re.sub(r"\$\$\s*(.+?)\s*\$\$", _replace_display_math, work, flags=re.DOTALL)

    # 3. Rasterize genuine inline LaTeX math $...$ containing LaTeX commands (\frac, \sum, ^, _, etc.)
    #    while strictly ignoring currency ($5, $100) and plain numbers!
    def _replace_inline_math(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        # Require at least one genuine LaTeX math token (\cmd, ^, _, \alpha, etc.) and reject currency
        if re.match(r"^\d", expr) or not re.search(r"(\\[a-zA-Z]+|[\^_{}])", expr):
            return match.group(0)
        digest = hashlib.sha256(f"inline:{expr}".encode("utf-8")).hexdigest()[:10]
        fname = f"math_inline_{digest}.png"
        out_png = rendered_dir / fname
        if not out_png.is_file():
            ok = render_latex_to_png(expr, out_png, display_mode=False)
            if not ok:
                return match.group(0)
        generated_files.append(out_png)
        return f"![{expr}]({rel_img_prefix}/{fname})"

    work = re.sub(r"(?<!\$)\$(?!\$)([^\$\n]{2,160}?)(?<!\$)\$(?!\$)", _replace_inline_math, work)

    # Restore inline code and non-mermaid fences
    for idx, val in enumerate(protected_inline):
        work = work.replace(f"@@RASTER_PROTECT_INLINE_{idx}@@", val)
    for idx, val in enumerate(protected_blocks):
        work = work.replace(f"@@RASTER_PROTECT_BLOCK_{idx}@@", val)

    return work, generated_files


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rasterize Mermaid and LaTeX math blocks in Markdown to PNGs.")
    parser.add_argument("--input-md", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--rendered-dir", required=True)
    parser.add_argument("--rel-prefix", default="rendered")
    args = parser.parse_args()

    src = Path(args.input_md).read_text(encoding="utf-8")
    out_md, files = rasterize_markdown_mermaid_and_math(src, Path(args.rendered_dir), args.rel_prefix)
    Path(args.output_md).write_text(out_md, encoding="utf-8")
    print(f"Rasterized {len(files)} Mermaid/Math blocks into {args.rendered_dir}")
