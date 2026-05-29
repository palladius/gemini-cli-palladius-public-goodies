---
name: carlessian-gog
description: Google Workspace CLI managed the Carlesso way—featuring isolated configurations, selective read-only security, and standard workflows.
version: 1.0.0
---

# GOG (Google Workspace CLI) - The Carlesso Way

Opinionated guidelines and commands to manage GOG safely and efficiently under the Carlesso identity.

> [!IMPORTANT]
> **Use `gog`, not `gws`.** For some reason, `gws` does not work in this environment. Always prefer `gog` commands.

## 🔐 1. Selective Read-Only Security (The Gold Standard)
To protect your Gmail inbox from accidental write/send actions while maintaining write access to your Google Calendar, always authenticate personal accounts with selective scopes:

```bash
gog auth add palladiusbonton@gmail.com \
  --services all \
  --readonly \
  --extra-scopes "https://www.googleapis.com/auth/calendar" \
  --force-consent
```

### Why Read-Only is Crucial for Riccardo
Always enforce **READ-ONLY** access for critical personal and work accounts (`palladiusbonton@gmail.com` and `ricc@google.com`) because:
1. **Intimate/Private Life Safety**: These accounts contain your entire private and work history. Under no circumstances should important information be destroyed or mutated accidentally.
2. **Account Suspension Risk**: Google has a history of closing down heavily automated accounts. Safe, read-only scopes protect your lifelong accounts from triggering automated flag thresholds.
3. **General Risk Mitigation**: Automated LLM interactions are inherently unpredictable. Restricting writes provides peace of mind.

### Gmail Agent Safety
Even with full scopes, you can block all Gmail send/write operations at the CLI level for safety by using the `--gmail-no-send` flag:
```bash
gog --gmail-no-send send --to=recipient@example.com --subject="Hi" --body="Hello"
```

## 🌍 2. Isolated Multi-Identity Configurations
Keep your corporate, personal, and **Rubycon** identities completely separate by using isolated `XDG_CONFIG_HOME` paths.

### Rubycon Identity Setup
To authenticate strictly for `rubycon.italy@gmail.com` without mixing tokens:
```bash
XDG_CONFIG_HOME=~/.config/gog-rubycon gog auth add rubycon.italy@gmail.com --services=all --force-consent
```

### Recommended Shell Aliases
Add these to your shell config (`.bashrc` or `.bash_aliases`) to make isolated CLI usage safe and fast:
```bash
alias gog-rubycon='XDG_CONFIG_HOME=~/.config/gog-rubycon gog'
alias gws-rubycon='GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-rubycon gws'
```

## 🗓️ 3. Google Calendar Workflows
Standard operations for managing calendar events:

*   **List Calendars**: `gog calendar list`
*   **Search Events**: `gog calendar events primary --from "2026-05-29T00:00:00+02:00" --to "2026-05-29T23:59:59+02:00"`
*   **Create Event**:
    ```bash
    gog calendar create primary \
      --summary "Riccardo fixed gog auth on mini-lobby" \
      --from "2026-05-29T08:17:00+02:00" \
      --to "2026-05-29T08:47:00+02:00"
    ```

## 📧 4. Gmail Search Workflows
Standard operations for searching mail:

*   **List Unread**: `gog gmail search is:unread`
*   **Search by Sender**: `gog gmail search "from:ilfattoquotidiano.it"`
*   **Recent Mail**: `gog gmail search "newer_than:7d"`

## 📂 5. Google Drive Workflows
Standard operations for listing and searching files:

*   **List Drive Files**: `gog ls`
*   **Search Drive Files**: `gog search "Carlesso"`
