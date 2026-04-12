import os
import re
import sys

# Requirements categorization
# MUST (Errors): name, description, SKILL.md existence
# SHOULD (Warnings): compatibility, metadata.version, CHANGELOG.md existence

def validate_skill(skill_dir):
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_path):
        return [f"Missing {skill_path}"], []
    
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return ["Missing or invalid frontmatter"], []
    
    frontmatter_text = match.group(1)
    errors = []
    warnings = []
    
    # Simple YAML-ish parser for frontmatter
    frontmatter = {}
    current_key = None
    for line in frontmatter_text.split('\n'):
        if not line.strip():
            continue
        if ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            current_key = key.strip()
            frontmatter[current_key] = value.strip()
        elif line.startswith('  ') and current_key:
            # Handle nested keys like metadata: version:
            sub_key_match = re.match(r'^\s+(\w+):\s*(.*)', line)
            if sub_key_match:
                sub_key, sub_value = sub_key_match.groups()
                if not isinstance(frontmatter[current_key], dict):
                    frontmatter[current_key] = {}
                frontmatter[current_key][sub_key] = sub_value.strip()

    # MUST
    if 'name' not in frontmatter:
        errors.append("Missing 'name'")
    if 'description' not in frontmatter:
        errors.append("Missing 'description'")
    
    # SHOULD
    if 'compatibility' not in frontmatter:
        warnings.append("Missing 'compatibility'")
    
    metadata = frontmatter.get('metadata')
    if not metadata or (isinstance(metadata, dict) and 'version' not in metadata):
        warnings.append("Missing 'metadata.version'")
    
    # Check for CHANGELOG.md in the skill directory
    changelog_path = os.path.join(skill_dir, 'CHANGELOG.md')
    if not os.path.exists(changelog_path):
        warnings.append(f"Missing {changelog_path}")
    
    return errors, warnings

def main():
    skills_dir = 'skills'
    if not os.path.exists(skills_dir):
        print(f"Directory {skills_dir} not found.")
        sys.exit(1)
    
    total_errors = 0
    total_warnings = 0
    
    # Sort for deterministic output
    skill_names = sorted(os.listdir(skills_dir))
    
    for skill_name in skill_names:
        skill_dir = os.path.join(skills_dir, skill_name)
        if os.path.isdir(skill_dir):
            errors, warnings = validate_skill(skill_dir)
            
            if errors or warnings:
                print(f"Skill: {skill_name}")
                for e in errors:
                    print(f"  [ERROR] {e}")
                for w in warnings:
                    print(f"  [WARN]  {w}")
                total_errors += len(errors)
                total_warnings += len(warnings)
    
    print(f"\nFinished: {total_errors} errors, {total_warnings} warnings")
    
    # Exit with 1 only if there are errors
    if total_errors > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
