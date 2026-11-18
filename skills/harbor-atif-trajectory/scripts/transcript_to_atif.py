"""ATIF Converters for Google Agent Transcripts.

Provides converters for:
1. Antigravity CLI (agy) JSONL transcripts
2. Google Gemini CLI JSONL session logs
3. Antigravity 2.0 IDE transcripts
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from harbor.models.trajectories import (
    Agent,
    FinalMetrics,
    Metrics,
    Observation,
    ObservationResult,
    Step,
    ToolCall,
    Trajectory,
)
from harbor.utils.trajectory_validator import TrajectoryValidator


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def convert_antigravity_cli_to_atif(
    records: list[dict[str, Any]],
    session_id: str = "agy-sim-001",
    model_name: str = "gemini-3.0-flash",
    version: str = "1.1.14",
) -> Trajectory:
    """Convert Antigravity CLI (agy) transcript records into an ATIF Trajectory."""
    steps: list[Step] = []
    pending_calls: list[tuple[Step, str]] = []
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_cached_tokens = 0

    for record in records:
        record_type = str(record.get("type", "")).upper()
        content = record.get("content") or ""
        timestamp = record.get("created_at") or _iso_now()

        if record_type == "USER_INPUT":
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    timestamp=timestamp,
                    source="user",
                    message=content,
                )
            )
            continue

        if record_type == "PLANNER_RESPONSE":
            tool_calls: list[ToolCall] = []
            step_index = record.get("step_index", len(steps))
            for call_index, raw_call in enumerate(record.get("tool_calls") or []):
                call_id = f"agy-{step_index}-{call_index}"
                args = raw_call.get("args") or {}
                if not isinstance(args, dict):
                    args = {"value": args}
                tool_calls.append(
                    ToolCall(
                        tool_call_id=call_id,
                        function_name=str(raw_call.get("name") or "unknown_tool"),
                        arguments=args,
                    )
                )

            # Step tokens if available
            tokens = record.get("tokens") or {}
            step_metrics = None
            if tokens:
                p_tok = tokens.get("input", 0)
                c_tok = tokens.get("output", 0)
                ca_tok = tokens.get("cached", 0)
                total_prompt_tokens += p_tok
                total_completion_tokens += c_tok
                total_cached_tokens += ca_tok
                step_metrics = Metrics(
                    prompt_tokens=p_tok,
                    completion_tokens=c_tok,
                    cached_tokens=ca_tok,
                )

            step = Step(
                step_id=len(steps) + 1,
                timestamp=timestamp,
                source="agent",
                model_name=model_name,
                message=content,
                reasoning_content=record.get("thinking") or None,
                tool_calls=tool_calls or None,
                metrics=step_metrics,
            )
            steps.append(step)
            for call in tool_calls:
                pending_calls.append((step, call.tool_call_id))
            continue

        # Handle tool results / observation records
        if pending_calls and (
            record_type in ("TOOL_RESULT", "COMMAND_OUTPUT", "OBSERVATION")
            or "content" in record
        ):
            target_step, call_id = pending_calls.pop(0)
            res = ObservationResult(
                source_call_id=call_id,
                content=str(content),
                extra={"status": record.get("status", "SUCCESS")},
            )
            if target_step.observation is None:
                target_step.observation = Observation(results=[res])
            else:
                target_step.observation.results.append(res)
            continue

        # Fallback for system announcements/errors
        if content or record.get("error"):
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    timestamp=timestamp,
                    source="system",
                    message=content or str(record.get("error")),
                )
            )

    return Trajectory(
        schema_version="ATIF-v1.8",
        session_id=session_id,
        agent=Agent(name="antigravity-cli", version=version, model_name=model_name),
        steps=steps,
        final_metrics=FinalMetrics(
            total_prompt_tokens=total_prompt_tokens or None,
            total_completion_tokens=total_completion_tokens or None,
            total_cached_tokens=total_cached_tokens or None,
            total_steps=len(steps),
        ),
    )


def convert_gemini_cli_to_atif(
    records: list[dict[str, Any]],
    session_id: str = "gemini-cli-sim-001",
    model_name: str = "gemini-2.5-pro",
    version: str = "0.42.0",
) -> Trajectory:
    """Convert Google Gemini CLI session records into an ATIF Trajectory."""
    steps: list[Step] = []
    messages_by_id: dict[str, dict[str, Any]] = {}
    total_input = 0
    total_output = 0
    total_cached = 0

    for record in records:
        rec_type = record.get("type")
        msg_id = record.get("id")

        if rec_type in ("user", "gemini"):
            messages_by_id[msg_id] = record
        elif rec_type == "message_update" and msg_id in messages_by_id:
            # Merge incremental tokens
            tokens = record.get("tokens", {})
            messages_by_id[msg_id]["tokens"] = tokens
            total_input += tokens.get("input", 0)
            total_output += tokens.get("output", 0)
            total_cached += tokens.get("cached", 0)

    for msg in messages_by_id.values():
        rec_type = msg.get("type")
        timestamp = msg.get("timestamp") or _iso_now()
        raw_content = msg.get("content") or []
        text = ""
        if isinstance(raw_content, list):
            text = "\n".join(
                c.get("text", "") for c in raw_content if isinstance(c, dict)
            )
        elif isinstance(raw_content, str):
            text = raw_content

        tokens = msg.get("tokens") or {}
        step_metrics = None
        if tokens:
            step_metrics = Metrics(
                prompt_tokens=tokens.get("input", 0),
                completion_tokens=tokens.get("output", 0),
                cached_tokens=tokens.get("cached", 0),
            )

        if rec_type == "user":
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    timestamp=timestamp,
                    source="user",
                    message=text,
                )
            )
        elif rec_type == "gemini":
            steps.append(
                Step(
                    step_id=len(steps) + 1,
                    timestamp=timestamp,
                    source="agent",
                    model_name=msg.get("model", model_name),
                    message=text,
                    metrics=step_metrics,
                )
            )

    return Trajectory(
        schema_version="ATIF-v1.8",
        session_id=session_id,
        agent=Agent(name="gemini-cli", version=version, model_name=model_name),
        steps=steps,
        final_metrics=FinalMetrics(
            total_prompt_tokens=total_input or None,
            total_completion_tokens=total_output or None,
            total_cached_tokens=total_cached or None,
            total_steps=len(steps),
        ),
    )


def convert_antigravity20_ide_to_atif(
    records: list[dict[str, Any]],
    session_id: str = "antigravity20-ide-session",
    model_name: str = "gemini-3.0-pro",
    version: str = "2.0.0-preview",
) -> Trajectory:
    """Convert Antigravity 2.0 IDE transcript records into an ATIF Trajectory."""
    # Uses Antigravity CLI structure with rich IDE metadata
    trajectory = convert_antigravity_cli_to_atif(
        records, session_id=session_id, model_name=model_name, version=version
    )
    # Customize agent name to reflect Antigravity IDE
    trajectory.agent.name = "antigravity20-ide"
    trajectory.notes = "Antigravity 2.0 IDE pair-programming session with RiccardinoCM26 🦖"
    return trajectory


def validate_trajectory_file(path: Path) -> tuple[bool, list[str]]:
    """Validate an ATIF file with Harbor's official TrajectoryValidator."""
    validator = TrajectoryValidator()
    valid = validator.validate(path)
    return valid, validator.errors
