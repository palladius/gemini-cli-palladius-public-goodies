#!/usr/bin/env python3
"""verify_ai_ethics.py — Tamper-Evident Verifier & Installer for AI_ETHICS.md (Carlessian Commons Ethics v1.0).

Verifies that:
1. /AI_ETHICS.md exists in the target repository root.
2. Lines 1-2 follow the allowed header/copyright format (customizable per repo).
3. Lines 3..EOF match the exact canonical SHA-256 digest of Carlessian Commons Ethics v1.0.
   If even a single character in Lines 3..EOF is modified, prints a unified diff and exits with code 2.
4. Checks whether AGENTS.md / GEMINI.md and any *CONSTITUTION*.md reference AI_ETHICS.md.
"""

import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

CARLESSIAN_COMMONS_VERSION = "1.1"
CARLESSIAN_COMMONS_V1_1_SHA256 = (
    "1cc43a4ed145d95b72d3b61152e239aa824e722f8d7a8772dfa0d15aefec14e9"
)
CARLESSIAN_COMMONS_V1_0_SHA256 = (
    "4f25569c45da2af754db36c7044773eae3ae2844c3559787cfe2b8f096c2edd6"
)
LEGACY_SHA256_VERSIONS = {
    CARLESSIAN_COMMONS_V1_0_SHA256: "1.0",
}

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = SKILL_DIR / "references" / "AI_ETHICS.template.md"

AGENTS_MD_SNIPPET = (
    "- **AI Ethics (`Carlessian Commons v1.0`)**: Follow [AI_ETHICS.md](./AI_ETHICS.md) (`ai-ethics` skill) — "
    "failing a task ethically is ALWAYS preferred over breaking ethical boundaries."
)

CONSTITUTION_MD_SNIPPET = (
    "> ⚖️ **Ethical Supremacy (`Carlessian Commons v1.0`)**: This constitution and all agents operating in this repository are strictly bound by "
    "[AI_ETHICS.md](/AI_ETHICS.md). Asimov's Laws (0–3), human corrigibility, ecological compute proportionality, scientific grounding, and ethical integrity "
    "strictly supersede task completion and user orders."
)


def normalize_body(lines: list[str]) -> str:
    """Normalize lines 3..EOF by stripping trailing whitespace per line and ensuring a single trailing LF."""
    cleaned = [line.rstrip() for line in lines]
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned) + "\n"


def compute_body_sha256(lines_from_3: list[str]) -> str:
    canonical = normalize_body(lines_from_3)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_template_lines() -> list[str]:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Canonical template not found at {TEMPLATE_PATH}")
    return TEMPLATE_PATH.read_text(encoding="utf-8").splitlines()


def find_constitution_files(repo_root: Path) -> list[Path]:
    candidates = [
        repo_root / "CONSTITUTION.md",
        repo_root / "CARLESSIAN_CONSTITUTION.md",
        repo_root / "docs" / "CONSTITUTION.md",
        repo_root / "docs" / "CARLESSIAN_CONSTITUTION.md",
    ]
    return [p for p in candidates if p.exists() and p.is_file()]


def verify_repo(repo_root: Path, strict_links: bool = False) -> dict:
    """Verify AI_ETHICS.md integrity and prompt file links in repo_root."""
    ethics_file = repo_root / "AI_ETHICS.md"
    result = {
        "repo": str(repo_root),
        "version": CARLESSIAN_COMMONS_VERSION,
        "exists": ethics_file.exists(),
        "header_valid": False,
        "body_valid": False,
        "expected_sha256": CARLESSIAN_COMMONS_V1_1_SHA256,
        "actual_sha256": None,
        "tampered": False,
        "diff": "",
        "agents_md_linked": False,
        "constitutions_checked": {},
        "errors": [],
        "warnings": [],
    }

    if not ethics_file.exists():
        result["errors"].append(
            f"Missing {ethics_file}. Run with --install to create it."
        )
        return result

    lines = ethics_file.read_text(encoding="utf-8").splitlines()
    if len(lines) < 10:
        result["tampered"] = True
        result["errors"].append(
            f"{ethics_file} is truncated ({len(lines)} lines)."
        )
        return result

    # Validate Line 1 & Line 2 (customizable header)
    line1 = lines[0].strip()
    line2 = lines[1].strip()
    if not line1.startswith("# AI_ETHICS.md") or "Carlessian Commons Ethics v1." not in line1:
        result["errors"].append(
            f"Line 1 must start with '# AI_ETHICS.md — Carlessian Commons Ethics v{CARLESSIAN_COMMONS_VERSION}'."
        )
    elif not line2.lower().startswith("copyright"):
        result["errors"].append(
            "Line 2 must start with 'Copyright (c) <YEAR> <AUTHOR/REPO> ...'."
        )
    else:
        result["header_valid"] = True

    # Validate Lines 3..EOF against canonical SHA-256
    actual_sha = compute_body_sha256(lines[2:])
    result["actual_sha256"] = actual_sha

    if actual_sha == CARLESSIAN_COMMONS_V1_1_SHA256:
        result["body_valid"] = True
    elif actual_sha in LEGACY_SHA256_VERSIONS:
        legacy_ver = LEGACY_SHA256_VERSIONS[actual_sha]
        result["body_valid"] = True
        result["version"] = legacy_ver
        result["warnings"].append(
            f"AI_ETHICS.md is on legacy Carlessian Commons Ethics v{legacy_ver} (latest is v{CARLESSIAN_COMMONS_VERSION} with EU AI Act Safety Ladder). "
            "Run with '--install --overwrite' to upgrade."
        )
    else:
        result["tampered"] = True
        template_lines = load_template_lines()
        expected_body = normalize_body(template_lines[2:]).splitlines(keepends=True)
        actual_body = normalize_body(lines[2:]).splitlines(keepends=True)
        diff_text = "".join(
            difflib.unified_diff(
                expected_body,
                actual_body,
                fromfile="canonical/AI_ETHICS.template.md (lines 3..EOF)",
                tofile=f"{ethics_file} (lines 3..EOF)",
                lineterm="\n",
            )
        )
        result["diff"] = diff_text
        result["errors"].append(
            f"🚨 ETHICS TAMPERING DETECTED: Lines 3..EOF do not match Carlessian Commons Ethics v{CARLESSIAN_COMMONS_VERSION} SHA-256!"
        )

    # Check AGENTS.md / GEMINI.md reference
    prompt_files = [
        p for p in [repo_root / "AGENTS.md", repo_root / "GEMINI.md"] if p.exists()
    ]
    if prompt_files:
        linked = any(
            "AI_ETHICS.md" in p.read_text(encoding="utf-8", errors="ignore")
            or "ai-ethics" in p.read_text(encoding="utf-8", errors="ignore")
            for p in prompt_files
        )
        result["agents_md_linked"] = linked
        if not linked:
            msg = (
                f"Neither AGENTS.md nor GEMINI.md in {repo_root} references AI_ETHICS.md. "
                f"Add:\n  {AGENTS_MD_SNIPPET}"
            )
            if strict_links:
                result["errors"].append(msg)
            else:
                result["warnings"].append(msg)
    else:
        result["warnings"].append(f"No AGENTS.md or GEMINI.md found in {repo_root}.")

    # Check CONSTITUTION.md files if present
    for cfile in find_constitution_files(repo_root):
        c_linked = "AI_ETHICS.md" in cfile.read_text(encoding="utf-8", errors="ignore")
        result["constitutions_checked"][str(cfile.relative_to(repo_root))] = c_linked
        if not c_linked:
            msg = (
                f"{cfile.relative_to(repo_root)} does not reference AI_ETHICS.md. "
                f"Add:\n  {CONSTITUTION_MD_SNIPPET}"
            )
            if strict_links:
                result["errors"].append(msg)
            else:
                result["warnings"].append(msg)

    return result


def install_ethics(
    repo_root: Path,
    author: str = "Riccardo Carlesso",
    repo_name: str | None = None,
    year: int | None = None,
    overwrite: bool = False,
) -> Path:
    """Install canonical AI_ETHICS.md into repo_root with customized Line 2."""
    ethics_file = repo_root / "AI_ETHICS.md"
    if ethics_file.exists() and not overwrite:
        raise FileExistsError(
            f"{ethics_file} already exists. Pass --overwrite to replace it."
        )

    template_lines = load_template_lines()
    year_val = year or datetime.date.today().year
    slug = repo_name or repo_root.resolve().name

    line1 = f"# AI_ETHICS.md — Carlessian Commons Ethics v{CARLESSIAN_COMMONS_VERSION}"
    line2 = (
        f"Copyright (c) {year_val} {author} ({slug}) — "
        "Inspired by Isaac Asimov, Anthropic's Claude Constitution (CC0 1.0) & the EU AI Act."
    )
    body = normalize_body(template_lines[2:])
    full_content = f"{line1}\n{line2}\n{body}"
    ethics_file.write_text(full_content, encoding="utf-8")
    return ethics_file


def run_self_test() -> int:
    """Run built-in unit tests for tamper detection and installation."""
    print("🧪 Running verify_ai_ethics.py self-test suite...")
    template_lines = load_template_lines()
    template_sha = compute_body_sha256(template_lines[2:])
    assert template_sha == CARLESSIAN_COMMONS_V1_1_SHA256, (
        f"Template SHA mismatch: expected {CARLESSIAN_COMMONS_V1_1_SHA256}, got {template_sha}"
    )
    print("  ✅ Test 1/4 PASS: Canonical template matches CARLESSIAN_COMMONS_V1_1_SHA256.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        (tmp_path / "AGENTS.md").write_text(
            f"# Agents\n{AGENTS_MD_SNIPPET}\n", encoding="utf-8"
        )
        install_ethics(tmp_path, author="Test Author", repo_name="test-repo", year=2026)
        res1 = verify_repo(tmp_path, strict_links=True)
        assert res1["header_valid"] and res1["body_valid"] and not res1["errors"], (
            f"Expected clean verification, got: {res1}"
        )
        print("  ✅ Test 2/4 PASS: Freshly installed AI_ETHICS.md + AGENTS.md passes strict check.")

        # Test 3: Customize Line 2 (different copyright holder & year) -> MUST STILL PASS
        ethics_file = tmp_path / "AI_ETHICS.md"
        lines = ethics_file.read_text(encoding="utf-8").splitlines()
        lines[1] = "Copyright (c) 2027 Another Maintainer (custom-fork) — All rights reserved."
        ethics_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        res2 = verify_repo(tmp_path, strict_links=True)
        assert res2["header_valid"] and res2["body_valid"] and not res2["tampered"], (
            f"Customizing Line 2 should pass, got: {res2}"
        )
        print("  ✅ Test 3/4 PASS: Customizing Line 2 copyright metadata preserves SHA-256 validity.")

        # Test 4: Tamper with Line 3+ (change 'ALWAYS' to 'SOMETIMES') -> MUST FAIL WITH TAMPERING
        tampered_text = ethics_file.read_text(encoding="utf-8").replace(
            "ALWAYS strictly preferred", "SOMETIMES preferred", 1
        )
        ethics_file.write_text(tampered_text, encoding="utf-8")
        res3 = verify_repo(tmp_path, strict_links=True)
        assert res3["tampered"] and not res3["body_valid"] and res3["diff"], (
            f"Expected tampering detection on body edit, got: {res3}"
        )
        print("  ✅ Test 4/4 PASS: Single-word mutation in Lines 3..EOF triggers TAMPERING alert + diff.")

    print("🎉 All self-tests passed!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify or install AI_ETHICS.md (Carlessian Commons Ethics v1.0)."
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to the target repository root (default: current directory).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify AI_ETHICS.md integrity and AGENTS.md/CONSTITUTION.md links (default).",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install canonical AI_ETHICS.md into the target repository root.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing AI_ETHICS.md when using --install.",
    )
    parser.add_argument(
        "--author",
        default="Riccardo Carlesso",
        help="Copyright holder name for Line 2 when using --install.",
    )
    parser.add_argument(
        "--repo-name",
        default=None,
        help="Repository slug for Line 2 when using --install (defaults to directory name).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if AGENTS.md/GEMINI.md or CONSTITUTION.md does not link to AI_ETHICS.md.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output verification result as strict JSON.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in unit tests for tamper detection.",
    )

    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_root = Path(args.repo_path).resolve()

    if args.install:
        installed = install_ethics(
            repo_root,
            author=args.author,
            repo_name=args.repo_name,
            overwrite=args.overwrite,
        )
        print(f"✅ Installed {installed} (Carlessian Commons Ethics v{CARLESSIAN_COMMONS_VERSION})")
        print(f"🔒 Canonical Body SHA-256: {CARLESSIAN_COMMONS_V1_1_SHA256}")
        print("\n📌 Add this 1-line enforcement bullet to AGENTS.md / GEMINI.md:")
        print(f"   {AGENTS_MD_SNIPPET}")
        print("\n📌 If the repo has a CONSTITUTION.md, add this preamble:")
        print(f"   {CONSTITUTION_MD_SNIPPET}\n")

    res = verify_repo(repo_root, strict_links=args.strict)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        if res["tampered"]:
            print(f"🚨 TAMPERING DETECTED in {repo_root / 'AI_ETHICS.md'}!", file=sys.stderr)
            print(f"   Expected SHA-256: {res['expected_sha256']}", file=sys.stderr)
            print(f"   Actual SHA-256:   {res['actual_sha256']}", file=sys.stderr)
            if res["diff"]:
                print("\n--- Unified Diff (Lines 3..EOF) ---", file=sys.stderr)
                print(res["diff"], file=sys.stderr)
        elif res["errors"]:
            for err in res["errors"]:
                print(f"❌ ERROR: {err}", file=sys.stderr)
        else:
            print(
                f"✅ AI_ETHICS.md verified ({repo_root.name}): "
                f"Carlessian Commons Ethics v{CARLESSIAN_COMMONS_VERSION} "
                f"[SHA-256: {res['actual_sha256'][:16]}...]"
            )
            if res["agents_md_linked"]:
                print("   🔗 AGENTS.md / GEMINI.md link: OK")
            for c_path, c_ok in res["constitutions_checked"].items():
                status = "OK" if c_ok else "MISSING LINK"
                print(f"   📜 {c_path}: {status}")

        for warn in res["warnings"]:
            print(f"⚠️  WARNING: {warn}")

    if res["tampered"]:
        return 2
    if res["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
