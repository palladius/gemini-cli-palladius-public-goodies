#!/usr/bin/env python3
"""Analyze Git diff history (or uncommitted changes) of agent prompt markdown files for bloat.

Detects anti-patterns in GEMINI.md, AGENTS.md, CLAUDE.md, CONTRIBUTING.md, SPECS.md,
INSTRUCTIONS.md, SKILL.md, etc.:
  1. OVERFITTING_H2_SECTION: Adding a whole H2/H3 section with only 1-2 lines/bullets
     for a narrow, hyper-specific edge case.
  2. CRAMMED_LINE: Packing many instructions/clauses into a single run-on line
     ("10 instructions in 1 line").
  3. APPEND_ONLY_EOF: Purely appending to the bottom of the file (+N / -0 lines)
     without consolidating existing sections.
  4. CONFLICT_OR_GARBAGE: Leaving git conflict markers (<<<<<<<, =======, >>>>>>>)
     in the prompt file.
  5. WALL_OF_TEXT: Dumping >25 added lines in a single hunk without refactoring.

Usage:
  python3 $SKILL_DIR/scripts/analyze_bloat_history.py GEMINI.md
  python3 $SKILL_DIR/scripts/analyze_bloat_history.py --all
  python3 $SKILL_DIR/scripts/analyze_bloat_history.py --uncommitted GEMINI.md
  python3 $SKILL_DIR/scripts/analyze_bloat_history.py --llm GEMINI.md
"""

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_PROMPT_FILES = (
    "GEMINI.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "SPECS.md",
    "SPEC.md",
    "INSTRUCTIONS.md",
    "SKILL.md",
)

DEFAULT_LLM_MODELS = (
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
)

IMPERATIVE_PATTERNS = re.compile(
    r"\b("
    r"must|never|always|do not|don't|make sure|ensure|remember to|"
    r"avoid|prefer|require|mandatory|forbidden|only if|whenever|should not|should"
    r")\b",
    re.IGNORECASE,
)

OVERFIT_CONDITIONAL_PATTERNS = re.compile(
    r"\b("
    r"if you change|when you change|if you touch|remember to update|"
    r"specific to|only on host|workaround for|hack for|temporary"
    r")\b",
    re.IGNORECASE,
)

CONFLICT_MARKER_RE = re.compile(r"^(\+{1,2})\s*(<{7}|={7}|>{7}|> > > > > > >)")
HUNK_HEADER_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$")


@dataclasses.dataclass
class BloatSignal:
    code: str
    weight: float
    description: str


@dataclasses.dataclass
class HunkAnalysis:
    commit_hash: str
    commit_short: str
    author: str
    date: str
    subject: str
    file_path: str
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    hunk_header: str
    raw_diff_lines: List[str]
    added_lines: List[str]
    removed_lines: List[str]
    signals: List[BloatSignal]
    deterministic_probability: float
    deterministic_reason: str
    llm_result: Optional[Dict[str, Any]] = None

    @property
    def line_range_str(self) -> str:
        end_line = self.new_start + max(self.new_count - 1, 0)
        return f"Line {self.new_start}..{end_line} ({self.hunk_header.strip()})"

    @property
    def final_probability(self) -> float:
        if self.llm_result and isinstance(self.llm_result.get("probability"), (int, float)):
            return round(float(self.llm_result["probability"]), 2)
        return round(self.deterministic_probability, 2)

    @property
    def final_reason(self) -> str:
        if self.llm_result and self.llm_result.get("reason"):
            return str(self.llm_result["reason"])
        return self.deterministic_reason


def _count_clauses_and_directives(line_text: str) -> Tuple[int, int]:
    """Count imperative keywords and sentence/clause breaks in a single line."""
    directives = len(IMPERATIVE_PATTERNS.findall(line_text))
    inline_bullets = len(re.findall(r"(?:^|\s)(?:\(\d+\)|\d+\)|\d+\.|-|\*)\s+\w+", line_text))
    sentence_splits = len(re.findall(r"(?:;\s*\w|[.!]\s+[A-Z`*])", line_text))
    comma_clauses = len(
        re.findall(
            r",\s+(?:and\s+|but\s+|or\s+|then\s+|never\s+|always\s+|make\s+|ensure\s+|do\s+|don't\s+|avoid\s+|prefer\s+)?\w+",
            line_text,
            re.IGNORECASE,
        )
    )
    clauses = 1 + sentence_splits + comma_clauses + max(0, inline_bullets - 1)
    return directives, clauses


def analyze_hunk_deterministic(
    added_lines: List[str],
    removed_lines: List[str],
    old_start: int,
    old_count: int,
    new_start: int,
    new_count: int,
) -> Tuple[List[BloatSignal], float, str]:
    """Run fast, deterministic heuristics on a single git diff hunk."""
    signals: List[BloatSignal] = []

    non_empty_added = [line for line in added_lines if line.strip()]
    non_empty_removed = [line for line in removed_lines if line.strip()]

    if not non_empty_added:
        return [], 0.0, "No net content lines added."

    # 1. Check for git conflict markers or merge garbage
    for line in non_empty_added:
        if re.match(r"^\s*(<{7}|={7}|>{7}|> > > > > > >)", line):
            signals.append(
                BloatSignal(
                    code="CONFLICT_OR_GARBAGE",
                    weight=0.85,
                    description=f"Git merge conflict marker committed into prompt: '{line.strip()[:40]}'",
                )
            )
            break

    # 2. Check for OVERFITTING_H2_SECTION:
    headings_in_hunk: List[Tuple[int, str]] = []
    for idx, line in enumerate(non_empty_added):
        if re.match(r"^#{2,3}\s+\S+", line.strip()):
            headings_in_hunk.append((idx, line.strip()))

    for pos, (h_idx, heading_text) in enumerate(headings_in_hunk):
        next_h_idx = headings_in_hunk[pos + 1][0] if pos + 1 < len(headings_in_hunk) else len(non_empty_added)
        body_lines = [
            l.strip()
            for l in non_empty_added[h_idx + 1 : next_h_idx]
            if l.strip() and not l.strip().startswith("```")
        ]
        body_text = " ".join(body_lines)
        has_overfit_phrase = bool(OVERFIT_CONDITIONAL_PATTERNS.search(body_text))

        if len(body_lines) == 1:
            weight = 0.65 if has_overfit_phrase else 0.55
            signals.append(
                BloatSignal(
                    code="OVERFITTING_H2_SECTION",
                    weight=weight,
                    description=(
                        f"Added whole heading '{heading_text}' for a single-concept / "
                        f"1-item rule ({body_lines[0][:80]}...)."
                    ),
                )
            )
        elif len(body_lines) == 2 and has_overfit_phrase:
            signals.append(
                BloatSignal(
                    code="OVERFITTING_H2_SECTION",
                    weight=0.50,
                    description=(
                        f"Added heading '{heading_text}' with only 2 lines for a narrow/conditional case."
                    ),
                )
            )

    # 3. Check for CRAMMED_LINE ("10 instructions in 1 line")
    for line in non_empty_added:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("|"):
            continue
        char_len = len(stripped)
        directives, clauses = _count_clauses_and_directives(stripped)

        if (directives >= 3 and clauses >= 3) or (char_len > 240 and (directives >= 2 or clauses >= 3)) or clauses >= 5:
            signals.append(
                BloatSignal(
                    code="CRAMMED_LINE",
                    weight=0.55,
                    description=(
                        f"Single line packs {clauses} clauses / {directives} directives "
                        f"({char_len} chars): '{stripped[:90]}...'"
                    ),
                )
            )
            break
        elif char_len > 300:
            signals.append(
                BloatSignal(
                    code="CRAMMED_LINE",
                    weight=0.40,
                    description=f"Excessively long instruction line ({char_len} chars): '{stripped[:90]}...'",
                )
            )
            break

    # 4. Check for APPEND_ONLY_EOF
    if len(non_empty_removed) == 0 and old_count <= 4 and new_start > 15 and len(non_empty_added) >= 2:
        signals.append(
            BloatSignal(
                code="APPEND_ONLY_EOF",
                weight=0.20,
                description=(
                    f"Pure append (+{len(non_empty_added)} / -0 non-empty lines) near line {new_start} "
                    f"without consolidating existing instructions."
                ),
            )
        )

    # 5. Check for WALL_OF_TEXT
    if len(non_empty_added) > 25 and len(non_empty_removed) <= 2:
        signals.append(
            BloatSignal(
                code="WALL_OF_TEXT",
                weight=0.35,
                description=(
                    f"Added {len(non_empty_added)} non-empty lines in one hunk (only {len(non_empty_removed)} removed); "
                    f"consider moving detailed runbooks into a dedicated skill or reference doc."
                ),
            )
        )

    if not signals:
        return [], 0.05, "Clean diff: atomic change with no bloat signals detected."

    total_weight = sum(s.weight for s in signals)
    probability = min(0.98, round(total_weight, 2))
    reason = "; ".join(f"[{s.code}] {s.description}" for s in signals)
    return signals, probability, reason


def parse_git_diff_output(raw_output: str, default_file_path: str) -> List[HunkAnalysis]:
    """Parse `git log -p` or `git diff` output into analyzed hunks."""
    hunks: List[HunkAnalysis] = []

    current_commit = "UNCOMMITTED"
    current_short = "WORKTREE"
    current_author = "local"
    current_date = "now"
    current_subject = "Uncommitted working tree changes"
    current_file = default_file_path

    lines = raw_output.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        if line.startswith("commit "):
            parts = line.split()
            current_commit = parts[1] if len(parts) > 1 else "UNKNOWN"
            current_short = current_commit[:7]
            current_author = ""
            current_date = ""
            current_subject = ""
            i += 1
            while i < n and not lines[i].startswith("diff --git ") and not lines[i].startswith("commit "):
                hdr = lines[i]
                if hdr.startswith("Author:"):
                    current_author = hdr[len("Author:") :].strip()
                elif hdr.startswith("Date:"):
                    current_date = hdr[len("Date:") :].strip()
                elif hdr.startswith("    ") and not current_subject:
                    current_subject = hdr.strip()
                i += 1
            continue

        if line.startswith("diff --git "):
            m = re.match(r"^diff --git a/(.*) b/(.*)$", line)
            if m:
                current_file = m.group(2)
            i += 1
            continue

        if line.startswith("+++ b/"):
            current_file = line[len("+++ b/") :].strip()
            i += 1
            continue

        hunk_match = HUNK_HEADER_RE.match(line)
        if hunk_match:
            old_start = int(hunk_match.group(1))
            old_count = int(hunk_match.group(2) or "1")
            new_start = int(hunk_match.group(3))
            new_count = int(hunk_match.group(4) or "1")
            hunk_header = f"@@ -{old_start},{old_count} +{new_start},{new_count} @@"

            raw_diff_lines: List[str] = []
            added_lines: List[str] = []
            removed_lines: List[str] = []

            i += 1
            while i < n:
                dl = lines[i]
                if dl.startswith("commit ") or dl.startswith("diff --git ") or HUNK_HEADER_RE.match(dl):
                    break
                if dl.startswith("+") and not dl.startswith("+++"):
                    raw_diff_lines.append(dl)
                    added_lines.append(dl[1:])
                elif dl.startswith("-") and not dl.startswith("---"):
                    raw_diff_lines.append(dl)
                    removed_lines.append(dl[1:])
                elif dl.startswith(" "):
                    raw_diff_lines.append(dl)
                i += 1

            signals, prob, reason = analyze_hunk_deterministic(
                added_lines=added_lines,
                removed_lines=removed_lines,
                old_start=old_start,
                old_count=old_count,
                new_start=new_start,
                new_count=new_count,
            )

            hunks.append(
                HunkAnalysis(
                    commit_hash=current_commit,
                    commit_short=current_short,
                    author=current_author,
                    date=current_date,
                    subject=current_subject,
                    file_path=current_file,
                    old_start=old_start,
                    old_count=old_count,
                    new_start=new_start,
                    new_count=new_count,
                    hunk_header=hunk_header,
                    raw_diff_lines=raw_diff_lines,
                    added_lines=added_lines,
                    removed_lines=removed_lines,
                    signals=signals,
                    deterministic_probability=prob,
                    deterministic_reason=reason,
                )
            )
            continue

        i += 1

    return hunks


def evaluate_hunk_with_llm(
    hunk: HunkAnalysis,
    preferred_model: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate a hunk for prompt bloat using Gemini Flash (`gemini-flash-latest` or `gemini-3.1-flash-lite`).

    Always returns a dict with:
      - error: bool
      - error_message: Optional[str]
      - probability: float (0.0 to 1.0, ALWAYS present)
      - reason: str (ALWAYS present)
      - model_used: Optional[str]
    """
    models_to_try = list(DEFAULT_LLM_MODELS)
    if preferred_model:
        models_to_try = [preferred_model] + [m for m in DEFAULT_LLM_MODELS if m != preferred_model]

    diff_snippet = "\n".join(hunk.raw_diff_lines[:80])
    prompt = (
        "You are an expert AI system-prompt auditor checking a Git diff on an agent instruction file "
        f"({hunk.file_path}) for 'prompt bloat'.\n\n"
        "Signs of prompt bloat:\n"
        "1. Packing many instructions into a single run-on line ('10 instructions in 1 line').\n"
        "2. Adding a whole new H2/H3 section (## Heading) with just 1-2 lines for a narrow, overfitting edge case.\n"
        "3. Appending reactive one-off rules to the end of the file instead of consolidating or moving to a specific skill.\n"
        "4. Committing merge conflict markers or verbose walls of text.\n\n"
        f"Commit: #{hunk.commit_short} ({hunk.subject})\n"
        f"Location: {hunk.line_range_str}\n"
        f"Deterministic Pre-Check Probability: {hunk.deterministic_probability:.2f} ({hunk.deterministic_reason})\n"
        f"Diff:\n```diff\n{diff_snippet}\n```\n\n"
        "Respond ONLY with a valid JSON object matching this exact schema:\n"
        '{"probability": <float between 0.0 and 1.0>, "reason": "<concise explanation of why that probability was given and how to fix it if bloated>"}'
    )

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    last_error = ""

    if api_key:
        import urllib.error
        import urllib.request

        for model_name in models_to_try:
            if not model_name:
                continue
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                req_body = json.dumps(
                    {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.1,
                        },
                    }
                ).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=req_body,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                candidates = resp_data.get("candidates") or []
                raw_text = (
                    candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    if candidates
                    else ""
                ).strip()
                parsed = json.loads(raw_text)
                prob = float(parsed.get("probability", hunk.deterministic_probability))
                prob = max(0.0, min(1.0, round(prob, 2)))
                reason = str(parsed.get("reason") or hunk.deterministic_reason)
                return {
                    "error": False,
                    "error_message": None,
                    "probability": prob,
                    "reason": reason,
                    "model_used": model_name,
                }
            except urllib.error.HTTPError as http_err:
                err_body = ""
                try:
                    err_body = http_err.read().decode("utf-8", errors="ignore")[:200]
                except Exception:
                    pass
                last_error = f"Model {model_name} HTTP {http_err.code}: {err_body or http_err.reason}"
            except Exception as model_err:
                last_error = f"Model {model_name} failed: {model_err}"
    else:
        last_error = "Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set in environment."

    return {
        "error": True,
        "error_message": last_error,
        "probability": round(hunk.deterministic_probability, 2),
        "reason": f"[Deterministic fallback due to LLM error] {hunk.deterministic_reason}",
        "model_used": None,
    }


def _severity_label(prob: float) -> str:
    if prob >= 0.65:
        return "HIGH"
    if prob >= 0.35:
        return "MEDIUM"
    return "LOW"


def format_agent_friendly_text(hunks: List[HunkAnalysis], min_probability: float = 0.0) -> str:
    """Format hunks into the requested agent-friendly text blocks."""
    filtered = [h for h in hunks if h.final_probability >= min_probability]
    if not filtered:
        return "✅ No commits/hunks exceeded the bloat threshold."

    blocks: List[str] = []
    for h in filtered:
        prob = h.final_probability
        pct = int(round(prob * 100))
        sev = _severity_label(prob)
        sig_names = ", ".join(s.code for s in h.signals) if h.signals else "NONE"
        diff_rendered = "\n".join(h.raw_diff_lines)

        block = [
            "================================================================================",
            f"commit #{h.commit_short} , file {h.file_path}",
            f"Date: {h.date} | Author: {h.author} | Subject: {h.subject}",
            f"{h.line_range_str}",
            f"Bloat Probability: {prob:.2f} ({pct}%) [{sev}] — Signals: {sig_names}",
            f"Reason: {h.final_reason}",
            "Diff:",
            diff_rendered,
        ]
        blocks.append("\n".join(block))

    blocks.append("================================================================================")
    return "\n".join(blocks)


def format_llm_json_output(
    hunks: List[HunkAnalysis],
    min_probability: float = 0.0,
    top_level_error: Optional[str] = None,
) -> str:
    """Format strictly valid JSON output required when `--llm` or `--json` is used.

    Guarantees top-level and per-hunk fields:
      - error (bool)
      - error_message (str | None)
      - probability (float, ALWAYS present)
      - reason (str, ALWAYS present)
    """
    if top_level_error is not None:
        payload = {
            "error": True,
            "error_message": top_level_error,
            "probability": 0.0,
            "reason": f"Analysis could not run: {top_level_error}",
            "findings": [],
        }
        return json.dumps(payload, indent=2)

    filtered = [h for h in hunks if h.final_probability >= min_probability]
    any_llm_error = any(bool(h.llm_result and h.llm_result.get("error")) for h in filtered)
    first_error_msg = next(
        (h.llm_result.get("error_message") for h in filtered if h.llm_result and h.llm_result.get("error")),
        None,
    )

    max_hunk: Optional[HunkAnalysis] = max(filtered, key=lambda x: x.final_probability) if filtered else None
    overall_prob = max_hunk.final_probability if max_hunk else 0.0
    overall_reason = (
        f"Highest bloat probability found in commit #{max_hunk.commit_short} "
        f"({max_hunk.file_path}, {max_hunk.line_range_str}): {max_hunk.final_reason}"
        if max_hunk
        else "No bloat signals detected across analyzed hunks."
    )

    findings = []
    for h in filtered:
        h_err = bool(h.llm_result.get("error")) if h.llm_result else False
        h_err_msg = h.llm_result.get("error_message") if h.llm_result else None
        findings.append(
            {
                "commit": f"#{h.commit_short}",
                "commit_full": h.commit_hash,
                "file": h.file_path,
                "line": h.line_range_str,
                "date": h.date,
                "author": h.author,
                "subject": h.subject,
                "error": h_err,
                "error_message": h_err_msg,
                "probability": h.final_probability,
                "reason": h.final_reason,
                "signals": [dataclasses.asdict(s) for s in h.signals],
                "diff": "\n".join(h.raw_diff_lines),
            }
        )

    payload = {
        "error": any_llm_error,
        "error_message": first_error_msg,
        "probability": overall_prob,
        "reason": overall_reason,
        "total_hunks_analyzed": len(hunks),
        "flagged_hunks_count": len(findings),
        "findings": findings,
    }
    return json.dumps(payload, indent=2)


def discover_prompt_files(repo_root: str) -> List[str]:
    """Find checked-in system prompt markdown files in the repository root."""
    found: List[str] = []
    for fname in DEFAULT_PROMPT_FILES:
        candidate = os.path.join(repo_root, fname)
        if os.path.isfile(candidate):
            found.append(candidate)
    return found


def run_git_diff_for_file(
    file_path: str,
    limit: int = 20,
    uncommitted: bool = False,
) -> Tuple[bool, str]:
    """Run git log -p or git diff for a target file."""
    abs_path = os.path.abspath(file_path)
    work_dir = os.path.dirname(abs_path) if os.path.exists(abs_path) else os.getcwd()

    if uncommitted:
        cmd = ["git", "-C", work_dir, "diff", "HEAD", "--no-color", "-U2", "--", abs_path]
    else:
        cmd = [
            "git",
            "-C",
            work_dir,
            "log",
            "-p",
            "--no-color",
            "-U2",
            f"-n{limit}",
            "--",
            abs_path,
        ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if res.returncode != 0:
            return False, res.stderr.strip() or f"git exited with code {res.returncode}"
        return True, res.stdout
    except Exception as exc:
        return False, str(exc)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze Git history or uncommitted diffs of agent prompt files (GEMINI.md, AGENTS.md, etc.) for bloat."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Path(s) to markdown prompt files (e.g. GEMINI.md, AGENTS.md). Use --all to auto-discover.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Auto-discover GEMINI.md, AGENTS.md, CONTRIBUTING.md, SPECS.md, etc. in the current directory.",
    )
    parser.add_argument(
        "--uncommitted",
        "--staged",
        action="store_true",
        dest="uncommitted",
        help="Analyze uncommitted working-tree / staged diffs (`git diff HEAD`) instead of commit history.",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=25,
        help="Max number of git commits to inspect per file (default: 25).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.20,
        help="Minimum bloat probability (0.0 to 1.0) to include in output (default: 0.20; use 0.0 for all).",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use Gemini Flash LLM evaluation and output strict JSON with error, probability, and reason.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.environ.get("GEMINI_MODEL", "gemini-flash-latest"),
        help="Gemini model to use with --llm (default: gemini-flash-latest).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON even in deterministic mode.",
    )

    args = parser.parse_args(argv)

    target_files = list(args.files)
    if args.all or not target_files:
        discovered = discover_prompt_files(os.getcwd())
        for d in discovered:
            if d not in target_files:
                target_files.append(d)

    if not target_files:
        err_msg = "No prompt markdown files specified or discovered in current directory."
        if args.llm or args.json:
            print(format_llm_json_output([], top_level_error=err_msg))
        else:
            print(f"❌ {err_msg}", file=sys.stderr)
        return 1

    all_hunks: List[HunkAnalysis] = []
    errors: List[str] = []

    for fpath in target_files:
        ok, raw_out = run_git_diff_for_file(fpath, limit=args.limit, uncommitted=args.uncommitted)
        if not ok:
            errors.append(f"{fpath}: {raw_out}")
            continue
        rel_display = os.path.relpath(fpath, os.getcwd()) if os.path.isabs(fpath) else fpath
        file_hunks = parse_git_diff_output(raw_out, default_file_path=rel_display)
        all_hunks.extend(file_hunks)

    if errors and not all_hunks:
        joined_err = "; ".join(errors)
        if args.llm or args.json:
            print(format_llm_json_output([], top_level_error=joined_err))
        else:
            print(f"❌ Error running git diff: {joined_err}", file=sys.stderr)
        return 1

    if args.llm:
        for hunk in all_hunks:
            if hunk.deterministic_probability >= args.threshold or args.threshold == 0.0:
                hunk.llm_result = evaluate_hunk_with_llm(hunk, preferred_model=args.model)

    if args.llm or args.json:
        print(format_llm_json_output(all_hunks, min_probability=args.threshold))
    else:
        print(format_agent_friendly_text(all_hunks, min_probability=args.threshold))

    return 0


if __name__ == "__main__":
    sys.exit(main())
