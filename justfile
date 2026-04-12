test:
    python3 test/validate_skills.py
    find skills -name SKILL.md | npx @govcraft/agent-skills validate -
