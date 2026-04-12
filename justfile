test:
    python3 test/validate_skills.py
    find skills -name SKILL.md | xargs -n 1 npx @govcraft/agent-skills validate
