# 💻 Terminal & TUI Video Demos with Charm VHS

Record deterministic terminal recordings (GIF and MP4) from declarative `.tape` scripts using [Charm VHS](https://github.com/charmbracelet/vhs).

---

## 🛠️ Prerequisites

Make sure `vhs`, `ttyd`, and `ffmpeg` are installed:

```bash
# macOS
brew install vhs ffmpeg

# Linux / Debian
# Install ttyd and vhs binary from https://github.com/charmbracelet/vhs/releases
```

Verify versions:
```bash
vhs --version   # >= 0.7.0
ffmpeg -version
```

---

## 📜 1. Tape Script Anatomy

VHS reads `.tape` scripts specifying terminal dimensions, themes, typing speed, and commands:

```tape
# 1. Output files
Output demo.gif
Output demo.mp4

# 2. Terminal Appearance
Set FontSize 16
Set FontFamily "Menlo"
Set Width 1024
Set Height 600
Set Padding 20
Set Theme "TokyoNight"
Set TypingSpeed 50ms
Set PlaybackSpeed 1

# 3. Execution Commands
Type "echo Hello Antigravity"
Sleep 500ms
Enter

# 4. Wait for processing / streaming
Sleep 5s
```

Run VHS to record:
```bash
vhs demo.tape
```

---

## ⚠️ Critical Tape Rules

### A. The Output Path Rule
`Output` and file paths are **relative to the directory where `vhs` is executed**, NOT necessarily the project root or the `.tape` file location:

```bash
# If invoked from demos/console:
cd demos/console && vhs demo.tape

# Inside demo.tape:
Output demo.mp4           # => demos/console/demo.mp4 (CORRECT)
Output demos/demo.mp4     # => demos/console/demos/demo.mp4 (WRONG - double nested)
```

### B. ⚠️ The Quoting Catastrophe (CRITICAL)
VHS `Type` commands have broken quoting parser logic. Follow these non-negotiable rules:

| Rule | Bad Example | Why |
|---|---|---|
| **NO single quotes** inside `Type` | `Type "puts 'hello'"` ❌ | VHS chokes on nested quotes |
| **NO `%()` or `%[]`** inside `Type` | `Type "%(hello)"` ❌ | Interpreted as VHS syntax |
| **NO backticks** inside `Type` | `Type "run \`cmd\`"` ❌ | Shell expansion issues |

**Workaround using `chr()` construction in Ruby/Shell:**
```tape
# Instead of: Type "DOTENV = '.env'"
Type "DOTENV = 46.chr + :env.to_s"       # 46 is ASCII '.'

# Instead of: Type "puts '🟢 hello'"
Type "GREEN = 128994.chr(Encoding::UTF_8) + 32.chr"
Type "puts GREEN + :hello.to_s"

# Instead of: Type "path = '~/git'"
Type "path = File.join(Dir.home, :git.to_s)"
```

### C. Sleep Timing (Prevent Command Pile-Up)
If `Sleep` is too short, VHS types the next command while the previous command is still running. Commands pile up unexecuted in the terminal buffer.

| Operation | Minimum Sleep | Notes |
|---|---|---|
| Launch Ruby/Node app | `Sleep 10s` | Gem/dependency resolution, boot |
| LLM API call | `Sleep 8s` | Streaming model response |
| Shell command / eval | `Sleep 2s` | Prompt ready |
| `cd()` with workspace scan | `Sleep 8-12s` | Depends on workspace file count |
| Variable assignment | `Sleep 1-2s` | Fast eval |

### D. Return Value Pollution
In interactive shells (IRB, Python REPL), methods returning large objects (arrays, hashes, rulesets) dump dozens of lines on screen, pushing the valuable demo content offscreen. Fix:
- In Ruby: return `self` from configuration/deny methods and implement custom `#inspect`.
- End statements with `; nil` if necessary to suppress output.
