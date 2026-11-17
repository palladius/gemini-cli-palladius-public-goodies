#!/usr/bin/env python3
"""Zero-Dependency Chrome DevTools Protocol (CDP) Stager for Medium Drafts.

Connects directly to the user's real authenticated Chrome instance via `DevToolsActivePort`
(enabled once at `chrome://inspect/#remote-debugging`) over a SINGLE persistent WebSocket
session (so Chrome 136+ prompts 'Allow remote debugging?' at most ONCE per run).

HARD SAFETY INVARIANTS (NON-NEGOTIABLE):
  1. DRAFT-ONLY: Never clicks or triggers 'Publish', 'Publish now', 'Schedule', or 'Submit'.
     Every click helper enforces an explicit regex denylist against publish buttons.
  2. TAB ISOLATION: Attaches strictly to the single matched `medium.com` targetId.
  3. SAFE CLEANUP: `cleanup-test-drafts` ONLY deletes drafts whose title begins with the
     explicit `[TEST - DELETE ME]` safety prefix.
"""
from __future__ import annotations

import argparse
import base64
import html as html_lib
import json
import os
import platform
import re
import socket
import struct
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


FORBIDDEN_BUTTON_RE = re.compile(
    r"\b(publish|publish\s+now|schedule\s+for\s+later|submit\s+to\s+publication|publish\s+and\s+send)\b",
    re.I,
)
TEST_DRAFT_PREFIX = "[TEST - DELETE ME]"


def default_chrome_roots() -> list[Path]:
    home = Path.home()
    if platform.system().lower() == "darwin":
        return [
            home / "Library/Application Support/Google/Chrome",
            home / "Library/Application Support/Google/Chrome Canary",
            home / "Library/Application Support/Chromium",
        ]
    return [
        home / ".config/google-chrome",
        home / ".config/google-chrome-beta",
        home / ".config/chromium",
        home / ".config/chrome-remote-desktop/chrome-config/google-chrome",
    ]


def find_devtools_active_port(custom_root: str | None = None) -> tuple[int, str, Path]:
    roots = [Path(custom_root).expanduser()] if custom_root else default_chrome_roots()
    for root in roots:
        port_file = root / "DevToolsActivePort"
        if port_file.is_file():
            lines = [ln.strip() for ln in port_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
            if len(lines) >= 2 and lines[0].isdigit():
                return int(lines[0]), lines[1], port_file
    raise FileNotFoundError(
        "Could not find DevToolsActivePort. Open chrome://inspect/#remote-debugging in your "
        "authenticated Chrome browser and enable remote debugging."
    )


class CDPClient:
    """Minimal pure-stdlib RFC 6455 WebSocket JSON-RPC client for Chrome DevTools Protocol."""

    def __init__(self, host: str, port: int, path: str, handshake_timeout: float = 120.0):
        self.host = host
        self.port = int(port)
        self.path = path
        self.sock = socket.create_connection((self.host, self.port), timeout=handshake_timeout)
        self._next_id = 0
        self._rx_buf = b""
        self._pending_events: list[dict[str, Any]] = []
        self._handshake(timeout=handshake_timeout)

    def _handshake(self, timeout: float = 120.0) -> None:
        self.sock.settimeout(timeout)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode("ascii"))
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("CDP WebSocket handshake closed (click 'Allow' in Chrome prompt and retry).")
            buf += chunk
        header, rest = buf.split(b"\r\n\r\n", 1)
        status_line = header.decode("latin1", errors="replace").splitlines()[0]
        if "101" not in status_line:
            raise RuntimeError(f"CDP WebSocket handshake rejected: {status_line}")
        self._rx_buf = rest

    def _recv_exact(self, n: int) -> bytes:
        while len(self._rx_buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise EOFError("CDP socket closed while reading frame")
            self._rx_buf += chunk
        out, self._rx_buf = self._rx_buf[:n], self._rx_buf[n:]
        return out

    def _send_frame(self, payload_bytes: bytes, opcode: int = 0x1) -> None:
        mask_key = os.urandom(4)
        length = len(payload_bytes)
        header = bytearray([0x80 | (opcode & 0x0F)])
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        header.extend(mask_key)
        masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload_bytes))
        self.sock.sendall(bytes(header) + masked)

    def _recv_message(self) -> str:
        fragments: list[bytes] = []
        while True:
            b1, b2 = self._recv_exact(2)
            fin = bool(b1 & 0x80)
            opcode = b1 & 0x0F
            masked = bool(b2 & 0x80)
            length = b2 & 0x7F
            if length == 126:
                length = struct.unpack("!H", self._recv_exact(2))[0]
            elif length == 127:
                length = struct.unpack("!Q", self._recv_exact(8))[0]
            mask_key = self._recv_exact(4) if masked else None
            data = self._recv_exact(length)
            if mask_key:
                data = bytes(b ^ mask_key[i % 4] for i, b in enumerate(data))
            if opcode == 0x9:
                self._send_frame(data, opcode=0xA)
                continue
            if opcode == 0x8:
                raise EOFError("CDP server closed WebSocket")
            if opcode in (0x0, 0x1, 0x2):
                fragments.append(data)
                if fin:
                    return b"".join(fragments).decode("utf-8", errors="replace")

    def call(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        session_id: str | None = None,
        call_timeout: float = 25.0,
    ) -> dict[str, Any]:
        self._next_id += 1
        req_id = self._next_id
        msg: dict[str, Any] = {"id": req_id, "method": method}
        if params:
            msg["params"] = params
        if session_id:
            msg["sessionId"] = session_id
        self._send_frame(json.dumps(msg).encode("utf-8"))
        deadline = time.monotonic() + call_timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError(f"CDP {method} timed out after {call_timeout}s")
            self.sock.settimeout(max(0.5, remaining))
            raw = self._recv_message()
            resp = json.loads(raw)
            # Auto-accept beforeunload / JS dialogs so dirty editor navigation never stalls
            if resp.get("method") == "Page.javascriptDialogOpening":
                dlg_sess = resp.get("sessionId") or session_id
                self._next_id += 1
                ack: dict[str, Any] = {
                    "id": self._next_id,
                    "method": "Page.handleJavaScriptDialog",
                    "params": {"accept": True},
                }
                if dlg_sess:
                    ack["sessionId"] = dlg_sess
                self._send_frame(json.dumps(ack).encode("utf-8"))
                continue
            if resp.get("id") == req_id:
                if "error" in resp:
                    raise RuntimeError(f"CDP {method} error: {resp['error']}")
                return resp.get("result", {})
            if "method" in resp:
                self._pending_events.append(resp)

    def wait_for_event(self, method_name: str, timeout: float = 4.0) -> dict[str, Any] | None:
        for i, ev in enumerate(self._pending_events):
            if ev.get("method") == method_name:
                return self._pending_events.pop(i)
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rem = deadline - time.monotonic()
            self.sock.settimeout(max(0.2, rem))
            try:
                raw = self._recv_message()
            except Exception:
                return None
            resp = json.loads(raw)
            if resp.get("method") == method_name:
                return resp
            if "method" in resp:
                self._pending_events.append(resp)
        return None

    def eval_js(self, session_id: str, expression: str, await_promise: bool = True, timeout: float = 25.0) -> Any:
        res = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": await_promise,
                "userGesture": True,
            },
            session_id=session_id,
            call_timeout=timeout,
        )
        if "exceptionDetails" in res:
            raise RuntimeError(f"JS exception: {res['exceptionDetails']}")
        return res.get("result", {}).get("value")

    def disarm_beforeunload(self, session_id: str) -> None:
        try:
            self.eval_js(
                session_id,
                """(() => {
                    window.onbeforeunload = null;
                    window.addEventListener('beforeunload', e => {
                        e.stopImmediatePropagation();
                    }, true);
                    return true;
                })()""",
                await_promise=False,
                timeout=3.0,
            )
        except Exception:
            pass

    def navigate(self, session_id: str, url: str, wait_sec: float = 3.0) -> str:
        self.call("Page.enable", session_id=session_id)
        self.disarm_beforeunload(session_id)
        self.call("Page.navigate", {"url": url}, session_id=session_id, call_timeout=30.0)
        deadline = time.monotonic() + max(wait_sec, 15.0)
        time.sleep(0.8)
        while time.monotonic() < deadline:
            try:
                state = self.eval_js(session_id, "document.readyState", await_promise=False, timeout=5.0)
                if state == "complete":
                    break
            except Exception:
                pass
            time.sleep(0.4)
        time.sleep(wait_sec)
        try:
            return str(self.eval_js(session_id, "location.href", await_promise=False, timeout=5.0) or "")
        except Exception:
            return url

    def click_xy(self, session_id: str, x: float, y: float) -> None:
        for evt_type in ("mousePressed", "mouseReleased"):
            self.call(
                "Input.dispatchMouseEvent",
                {"type": evt_type, "x": float(x), "y": float(y), "button": "left", "clickCount": 1},
                session_id=session_id,
            )
            time.sleep(0.05)

    def press_command_shortcut(
        self, session_id: str, key: str, code: str, vk: int, command: str
    ) -> None:
        # Modifiers: 2 = Ctrl (Linux/Windows), 4 = Meta/Cmd (macOS). Passing `commands` triggers Blink Editor::Command directly.
        mod = 4 if platform.system().lower() == "darwin" else 2
        self.call(
            "Input.dispatchKeyEvent",
            {
                "type": "rawKeyDown",
                "key": key,
                "code": code,
                "windowsVirtualKeyCode": vk,
                "nativeVirtualKeyCode": vk,
                "modifiers": mod,
                "commands": [command],
            },
            session_id=session_id,
        )
        self.call(
            "Input.dispatchKeyEvent",
            {
                "type": "keyUp",
                "key": key,
                "code": code,
                "windowsVirtualKeyCode": vk,
                "nativeVirtualKeyCode": vk,
                "modifiers": mod,
            },
            session_id=session_id,
        )

    def press_enter(self, session_id: str) -> None:
        self.call(
            "Input.dispatchKeyEvent",
            {
                "type": "rawKeyDown",
                "key": "Enter",
                "code": "Enter",
                "windowsVirtualKeyCode": 13,
                "nativeVirtualKeyCode": 13,
                "text": "\r",
                "unmodifiedText": "\r",
            },
            session_id=session_id,
        )
        self.call(
            "Input.dispatchKeyEvent",
            {
                "type": "keyUp",
                "key": "Enter",
                "code": "Enter",
                "windowsVirtualKeyCode": 13,
                "nativeVirtualKeyCode": 13,
            },
            session_id=session_id,
        )

    def insert_text(self, session_id: str, text: str) -> None:
        self.call("Input.insertText", {"text": text}, session_id=session_id)

    def screenshot(self, session_id: str, out_path: Path) -> Path:
        self.call("Page.enable", session_id=session_id)
        res = self.call("Page.captureScreenshot", {"format": "png"}, session_id=session_id, call_timeout=30.0)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(base64.b64decode(res["data"]))
        return out_path

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass


def find_medium_target(cdp: CDPClient, match_domain: str = "medium.com") -> dict[str, Any]:
    targets = cdp.call("Target.getTargets", call_timeout=30.0).get("targetInfos", [])
    page_targets = [
        t for t in targets
        if t.get("type") == "page"
        and (urllib.parse.urlparse(t.get("url") or "").hostname or "").lower() in (match_domain, f"www.{match_domain}")
    ]
    if not page_targets:
        raise RuntimeError(
            f"No open '{match_domain}' tab found among {len(targets)} browser targets. "
            f"Open https://{match_domain} in your authenticated Chrome window first."
        )
    return page_targets[0]


AUDIT_EDITOR_JS = """(() => {
    const bodyText = document.body ? document.body.innerText : '';
    const savedMatch = bodyText.match(/\\b(Saved|Saving\\.\\.\\.)\\b/i);
    const errorMatch = bodyText.match(/(Something is wrong and we cannot save your story[^\\n]*)/i);
    const root = document.querySelector('.postArticle-content, section.section--body, main article, article') || document.body;
    const figures = Array.from(root.querySelectorAll('figure')).map(f => ({
        imgSrc: f.querySelector('img') ? f.querySelector('img').getAttribute('src') : null,
        imgDataId: f.querySelector('img') ? f.querySelector('img').getAttribute('data-image-id') : null,
        imgNaturalWidth: f.querySelector('img') ? f.querySelector('img').naturalWidth : null,
        caption: f.querySelector('figcaption') ? f.querySelector('figcaption').innerText.trim() : null,
        hasIframe: !!f.querySelector('iframe'),
        text: f.innerText.trim().slice(0, 100)
    }));
    const rawImgs = Array.from(root.querySelectorAll('img')).map(img => ({
        src: img.getAttribute('src'),
        alt: img.getAttribute('alt'),
        dataImageId: img.getAttribute('data-image-id'),
        naturalWidth: img.naturalWidth,
        parentTag: img.parentElement ? img.parentElement.tagName : null
    }));
    const pres = Array.from(root.querySelectorAll('pre')).map(p => ({
        lines: p.innerText.split('\\n').length,
        hasNbsp: p.innerHTML.includes('&nbsp;') || p.innerText.includes('\\u00a0'),
        preview: p.innerText.slice(0, 120)
    }));
    const headings = Array.from(root.querySelectorAll('h1, h2, h3, h4')).map(h => ({
        tag: h.tagName,
        name: h.getAttribute('name'),
        className: (h.className || '').toString().slice(0, 60),
        text: h.innerText.trim().slice(0, 100)
    }));
    return {
        url: location.href,
        docTitle: document.title,
        saveStatus: savedMatch ? savedMatch[1] : 'unknown',
        errorBanner: errorMatch ? errorMatch[1] : null,
        headingsCount: headings.length,
        headingsSample: headings.slice(0, 8),
        figuresCount: figures.length,
        figures: figures,
        rawImgsCount: rawImgs.length,
        rawImgs: rawImgs,
        preCount: pres.length,
        presSample: pres.slice(0, 8),
        blockquotesCount: root.querySelectorAll('blockquote').length,
        orderedListsCount: root.querySelectorAll('ol').length,
        unorderedListsCount: root.querySelectorAll('ul').length,
        tablesCount: root.querySelectorAll('table').length,
        hrCount: root.querySelectorAll('hr').length,
        paragraphsCount: root.querySelectorAll('p').length
    };
})()"""


def dismiss_editor_onboarding_overlay(cdp: CDPClient, sess: str) -> None:
    """Closes Medium's bottom 'Writing on Medium' onboarding tooltip if visible."""
    try:
        cdp.eval_js(
            sess,
            """(() => {
                const btns = Array.from(document.querySelectorAll('button, [role="button"]'));
                for (const b of btns) {
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    const txt = (b.innerText || '').trim();
                    if ((aria.includes('close') || txt === '×' || txt === '✕') && !/publish/i.test(txt)) {
                        const r = b.getBoundingClientRect();
                        if (r.top > 300 && r.width > 0) {
                            b.click();
                        }
                    }
                }
            })()""",
            await_promise=False,
            timeout=3.0,
        )
    except Exception:
        pass


def prefix_draft_title(cdp: CDPClient, sess: str, prefix: str) -> str:
    if not prefix:
        return ""
    box = cdp.eval_js(
        sess,
        """(() => {
            const titleEl = document.querySelector('h3.graf--title, h1[data-testid*="title"], [data-default-value*="Title"], .postArticle-content h3');
            if (!titleEl) return null;
            const r = titleEl.getBoundingClientRect();
            return { x: r.left + 8, y: r.top + Math.min(16, r.height / 2), text: titleEl.innerText || '' };
        })()""",
    )
    if not box:
        return "NO_TITLE_ELEMENT"
    if str(box.get("text", "")).startswith(prefix):
        return str(box["text"])

    # Click at start of title, press Home, and insert prefix via real CDP input so Medium auto-saves!
    cdp.click_xy(sess, box["x"], box["y"])
    time.sleep(0.2)
    cdp.eval_js(
        sess,
        """(() => {
            const titleEl = document.querySelector('h3.graf--title, h1[data-testid*="title"], [data-default-value*="Title"], .postArticle-content h3');
            if (!titleEl) return false;
            titleEl.focus();
            const sel = window.getSelection();
            const range = document.createRange();
            range.setStart(titleEl, 0);
            range.collapse(true);
            sel.removeAllRanges();
            sel.addRange(range);
            return true;
        })()""",
    )
    cdp.insert_text(sess, prefix)
    time.sleep(3.5)
    return str(
        cdp.eval_js(
            sess,
            """(() => {
                const t = document.querySelector('h3.graf--title, .postArticle-content h3');
                return t ? t.innerText : '';
            })()""",
        )
        or ""
    )


def inspect_and_set_canonical_in_settings(
    cdp: CDPClient,
    sess: str,
    story_id: str,
    canonical_url: str | None,
    topics: list[str] | None,
    screenshot_path: Path | None,
) -> dict[str, Any]:
    settings_url = f"https://medium.com/p/{story_id}/settings"
    cdp.navigate(sess, settings_url, wait_sec=3.5)

    # 1. Populate up to 5 Topics via 'Add a topic...' input on /settings if provided
    topics_added: list[str] = []
    if topics:
        topic_box = cdp.eval_js(
            sess,
            """(() => {
                const inp = document.querySelector('input[placeholder*="Add a topic" i]');
                if (!inp) return null;
                inp.scrollIntoView({ block: 'center' });
                const r = inp.getBoundingClientRect();
                return { x: r.left + 25, y: r.top + r.height / 2 };
            })()""",
        )
        if topic_box:
            cdp.click_xy(sess, topic_box["x"], topic_box["y"])
            time.sleep(0.25)
            for t_name in topics[:5]:
                clean_t = t_name.strip()
                if not clean_t:
                    continue
                cdp.insert_text(sess, clean_t)
                time.sleep(0.35)
                cdp.press_enter(sess)
                time.sleep(0.35)
                topics_added.append(clean_t)
            # Click the local 'Save' button inside Reader interests section (never Publish!)
            cdp.eval_js(
                sess,
                """(() => {
                    const inp = document.querySelector('input[placeholder*="Add a topic" i]');
                    const sec = inp ? inp.closest('section, div') : document;
                    const btns = Array.from((sec || document).querySelectorAll('button'));
                    const saveBtn = btns.find(b => /^save$/i.test((b.innerText || '').trim()) && !b.disabled);
                    if (saveBtn) saveBtn.click();
                })()""",
            )
            time.sleep(1.2)

    # 2. Expand Advanced Settings if collapsed (target <button> directly, not outer wrapper <div>!)
    cdp.eval_js(
        sess,
        """(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            for (const b of btns) {
                const txt = (el => (el.innerText || '').trim())(b);
                if (/^Advanced Settings$/i.test(txt)) {
                    b.scrollIntoView({ block: 'center' });
                    b.click();
                    return true;
                }
            }
            return false;
        })()""",
    )
    time.sleep(1.2)

    before_info = cdp.eval_js(
        sess,
        """(() => {
            const inputs = Array.from(document.querySelectorAll('input')).map(i => ({
                type: i.type,
                name: i.name,
                id: i.id,
                placeholder: i.placeholder,
                value: i.value,
                checked: i.checked,
                disabled: i.disabled
            }));
            const buttons = Array.from(document.querySelectorAll('button')).map(b => ({
                text: (b.innerText || '').trim(),
                disabled: b.disabled
            })).filter(b => b.text && b.text.length < 60);
            return { url: location.href, inputs, buttons };
        })()""",
    )

    updated = False
    if canonical_url:
        # Step A: Click 'This story was originally published elsewhere' checkbox first, then wait 0.8s for React to mount the URL input!
        cdp.eval_js(
            sess,
            """(() => {
                const cbs = Array.from(document.querySelectorAll('input[type="checkbox"]'));
                for (const cb of cbs) {
                    const rowText = (cb.closest('div, section, label, li')?.innerText || '');
                    if (/canonical|originally published/i.test(rowText) && !cb.checked) {
                        cb.scrollIntoView({ block: 'center' });
                        cb.click();
                        return true;
                    }
                }
                return false;
            })()""",
        )
        time.sleep(0.9)

        # Step B: Now locate the newly mounted Canonical URL input, insert canonical_url, and click Save Canonical Link
        target_box = cdp.eval_js(
            sess,
            """(() => {
                const candidates = Array.from(document.querySelectorAll('input[type="text"], input[type="url"], input:not([type])'))
                    .filter(el => {
                        const meta = ((el.name || '') + ' ' + (el.placeholder || '') + ' ' + (el.id || '')).toLowerCase();
                        if (meta.includes('search') || meta.includes('topic') || el.disabled) return false;
                        const ctx = (el.closest('div, section, li')?.innerText || '').toLowerCase();
                        return meta.includes('canonical') || meta.includes('http') || ctx.includes('canonical') || ctx.includes('originally published');
                    });
                if (!candidates.length) return null;
                const el = candidates[0];
                el.scrollIntoView({ block: 'center' });
                const r = el.getBoundingClientRect();
                return { x: r.left + Math.min(40, r.width / 2), y: r.top + r.height / 2 };
            })()""",
        )
        if target_box:
            cdp.click_xy(sess, target_box["x"], target_box["y"])
            time.sleep(0.2)
            cdp.press_command_shortcut(sess, "a", "KeyA", 65, "SelectAll")
            cdp.insert_text(sess, canonical_url)
            time.sleep(0.5)
            updated = bool(
                cdp.eval_js(
                    sess,
                    """(() => {
                        const btns = Array.from(document.querySelectorAll('button'));
                        const saveBtn = btns.find(b => /save\\s+canonical|^save$/i.test((b.innerText || '').trim()) && !b.disabled && !/publish/i.test(b.innerText));
                        if (saveBtn) {
                            saveBtn.click();
                            return true;
                        }
                        return false;
                    })()""",
                )
            )
            time.sleep(2.2)

    after_info = cdp.eval_js(
        sess,
        """(() => ({
            inputs: Array.from(document.querySelectorAll('input')).map(i => ({
                type: i.type, name: i.name, placeholder: i.placeholder, value: i.value, checked: i.checked
            }))
        }))()""",
    )
    if screenshot_path:
        cdp.screenshot(sess, screenshot_path)

    return {
        "settings_url": settings_url,
        "topics_added": topics_added,
        "before": before_info,
        "canonical_set_attempted": updated,
        "after": after_info,
    }


def run_method_a_import(
    cdp: CDPClient,
    sess: str,
    source_url: str,
    title_prefix: str,
    out_dir: Path,
) -> dict[str, Any]:
    cdp.navigate(sess, "https://medium.com/p/import", wait_sec=3.5)

    # Inspect all inputs & contenteditables on /p/import, excluding navbar search (y < 95 or 'search')
    field_info = cdp.eval_js(
        sess,
        """(() => {
            const all = Array.from(document.querySelectorAll('input, textarea, [contenteditable="true"], .js-importUrlInput'));
            const mapped = all.map((el, idx) => {
                const r = el.getBoundingClientRect();
                return {
                    idx,
                    tag: el.tagName,
                    type: el.getAttribute('type') || '',
                    placeholder: el.getAttribute('placeholder') || el.getAttribute('data-default-value') || el.getAttribute('data-placeholder') || '',
                    ariaLabel: el.getAttribute('aria-label') || '',
                    className: (el.className || '').toString().slice(0, 80),
                    inHeader: !!el.closest('header, nav, [role="navigation"]'),
                    x: r.left + r.width / 2,
                    y: r.top + r.height / 2,
                    w: r.width,
                    h: r.height
                };
            });
            const valid = mapped.filter(m =>
                m.w > 80 &&
                m.h > 14 &&
                m.y > 100 &&
                !m.inHeader &&
                !/search/i.test(m.placeholder + ' ' + m.ariaLabel + ' ' + m.type + ' ' + m.className)
            );
            return { allFields: mapped, chosen: valid[0] || null };
        })()""",
    )

    chosen = (field_info or {}).get("chosen")
    if not chosen:
        shot = out_dir / "method_a_editor.png"
        cdp.screenshot(sess, shot)
        return {
            "method": "A_URL_IMPORT",
            "error": "Could not locate central import URL input on /p/import",
            "field_info": field_info,
            "editor_screenshot": str(shot),
        }

    # Click the central import box via real CDP mouse click, SelectAll, type URL, and fire input/keyup on div.js-importUrl
    cdp.click_xy(sess, chosen["x"], chosen["y"])
    time.sleep(0.25)
    cdp.insert_text(sess, source_url)
    cdp.eval_js(
        sess,
        """(() => {
            const el = document.querySelector('.js-importUrl, .js-importUrlInput, input[placeholder*="http" i]');
            if (el) {
                el.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText' }));
                el.dispatchEvent(new KeyboardEvent('keyup', { key: '/', bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        })()""",
    )
    time.sleep(0.8)

    # Locate and click the 'Import' button (enforcing FORBIDDEN_BUTTON_RE)
    import_btn = cdp.eval_js(
        sess,
        """(() => {
            const btns = Array.from(document.querySelectorAll('button, a[role="button"], .button'));
            const b = btns.find(el => /^import$/i.test((el.innerText || '').trim()));
            if (!b) return null;
            const r = b.getBoundingClientRect();
            return { text: (b.innerText || '').trim(), x: r.left + r.width / 2, y: r.top + r.height / 2 };
        })()""",
    )
    if not import_btn or FORBIDDEN_BUTTON_RE.search(import_btn.get("text", "")):
        raise RuntimeError(f"Unsafe or missing Import button on /p/import: {import_btn}")

    cdp.click_xy(sess, import_btn["x"], import_btn["y"])

    # Poll up to 30s for 'See your story' button or direct redirect to /p/<id>/edit
    clicked_see_story = False
    import_error_text = None
    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        time.sleep(1.2)
        state = cdp.eval_js(
            sess,
            """(() => {
                const href = location.href;
                const bodyTxt = document.body ? document.body.innerText : '';
                const err = bodyTxt.match(/(import failed|uh oh|could not import|sorry, we couldn't import[^\\n]*)/i);
                const els = Array.from(document.querySelectorAll('button, a'));
                const see = els.find(e => /see your story/i.test((e.innerText || '').trim()));
                if (see) {
                    const r = see.getBoundingClientRect();
                    return { href, seeBtn: { text: see.innerText.trim(), x: r.left + r.width / 2, y: r.top + r.height / 2 }, err: err ? err[1] : null };
                }
                return { href, seeBtn: null, err: err ? err[1] : null };
            })()""",
        )
        href = str((state or {}).get("href") or "")
        if re.search(r"/p/[0-9a-f]+/edit", href):
            break
        see_btn = (state or {}).get("seeBtn")
        if see_btn and not FORBIDDEN_BUTTON_RE.search(see_btn["text"]):
            cdp.click_xy(sess, see_btn["x"], see_btn["y"])
            clicked_see_story = True
            time.sleep(4.5)
            break
        if (state or {}).get("err"):
            import_error_text = state["err"]
            break

    time.sleep(3.5)
    dismiss_editor_onboarding_overlay(cdp, sess)
    edit_url = str(cdp.eval_js(sess, "location.href", await_promise=False) or "")
    m_id = re.search(r"/p/([0-9a-f]+)", edit_url)
    story_id = m_id.group(1) if m_id else ""

    new_title = prefix_draft_title(cdp, sess, title_prefix) if story_id else "NOT_ON_EDIT_PAGE"
    time.sleep(2.5)
    editor_audit = cdp.eval_js(sess, AUDIT_EDITOR_JS)
    editor_shot = out_dir / "method_a_editor.png"
    cdp.screenshot(sess, editor_shot)

    settings_audit = {}
    if story_id:
        settings_audit = inspect_and_set_canonical_in_settings(
            cdp,
            sess,
            story_id=story_id,
            canonical_url=None,  # Inspect first whether Method A auto-populated canonical!
            topics=None,
            screenshot_path=out_dir / "method_a_settings.png",
        )
        cdp.navigate(sess, f"https://medium.com/p/{story_id}/edit", wait_sec=2.5)

    return {
        "method": "A_URL_IMPORT",
        "field_chosen": chosen,
        "clicked_see_story": clicked_see_story,
        "import_error": import_error_text,
        "story_id": story_id,
        "edit_url": f"https://medium.com/p/{story_id}/edit" if story_id else edit_url,
        "prefixed_title": new_title,
        "editor_screenshot": str(editor_shot),
        "editor_audit": editor_audit,
        "settings_audit": settings_audit,
    }


def extract_story_payload_from_html(html_path: Path) -> tuple[str, str, str]:
    raw = html_path.read_text(encoding="utf-8")
    m_title = re.search(r'data-title="([^"]+)"', raw)
    title = html_lib.unescape(m_title.group(1)).strip() if m_title else "Draft Story"
    m_canon = re.search(r'data-canonical-url="([^"]+)"', raw)
    canon = html_lib.unescape(m_canon.group(1)).strip() if m_canon else ""
    m_body = re.search(r'<article[^>]+id="medium-story-body"[^>]*>(.*?)</article>', raw, re.DOTALL | re.IGNORECASE)
    body_html = m_body.group(1).strip() if m_body else raw
    return title, canon, body_html


def _check_url_reachable(url: str, timeout: float = 5.0) -> tuple[bool, int | str]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (publish-to-medium/1.0)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return (resp.status < 400, resp.status)
    except urllib.error.HTTPError as e:
        if e.code in (403, 405):
            # Retry with GET in case server rejects HEAD
            req_get = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 (publish-to-medium/1.0)"})
            try:
                with urllib.request.urlopen(req_get, timeout=timeout) as resp2:
                    return (resp2.status < 400, resp2.status)
            except urllib.error.HTTPError as e2:
                return (False, e2.code)
            except Exception as ex2:
                return (False, str(ex2))
        return (False, e.code)
    except Exception as ex:
        return (False, str(ex))


def resolve_local_asset_file(src: str, assets_root: Path) -> Path | None:
    """Maps a relative path or an un-deployed remote URL (e.g. https://.../demos/foo.gif or .../rendered/mermaid_x.png)
    back to a local file inside `assets_root` (out/medium/) when present on disk.
    """
    parsed_path = urllib.parse.unquote(urllib.parse.urlparse(src).path).lstrip("/")
    if not parsed_path:
        return None
    direct = assets_root / parsed_path
    if direct.is_file():
        return direct
    parts = Path(parsed_path).parts
    # Try progressively shorter suffixes (e.g. demos/richard-console/demo.gif, rendered/mermaid_xxx.png, images/foo.png)
    for i in range(len(parts)):
        cand = assets_root.joinpath(*parts[i:])
        if cand.is_file():
            return cand
    return None


def prepare_html_and_local_uploads(
    raw_html: str, assets_root: Path
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    """1. Reachable HTTP 200 remote <figure>/<img> tags stay untouched (Medium auto-uploads them on paste!).
    2. Unreachable/404 or relative <figure>/<img> tags that exist locally in `assets_root` become
       `<p>__MEDIUM_LOCAL_UPLOAD_i__</p>` markers queued for direct CDP file-input upload!
    3. Truly missing assets become visible `[TODO]` callouts so Medium never throws 'Uh oh!'.
    """
    local_upload_queue: list[dict[str, Any]] = []
    skipped_missing: list[dict[str, Any]] = []

    def handle_img_or_figure(src: str, alt: str, caption: str, original_html: str) -> str:
        if src.startswith(("http://", "https://")):
            ok, status = _check_url_reachable(src)
            if ok:
                return original_html
        else:
            status = "local_relative"

        local_file = resolve_local_asset_file(src, assets_root)
        if local_file is not None:
            marker = f"__MEDIUM_LOCAL_UPLOAD_{len(local_upload_queue)}__"
            local_upload_queue.append(
                {
                    "marker": marker,
                    "file": str(local_file.resolve()),
                    "caption": caption or alt,
                    "original_src": src,
                }
            )
            return f"<p>{marker}</p>"

        skipped_missing.append({"src": src, "alt": alt, "status": status})
        return (
            f'<p>⚠️ <strong>[TODO: Upload missing image ({status}): {html_lib.escape(alt or "Image")}]</strong>'
            f" — <code>{html_lib.escape(src)}</code></p>"
        )

    def repl_figure(match: re.Match[str]) -> str:
        fig_html = match.group(0)
        m_src = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', fig_html, re.I)
        if not m_src:
            return fig_html
        m_alt = re.search(r'<img\b[^>]*\balt="([^"]*)"', fig_html, re.I)
        m_cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", fig_html, re.I | re.DOTALL)
        src = html_lib.unescape(m_src.group(1))
        alt = html_lib.unescape(m_alt.group(1)) if m_alt else ""
        cap = re.sub(r"<[^>]+>", "", m_cap.group(1)).strip() if m_cap else alt
        return handle_img_or_figure(src, alt, cap, fig_html)

    # First pass: <figure>...<img ...>...</figure>
    stage1 = re.sub(r"<figure\b[^>]*>.*?</figure>", repl_figure, raw_html, flags=re.I | re.DOTALL)

    # Second pass: standalone <img ...> outside <figure>
    def repl_standalone_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        m_src = re.search(r'src="([^"]+)"', tag, re.I)
        m_alt = re.search(r'alt="([^"]*)"', tag, re.I)
        src = html_lib.unescape(m_src.group(1)) if m_src else ""
        alt = html_lib.unescape(m_alt.group(1)) if m_alt else ""
        return handle_img_or_figure(src, alt, alt, tag)

    # Avoid re-processing <img> already inside <figure> by splitting around <figure>...</figure>
    parts = re.split(r"(<figure\b[^>]*>.*?</figure>)", stage1, flags=re.I | re.DOTALL)
    for idx_p, part in enumerate(parts):
        if not part.lower().startswith("<figure"):
            parts[idx_p] = re.sub(r"<img\b[^>]*>", repl_standalone_img, part, flags=re.I)

    return "".join(parts), local_upload_queue, skipped_missing


def upload_queued_local_assets(
    cdp: CDPClient, sess: str, queue: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Uploads local .png/.jpg/.gif files directly into Medium's editor at each `__MEDIUM_LOCAL_UPLOAD_i__`
    marker paragraph using CDP `Page.setInterceptFileChooserDialog` + `DOM.setFileInputFiles` (zero OS dialogs!).
    """
    if not queue:
        return []

    results: list[dict[str, Any]] = []
    cdp.call("DOM.enable", session_id=sess)
    cdp.call("Page.setInterceptFileChooserDialog", {"enabled": True}, session_id=sess)
    try:
        for item in queue:
            marker = item["marker"]
            file_path = item["file"]
            caption = item.get("caption") or ""

            # 1. Scroll marker paragraph into view and get center coordinates
            loc = cdp.eval_js(
                sess,
                f"""(() => {{
                    const marker = {json.dumps(marker)};
                    const root = document.querySelector('.postArticle-content, section.section--body, article') || document.body;
                    const p = Array.from(root.querySelectorAll('p')).find(el => (el.innerText || '').includes(marker));
                    if (!p) return null;
                    p.scrollIntoView({{ block: 'center' }});
                    const r = p.getBoundingClientRect();
                    return {{ x: r.left + 30, y: r.top + r.height / 2 }};
                }})()""",
            )
            if not loc:
                results.append({"marker": marker, "file": file_path, "uploaded": False, "reason": "marker_not_found"})
                continue

            # 2. Place cursor at END of marker paragraph and press Enter to open a clean empty paragraph (where Medium's (+) button appears!)
            cdp.click_xy(sess, loc["x"], loc["y"])
            time.sleep(0.2)
            cdp.eval_js(
                sess,
                f"""(() => {{
                    const marker = {json.dumps(marker)};
                    const root = document.querySelector('.postArticle-content, section.section--body, article') || document.body;
                    const p = Array.from(root.querySelectorAll('p')).find(el => (el.innerText || '').includes(marker));
                    if (!p) return false;
                    p.focus();
                    const sel = window.getSelection();
                    const range = document.createRange();
                    range.selectNodeContents(p);
                    range.collapse(false);
                    sel.removeAllRanges();
                    sel.addRange(range);
                    return true;
                }})()""",
            )
            cdp.press_enter(sess)
            time.sleep(0.55)

            # Clear stale fileChooserOpened events
            cdp._pending_events = [e for e in cdp._pending_events if e.get("method") != "Page.fileChooserOpened"]

            # 3. Click Medium's inline '+' button next to the empty paragraph, then click the 'Add an image' camera icon
            plus_btn = cdp.eval_js(
                sess,
                """(() => {
                    const sel = [
                        'button[data-action="inline-menu"]',
                        '.js-inlineTooltipControl',
                        '.inlineTooltip button',
                        'button[title*="Add" i]',
                        'button[aria-label*="Add" i]'
                    ];
                    for (const s of sel) {
                        const b = document.querySelector(s);
                        if (b) {
                            const r = b.getBoundingClientRect();
                            if (r.width > 0 && r.height > 0) return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                        }
                    }
                    // Geometric fallback: circular (+) button next to the currently selected empty paragraph
                    const curP = document.querySelector('p.is-selected, .graf--empty') || document.activeElement;
                    if (curP) {
                        const pr = curP.getBoundingClientRect();
                        const near = Array.from(document.querySelectorAll('button')).find(b => {
                            const br = b.getBoundingClientRect();
                            return br.width >= 20 && br.width <= 60 && Math.abs((br.top + br.height / 2) - (pr.top + pr.height / 2)) < 50 && !/publish/i.test(b.innerText || '');
                        });
                        if (near) {
                            const br = near.getBoundingClientRect();
                            return { x: br.left + br.width / 2, y: br.top + br.height / 2 };
                        }
                    }
                    return null;
                })()""",
            )
            if plus_btn:
                cdp.click_xy(sess, plus_btn["x"], plus_btn["y"])
                time.sleep(0.4)

            img_btn = cdp.eval_js(
                sess,
                """(() => {
                    const sel = [
                        'button[data-action="inline-menu-image"]',
                        '.inlineTooltip-menu button[title*="image" i]',
                        '.inlineTooltip-menu button[aria-label*="image" i]',
                        'button[data-testid*="image" i]',
                        '.inlineTooltip-menu button'
                    ];
                    for (const s of sel) {
                        const b = document.querySelector(s);
                        if (b) {
                            const r = b.getBoundingClientRect();
                            if (r.width > 0 && r.height > 0) return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                        }
                    }
                    return null;
                })()""",
            )
            if img_btn:
                cdp.click_xy(sess, img_btn["x"], img_btn["y"])

            evt = cdp.wait_for_event("Page.fileChooserOpened", timeout=2.5)
            uploaded_ok = False
            if evt and evt.get("params", {}).get("backendNodeId"):
                cdp.call(
                    "DOM.setFileInputFiles",
                    {"backendNodeId": evt["params"]["backendNodeId"], "files": [file_path]},
                    session_id=sess,
                )
                uploaded_ok = True
            else:
                # Fallback: query <input type="file"> directly in DOM
                doc_root = cdp.call("DOM.getDocument", {"depth": 1}, session_id=sess)["root"]["nodeId"]
                q = cdp.call(
                    "DOM.querySelector",
                    {"nodeId": doc_root, "selector": 'input[type="file"]'},
                    session_id=sess,
                )
                if q.get("nodeId"):
                    cdp.call(
                        "DOM.setFileInputFiles",
                        {"nodeId": q["nodeId"], "files": [file_path]},
                        session_id=sess,
                    )
                    uploaded_ok = True

            time.sleep(2.5)
            if uploaded_ok and caption:
                # Focus the newly inserted <figcaption> (if empty) and insert caption text
                cap_box = cdp.eval_js(
                    sess,
                    """(() => {
                        const figs = Array.from(document.querySelectorAll('.postArticle-content figure, section.section--body figure'));
                        for (const f of figs) {
                            const fc = f.querySelector('figcaption');
                            if (fc && (!fc.innerText.trim() || /type caption/i.test(fc.innerText))) {
                                fc.scrollIntoView({ block: 'center' });
                                const r = fc.getBoundingClientRect();
                                if (r.width > 0) return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
                            }
                        }
                        return null;
                    })()""",
                )
                if cap_box:
                    cdp.click_xy(sess, cap_box["x"], cap_box["y"])
                    time.sleep(0.15)
                    cdp.insert_text(sess, caption)
                    time.sleep(0.25)

            # Remove the temporary marker paragraph once upload triggered
            cdp.eval_js(
                sess,
                f"""(() => {{
                    const marker = {json.dumps(marker)};
                    const root = document.querySelector('.postArticle-content, section.section--body, article') || document.body;
                    const p = Array.from(root.querySelectorAll('p')).find(el => (el.innerText || '').includes(marker));
                    if (p) p.remove();
                }})()""",
            )
            results.append({"marker": marker, "file": Path(file_path).name, "uploaded": uploaded_ok})
    finally:
        try:
            cdp.call("Page.setInterceptFileChooserDialog", {"enabled": False}, session_id=sess)
        except Exception:
            pass
    return results


def _native_copy_from_local_html_and_paste_into_medium(
    cdp: CDPClient,
    sess: str,
    html_file_to_copy: Path,
    full_title: str,
) -> dict[str, Any]:
    """Brings tab to front, navigates to local HTML file, selects #medium-story-body via Blink Range,
    executes both document.execCommand('copy') and native CDP Copy, navigates to Medium /new-story,
    types Title into h3.graf--title, presses Enter, and pastes #medium-story-body into the story body!
    """
    cdp.call("Page.bringToFront", session_id=sess)
    file_url = html_file_to_copy.resolve().as_uri()
    cdp.navigate(sess, file_url, wait_sec=1.5)
    cdp.call("Page.bringToFront", session_id=sess)

    copied_info = cdp.eval_js(
        sess,
        """(() => {
            const bodyEl = document.getElementById('medium-story-body') || document.querySelector('article') || document.body;
            const sel = window.getSelection();
            sel.removeAllRanges();
            const range = document.createRange();
            range.selectNodeContents(bodyEl);
            sel.addRange(range);
            const execCopied = document.execCommand('copy');
            return { selectedChars: sel.toString().length, execCopied };
        })()""",
    )
    cdp.press_command_shortcut(sess, "c", "KeyC", 67, "Copy")
    time.sleep(0.4)

    cdp.navigate(sess, "https://medium.com/new-story", wait_sec=4.0)
    cdp.call("Page.bringToFront", session_id=sess)
    dismiss_editor_onboarding_overlay(cdp, sess)

    title_box = cdp.eval_js(
        sess,
        """(() => {
            const t = document.querySelector('h3.graf--title, [data-default-value*="Title"], .postArticle-content h3');
            if (!t) return null;
            t.focus();
            const r = t.getBoundingClientRect();
            return { x: r.left + 25, y: r.top + Math.min(20, r.height / 2) };
        })()""",
    )
    if not title_box:
        return {"ok": False, "error": "Could not locate Title element on /new-story"}

    # 1. Click h3.graf--title, insert Title text, press Enter to advance cursor to p.graf--p ('Tell your story...')
    cdp.click_xy(sess, title_box["x"], title_box["y"])
    time.sleep(0.25)
    cdp.insert_text(sess, full_title)
    time.sleep(0.35)
    cdp.press_enter(sess)
    time.sleep(0.6)

    # 2. Explicitly focus the body paragraph ('Tell your story...') and execute native Paste!
    body_box = cdp.eval_js(
        sess,
        """(() => {
            const p = document.querySelector('p.is-selected, .postArticle-content p, p.graf--p');
            if (!p) return null;
            p.focus();
            const r = p.getBoundingClientRect();
            return { x: r.left + 25, y: r.top + Math.min(18, r.height / 2) };
        })()""",
    )
    if body_box:
        cdp.click_xy(sess, body_box["x"], body_box["y"])
        time.sleep(0.2)
    cdp.press_command_shortcut(sess, "v", "KeyV", 86, "Paste")

    return {"ok": True, "copied_info": copied_info}


def dismiss_uh_oh_modal_if_present(cdp: CDPClient, sess: str) -> bool:
    try:
        return bool(
            cdp.eval_js(
                sess,
                """(() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const okBtn = btns.find(b => /^ok$/i.test((b.innerText || '').trim()));
                    if (okBtn) {
                        okBtn.click();
                        return true;
                    }
                    return false;
                })()""",
                await_promise=False,
                timeout=3.0,
            )
        )
    except Exception:
        return False


def wait_for_medium_images_and_save(cdp: CDPClient, sess: str, timeout_sec: float = 65.0) -> dict[str, Any]:
    """Polls until every <img> inside the Medium editor has finished uploading to Medium's CDN
    (data-image-id populated, zero external pending src), flushes a tiny title edit so Medium commits
    the post-upload imageId delta to its backend, and waits until header status shows 'Saved'.
    """
    deadline = time.monotonic() + timeout_sec
    last_state: dict[str, Any] = {}
    all_uploaded = False

    while time.monotonic() < deadline:
        dismiss_uh_oh_modal_if_present(cdp, sess)
        last_state = cdp.eval_js(
            sess,
            """(() => {
                const bodyText = document.body ? document.body.innerText : '';
                const savedMatch = bodyText.match(/\\b(Saved|Saving\\.\\.\\.)\\b/i);
                const root = document.querySelector('.postArticle-content, section.section--body, main article, article') || document.body;
                const imgs = Array.from(root.querySelectorAll('figure img, p img, img')).filter(i => {
                    const src = i.getAttribute('src') || '';
                    return !src.includes('/fit/c/60/60/'); // exclude navbar avatar
                });
                const total = imgs.length;
                const uploaded = imgs.filter(i => {
                    const src = i.getAttribute('src') || '';
                    const id = i.getAttribute('data-image-id') || '';
                    return (src.includes('medium.com') || Boolean(id)) && i.naturalWidth > 0;
                }).length;
                return {
                    url: location.href,
                    saveStatus: savedMatch ? savedMatch[1] : 'unknown',
                    totalImgs: total,
                    uploadedImgs: uploaded
                };
            })()""",
        ) or {}
        total = int(last_state.get("totalImgs", 0))
        uploaded = int(last_state.get("uploadedImgs", 0))
        if total == 0 or uploaded >= total:
            all_uploaded = True
            break
        time.sleep(1.5)

    # Flush a 1-space-and-backspace edit at the end of the title so Medium's delta-saver persists all uploaded data-image-ids!
    try:
        title_end = cdp.eval_js(
            sess,
            """(() => {
                const t = document.querySelector('h3.graf--title, .postArticle-content h3');
                if (!t) return null;
                t.scrollIntoView({ block: 'center' });
                const r = t.getBoundingClientRect();
                return { x: r.right - 6, y: r.top + Math.min(18, r.height / 2) };
            })()""",
        )
        if title_end:
            cdp.click_xy(sess, title_end["x"], title_end["y"])
            time.sleep(0.15)
            cdp.insert_text(sess, " ")
            time.sleep(0.3)
            cdp.call(
                "Input.dispatchKeyEvent",
                {"type": "rawKeyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8, "nativeVirtualKeyCode": 8},
                session_id=sess,
            )
            cdp.call(
                "Input.dispatchKeyEvent",
                {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8, "nativeVirtualKeyCode": 8},
                session_id=sess,
            )
    except Exception:
        pass

    # Now wait up to 15s for 'Saved' (not 'Saving...')
    save_deadline = time.monotonic() + 15.0
    while time.monotonic() < save_deadline:
        time.sleep(1.2)
        status = str(
            cdp.eval_js(
                sess,
                """(() => {
                    const m = (document.body ? document.body.innerText : '').match(/\\b(Saved|Saving\\.\\.\\.)\\b/i);
                    return m ? m[1] : 'unknown';
                })()""",
            )
            or "unknown"
        )
        last_state["saveStatus"] = status
        if status.lower() == "saved":
            time.sleep(1.5)
            break

    last_state["allUploaded"] = all_uploaded
    return last_state


def run_method_b_paste(
    cdp: CDPClient,
    sess: str,
    html_path: Path,
    title_prefix: str,
    canonical_override: str | None,
    out_dir: Path,
) -> dict[str, Any]:
    title, canon_from_html, _ = extract_story_payload_from_html(html_path)
    canonical_url = canonical_override or canon_from_html
    full_title = f"{title_prefix}{title}"

    # Keep reachable 200-OK remote images intact, queue local/un-deployed PNGs & GIFs (Mermaid, Math, local GIFs) for direct upload!
    raw_html = html_path.read_text(encoding="utf-8")
    m_topics = re.search(r'data-topics="([^"]*)"', raw_html)
    topics_list = [t.strip() for t in html_lib.unescape(m_topics.group(1)).split(",") if t.strip()] if m_topics else []
    filtered_html, local_upload_queue, skipped_imgs = prepare_html_and_local_uploads(raw_html, html_path.parent)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as tmp_f:
        tmp_f.write(filtered_html)
        staged_html_path = Path(tmp_f.name)

    try:
        paste_res = _native_copy_from_local_html_and_paste_into_medium(cdp, sess, staged_html_path, full_title)
    finally:
        staged_html_path.unlink(missing_ok=True)

    time.sleep(3.5)
    dismiss_editor_onboarding_overlay(cdp, sess)
    local_upload_results = upload_queued_local_assets(cdp, sess, local_upload_queue)
    upload_sync_state = wait_for_medium_images_and_save(cdp, sess, timeout_sec=110.0)

    edit_url = str(cdp.eval_js(sess, "location.href", await_promise=False) or "")
    m_id = re.search(r"/p/([0-9a-f]+)", edit_url)
    story_id = m_id.group(1) if m_id else ""

    settings_audit = {}
    if story_id:
        settings_audit = inspect_and_set_canonical_in_settings(
            cdp,
            sess,
            story_id=story_id,
            canonical_url=canonical_url,
            topics=topics_list,
            screenshot_path=out_dir / "method_b_settings.png",
        )
        # Navigate back to /p/<story_id>/edit to force a FULL SERVER RELOAD and prove image persistence!
        cdp.navigate(sess, f"https://medium.com/p/{story_id}/edit", wait_sec=4.0)
        dismiss_editor_onboarding_overlay(cdp, sess)

    final_audit = cdp.eval_js(sess, AUDIT_EDITOR_JS)
    editor_shot = out_dir / "method_b_editor.png"
    cdp.screenshot(sess, editor_shot)

    return {
        "method": "B_HTML_PASTE",
        "paste_result": paste_res,
        "local_uploads": local_upload_results,
        "upload_sync_state": upload_sync_state,
        "skipped_unreachable_imgs": skipped_imgs,
        "story_id": story_id,
        "edit_url": f"https://medium.com/p/{story_id}/edit" if story_id else edit_url,
        "prefixed_title": full_title,
        "editor_screenshot": str(editor_shot),
        "editor_audit": final_audit,
        "settings_audit": settings_audit,
    }


def delete_test_draft_by_id(
    cdp: CDPClient, sess: str, story_id: str, allow_unprefixed: bool = False
) -> dict[str, Any]:
    """Deletes a single draft ONLY after verifying its title starts with `[TEST - DELETE ME]` (unless allow_unprefixed=True on explicit ID)."""
    if not story_id:
        return {"story_id": story_id, "deleted": False, "reason": "empty_story_id"}

    cdp.navigate(sess, f"https://medium.com/p/{story_id}/edit", wait_sec=3.0)
    title_txt = str(
        cdp.eval_js(
            sess,
            """(() => {
                const t = document.querySelector('h3.graf--title, .postArticle-content h3, h1');
                return t ? t.innerText.trim() : '';
            })()""",
        )
        or ""
    )
    if not allow_unprefixed and not title_txt.startswith(TEST_DRAFT_PREFIX):
        return {
            "story_id": story_id,
            "deleted": False,
            "reason": f"SAFETY_REFUSED: title {title_txt!r} does not start with {TEST_DRAFT_PREFIX!r}",
        }

    cdp.navigate(sess, f"https://medium.com/p/{story_id}/settings", wait_sec=3.5)
    # Click 'Delete story' in settings, then confirm 'Delete' in modal
    clicked_delete_story = cdp.eval_js(
        sess,
        """(() => {
            const btns = Array.from(document.querySelectorAll('button, a, [role="button"]'));
            const del = btns.find(b => /^delete\\s+story$/i.test((b.innerText || '').trim()));
            if (!del) return false;
            del.scrollIntoView({ block: 'center' });
            del.click();
            return true;
        })()""",
    )
    if not clicked_delete_story:
        return {"story_id": story_id, "deleted": False, "reason": "no_delete_story_button_on_settings"}

    time.sleep(1.5)
    confirmed = cdp.eval_js(
        sess,
        """(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const confirmBtn = btns.find(b => /^delete$/i.test((b.innerText || '').trim()));
            if (!confirmBtn) return false;
            confirmBtn.click();
            return true;
        })()""",
    )
    time.sleep(3.0)
    return {"story_id": story_id, "title": title_txt, "deleted": bool(confirmed)}


def cleanup_all_test_drafts(cdp: CDPClient, sess: str, extra_ids: list[str] | None = None) -> list[dict[str, Any]]:
    """Deletes any specified test draft IDs plus any `[TEST - DELETE ME]` drafts visible on /me/stories/drafts."""
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for sid in extra_ids or []:
        if sid and sid not in seen:
            seen.add(sid)
            results.append(delete_test_draft_by_id(cdp, sess, sid))

    # Also scan https://medium.com/me/stories/drafts (or /me/stories?tab=posts-draft) for leftover [TEST - DELETE ME] drafts
    cdp.navigate(sess, "https://medium.com/me/stories?tab=posts-draft", wait_sec=3.5)
    found_ids = cdp.eval_js(
        sess,
        f"""(() => {{
            const prefix = {json.dumps(TEST_DRAFT_PREFIX)};
            const links = Array.from(document.querySelectorAll('a[href*="/p/"]'));
            const ids = [];
            for (const a of links) {{
                const txt = (a.innerText || '').trim();
                const rowTxt = (a.closest('div, li, tr, article')?.innerText || '').trim();
                if (txt.startsWith(prefix) || rowTxt.includes(prefix)) {{
                    const m = (a.getAttribute('href') || '').match(/\\/p\\/([0-9a-f]+)/);
                    if (m) ids.push(m[1]);
                }}
            }}
            return Array.from(new Set(ids));
        }})()""",
    )
    for sid in found_ids or []:
        if sid and sid not in seen:
            seen.add(sid)
            results.append(delete_test_draft_by_id(cdp, sess, sid))

    cdp.navigate(sess, "https://medium.com/me/stories?tab=posts-draft", wait_sec=3.0)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Single-connection CDP Medium Draft Stager (Draft-Only HITL).")
    parser.add_argument(
        "action",
        choices=["status", "import-url", "paste-html", "ab-experiment", "cleanup-test-drafts", "delete-story"],
    )
    parser.add_argument("--chrome-root", default=None)
    parser.add_argument("--target-id", default=None)
    parser.add_argument("--story-id", default=None, help="Draft story ID for delete-story")
    parser.add_argument("--allow-unprefixed", action="store_true", help="Allow delete-story on an explicit --story-id without [TEST - DELETE ME] prefix")
    parser.add_argument("--url", default=None, help="Public article URL for Method A import or Canonical URL")
    parser.add_argument("--html", default=None, help="Compiled index.html path for Method B paste")
    parser.add_argument(
        "--title-prefix",
        default="[TEST - DELETE ME] ",
        help="Prefix added to draft title (pass '' for production)",
    )
    parser.add_argument("--out-dir", default="/tmp/medium_cdp_out", help="Directory for screenshots and JSON report")
    parser.add_argument(
        "--handshake-timeout",
        type=float,
        default=300.0,
        help="Seconds to wait for user to click 'Allow' on Chrome remote debugging prompt (default: 300)",
    )
    parser.add_argument(
        "--cleanup-after",
        action="store_true",
        help="Automatically delete `[TEST - DELETE ME]` drafts after capturing screenshots and reports",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    port, ws_path, _ = find_devtools_active_port(args.chrome_root)
    print(
        f"🔌 Connecting to Chrome CDP on 127.0.0.1:{port} (click 'Allow' in Chrome if prompted)...",
        file=sys.stderr,
        flush=True,
    )
    cdp = CDPClient("127.0.0.1", port, ws_path, handshake_timeout=args.handshake_timeout)
    try:
        if args.action == "status":
            targets = cdp.call("Target.getTargets", call_timeout=30.0).get("targetInfos", [])
            matched = [
                {"targetId": t.get("targetId"), "title": t.get("title"), "url": t.get("url")}
                for t in targets
                if t.get("type") == "page" and "medium.com" in (t.get("url") or "")
            ]
            print(json.dumps({"total_targets": len(targets), "matched_pages": matched}, indent=2))
            return 0

        tid = args.target_id or find_medium_target(cdp, "medium.com")["targetId"]
        sess = cdp.call("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]

        report: dict[str, Any] = {}
        created_ids: list[str] = []

        if args.action == "delete-story":
            if not args.story_id:
                raise ValueError("--story-id is required for delete-story")
            res_del = delete_test_draft_by_id(cdp, sess, args.story_id, allow_unprefixed=args.allow_unprefixed)
            print(json.dumps({"ok": True, "deleted": res_del}, indent=2))
            return 0

        if args.action == "cleanup-test-drafts":
            report["cleanup"] = cleanup_all_test_drafts(cdp, sess)
            cdp.screenshot(sess, out_dir / "drafts_after_cleanup.png")
            print(json.dumps({"ok": True, "cleanup": report["cleanup"]}, indent=2))
            return 0

        if args.action == "import-url":
            if not args.url:
                raise ValueError("--url is required for import-url")
            res_a = run_method_a_import(cdp, sess, args.url, args.title_prefix, out_dir)
            report["method_a"] = res_a
            if res_a.get("story_id"):
                created_ids.append(res_a["story_id"])

        elif args.action == "paste-html":
            if not args.html:
                raise ValueError("--html is required for paste-html")
            res_b = run_method_b_paste(
                cdp, sess, Path(args.html).expanduser().resolve(), args.title_prefix, args.url, out_dir
            )
            report["method_b"] = res_b
            if res_b.get("story_id"):
                created_ids.append(res_b["story_id"])

        elif args.action == "ab-experiment":
            if not args.url or not args.html:
                raise ValueError("Both --url and --html are required for ab-experiment")
            res_a = run_method_a_import(cdp, sess, args.url, f"{args.title_prefix}[A-IMPORT] ", out_dir)
            report["method_a"] = res_a
            if res_a.get("story_id"):
                created_ids.append(res_a["story_id"])

            res_b = run_method_b_paste(
                cdp,
                sess,
                Path(args.html).expanduser().resolve(),
                f"{args.title_prefix}[B-PASTE] ",
                args.url,
                out_dir,
            )
            report["method_b"] = res_b
            if res_b.get("story_id"):
                created_ids.append(res_b["story_id"])

        if args.cleanup_after:
            report["cleanup"] = cleanup_all_test_drafts(cdp, sess, extra_ids=created_ids)
            cdp.screenshot(sess, out_dir / "drafts_after_cleanup.png")

        report_file = out_dir / "ab_report.json"
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        summary = {}
        for k in ("method_a", "method_b"):
            if k in report:
                v = report[k]
                summary[k] = {
                    "story_id": v.get("story_id"),
                    "edit_url": v.get("edit_url"),
                    "save_status": v.get("editor_audit", {}).get("saveStatus"),
                    "error_banner": v.get("editor_audit", {}).get("errorBanner"),
                    "skipped_unreachable_imgs": v.get("skipped_unreachable_imgs"),
                    "figures_count": v.get("editor_audit", {}).get("figuresCount"),
                    "raw_imgs_count": v.get("editor_audit", {}).get("rawImgsCount"),
                    "pre_count": v.get("editor_audit", {}).get("preCount"),
                    "tables_count": v.get("editor_audit", {}).get("tablesCount"),
                    "blockquotes_count": v.get("editor_audit", {}).get("blockquotesCount"),
                    "ordered_lists_count": v.get("editor_audit", {}).get("orderedListsCount"),
                    "unordered_lists_count": v.get("editor_audit", {}).get("unorderedListsCount"),
                }
        if "cleanup" in report:
            summary["cleanup"] = report["cleanup"]
        print(json.dumps({"ok": True, "report_file": str(report_file), "summary": summary}, indent=2, ensure_ascii=False))
    finally:
        cdp.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
