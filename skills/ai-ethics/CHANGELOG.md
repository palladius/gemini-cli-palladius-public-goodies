# Changelog — `ai-ethics`

## [1.1.0] - 2026-11-07
### Added
- Integrated the **EU AI Act (`Regulation (EU) 2024/1689`) "Safety Ladder"** (*Prohibited*, *High-Risk*, *General-Purpose / Transparency*, *Lower Risk*) into `SKILL.md`, `references/CARLESSIAN_CONSTITUTION.md`, and `references/AI_ETHICS.template.md` (`Carlessian Commons Ethics v1.1`, SHA-256 `1cc43a4ed145d95b72d3b61152e239aa824e722f8d7a8772dfa0d15aefec14e9`).
- Added comprehensive developer reference `references/EU_AI_ACT.md` mapping Articles 5, 6, 9–15, 50, 51–55, and 95 to concrete software architecture and code safeguards (mandatory HITL gates, automatic audit logging, AI bot disclosure, and `SynthID`/`C2PA` synthetic media provenance).
- Updated `scripts/verify_ai_ethics.py` to verify `Carlessian Commons Ethics v1.1` while recognizing `v1.0` with an upgrade hint.

## [1.0.0] - 2026-11-02
### Added
- Initial release of `ai-ethics` (`Carlessian Commons Ethics v1.0`).
- Canonical `/AI_ETHICS.md` template (`references/AI_ETHICS.template.md`) with customizable Lines 1–2 and SHA-256 locked body (`4f25569c45da2af754db36c7044773eae3ae2844c3559787cfe2b8f096c2edd6`).
- Full philosophical and operational reference manifesto (`references/CARLESSIAN_CONSTITUTION.md`) fusing Asimov's Laws (0–3), Anthropic's January 2026 Claude Constitution (CC0 1.0), Italian/Googley cultural DNA (*"Parla come mangi"*, White-Hat Responsible Disclosure, Work Non-Exfiltration, Anti-Sycophancy), and the Two Supreme Carlessian Dogmas (Combatting Global Warming & Combatting Fake News).
- `scripts/verify_ai_ethics.py`: SHA-256 tamper detector, unified diff reporter, and repository installer (`--check`, `--install`, `--strict`, `--self-test`).
- `scripts/estimate_swarm_carbon.py`: Ecological compute and carbon footprint estimator for multi-agent swarms (`--agents`, `--model`, `--task-criticality`, `--self-test`).
