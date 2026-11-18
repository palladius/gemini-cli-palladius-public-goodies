#!/usr/bin/env python3
"""Deterministic 2x Retina renderer for Engine 2 (Bipartite M*N vs M+N) & Engine 3 (Multi-Tab Contrast Cards).

Usage:
  python3 render_slide_diagram.py --mode multitab  --spec spec.json --out /tmp/multitab.png
  python3 render_slide_diagram.py --mode bipartite --spec spec.json --out /tmp/bipartite.png
  python3 render_slide_diagram.py --demo-multitab  --out /tmp/demo_multitab.png
  python3 render_slide_diagram.py --demo-bipartite --out /tmp/demo_bipartite.png

Renders a 1232x560 CSS viewport at deviceScaleFactor=2 -> 2464x1120 PNG (~2.2:1 slide-body ratio)
using local headless Chrome/Chromium, and runs an automatic DOM audit (font >= 18px, zero overflow)
before saving the PNG. Falls back to writing a standalone .svg/.html when no browser is installed.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

W, H = 1232, 560

PALETTE = {
    "red": ("#C5221F", "#FFF8F7", "#FDE7E5"),
    "amber": ("#B06000", "#FFFAEE", "#FEF3C7"),
    "green": ("#188038", "#F1FAF3", "#E6F4EA"),
    "blue": ("#1A73E8", "#F5F9FF", "#E8F0FE"),
    "purple": ("#8430CE", "#FBF7FF", "#F3E8FD"),
    "slate": ("#334155", "#F8FAFC", "#E2E8F0"),
}

AUDIT_JS = """
<script>
window.addEventListener('load', () => {
  const issues = [];
  const W = %d, H = %d;
  const root = document.querySelector('.outer') || document.body;
  root.querySelectorAll('*:not(script):not(style)').forEach(el => {
    const cs = getComputedStyle(el);
    const txt = (el.childNodes.length === 1 && el.childNodes[0].nodeType === 3)
      ? el.childNodes[0].textContent.trim() : '';
    if (txt) {
      const fs = parseFloat(cs.fontSize);
      if (fs < 17.5) issues.push('FONT_TOO_SMALL(' + fs + 'px): ' + txt.slice(0, 40));
    }
    const r = el.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) {
      if (r.right > W + 2 || r.bottom > H + 2) {
        issues.push('CLIPPED(' + el.className + '): right=' + Math.round(r.right) + ' bottom=' + Math.round(r.bottom));
      }
      if (el.scrollHeight > el.clientHeight + 3 && cs.overflow !== 'visible') {
        issues.push('OVERFLOW_Y(' + el.className + ')');
      }
      if (el.scrollWidth > el.clientWidth + 3 && cs.overflow !== 'visible') {
        issues.push('OVERFLOW_X(' + el.className + '): ' + el.scrollWidth + '>' + el.clientWidth);
      }
    }
  });
  const pre = document.createElement('pre');
  pre.id = 'dom_audit_report';
  pre.style.display = 'none';
  pre.textContent = JSON.stringify(issues);
  document.body.appendChild(pre);
});
</script>
""" % (W, H)


def find_chrome() -> str | None:
    for candidate in ("google-chrome", "chromium", "chromium-browser",
                      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        found = shutil.which(candidate)
        if found:
            return found
        if Path(candidate).is_file():
            return candidate
    return None


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def build_multitab_html(spec: dict, include_audit: bool = False) -> str:
    title = esc(spec.get("title", "Multi-Column Comparison"))
    subtitle = esc(spec.get("subtitle", ""))
    title_tone = spec.get("title_tone", "green")
    title_color = PALETTE.get(title_tone, PALETTE["green"])[0]

    cols_html: list[str] = []
    columns = spec.get("columns", [])
    for idx, col in enumerate(columns):
        tone = col.get("tone", "slate")
        stroke, bg, foot_bg = PALETTE.get(tone, PALETTE["slate"])
        badge_txt = col.get("badge", "")
        badge_html = (
            f'<span class="badge" style="background:{stroke};">{esc(badge_txt)}</span>'
            if badge_txt else ""
        )
        col_title = esc(col.get("title", ""))
        col_sub = f'<div class="cs">{esc(col["subtitle"])}</div>' if col.get("subtitle") else ""

        body_parts: list[str] = []
        if col.get("code"):
            body_parts.append(f'<div class="code">{esc(col["code"])}</div>')
        if col.get("caption"):
            body_parts.append(f'<div class="caption">{esc(col["caption"])}</div>')

        steps = col.get("steps", [])
        for s_idx, step in enumerate(steps):
            if isinstance(step, dict) and step.get("code"):
                body_parts.append(f'<div class="code">{esc(step["code"])}</div>')
            else:
                label = step.get("label", "") if isinstance(step, dict) else str(step)
                sub = step.get("sub", "") if isinstance(step, dict) else ""
                if sub:
                    body_parts.append(
                        f'<div class="bullet"><span class="dot" style="background:{stroke};">×</span>'
                        f'<div><div class="bt">{esc(label)}</div><div class="cs">{esc(sub)}</div></div></div>'
                    )
                else:
                    body_parts.append(
                        f'<div class="chip"><span class="mini-dot" style="background:{stroke};"></span>'
                        f'<span>{esc(label)}</span></div>'
                    )
            if col.get("flow_arrows", False) and s_idx < len(steps) - 1:
                body_parts.append('<div class="down">↓</div>')

        foot_html = (
            f'<div class="foot" style="background:{foot_bg};">{esc(col["footer"])}</div>'
            if col.get("footer") else ""
        )
        width_style = f'flex: 0 0 {int(col["width_px"])}px;' if col.get("width_px") else "flex: 1;"
        title_col = f'color:{stroke};' if not badge_txt else ""
        cols_html.append(
            f'<div class="card" style="{width_style}border-color:{stroke};background:{bg};">'
            f'<div class="ct" style="{title_col}">{badge_html}<span>{col_title}</span></div>'
            f'{col_sub}{"".join(body_parts)}{foot_html}</div>'
        )
        if col.get("arrow_after"):
            cols_html.append('<div class="col-arrow">→</div>')

    audit_tag = AUDIT_JS if include_audit else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #FFFFFF;
                font-family: 'Inter', 'Roboto', 'DejaVu Sans', sans-serif; }}
  .outer {{ width: {W}px; height: {H}px; background: #F8FAFC; border: 2px solid #CBD5E1;
            border-radius: 20px; padding: 14px 18px 16px; display: flex; flex-direction: column; gap: 10px; }}
  .hdr {{ display: flex; align-items: baseline; gap: 16px; white-space: nowrap; }}
  .hdr-t {{ font-size: 30px; font-weight: 800; line-height: 1.15; color: {title_color}; }}
  .hdr-s {{ font-size: 20px; font-weight: 600; color: #475569; }}
  .row {{ display: flex; gap: 12px; flex: 1; min-height: 0; align-items: stretch; }}
  .col-arrow {{ display: flex; align-items: center; font-size: 26px; font-weight: 800; color: #64748B; }}
  .card {{ border: 2.5px solid #CBD5E1; border-radius: 16px; padding: 10px 12px;
           display: flex; flex-direction: column; gap: 7px; min-width: 0; }}
  .ct {{ display: flex; align-items: center; gap: 9px; font-size: 21px; font-weight: 800; color: #0F172A; line-height: 1.15; }}
  .cs {{ font-size: 18px; font-weight: 600; color: #475569; line-height: 1.22; }}
  .badge {{ flex: 0 0 30px; width: 30px; height: 30px; border-radius: 50%; color: #FFFFFF; font-size: 18px;
            font-weight: 800; display: flex; align-items: center; justify-content: center; }}
  .code {{ font-family: 'JetBrains Mono', 'DejaVu Sans Mono', 'Roboto Mono', monospace; font-size: 18px;
           line-height: 1.28; white-space: pre-wrap; word-break: break-word; overflow: hidden; color: #0F172A; background: #FFFFFF;
           border: 1.5px solid #CBD5E1; border-radius: 10px; padding: 6px 9px; }}
  .caption {{ font-size: 18px; font-weight: 700; color: #475569; text-align: center; }}
  .chip {{ display: flex; align-items: center; gap: 8px; background: #FFFFFF; border: 1.5px solid #CBD5E1;
           border-radius: 10px; padding: 5px 10px; font-size: 18.5px; font-weight: 700; color: #1E293B; white-space: nowrap; }}
  .mini-dot {{ width: 10px; height: 10px; border-radius: 50%; flex: 0 0 10px; }}
  .bullet {{ display: flex; gap: 9px; align-items: flex-start; }}
  .dot {{ width: 24px; height: 24px; border-radius: 50%; color: #FFFFFF; font-size: 18px; font-weight: 800;
          display: flex; align-items: center; justify-content: center; flex: 0 0 24px; margin-top: 2px; }}
  .bt {{ font-size: 19px; font-weight: 800; color: #0F172A; line-height: 1.15; }}
  .down {{ text-align: center; font-size: 19px; font-weight: 900; color: #64748B; line-height: 1.0; }}
  .foot {{ margin-top: auto; font-size: 18px; font-weight: 700; color: #0F172A; border-radius: 10px;
           padding: 6px 10px; line-height: 1.22; }}
</style></head>
<body><div class="outer">
  <div class="hdr"><span class="hdr-t">{title}</span><span class="hdr-s">{subtitle}</span></div>
  <div class="row">{"".join(cols_html)}</div>
</div>{audit_tag}</body></html>"""


def build_bipartite_svg(spec: dict) -> str:
    left_nodes = spec.get("left_nodes", [])
    right_nodes = spec.get("right_nodes", [])
    hub = spec.get("hub", {"title": "MCP", "subtitle": "Protocol hub", "pills": ["Tools", "Resources", "Prompts"]})
    m, n = len(left_nodes), len(right_nodes)
    left_title = esc(spec.get("before_title", f"Before: {m} × {n} spaghetti"))
    right_title = esc(spec.get("after_title", f"After: {m} + {n} one standard"))
    left_summary = esc(spec.get("before_summary", f"{m} × {n} = {m * n} custom integrations"))
    right_summary = esc(spec.get("after_summary", f"{m} + {n} = {m + n} standard connectors"))

    def node_box(x: int, y: int, w: int, h: int, item: dict, stroke: str, sub_col: str) -> str:
        name = esc(item.get("name", ""))
        role = esc(item.get("role", ""))
        badge_bg = esc(item.get("color", stroke))
        monogram = esc(item.get("monogram", name[:2].upper()))
        return (
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FFFFFF" stroke="{stroke}" stroke-width="2"/>'
            f'<rect x="{x + 10}" y="{y + 13}" width="38" height="38" rx="9" fill="{badge_bg}"/>'
            f'<text x="{x + 29}" y="{y + 38}" font-size="18" font-weight="800" fill="#FFFFFF" text-anchor="middle">{monogram}</text>'
            f'<text x="{x + 58}" y="{y + 30}" font-size="18.5" font-weight="800" fill="#0F172A">{name}</text>'
            f'<text x="{x + 58}" y="{y + 50}" font-size="16" font-weight="600" fill="{sub_col}">{role}</text>'
        )

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'font-family="Inter, Roboto, DejaVu Sans, sans-serif">',
        f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
        # Left panel (Before: M x N)
        '<rect x="14" y="12" width="592" height="536" rx="16" fill="#FFFDFD" stroke="#DC2626" stroke-width="2"/>',
        '<path d="M14 28 Q14 12 30 12 H590 Q606 12 606 28 V52 H14 Z" fill="#FEE2E2"/>',
        f'<text x="32" y="39" font-size="20" font-weight="800" fill="#991B1B">{left_title}</text>',
        # Right panel (After: M + N)
        '<rect x="626" y="12" width="592" height="536" rx="16" fill="#FAFFFC" stroke="#16A34A" stroke-width="2"/>',
        '<path d="M626 28 Q626 12 642 12 H1202 Q1218 12 1218 28 V52 H626 Z" fill="#DCFCE7"/>',
        f'<text x="644" y="39" font-size="20" font-weight="800" fill="#166534">{right_title}</text>',
    ]

    ys_l = [72 + i * 98 for i in range(m)]
    ys_r = [72 + j * 98 for j in range(n)]

    # M x N spaghetti Bezier curves
    for i, yl in enumerate(ys_l):
        for j, yr in enumerate(ys_r):
            y1, y2 = yl + 32, yr + 32
            opacity = "0.82" if i == j else "0.45"
            parts.append(
                f'<path d="M226 {y1} C 308 {y1}, 312 {y2}, 394 {y2}" fill="none" '
                f'stroke="#DC2626" stroke-width="2.2" stroke-opacity="{opacity}"/>'
            )

    for i, node in enumerate(left_nodes):
        parts.append(node_box(28, ys_l[i], 198, 66, node, "#94A3B8", "#475569"))
    for j, node in enumerate(right_nodes):
        parts.append(node_box(394, ys_r[j], 198, 66, node, "#94A3B8", "#475569"))

    # Hub & M + N clean curves
    hub_x, hub_y, hub_w, hub_h = 858, 92, 132, 344
    for i, yl in enumerate(ys_l):
        y1 = yl + 33
        hy = hub_y + 70 + i * 62
        parts.append(f'<path d="M834 {y1} C 846 {y1}, 846 {hy}, {hub_x} {hy}" fill="none" stroke="#1D4ED8" stroke-width="2.6"/>')
    for j, yr in enumerate(ys_r):
        y2 = yr + 33
        hy = hub_y + 70 + j * 62
        parts.append(f'<path d="M{hub_x + hub_w} {hy} C 1002 {hy}, 1002 {y2}, 1014 {y2}" fill="none" stroke="#15803D" stroke-width="2.6"/>')

    for i, node in enumerate(left_nodes):
        parts.append(node_box(638, ys_l[i], 196, 66, node, "#2563EB", "#1D4ED8"))
    for j, node in enumerate(right_nodes):
        n_copy = dict(node, role=node.get("after_role", "MCP server"))
        parts.append(node_box(1014, ys_r[j], 192, 66, n_copy, "#16A34A", "#15803D"))

    parts.append(f'<rect x="{hub_x}" y="{hub_y}" width="{hub_w}" height="{hub_h}" rx="18" fill="#FFFFFF" stroke="#1D4ED8" stroke-width="2.8"/>')
    parts.append(f'<text x="{hub_x + hub_w // 2}" y="{hub_y + 52}" font-size="28" font-weight="900" fill="#1E3A8A" text-anchor="middle">{esc(hub.get("title", "MCP"))}</text>')
    parts.append(f'<text x="{hub_x + hub_w // 2}" y="{hub_y + 78}" font-size="17" font-weight="700" fill="#1D4ED8" text-anchor="middle">{esc(hub.get("subtitle", "Protocol hub"))}</text>')

    pill_colors = [("#DBEAFE", "#1E40AF"), ("#F3E8FF", "#6B21A8"), ("#DCFCE7", "#166534")]
    for p_idx, pill in enumerate(hub.get("pills", ["Tools", "Resources", "Prompts"])[:3]):
        py = hub_y + 118 + p_idx * 64
        pbg, pfg = pill_colors[p_idx % len(pill_colors)]
        parts.append(f'<rect x="{hub_x + 16}" y="{py}" width="{hub_w - 32}" height="44" rx="22" fill="{pbg}" stroke="{pfg}" stroke-width="1.6"/>')
        parts.append(f'<text x="{hub_x + hub_w // 2}" y="{py + 28}" font-size="18" font-weight="800" fill="{pfg}" text-anchor="middle">{esc(pill)}</text>')

    # Summary pills at bottom
    parts.append('<rect x="64" y="482" width="492" height="48" rx="24" fill="#FEE2E2" stroke="#DC2626" stroke-width="1.8"/>')
    parts.append(f'<text x="310" y="513" font-size="21" font-weight="800" fill="#991B1B" text-anchor="middle">{left_summary}</text>')
    parts.append('<rect x="676" y="482" width="492" height="48" rx="24" fill="#DCFCE7" stroke="#16A34A" stroke-width="1.8"/>')
    parts.append(f'<text x="922" y="513" font-size="21" font-weight="800" fill="#166534" text-anchor="middle">{right_summary}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def render_html_via_chrome(html_str: str, out_png: Path, audit_html_str: str | None = None) -> list[str]:
    chrome = find_chrome()
    if not chrome:
        fallback = out_png.with_suffix(".html")
        fallback.write_text(html_str, encoding="utf-8")
        raise RuntimeError(f"No Chrome/Chromium binary found; wrote HTML fallback to {fallback}")

    warnings: list[str] = []
    with tempfile.TemporaryDirectory(prefix="slide_diag_") as tmpd:
        tmp = Path(tmpd)
        if audit_html_str:
            af = tmp / "audit.html"
            af.write_text(audit_html_str, encoding="utf-8")
            dom = subprocess.run(
                [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                 f"--user-data-dir={tmp}/p_audit", f"--window-size={W},{H}",
                 "--virtual-time-budget=2000", "--dump-dom", f"file://{af}"],
                check=True, capture_output=True, text=True,
            ).stdout
            m = re.search(r'<pre id="dom_audit_report"[^>]*>(.*?)</pre>', dom, re.S)
            if m:
                warnings = json.loads(html.unescape(m.group(1)))

        rf = tmp / "render.html"
        rf.write_text(html_str, encoding="utf-8")
        out_png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
             "--force-device-scale-factor=2", f"--user-data-dir={tmp}/p_shot",
             f"--window-size={W},{H}", f"--screenshot={out_png}", f"file://{rf}"],
            check=True, capture_output=True, text=True,
        )
    return warnings


DEMO_MULTITAB = {
    "title": "2024: grounding fragile models",
    "subtitle": "3 crutches built around a weak model",
    "title_tone": "green",
    "columns": [
        {
            "title": "Fragile model",
            "tone": "red",
            "width_px": 228,
            "steps": [
                {"label": "hallucinates", "sub": "confident, wrong facts"},
                {"label": "no tools", "sub": "cannot act or look up"},
                {"label": "knowledge cutoff", "sub": "frozen at training date"},
            ],
            "footer": "e.g. GPT-4o, Claude 3, Gemini 1.5",
            "arrow_after": True,
        },
        {
            "badge": "a",
            "title": "Heavy prompt eng.",
            "subtitle": "long, hand-tuned prompts",
            "tone": "amber",
            "code": "SYSTEM PROMPT\nYou are a helpful,\nprecise assistant.\nNEVER invent facts.\nALWAYS cite sources.\nAnswer ONLY in JSON.",
            "caption": "... plus 3 more pages",
            "footer": "brittle: model update breaks it",
        },
        {
            "badge": "b",
            "title": "Embeddings + RAG",
            "subtitle": "ground answers in docs",
            "tone": "green",
            "flow_arrows": True,
            "steps": ["docs", "chunks", "vectors (embeddings)", "top-5 by similarity", "pasted into prompt"],
            "footer": "good retrieval = good answers",
        },
        {
            "badge": "c",
            "title": "Function calling",
            "subtitle": "early tools: model asks",
            "tone": "blue",
            "flow_arrows": True,
            "steps": [
                "model emits JSON call",
                {"code": '{\n  "name": "get_weather",\n  "args": {"city": "Zurich"}\n}'},
                "your code runs it",
                "result goes back in",
            ],
            "footer": "each tool hand-wired, per app",
        },
    ],
}

DEMO_BIPARTITE = {
    "before_title": "Before MCP: M × N spaghetti",
    "after_title": "After MCP: M + N one standard",
    "left_nodes": [
        {"name": "Claude Desktop", "role": "AI assistant", "monogram": "CD", "color": "#D97757"},
        {"name": "Cursor", "role": "AI code editor", "monogram": "CU", "color": "#0F172A"},
        {"name": "Gemini CLI", "role": "Terminal agent", "monogram": "GC", "color": "#1A73E8"},
        {"name": "GitHub Copilot", "role": "IDE agent", "monogram": "CP", "color": "#24292F"},
    ],
    "right_nodes": [
        {"name": "PostgreSQL", "role": "Database", "monogram": "PG", "color": "#336791"},
        {"name": "GitHub", "role": "Code & issues", "monogram": "GH", "color": "#24292F"},
        {"name": "Slack", "role": "Team chat", "monogram": "SL", "color": "#611F69"},
        {"name": "Google Drive", "role": "Documents", "monogram": "GD", "color": "#188038"},
    ],
    "hub": {"title": "MCP", "subtitle": "Protocol hub", "pills": ["Tools", "Resources", "Prompts"]},
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=("multitab", "bipartite"), help="Diagram engine mode")
    ap.add_argument("--spec", type=Path, help="JSON specification file")
    ap.add_argument("--demo-multitab", action="store_true", help="Render built-in 4-column Multi-Tab demo")
    ap.add_argument("--demo-bipartite", action="store_true", help="Render built-in M*N vs M+N Bipartite demo")
    ap.add_argument("--out", type=Path, required=True, help="Output .png (or .svg for bipartite)")
    args = ap.parse_args()

    if args.demo_multitab:
        mode, spec = "multitab", DEMO_MULTITAB
    elif args.demo_bipartite:
        mode, spec = "bipartite", DEMO_BIPARTITE
    elif args.mode and args.spec:
        mode = args.mode
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
    else:
        ap.error("Pass either (--mode and --spec) or --demo-multitab / --demo-bipartite.")

    if mode == "multitab":
        clean_html = build_multitab_html(spec, include_audit=False)
        audit_html = build_multitab_html(spec, include_audit=True)
        warnings = render_html_via_chrome(clean_html, args.out, audit_html)
        if warnings:
            print(f"WARN: rendered {args.out} with {len(warnings)} DOM audit warning(s): {warnings[:3]}")
            return 2
        print(f"OK: rendered 2464x1120 HiDPI Multi-Tab PNG (0 DOM warnings) -> {args.out}")
        return 0

    svg_str = build_bipartite_svg(spec)
    if args.out.suffix.lower() == ".svg":
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(svg_str, encoding="utf-8")
        print(f"OK: wrote Bipartite SVG -> {args.out}")
        return 0

    wrapped = (
        f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>'
        f'*{{margin:0;padding:0;}}html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#FFFFFF;}}'
        f'</style></head><body>{svg_str}</body></html>'
    )
    render_html_via_chrome(wrapped, args.out, None)
    print(f"OK: rendered 2464x1120 HiDPI Bipartite PNG -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
