---
name: using-zapfast
description: >-
  💛 Guide for interacting with ZapFast (native Rust + egui WhatsApp client) on Linux/macOS/Windows: CLI URI targets, local XDG file paths, SQLCipher archive encryption pitfalls, and safe ways to export or inspect chats for AI agents.
compatibility: Gemini CLI
metadata:
  version: "1.0.0"
  author: Riccardo Carlesso
---

# Using ZapFast (💛)

Guide to **ZapFast** ([zapfast.rocks](https://zapfast.rocks/) / [`crmne/zapfast`](https://github.com/crmne/zapfast)), a native Rust + `egui` WhatsApp desktop client that communicates directly via the WhatsApp Web companion protocol without Electron/Chromium.

---

## 1. CLI & URI Invocation

ZapFast registers the `whatsapp:` and `wa:` schemes and accepts a target on the command line (bringing the existing window forward if already running):

```bash
# Open a 1:1 chat by phone number or link
zapfast +391234567890
zapfast 'https://wa.me/391234567890?text=Hello'
zapfast 'whatsapp://send?phone=391234567890'

# Preview/join a group invite link
zapfast 'https://chat.whatsapp.com/AbCdEf1234567890XyZ'

# Lifecycle & debugging
zapfast --start-hidden   # Start in system tray
zapfast -v               # Verbose WhatsApp protocol logging
zapfast quit             # Gracefully quit running instance
```

> [!NOTE]
> Opening an existing group by `@g.us` JID from CLI is not supported directly (`crmne/zapfast#859`); use `Ctrl+K` inside the window to jump to a group.

---

## 2. Local File Layout (Linux XDG)

Each linked phone number gets an isolated folder `<id>` (e.g. `1`):

| Purpose | Path (Linux) | Encrypted? |
|---|---|---|
| Global settings & account order | `~/.config/zapfast/settings.json`, `accounts.json` | No (JSON) |
| Custom themes | `~/.config/zapfast/themes/` | No (JSON) |
| Per-account settings (`last_chat`, etc.) | `~/.local/state/zapfast/accounts/<id>/settings.json` | No (JSON) |
| Signal/WhatsApp session state | `~/.local/state/zapfast/accounts/<id>/session.db` | No (SQLite 3) |
| **Message archive** | `~/.local/state/zapfast/accounts/<id>/archive.db` (+ `-wal`, `-shm`) | **Yes (SQLCipher 4)** |
| Media & avatar cache | `~/.cache/zapfast/accounts/<id>/media/`, `avatars/` | No (raw `.jpg`, `.ogg`, `.mp4`, named `<jid>-<msgid>.<ext>`) |
| Logs | `~/.local/state/zapfast/zapfast.log`, `zapfast.previous.log` | No (text) |

* **macOS:** `~/Library/Application Support/me.paolino.zapfast` and `~/Library/Caches/me.paolino.zapfast`.
* **Windows:** `%APPDATA%\paolino\zapfast\config`, `%LOCALAPPDATA%\paolino\zapfast\data`, `%LOCALAPPDATA%\paolino\zapfast\cache`.

---

## 3. Why `sqlite3` Fails on `archive.db`

`archive.db` is **not** a plain SQLite file — it is encrypted with **SQLCipher 4 (HMAC-SHA512)** using a random 256-bit (32-byte) binary key stored in the OS credential store:

- **Linux:** Secret Service (`org.freedesktop.secrets`, e.g., GNOME Keyring / KeePassXC) under `service = rocks.zapfast.ZapFast`.
- **macOS:** Keychain (`me.paolino.zapfast`).
- **Windows:** Windows Credential Manager.

Running `sqlite3 archive.db` directly fails with `Error: file is not a database`.

> [!CAUTION]
> **Agent Safety Rule:** AI agents must **never** read or dump secrets from the OS keyring (`secretstorage`, `secret-tool`, Keychain) into logs or model context. When an agent needs conversation text from ZapFast, use one of the safe workflows below.

---

## 4. Safe Ways to Feed ZapFast Chats to an Agent

1. **Built-in Plaintext Export (Recommended):**
   In ZapFast, open the conversation → click **`⋮`** (top-right chat menu) → **Export chat…** (*Esporta chat…*).
   - Saves a clean UTF-8 `_chat.txt` with UTC timestamps (or a `.zip` including already-downloaded attachments).
   - Zero keyring access required.
2. **Visual Capture:**
   Bring the target chat to the front (`zapfast +<number>`) and capture the window using the `take-screenshot` skill.
3. **Human-Run Local Query (SQLCipher):**
   If the user manually inspects `archive.db` from their own shell/script:
   - Always copy `archive.db`, `archive.db-wal`, and `archive.db-shm` together into a temporary directory before opening so you do not contend with ZapFast's active WAL lock.
   - Open with `sqlcipher` / Python `sqlcipher3` using `PRAGMA key = "x'<64-hex-chars>'"` (raw 32-byte key hex literal, since the secret is binary bytes rather than an ASCII passphrase).
