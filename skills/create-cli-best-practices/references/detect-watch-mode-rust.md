# Rust/Go CLI Best Practices — Reference

## Recommended Libraries

| Language | Library | Purpose |
|----------|---------|---------|
| **Rust** | [`clap`](https://docs.rs/clap) | Argument parsing, subcommands, `--help` generation |
| **Go**   | [`cobra`](https://github.com/spf13/cobra) | Command structure, subcommands, completions |

---

# Detecting Linux `watch` Mode in Rust CLIs

## Problem

The Linux `watch` command uses an ncurses renderer that **does not support OSC-8
hyperlinks**, and renders raw ANSI escape sequences as garbage:

```
]8;;http://go/rx6/e/9966\9966]8;;\   abdelfettah  WeAreDevelopers ...
```

`watch` allocates a pseudo-TTY, so `isatty()` returns `true`. It sets no special
env vars. The only reliable signal is the **parent process name** in `/proc`.

## Solution: Walk the `/proc` Process Tree

```rust
/// Returns true if any ancestor (up to 6 levels) is the Linux `watch` command.
/// Handles both:
///   `watch drc cmd`             → parent      = watch  (1 hop)
///   `watch bash -c 'drc cmd'`   → grandparent = watch  (2 hops)
fn is_inside_watch() -> bool {
    let mut pid = std::process::id();
    for _ in 0..6 {
        let status = match std::fs::read_to_string(format!("/proc/{}/status", pid)) {
            Ok(s) => s,
            Err(_) => return false,
        };
        let ppid: u32 = status.lines()
            .find(|l| l.starts_with("PPid:"))
            .and_then(|l| l.split_whitespace().nth(1))
            .and_then(|v| v.parse().ok())
            .unwrap_or(0);
        if ppid <= 1 { return false; }  // reached init — stop
        let comm = std::fs::read_to_string(format!("/proc/{}/comm", ppid))
            .unwrap_or_default();
        if comm.trim() == "watch" { return true; }
        pid = ppid;
    }
    false
}

/// Gate ALL fancy output on this one function.
fn supports_hyperlinks() -> bool {
    if std::env::var("NO_COLOR").is_ok() { return false; }
    if std::env::var("TERM").map(|t| t == "dumb").unwrap_or(false) { return false; }
    !is_inside_watch()
}

/// OSC-8 hyperlink — plain text fallback under watch.
fn osc8(url: &str, text: &str) -> String {
    if url.is_empty() || !supports_hyperlinks() { return text.to_string(); }
    format!("\x1b]8;;{}\x1b\\{}\x1b]8;;\x1b\\", url, text)
}

/// ANSI color — stripped under watch.
fn ansi(code: &str, text: &str) -> String {
    if supports_hyperlinks() { format!("\x1b[{}m{}\x1b[0m", code, text) }
    else { text.to_string() }
}
```

## UX: Announce the Mode

```rust
if is_inside_watch() {
    println!("📺 watch mode — plain text (no hyperlinks)");
} else {
    println!("🖥️  normal mode — OSC-8 hyperlinks active");
}
```

## Why Not `isatty` / Env Vars?

| Signal              | Works? | Why                                     |
|---------------------|--------|-----------------------------------------|
| `isatty(stdout)`    | ❌     | `watch` allocates a PTY → returns true  |
| `WATCH_INTERVAL`    | ❌     | `watch` sets no env vars                |
| `TERM=dumb`         | ❌     | `watch` inherits parent `TERM`          |
| `/proc/<ppid>/comm` | ✅     | Kernel truth, always accurate           |

## Portability

Linux-only (`/proc` is Linux-specific). On macOS, use `sysctl KERN_PROC_PPID`
or skip detection (OSC-8 works in iTerm2/Terminal.app anyway).

## Origin

Discovered while building `drc sheetless list` in devrel-cli (2026-06-25).
Also lives as standalone skill: `detect-watch-mode` in palladius-public-goodies.
