#!/usr/bin/env python3
"""
git_disk_cleanup.py — Non-destructive workspace-wide Git & disk bloat discovery and cleanup tool.

Features:
- Resolves workspace root via --root, $GIT_WORKSPACE_DIR, $WORKSPACE_DIR, ~/git, or ~/workspace.
- Detects leftover '.chumbia.touch' breadcrumb locks from interrupted '/chumbia' sessions.
- Audits global 'uv' cache (~/.cache/uv).
- Discovers Tier 1 dev caches (node_modules, .venv, .next, target, __pycache__, .pytest_cache).
- Discovers Tier 2 build outputs (publish, out, dist, build) with an mtime freshness guard
  (--protect-days 7) so active work from today/this week is NEVER deleted.
- Audits Tier 3 Git worktrees (both repo-local .worktrees/ and ~/.gemini/antigravity/worktrees/),
  checking MERGED status against main/master and dirty file counts.
- Flags Tier 4 "GOLD" media/archive files (.zip, .tgz, .mp4, .mov > 50MB) so they are never zapped.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


TIER1_DIR_NAMES = {
    "node_modules",
    ".venv",
    "venv",
    ".next",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}

TIER2_BUILD_DIR_NAMES = {
    "publish",
    "out",
    "dist",
    "build",
}

GOLD_EXTENSIONS = {".zip", ".tgz", ".tar.gz", ".mp4", ".mov", ".mkv", ".dmg", ".iso"}
GOLD_MIN_BYTES = 50 * 1024 * 1024  # 50 MB


def resolve_workspace_dir(cli_root: Optional[str]) -> Path:
    if cli_root:
        return Path(cli_root).expanduser().resolve()
    for env_var in ("GIT_WORKSPACE_DIR", "CARLESSIAN_GIT_DIR", "WORKSPACE_DIR"):
        val = os.environ.get(env_var)
        if val:
            return Path(val).expanduser().resolve()
    home = Path.home()
    for candidate in (home / "git", home / "workspace", home / "src"):
        if candidate.is_dir():
            return candidate.resolve()
    return (home / "git").resolve()


def human_size(num_bytes: int) -> str:
    val = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if val < 1024.0 or unit == "TB":
            return f"{val:.1f} {unit}" if unit != "B" else f"{int(val)} B"
        val /= 1024.0
    return f"{val:.1f} TB"


def dir_size_and_newest_mtime(path: Path) -> Tuple[int, float]:
    total = 0
    newest = 0.0
    try:
        for root, dirs, files in os.walk(path, followlinks=False):
            for f in files:
                fp = Path(root) / f
                try:
                    st = fp.lstat()
                    total += st.st_size
                    if st.st_mtime > newest:
                        newest = st.st_mtime
                except OSError:
                    pass
    except OSError:
        pass
    return total, newest


def run_cmd(args: List[str], cwd: Optional[Path] = None, timeout: int = 15) -> Tuple[int, str]:
    try:
        res = subprocess.run(
            args,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        return res.returncode, res.stdout.strip()
    except Exception as exc:
        return 1, str(exc)


def is_git_ignored(path: Path) -> bool:
    parent = path.parent
    rc, _ = run_cmd(["git", "check-ignore", "-q", str(path)], cwd=parent)
    return rc == 0


def check_uv_cache() -> Optional[Dict[str, Any]]:
    rc, out = run_cmd(["uv", "cache", "dir"])
    if rc != 0 or not out:
        default_uv = Path.home() / ".cache" / "uv"
        cache_dir = default_uv if default_uv.is_dir() else None
    else:
        cache_dir = Path(out.splitlines()[0].strip())
    if not cache_dir or not cache_dir.is_dir():
        return None
    size_bytes, newest = dir_size_and_newest_mtime(cache_dir)
    if size_bytes < 1024 * 1024:
        return None
    return {
        "path": str(cache_dir),
        "size_bytes": size_bytes,
        "size_human": human_size(size_bytes),
        "kind": "uv_cache",
    }


def audit_worktree(wt_path: Path, main_repo: Optional[Path] = None) -> Dict[str, Any]:
    size_bytes, newest_mtime = dir_size_and_newest_mtime(wt_path)
    _, branch = run_cmd(["git", "branch", "--show-current"], cwd=wt_path)
    branch = branch or "DETACHED"

    _, status_out = run_cmd(["git", "status", "--porcelain"], cwd=wt_path)
    dirty_lines = [ln for ln in status_out.splitlines() if ln.strip() and not ln.endswith(".chumbia.touch")]
    dirty_count = len(dirty_lines)

    _, last_commit = run_cmd(
        ["git", "log", "-1", "--format=%cd %h %s", "--date=format:%Y-%m-%d"],
        cwd=wt_path,
    )

    # Check if merged into main or origin/main
    check_repo = main_repo or wt_path
    merged = False
    for target_ref in ("origin/main", "main", "origin/master", "master"):
        rc_ref, _ = run_cmd(["git", "rev-parse", "--verify", "--quiet", target_ref], cwd=check_repo)
        if rc_ref == 0 and branch != "DETACHED":
            rc_anc, _ = run_cmd(["git", "merge-base", "--is-ancestor", branch, target_ref], cwd=check_repo)
            if rc_anc == 0:
                merged = True
                break

    # Check inner node_modules / publish bloat inside worktree
    inner_bloat: List[Dict[str, Any]] = []
    for root, dirs, _ in os.walk(wt_path, followlinks=False):
        for d in list(dirs):
            if d in ("node_modules", "publish", ".next", ".venv"):
                sub = Path(root) / d
                if is_git_ignored(sub):
                    b_size, _ = dir_size_and_newest_mtime(sub)
                    if b_size >= 5 * 1024 * 1024:
                        inner_bloat.append(
                            {
                                "path": str(sub),
                                "size_bytes": b_size,
                                "size_human": human_size(b_size),
                            }
                        )
                dirs.remove(d)
            elif d == ".git":
                dirs.remove(d)

    safe_to_remove = merged and dirty_count == 0
    return {
        "path": str(wt_path),
        "main_repo": str(main_repo) if main_repo else None,
        "branch": branch,
        "merged": merged,
        "dirty_count": dirty_count,
        "safe_to_remove": safe_to_remove,
        "size_bytes": size_bytes,
        "size_human": human_size(size_bytes),
        "last_commit": last_commit,
        "inner_bloat": inner_bloat,
    }


def scan_workspace(workspace_dir: Path, protect_days: int, min_mb: float = 5.0) -> Dict[str, Any]:
    now = dt.datetime.now().timestamp()
    protect_seconds = protect_days * 86400
    min_bytes = int(min_mb * 1024 * 1024)

    chumbia_locks: List[Dict[str, Any]] = []
    tier1_caches: List[Dict[str, Any]] = []
    tier2_stale_builds: List[Dict[str, Any]] = []
    tier2_protected_builds: List[Dict[str, Any]] = []
    worktrees_map: Dict[str, Dict[str, Any]] = {}
    gold_archives: List[Dict[str, Any]] = []

    # 1. Scan global agent worktree directories (~/.gemini/antigravity/worktrees, ~/.gemini/jetski/worktrees)
    for agent_wt_base in (
        Path.home() / ".gemini" / "antigravity" / "worktrees",
        Path.home() / ".gemini" / "jetski" / "worktrees",
    ):
        if agent_wt_base.is_dir():
            for repo_group in sorted(agent_wt_base.iterdir()):
                if not repo_group.is_dir():
                    continue
                for wt_dir in sorted(repo_group.iterdir()):
                    if wt_dir.is_dir() and (wt_dir / ".git").exists():
                        wt_key = str(wt_dir.resolve())
                        worktrees_map[wt_key] = audit_worktree(wt_dir)

    # 2. Walk workspace_dir
    visited_realpaths = set()
    for root, dirs, files in os.walk(workspace_dir, followlinks=True):
        root_path = Path(root)
        try:
            real_root = str(root_path.resolve())
            if real_root in visited_realpaths:
                dirs[:] = []
                continue
            visited_realpaths.add(real_root)
        except OSError:
            continue

        # Check for .chumbia.touch
        if ".chumbia.touch" in files:
            touch_fp = root_path / ".chumbia.touch"
            try:
                content = touch_fp.read_text(encoding="utf-8", errors="replace").strip()
            except OSError:
                content = ""
            chumbia_locks.append({"repo": str(root_path), "touch_file": str(touch_fp), "details": content})

        # Check if this directory is a Git repository root
        if ".git" in dirs or ".git" in files:
            # Discover registered worktrees via git worktree list
            rc, wt_out = run_cmd(["git", "worktree", "list", "--porcelain"], cwd=root_path)
            if rc == 0 and wt_out:
                blocks = wt_out.split("\n\n")
                for idx, blk in enumerate(blocks):
                    if idx == 0:
                        continue  # skip primary worktree
                    for line in blk.splitlines():
                        if line.startswith("worktree "):
                            wt_p = Path(line.split(" ", 1)[1].strip())
                            if wt_p.is_dir():
                                wt_key = str(wt_p.resolve())
                                if wt_key not in worktrees_map:
                                    worktrees_map[wt_key] = audit_worktree(wt_p, main_repo=root_path)

        # Check files for Gold archives (git-ignored > 50MB)
        for fname in files:
            lower = fname.lower()
            if any(lower.endswith(ext) for ext in GOLD_EXTENSIONS):
                fpath = root_path / fname
                try:
                    st = fpath.lstat()
                    if st.st_size >= GOLD_MIN_BYTES and is_git_ignored(fpath):
                        gold_archives.append(
                            {
                                "path": str(fpath),
                                "size_bytes": st.st_size,
                                "size_human": human_size(st.st_size),
                                "mtime": dt.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d"),
                            }
                        )
                except OSError:
                    pass

        # Prune & classify subdirectories
        for d in list(dirs):
            if d == ".git":
                dirs.remove(d)
                continue
            if d == ".worktrees":
                wt_container = root_path / d
                if wt_container.is_dir():
                    for sub_wt in sorted(wt_container.iterdir()):
                        if sub_wt.is_dir():
                            wt_key = str(sub_wt.resolve())
                            if wt_key not in worktrees_map:
                                worktrees_map[wt_key] = audit_worktree(sub_wt, main_repo=root_path)
                dirs.remove(d)
                continue

            sub_path = root_path / d
            if d in TIER1_DIR_NAMES:
                if is_git_ignored(sub_path):
                    sz, _ = dir_size_and_newest_mtime(sub_path)
                    if sz >= min_bytes:
                        tier1_caches.append(
                            {
                                "path": str(sub_path),
                                "kind": d,
                                "size_bytes": sz,
                                "size_human": human_size(sz),
                            }
                        )
                dirs.remove(d)
            elif d in TIER2_BUILD_DIR_NAMES:
                if is_git_ignored(sub_path):
                    sz, newest = dir_size_and_newest_mtime(sub_path)
                    if sz >= min_bytes:
                        age_sec = max(0.0, now - newest) if newest > 0 else 999999999.0
                        mtime_str = (
                            dt.datetime.fromtimestamp(newest).strftime("%Y-%m-%d %H:%M")
                            if newest > 0
                            else "unknown"
                        )
                        entry = {
                            "path": str(sub_path),
                            "kind": d,
                            "size_bytes": sz,
                            "size_human": human_size(sz),
                            "last_modified": mtime_str,
                            "age_days": round(age_sec / 86400.0, 1),
                        }
                        if age_sec <= protect_seconds:
                            tier2_protected_builds.append(entry)
                        else:
                            tier2_stale_builds.append(entry)
                dirs.remove(d)

    tier1_caches.sort(key=lambda x: x["size_bytes"], reverse=True)
    tier2_stale_builds.sort(key=lambda x: x["size_bytes"], reverse=True)
    tier2_protected_builds.sort(key=lambda x: x["size_bytes"], reverse=True)
    worktrees_list = sorted(worktrees_map.values(), key=lambda x: x["size_bytes"], reverse=True)
    gold_archives.sort(key=lambda x: x["size_bytes"], reverse=True)

    return {
        "workspace_dir": str(workspace_dir),
        "protect_days": protect_days,
        "uv_cache": check_uv_cache(),
        "chumbia_locks": chumbia_locks,
        "tier1_caches": tier1_caches,
        "tier2_stale_builds": tier2_stale_builds,
        "tier2_protected_builds": tier2_protected_builds,
        "worktrees": worktrees_list,
        "gold_archives": gold_archives,
    }


def execute_cleanup(report: Dict[str, Any], tiers: List[int]) -> None:
    freed_bytes = 0

    if 1 in tiers:
        print("\n=== 🚀 Executing Tier 1 Cleanup (Dev Caches & uv) ===")
        uv = report.get("uv_cache")
        if uv:
            print(f"  🧹 Running 'uv cache clean' ({uv['size_human']})...")
            run_cmd(["uv", "cache", "clean"], timeout=120)
            freed_bytes += uv["size_bytes"]
        for item in report["tier1_caches"]:
            p = Path(item["path"])
            if p.exists():
                print(f"  🗑️  Removing {item['kind']}: {p} ({item['size_human']})")
                shutil.rmtree(p, ignore_errors=True)
                freed_bytes += item["size_bytes"]

    if 2 in tiers:
        print("\n=== 🚀 Executing Tier 2 Cleanup (Stale Build Outputs) ===")
        for item in report["tier2_stale_builds"]:
            p = Path(item["path"])
            if p.exists():
                print(
                    f"  🗑️  Removing stale build dir (last mod {item['last_modified']}): {p} ({item['size_human']})"
                )
                shutil.rmtree(p, ignore_errors=True)
                freed_bytes += item["size_bytes"]

    if 3 in tiers:
        print("\n=== 🚀 Executing Tier 3 Cleanup (Merged Clean Worktrees & Inner Bloat) ===")
        for wt in report["worktrees"]:
            wt_p = Path(wt["path"])
            if not wt_p.exists():
                continue
            if wt["safe_to_remove"]:
                print(
                    f"  🌿 Removing MERGED & CLEAN worktree: {wt_p} [branch: {wt['branch']}] ({wt['size_human']})"
                )
                main_repo = Path(wt["main_repo"]) if wt.get("main_repo") else None
                if main_repo and main_repo.is_dir():
                    rc, out = run_cmd(["git", "worktree", "remove", str(wt_p)], cwd=main_repo, timeout=60)
                    if rc != 0:
                        shutil.rmtree(wt_p, ignore_errors=True)
                        run_cmd(["git", "worktree", "prune"], cwd=main_repo)
                else:
                    shutil.rmtree(wt_p, ignore_errors=True)
                freed_bytes += wt["size_bytes"]
            else:
                for ib in wt.get("inner_bloat", []):
                    ib_p = Path(ib["path"])
                    if ib_p.exists():
                        print(
                            f"  🧹 Removing inner bloat inside unmerged/dirty worktree {wt_p.name}: {ib_p} ({ib['size_human']})"
                        )
                        shutil.rmtree(ib_p, ignore_errors=True)
                        freed_bytes += ib["size_bytes"]

    print(f"\n✅ Cleanup complete! Estimated space reclaimed: {human_size(freed_bytes)}")


def print_human_report(report: Dict[str, Any]) -> None:
    print(f"=== 🧹💾 GIT DISK CLEANUP AUDIT ({report['workspace_dir']}) ===")
    print(f"⏱️  Freshness Guard: protecting build outputs modified within the last {report['protect_days']} days\n")

    locks = report["chumbia_locks"]
    if locks:
        print(f"🚨 INTERRUPTED /CHUMBIA BREADCRUMBS (.chumbia.touch) [{len(locks)} found]:")
        for lk in locks:
            print(f"  - {lk['touch_file']}")
            for ln in lk["details"].splitlines():
                print(f"      {ln}")
        print()
    else:
        print("✅ Chumbia Breadcrumbs: 0 leftover .chumbia.touch files found.\n")

    t1_total = sum(x["size_bytes"] for x in report["tier1_caches"])
    if report["uv_cache"]:
        t1_total += report["uv_cache"]["size_bytes"]
    print(f"--- TIER 1: Pure Dev Caches & uv ({human_size(t1_total)}) ---")
    if report["uv_cache"]:
        print(f"  📦 {report['uv_cache']['size_human']:>9}  | {report['uv_cache']['path']} (uv cache)")
    for item in report["tier1_caches"]:
        print(f"  📦 {item['size_human']:>9}  | {item['path']}")
    if not report["uv_cache"] and not report["tier1_caches"]:
        print("  (already squeaky clean!)")
    print()

    t2_total = sum(x["size_bytes"] for x in report["tier2_stale_builds"])
    print(f"--- TIER 2: Stale Git-Ignored Build Outputs >{report['protect_days']}d old ({human_size(t2_total)}) ---")
    for item in report["tier2_stale_builds"]:
        print(
            f"  🟢 {item['size_human']:>9}  | last mod: {item['last_modified']} ({item['age_days']}d ago) | {item['path']}"
        )
    if not report["tier2_stale_builds"]:
        print("  (none)")
    if report["tier2_protected_builds"]:
        print(f"\n  🔥 PROTECTED RECENT BUILD OUTPUTS (touched within <= {report['protect_days']}d — DO NOT DELETE):")
        for item in report["tier2_protected_builds"]:
            print(
                f"     🛡️ {item['size_human']:>9} | last mod: {item['last_modified']} ({item['age_days']}d ago) | {item['path']}"
            )
    print()

    safe_wts = [w for w in report["worktrees"] if w["safe_to_remove"]]
    unsafe_wts = [w for w in report["worktrees"] if not w["safe_to_remove"]]
    safe_wt_bytes = sum(w["size_bytes"] for w in safe_wts)
    inner_bloat_bytes = sum(ib["size_bytes"] for w in unsafe_wts for ib in w.get("inner_bloat", []))

    print(
        f"--- TIER 3A: MERGED & CLEAN Git Worktrees (Safe to Remove: {human_size(safe_wt_bytes)}, {len(safe_wts)} worktrees) ---"
    )
    for w in safe_wts:
        print(
            f"  🌿 {w['size_human']:>9}  | MERGED | dirty:0   | {w['last_commit'][:10]} | {w['path']} [{w['branch']}]"
        )
    if not safe_wts:
        print("  (none)")
    print()

    print(
        f"--- TIER 3B: UNMERGED or DIRTY Git Worktrees ({len(unsafe_wts)} worktrees, inner removable bloat: {human_size(inner_bloat_bytes)}) ---"
    )
    for w in unsafe_wts:
        state = "MERGED" if w["merged"] else "UNMERGED"
        ib_sum = human_size(sum(ib["size_bytes"] for ib in w.get("inner_bloat", [])))
        print(
            f"  ⚠️  {w['size_human']:>9}  | {state:<8} | dirty:{w['dirty_count']:<3} | inner_bloat:{ib_sum:<8} | {w['path']} [{w['branch']}]"
        )
    if not unsafe_wts:
        print("  (none)")
    print()

    if report["gold_archives"]:
        gold_total = sum(g["size_bytes"] for g in report["gold_archives"])
        print(f"--- 💎 TIER 4: GOLD MEDIA / ARCHIVES (>50MB, DO NOT ZAP — OFFLOAD TO NAS: {human_size(gold_total)}) ---")
        for g in report["gold_archives"]:
            print(f"  💎 {g['size_human']:>9}  | {g['mtime']} | {g['path']}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Workspace-wide Git & disk bloat janitor.")
    parser.add_argument("--root", help="Workspace directory (overrides $GIT_WORKSPACE_DIR / ~/git)")
    parser.add_argument(
        "--protect-days",
        type=int,
        default=7,
        help="Protect build outputs modified within the last N days (default: 7)",
    )
    parser.add_argument(
        "--min-mb",
        type=float,
        default=5.0,
        help="Minimum folder size in MB to report (default: 5.0)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--execute", action="store_true", help="Execute cleanup for selected --tier(s)")
    parser.add_argument(
        "--tier",
        type=int,
        action="append",
        choices=[1, 2, 3],
        help="Tier(s) to execute when --execute is passed (1, 2, 3)",
    )
    args = parser.parse_args()

    ws_dir = resolve_workspace_dir(args.root)
    if not ws_dir.is_dir():
        print(f"❌ Workspace directory not found: {ws_dir}", file=sys.stderr)
        sys.exit(1)

    report = scan_workspace(ws_dir, protect_days=args.protect_days, min_mb=args.min_mb)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print_human_report(report)

    if args.execute:
        tiers = args.tier or [1]
        execute_cleanup(report, tiers)


if __name__ == "__main__":
    main()
