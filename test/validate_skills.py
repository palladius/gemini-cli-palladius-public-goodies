import os
import re
import sys

# Requirements categorization
# MUST (Errors): name, description, SKILL.md existence
# SHOULD (Warnings): compatibility, metadata.version, CHANGELOG.md existence, version in CHANGELOG

def validate_skill(skill_dir):
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(skill_path):
        return [f"Missing {skill_path}"], []
    
    try:
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Error reading SKILL.md: {e}"], []
    
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
    version = None
    if not metadata or (isinstance(metadata, dict) and 'version' not in metadata):
        warnings.append("Missing 'metadata.version'")
    elif isinstance(metadata, dict):
        version = str(metadata.get('version'))

    # Check for CHANGELOG.md in the skill directory
    changelog_path = os.path.join(skill_dir, 'CHANGELOG.md')
    if not os.path.exists(changelog_path):
        warnings.append(f"Missing {changelog_path}")
    elif version:
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                changelog_content = f.read()
                version_pattern = rf'##\s+.*{re.escape(version)}.*'
                if not re.search(version_pattern, changelog_content):
                    errors.append(f"Version {version} from SKILL.md not found in {changelog_path}: make sure you add it there before you move on and forget")
        except Exception:
            warnings.append(f"Could not read {changelog_path}")
    
    return errors, warnings

def main():
    # Use command line arguments or default to current directory
    dirs_to_scan = sys.argv[1:] if len(sys.argv) > 1 else ['.']
    
    total_errors = 0
    total_warnings = 0
    
    for base_dir in dirs_to_scan:
        if not os.path.exists(base_dir):
            print(f"Path '{base_dir}' not found, skipping...")
            continue
        
        # If it's a directory, check if it's a skill or a container of skills
        if os.path.isdir(base_dir):
            # Case 1: The directory itself is a skill
            if os.path.exists(os.path.join(base_dir, 'SKILL.md')):
                errors, warnings = validate_skill(base_dir)
                if errors or warnings:
                    print(f"Skill: {base_dir}")
                    for e in errors: print(f"  [ERROR] {e}")
                    for w in warnings: print(f"  [WARN]  {w}")
                    total_errors += len(errors); total_warnings += len(warnings)
            # Case 2: It's a directory containing skills (like 'skills/')
            else:
                for item in sorted(os.listdir(base_dir)):
                    skill_dir = os.path.join(base_dir, item)
                    if os.path.isdir(skill_dir) and os.path.exists(os.path.join(skill_dir, 'SKILL.md')):
                        errors, warnings = validate_skill(skill_dir)
                        if errors or warnings:
                            print(f"Skill: {skill_dir}")
                            for e in errors: print(f"  [ERROR] {e}")
                            for w in warnings: print(f"  [WARN]  {w}")
                            total_errors += len(errors); total_warnings += len(warnings)
    
    print(f"\nFinished: {total_errors} errors, {total_warnings} warnings")
    if total_errors > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
