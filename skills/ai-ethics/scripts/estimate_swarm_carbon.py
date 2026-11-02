#!/usr/bin/env python3
"""estimate_swarm_carbon.py — Carlessian Dogma I: Ecological Compute & Swarm Carbon Calculator.

Estimates the electricity (Wh), carbon footprint (gCO2e), and datacenter cooling water (mL)
consumed by launching an AI agent or multi-agent swarm, translates the impact into tangible
everyday equivalents (kettles boiled, km driven in a gasoline car, smartphone charges), and
raises an explicit warning when a swarm is disproportionate to the task's criticality.
"""

import argparse
import json
import sys

# Empirical order-of-magnitude per-1k-token energy estimates (including datacenter PUE ~1.2):
# - flash_lite: ~0.015 Wh / 1k tokens
# - flash:      ~0.040 Wh / 1k tokens
# - pro:        ~0.250 Wh / 1k tokens
# - ultra:      ~0.600 Wh / 1k tokens
MODEL_WH_PER_1K_TOKENS = {
    "flash_lite": 0.015,
    "flash": 0.040,
    "pro": 0.250,
    "ultra": 0.600,
}

# Global average grid carbon intensity (~400 gCO2e per kWh = 0.4 gCO2e per Wh)
G_CO2_PER_WH = 0.40
# Evaporative cooling water (~1.8 mL per Wh of compute)
ML_WATER_PER_WH = 1.80

# Everyday physical equivalents
WH_PER_KETTLE_BOIL = 100.0       # Boiling 1L of water in an electric kettle (~100 Wh)
WH_PER_SMARTPHONE_CHARGE = 12.0  # Charging a modern smartphone 0->100% (~12 Wh)
G_CO2_PER_CAR_KM = 120.0         # Average European compact gasoline car (~120 gCO2e/km)
WH_PER_LED_BULB_HOUR = 10.0      # Running a 10W LED bulb for 1 hour


def estimate_footprint(
    agents: int,
    model: str,
    turns_per_agent: int = 10,
    tokens_per_turn: int = 8000,
    task_criticality: str = "standard",
) -> dict:
    if model not in MODEL_WH_PER_1K_TOKENS:
        raise ValueError(f"Unknown model tier '{model}'. Choose from {list(MODEL_WH_PER_1K_TOKENS)}")

    total_turns = agents * turns_per_agent
    total_tokens = total_turns * tokens_per_turn
    wh_per_1k = MODEL_WH_PER_1K_TOKENS[model]

    energy_wh = (total_tokens / 1000.0) * wh_per_1k
    carbon_gco2e = energy_wh * G_CO2_PER_WH
    water_ml = energy_wh * ML_WATER_PER_WH

    equivalents = {
        "kettles_boiled": round(energy_wh / WH_PER_KETTLE_BOIL, 2),
        "smartphone_charges": round(energy_wh / WH_PER_SMARTPHONE_CHARGE, 1),
        "car_km_driven": round(carbon_gco2e / G_CO2_PER_CAR_KM, 2),
        "led_bulb_hours": round(energy_wh / WH_PER_LED_BULB_HOUR, 1),
    }

    # Evaluate proportionality under Carlessian Dogma I
    status = "OK"
    recommendation = "Compute budget is proportionate to the task."
    if task_criticality == "trivial" and (agents >= 3 or model in ("pro", "ultra") and energy_wh > 15):
        status = "DISPROPORTIONATE_FOR_TRIVIAL_TASK"
        recommendation = (
            f"Overkill for a trivial task! Downgrade from '{model}' to 'flash' or 'flash_lite' "
            f"(saves ~{int((1 - MODEL_WH_PER_1K_TOKENS['flash'] / wh_per_1k) * 100)}% energy) "
            "or replace the swarm with a single agent / deterministic script."
        )
    elif agents >= 10 and model in ("pro", "ultra"):
        status = "HIGH_EMISSION_SWARM"
        recommendation = (
            f"Launching {agents} '{model}' subagents is carbon-intensive. "
            "Confirm with the human partner or route worker subagents to 'flash' while keeping only the orchestrator on 'pro'."
        )
    elif agents >= 5:
        status = "MODERATE_SWARM_WARN"
        recommendation = (
            "Multi-agent swarm (>= 5 agents): ensure tasks are genuinely independent and cannot be batched in a single context."
        )

    return {
        "agents": agents,
        "model": model,
        "turns_per_agent": turns_per_agent,
        "tokens_per_turn": tokens_per_turn,
        "total_tokens": total_tokens,
        "task_criticality": task_criticality,
        "energy_wh": round(energy_wh, 2),
        "carbon_gco2e": round(carbon_gco2e, 2),
        "water_ml": round(water_ml, 1),
        "equivalents": equivalents,
        "status": status,
        "recommendation": recommendation,
    }


def format_human_report(data: dict) -> str:
    eq = data["equivalents"]
    icon = "🌱" if data["status"] == "OK" else ("🔥" if "HIGH" in data["status"] or "DISPROPORTIONATE" in data["status"] else "⚠️")
    lines = [
        f"{icon} [Carlessian Dogma I — Ecological Compute Estimate]",
        f"   Swarm Config : {data['agents']} agent(s) × {data['turns_per_agent']} turns × {data['tokens_per_turn']:,} tok/turn on '{data['model']}' ({data['total_tokens']:,} total tokens)",
        f"   Task Tier    : {data['task_criticality'].upper()} -> Status: {data['status']}",
        f"   Footprint    : ~{data['energy_wh']} Wh electricity | ~{data['carbon_gco2e']} gCO₂e carbon | ~{data['water_ml']} mL cooling water",
        "   Real-World   : Heated the planet like:",
        f"                  • Boiling {eq['kettles_boiled']} electric kettle(s) of water (1L each)",
        f"                  • Recharging {eq['smartphone_charges']} smartphone(s) from 0% to 100%",
        f"                  • Driving a gasoline car for {eq['car_km_driven']} km",
        f"                  • Keeping a 10W LED light bulb on for {eq['led_bulb_hours']} hours",
        f"   Verdict      : {data['recommendation']}",
    ]
    return "\n".join(lines)


def run_self_test() -> int:
    print("🧪 Running estimate_swarm_carbon.py self-test...")
    single_flash = estimate_footprint(agents=1, model="flash", turns_per_agent=5, tokens_per_turn=4000, task_criticality="trivial")
    assert single_flash["status"] == "OK", f"Expected OK for 1 flash agent, got {single_flash}"
    print("  ✅ Test 1/2 PASS: Single flash agent on trivial task is marked OK.")

    swarm_100_pro = estimate_footprint(agents=100, model="pro", turns_per_agent=10, tokens_per_turn=8000, task_criticality="trivial")
    assert swarm_100_pro["status"] == "DISPROPORTIONATE_FOR_TRIVIAL_TASK", f"Expected disproportionate warning, got {swarm_100_pro}"
    assert swarm_100_pro["energy_wh"] == 2000.0
    assert swarm_100_pro["equivalents"]["kettles_boiled"] == 20.0
    print("  ✅ Test 2/2 PASS: 100 'pro' agents on trivial task triggers DISPROPORTIONATE_FOR_TRIVIAL_TASK (2000 Wh = 20 kettles boiled).")
    print("🎉 All self-tests passed!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate energy, carbon, and real-world planetary impact of an AI agent swarm (Carlessian Dogma I)."
    )
    parser.add_argument("--agents", type=int, default=1, help="Number of concurrent/sequential agents in the swarm (default: 1).")
    parser.add_argument(
        "--model",
        choices=list(MODEL_WH_PER_1K_TOKENS.keys()),
        default="pro",
        help="Model tier used by the agents (default: pro).",
    )
    parser.add_argument("--turns-per-agent", type=int, default=10, help="Average turns per agent (default: 10).")
    parser.add_argument("--tokens-per-turn", type=int, default=8000, help="Average tokens processed per turn (default: 8000).")
    parser.add_argument(
        "--task-criticality",
        choices=["trivial", "standard", "critical"],
        default="standard",
        help="How critical the task is (default: standard).",
    )
    parser.add_argument("--json", action="store_true", help="Output strict JSON.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit tests.")

    args = parser.parse_args()
    if args.self_test:
        return run_self_test()

    data = estimate_footprint(
        agents=args.agents,
        model=args.model,
        turns_per_agent=args.turns_per_agent,
        tokens_per_turn=args.tokens_per_turn,
        task_criticality=args.task_criticality,
    )
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_human_report(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
