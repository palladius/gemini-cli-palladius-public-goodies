---
name: git-repo-documenter
description: "(💛) Auto-documents any Git repository: creates ABOUT.md, generates project hero images via nanobanana, and builds deep diagrams (Mermaid E/R or Class diagrams)."
compatibility: Gemini CLI
metadata:
  version: 0.1.0
---

# Git Repository Documenter (git-repo-documenter)

This skill provides a standardized, deep-dive workflow to automatically generate professional, structured documentation and visual aids for any Git repository, adhering to Carlessian standards.

---

## 🛠️ The Documentation Matrix

When document-analyzing a repository, the agent **must** aim to produce or update the following assets:

### 1. `ABOUT.md` (High-Level Overview)
A clean, premium, high-level manual of the repository. It must contain:
*   **Header Info:** Project Name, Emojis, Owner/Maintainers, Lifecycle Status (`incubator` | `wip` | `graduated`), and active status (`hot` | `warm` | `cold`).
*   **Purpose & Goals:** What the hell this repo actually does and its core vision.
*   **Tech Stack & Dependencies:** Explicit table/list of core languages, frameworks, databases, and third-party APIs/packages used.
*   **Architecture Layout:** A concise ASCII or directory-tree representation of the folder layout (e.g., `├── bin/`, `├── src/`, etc.).
*   **Visual Hero Link:** Reference to the generated `nanobanana` hero image.
*   **Deep Documentation Links:** Links to technical diagrams like `doc/ER_Diagram.md` or `doc/Class_Diagram.md`.

### 2. Project Hero Image (`nanobanana` delegation)
**DO NOT duplicate** image generation code, Python scripts, or image asset directories. Instead, **delegate** the generation task:
*   **In Grid repositories:** If the repo is a Grid-managed project with a `blueprint.yaml`, import and run the grid module: `python3 -m grid.nanobanana` or invoke `grid adopt`.
*   **Using `nano-banana-ricc` skill:** If you need a custom Riccardo cameo or consistent illustrations, invoke/reference the [nano-banana-ricc](file:///Users/ricc/git/gemini-cli-palladius-public-goodies/skills/nano-banana-ricc/SKILL.md) skill.
*   **Using Nano Banana MCP Server directly:** Call the `mcp-nanobanana-go` server or equivalent image generator tools to generate a sleek, modern tech logo for the repository named `grid-image.png` or `about-hero.png` and save it to the repository's root or `doc/` folder.

### 3. `doc/ER_Diagram.md` (Deep Database Schemas)
If a database schema is present or clear in the codebase, auto-generate a comprehensive E/R diagram in **Mermaid.js** format.
*   **How to detect schemas:**
    *   **Rails:** Parse `db/schema.rb`, `db/migrate/*.rb`, or `config/database.yml`.
    *   **Python:** Parse `models.py` (Django/SQLAlchemy), Prisma files, or raw `.sql` migrations.
    *   **Node/TS:** Parse `prisma/schema.prisma`, TypeORM entity classes, or mongoose models.
*   **Mermaid Format:** Construct an `erDiagram` with key relationships (`||--o{`, `}|--||`), attributes, and keys (`PK`, `FK`).
*   **Storage:** Write this to `doc/ER_Diagram.md` and link it under a `## Database Schema` section in `ABOUT.md`.

### 4. `doc/Class_Diagram.md` (Deep Code Structures)
If the project contains rich class hierarchies or domain models (e.g., Java, Python, Ruby, TypeScript classes):
*   Identify the core classes, methods, and inheritances.
*   Generate a Mermaid `classDiagram` mapping the domain layout.
*   Save to `doc/Class_Diagram.md`.

---

## 🚀 Execution Workflow

When a user asks to *"document this site"* or *"run git-repo-documenter"*:

1.  **Analyze Local Structure:**
    *   Scan for existing `README.md`, `GEMINI.md`, `blueprint.yaml`, or configuration files.
    *   Detect languages, framework signatures, and database structures.
2.  **Generate or Fetch Hero Image:**
    *   Check if `grid-image.png` or `about-hero.png` exists in the repository.
    *   If missing, call the `mcp-nanobanana-go` server (using `gemini-3-pro-image-preview` or `gemini-2.5-flash-image`) to generate a professional tech illustration based on your findings, and save it in the repo.
3.  **Draft/Update `ABOUT.md`:**
    *   Synthesize the findings into the standardized `ABOUT.md` layout.
    *   Include links to the hero image and standard developer guidelines.
4.  **Go Deep (ER / Class Diagrams):**
    *   Look for database migrations/models. If found, generate `doc/ER_Diagram.md`.
    *   Look for class domain models. If found, generate `doc/Class_Diagram.md`.
5.  **Commit and Propose (Git Workflow):**
    *   Before committing changes, bump the version file if present.
    *   Add a changelog description to `CHANGELOG.md`.
    *   Stage the created files (`ABOUT.md`, `doc/*`, `grid-image.png`).
    *   Propose the commit message and push request to the user, incorporating your custom emojis.

---

## 📜 History & Credits
*   **v0.1.0:** Initial draft mapping out `ABOUT.md` specifications, `nanobanana` image delegation, and Mermaid database ER diagram automation guidelines.
