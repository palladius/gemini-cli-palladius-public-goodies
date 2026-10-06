# 🎬 Richard Console Demo — REAL VHS Tape v9
# Drives the ACTUAL console with live Gemini API.
#
# ⚠️ VHS QUOTING RULES:
#   - NO quotes (single/double/backtick) around strings inside Type
#   - Define emoji constants with chr(), then use them by name
#   - Use File.join(Dir.home, :symbol.to_s) for paths
#
# Usage: cd ~/git/antigravity-ruby-sdk && vhs demos/richard-console/demo.tape

Output demo.mp4
Output demo.gif

# ─── Terminal Setup ───────────────────────────────────────
Set FontSize 14
Set FontFamily "Menlo"
Set Width 1100
Set Height 700
Set Padding 16
Set Theme "Dracula"
Set TypingSpeed 50ms
Set PlaybackSpeed 1
Set LetterSpacing 0

# ═══════════════════════════════════════════════════════════
# ACT 1: Launch console
# ═══════════════════════════════════════════════════════════
Type "rv run ruby ../../examples/10_console.rb"
Enter
Sleep 10s

# ═══════════════════════════════════════════════════════════
# ACT 2: Quick LLM chat
# ═══════════════════════════════════════════════════════════
Type "Hello! What can you do?"
Enter
Sleep 8s

# ═══════════════════════════════════════════════════════════
# ACT 3: Shell + Ruby eval (deterministic!)
# ═══════════════════════════════════════════════════════════
Type "! pwd"
Enter
Sleep 2s

Type "r! Antigravity::VERSION"
Enter
Sleep 2s

# ═══════════════════════════════════════════════════════════
# ACT 4: /irb — THE MATRIX
# ═══════════════════════════════════════════════════════════
Type "/irb"
Enter
Sleep 2s

# Config slice
Type "config.select { |k,_| [:version, :model, :workspace_analysis].include?(k) }"
Enter
Sleep 2s

# Disable workspace analysis EARLY so cd() doesn't trigger slow scans
Type "set_workspace_analysis false"
Enter
Sleep 1s

# Define emoji helpers (with space baked in)
Type "GREEN_EMOJI = 128994.chr(Encoding::UTF_8) + 32.chr"
Enter
Sleep 1s

Type "RED_EMOJI = 128308.chr(Encoding::UTF_8) + 32.chr"
Enter
Sleep 1s

# 🟢🔴 Policy visualization — clean and readable!
Type "Antigravity::Policy::SAFE_CMDS.each { |c| puts GREEN_EMOJI + c.to_s }"
Enter
Sleep 3s

Type "Antigravity::Policy::CATASTROPHIC_CMDS.each { |c| puts RED_EMOJI + c.to_s }"
Enter
Sleep 3s


# ═══════════════════════════════════════════════════════════
# ACT 6: 🛡️ Dynamic Policy Deny — SECURITY WOW
# read_file → works, deny_file → read_file → BOOM!
# ═══════════════════════════════════════════════════════════

# Build .env string without quotes (46 = '.')
Type "DOTENV = 46.chr + :env.to_s"
Enter
Sleep 2s

# 1️⃣ Read .env — works fine!
Type "read_file(DOTENV)"
Enter
Sleep 3s

# 2️⃣ Lock it down!
Type "policy.deny(:read_file, DOTENV)"
Enter
Sleep 3s

# 3️⃣ Try again — DENIED! 🛡️💥
Type "read_file(DOTENV)"
Enter
Sleep 5s

# Exit Matrix
Type "exit"
Enter
Sleep 2s

# ═══════════════════════════════════════════════════════════
# FINALE
# ═══════════════════════════════════════════════════════════
Type "/quit"
Enter
Sleep 2s
