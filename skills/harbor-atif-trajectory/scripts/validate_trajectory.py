#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "pydantic>=2.0",
#   "pyyaml",
# ]
# ///
"""Harbor ATIF Trajectory Validator.

Validates an arbitrary JSON file against Harbor ATIF-v1.8 specifications.
"""

import json
import sys
from pathlib import Path

# Add GIC repo root to sys.path
GIC_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent / "gic"
sys.path.insert(0, str(GIC_ROOT))

from lib.python.atif.models import Trajectory


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_trajectory.py <path/to/trajectory.json>")
        sys.exit(1)

    traj_path = Path(sys.argv[1])
    if not traj_path.exists():
        print(f"❌ File not found: {traj_path}")
        sys.exit(1)

    print(f"🔍 Validating {traj_path} against Harbor ATIF-v1.8...")
    try:
        with open(traj_path, "r", encoding="utf-8") as f:
            content = f.read()

        traj = Trajectory.model_validate_json(content)
        traj.validate_step_sequence()

        print(f"✅ VALID ATIF-v1.8 Trajectory!")
        print(f"   • Schema Version: {traj.schema_version}")
        print(f"   • Trajectory ID:  {traj.trajectory_id or 'none'}")
        print(f"   • Agent:          {traj.agent.name}")
        print(f"   • Steps:          {len(traj.steps)}")
        if traj.final_metrics:
            print(f"   • Total Tokens:   {(traj.final_metrics.total_prompt_tokens or 0) + (traj.final_metrics.total_completion_tokens or 0):,}")
            print(f"   • Total Cost:     ${traj.final_metrics.total_cost_usd or 0.0:.4f} USD")
    except Exception as e:
        print(f"❌ Validation Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
