# Romin Security Skill

This skill enforces strict security practices for rapid application development and hackathons to prevent the accidental leaking of sensitive secrets, such as API keys and credentials.

## Acknowledgments and Thanks

This skill is heavily inspired by and directly based on **Romin Irani's** excellent article: 
[**The Hackathon Security Guide: How to Vibe-Code Without Burning Down Your Project**](https://medium.com/@romin.irani)

A huge thanks to Romin for shedding light on the millions of secrets leaked to public repositories every year, and for providing a practical framework to balance the speed of "vibe-coding" with fundamental security practices!

## What it does

It applies Romin's recommended security "goodies" to any repository:
- `.gitleaks.toml` for custom secret detection rules
- `.pre-commit-config.yaml` to run Gitleaks locally before any commit
- A secure `.gitignore` to prevent committing `.env` and `serviceAccountKey.json` files
- An `.env.example` file to outline required environment variables safely
- A `.github/workflows/security-scan.yml` to run Gitleaks in CI/CD 

*Remember: Vibe-Code without burning down your project!*
