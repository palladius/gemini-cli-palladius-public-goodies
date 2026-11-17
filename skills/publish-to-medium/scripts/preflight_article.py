#!/usr/bin/env python3
"""Deterministic Pre-Flight Auditor for Medium & LinkedIn Article Cross-Posting.

Zero external dependencies (Python 3 stdlib only).
Checks compiled HTML (or Markdown) for broken/localhost images, relative links,
corrupted <pre><code> blocks, unrendered Mermaid/LaTeX/tables/MP4s, and optional
HTTP 200 reachability of remote assets and canonical URL.
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_PRIVATE_PATTERNS = [
    (r"\bsso://[^\s\"'<>)]+", "Internal sso:// URI"),
    (r"https?://[^\s\"'<>)]*\.corp\.[^\s\"'<>)]*", "Internal .corp hostname"),
    (r"https?://localhost(?::\d+)?[^\s\"'<>)]*", "Localhost URL"),
    (r"https?://127\.0\.0\.1(?::\d+)?[^\s\"'<>)]*", "Loopback 127.0.0.1 URL"),
]


def http_head_or_get(url: str, timeout: float = 8.0) -> tuple[bool, int, str]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; publish-to-medium-preflight/0.1)"}
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if 200 <= resp.status < 400:
                    return True, resp.status, f"HTTP {resp.status}"
                return False, resp.status, f"HTTP {resp.status}"
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (403, 405, 406):
                continue
            return False, exc.code, f"HTTP {exc.code}"
        except Exception as exc:
            return False, 0, str(exc)
    return False, 0, "Unreachable"


def extract_metadata_from_html(raw_html: str) -> dict[str, Any]:
    title = ""
    canonical = ""
    topics: list[str] = []

    m_data_title = re.search(r'data-title="([^"]+)"', raw_html)
    m_title = re.search(r"<title>(.*?)</title>", raw_html, re.DOTALL | re.IGNORECASE)
    if m_data_title:
        title = html_lib.unescape(m_data_title.group(1)).strip()
    elif m_title:
        title = html_lib.unescape(m_title.group(1)).strip()

    m_data_canon = re.search(r'data-canonical-url="([^"]+)"', raw_html)
    m_link_canon = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', raw_html, re.IGNORECASE)
    if m_data_canon:
        canonical = html_lib.unescape(m_data_canon.group(1)).strip()
    elif m_link_canon:
        canonical = html_lib.unescape(m_link_canon.group(1)).strip()

    m_data_topics = re.search(r'data-topics="([^"]*)"', raw_html)
    m_banner_topics = re.search(r"<strong>Topics[^<]*</strong>\s*(?:<span[^>]*>)?([^<\n]+)", raw_html, re.IGNORECASE)
    raw_topics = ""
    if m_data_topics:
        raw_topics = html_lib.unescape(m_data_topics.group(1))
    elif m_banner_topics:
        raw_topics = html_lib.unescape(m_banner_topics.group(1))

    if raw_topics and raw_topics.lower() != "none specified":
        topics = [t.strip() for t in raw_topics.split(",") if t.strip()][:5]

    return {
        "title": title,
        "canonical_url": canonical,
        "topics": topics,
    }


def isolate_story_body(raw_html: str) -> str:
    """Extract #medium-story-body if present; otherwise strip <head> and helper aside."""
    m = re.search(
        r'<article[^>]+id="medium-story-body"[^>]*>(.*?)</article>',
        raw_html,
        re.DOTALL | re.IGNORECASE,
    )
    if m:
        return m.group(1)
    body_m = re.search(r"<body[^>]*>(.*?)</body>", raw_html, re.DOTALL | re.IGNORECASE)
    body = body_m.group(1) if body_m else raw_html
    body = re.sub(r'<aside[^>]+id="medium-meta-banner".*?</aside>', "", body, flags=re.DOTALL | re.IGNORECASE)
    return body


def audit_html(
    html_path: Path,
    canonical_override: str | None = None,
    platform: str = "medium",
    check_remote: bool = False,
) -> dict[str, Any]:
    raw_html = html_path.read_text(encoding="utf-8")
    meta = extract_metadata_from_html(raw_html)
    if canonical_override:
        meta["canonical_url"] = canonical_override

    story_html = isolate_story_body(raw_html)
    blockers: list[str] = []
    warnings: list[str] = []

    # 1. Private / localhost leaks
    for pattern, label in DEFAULT_PRIVATE_PATTERNS:
        for match in re.findall(pattern, story_html, flags=re.IGNORECASE):
            blockers.append(f"{label} found in story body: {match}")

    # 2. Placeholders & nested <p><p>
    if "TODO_MEDIUM_URL" in story_html:
        blockers.append("Unresolved placeholder 'TODO_MEDIUM_URL' in story body.")
    if re.search(r"<p>\s*<p>", story_html, re.IGNORECASE):
        warnings.append("Nested <p><p> tags detected in story HTML.")
    if "Note for Medium: replace with YouTube embed link!" in story_html:
        warnings.append(
            "Video placeholder '(Note for Medium: replace with YouTube embed link!)' present — "
            "upload MP4 to YouTube or remove note before publishing."
        )

    # 3. Corrupted HTML tags inside <pre><code>
    for pre_block in re.findall(r"<pre><code[^>]*>(.*?)</code></pre>", story_html, flags=re.DOTALL | re.IGNORECASE):
        if re.search(r"<(?:em|strong|a)\b", pre_block, re.IGNORECASE):
            blockers.append(
                "Corrupted inline HTML (<em/strong/a>) detected inside <pre><code> block! "
                "Rebuild with protected code-block placeholders."
            )
            break
        first_line = html_lib.unescape(pre_block.strip().splitlines()[0]) if pre_block.strip() else ""
        if re.match(r"^(?:graph\s+(?:TD|LR|TB|BT)|flowchart\s+|sequenceDiagram|classDiagram|stateDiagram|erDiagram)", first_line):
            warnings.append(
                f"Unrendered Mermaid diagram in <pre><code> ('{first_line[:35]}...'): "
                f"{platform.title()} does not render Mermaid — pre-render to PNG image."
            )

    # 4. Images & GIFs audit
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', story_html, flags=re.IGNORECASE)
    remote_results: list[dict[str, str]] = []
    for src in imgs:
        if not src.startswith(("http://", "https://")):
            blockers.append(f"Relative <img src='{src}'> cannot be fetched by {platform.title()} — must be absolute https:// URL.")
            continue
        if check_remote:
            ok, _code, detail = http_head_or_get(src)
            remote_results.append({"kind": "image", "url": src, "status": detail, "ok": "true" if ok else "false"})
            if not ok:
                blockers.append(f"Remote image broken/unreachable ({detail}): {src}")

    # 5. Links audit (relative check + remote HTTP 404/410/DNS check)
    links = re.findall(r'<a[^>]+href="([^"]+)"', story_html, flags=re.IGNORECASE)
    checked_hrefs: set[str] = set()
    for href in links:
        if not href.startswith(("http://", "https://", "mailto:", "#")):
            blockers.append(f"Relative <a href='{href}'> will 404 on {platform.title()} — convert to absolute URL.")
            continue
        if check_remote and href.startswith(("http://", "https://")) and href not in checked_hrefs:
            checked_hrefs.add(href)
            ok, code, detail = http_head_or_get(href)
            # Ignore anti-bot walls (401/403/429/999 e.g. LinkedIn/X), but block real 404/410/5xx/DNS errors
            if not ok and code not in (401, 403, 429, 999):
                remote_results.append({"kind": "link", "url": href, "status": detail, "ok": "false"})
                blockers.append(f"Broken outbound link ({detail}): {href}")
            else:
                remote_results.append({"kind": "link", "url": href, "status": detail, "ok": "true"})

    # 6. Canonical URL check
    canonical_url = meta.get("canonical_url", "")
    if not canonical_url:
        warnings.append("No canonical_url specified (required on Medium to preserve primary blog SEO).")
    elif check_remote and canonical_url.startswith(("http://", "https://")):
        ok, _code, detail = http_head_or_get(canonical_url)
        remote_results.append({"kind": "canonical", "url": canonical_url, "status": detail, "ok": "true" if ok else "false"})
        if not ok:
            warnings.append(
                f"Canonical URL not yet HTTP 200 ({detail}): {canonical_url} "
                "(Method A URL import requires live URL; Method B HTML paste works locally)."
            )

    # 7. Tables, <video>, and LaTeX checks
    table_count = len(re.findall(r"<table\b", story_html, flags=re.IGNORECASE))
    if table_count:
        warnings.append(
            f"{table_count} HTML <table> element(s) found: {platform.title()} flattens/strips tables — "
            "convert to bullet list or PNG screenshot."
        )
    if re.search(r"<video\b", story_html, flags=re.IGNORECASE):
        warnings.append(f"<video> tag found: {platform.title()} strips raw <video> embeds — use YouTube link.")

    prose_no_code = re.sub(r"<pre>.*?</pre>|<code>.*?</code>", "", story_html, flags=re.DOTALL | re.IGNORECASE)
    if re.search(r"\$\$[\s\S]+?\$\$|\$[^$\n]*\\[a-zA-Z]+[^$\n]*\$", prose_no_code):
        warnings.append(f"LaTeX math ($...$ / $$...$$) detected: {platform.title()} does not render KaTeX/MathJax.")

    if len(meta["topics"]) == 0:
        warnings.append("Zero topics/tags extracted (Medium supports up to 5 discovery topics).")

    return {
        "ok": len(blockers) == 0,
        "platform": platform,
        "html_path": str(html_path),
        "metadata": meta,
        "stats": {
            "images": len(imgs),
            "gifs": sum(1 for i in imgs if i.lower().endswith(".gif")),
            "links": len(links),
            "tables": table_count,
            "code_blocks": len(re.findall(r"<pre><code", story_html, flags=re.IGNORECASE)),
        },
        "remote_checks": remote_results,
        "blockers": blockers,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-flight validator for Medium & LinkedIn Article HTML.")
    parser.add_argument("--html", required=True, help="Path to compiled index.html (e.g. out/medium/index.html)")
    parser.add_argument("--canonical-url", default=None, help="Expected canonical URL of the primary blog post")
    parser.add_argument("--platform", choices=["medium", "linkedin", "all"], default="medium")
    parser.add_argument("--check-remote", action="store_true", help="Perform HTTP HEAD/GET checks on images and canonical URL")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    args = parser.parse_args()

    html_path = Path(args.html).expanduser().resolve()
    if not html_path.exists():
        print(f"❌ HTML file not found: {html_path}", file=sys.stderr)
        return 2

    report = audit_html(
        html_path=html_path,
        canonical_override=args.canonical_url,
        platform=args.platform,
        check_remote=args.check_remote,
    )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        meta = report["metadata"]
        stats = report["stats"]
        status_icon = "✅ PASS (Ready for Draft Import)" if report["ok"] else "❌ BLOCKED (Fix Blockers First)"
        print(f"=== 📰 Cross-Post Pre-Flight Report [{report['platform'].upper()}]: {status_icon} ===")
        print(f"  Title:         {meta['title']}")
        print(f"  Canonical URL: {meta['canonical_url'] or '(unset)'}")
        print(f"  Topics (<=5):  {', '.join(meta['topics']) if meta['topics'] else '(none)'}")
        print(
            f"  Elements:      {stats['images']} img ({stats['gifs']} gif), "
            f"{stats['code_blocks']} code blocks, {stats['links']} links, {stats['tables']} tables"
        )
        if report["blockers"]:
            print(f"\n❌ BLOCKERS ({len(report['blockers'])}):")
            for b in report["blockers"]:
                print(f"  - {b}")
        if report["warnings"]:
            print(f"\n⚠️  PLATFORM WARNINGS ({len(report['warnings'])}):")
            for w in report["warnings"]:
                print(f"  - {w}")
        if not report["blockers"] and not report["warnings"]:
            print("\n🎉 Zero blockers and zero warnings!")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
