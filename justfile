# Run tests on a specific directory (defaults to 'skills')
test DIR="skills":
    uv run --with pyyaml python3 test/validate_skills.py {{DIR}}
    find {{DIR}} -name SKILL.md | npx @govcraft/agent-skills validate -

# Run tests on private goodies
test-pvt:
    @just test ~/git/gemini-cli-palladius-private-goodies/skills/
