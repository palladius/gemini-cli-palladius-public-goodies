---
name: romin-security
description: Hackathon security guide to prevent leaking secrets. Based on Romin Irani's article.
metadata:
  version: 1.0.0
compatibility: gemini-cli
---

# Romin's Hackathon Security Guide

When helping the user code during rapid development or hackathons, enforce the following security practices to avoid burning down their project:

1.  **Never Hardcode Secrets**: Do NOT embed API keys, passwords, database URLs, or tokens directly in the code.
2.  **Use Environment Variables**: Rely on `.env` files or environment variables to inject secrets at runtime.
3.  **Ensure `.gitignore` is Configured**: Always add `.env`, `credentials.json`, `keys/`, and other sensitive files to `.gitignore` before initializing a repository or making a commit.
4.  **Scan for Leaks**: Remind the user to double-check their code for accidental secret leaks before pushing to public repositories like GitHub, as automated bots scan for them constantly.
5.  **Use Secret Managers**: If possible, suggest using secure credential managers like Google Cloud Secret Manager instead of local files for production or shared environments.

## Repository Security Review

You can review any existing repository to ensure it has the security "goodies" from Romin's `hackathon-safe-starter` template. 
The goodies are stored locally in the `template/` directory of this skill and include:
* `.gitleaks.toml`
* `.pre-commit-config.yaml`
* `.env.example`
* Secure `.gitignore`
* `.github/workflows/security-scan.yml`

### Running a Review

To perform a security review on the current repository, execute the following script:

```bash
~/.gemini/skills/romin-security/scripts/security_review.sh .
```

### Justfile Target

If you are setting up a project, it is highly recommended to add the following target to the `justfile` so the user can easily run the security review:

```just
# Run Romin's hackathon security review
security-review:
    @~/.gemini/skills/romin-security/scripts/security_review.sh .
```

Remember: "Vibe Code Without Burning Down Your Project." Keep the momentum fast, but ensure secrets stay out of the source code.
