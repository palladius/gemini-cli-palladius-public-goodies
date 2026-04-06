---
name: drawio
description: Generates and edits diagrams using draw.io via local files or the MCP service.
tags: ["OpenClaudio", "diagrams", "visualization", "microphone-dictated"]
version: 0.1
---

# draw.io Diagram Skill

This skill enables the creation and editing of diagrams using the powerful draw.io editor. It can operate in two modes.

## 1. Local File Mode (Default)

This is the default mode of operation. You provide a description of a diagram (in natural language, Mermaid syntax, or even CSV), and the skill will generate a `.drawio` file.

If you have the [draw.io Desktop application](https://github.com/jgraph/drawio-desktop) installed, the skill can also use its command-line interface to export the diagram to other formats like PNG, SVG, or PDF.

### Usage
```bash
# Describe a diagram
"Create a flowchart for a coffee making process."

# The assistant will then use this skill to generate the diagram file.
# The core logic is in the script:
{baseDir}/scripts/generate.sh --prompt "a description..." --output "diagram.drawio.png"
```

---

## 2. ⭐ Advanced Mode: MCP App Server Integration

For a much more integrated experience with interactive diagrams directly inside your chat, you can configure the official draw.io MCP server.

This is a **one-time setup** in your AI assistant's settings (e.g., Gemini Advanced Settings or the Claude.ai web UI).

### How to set it up:
1.  Go to your AI assistant's settings for tools or extensions.
2.  Find the section for adding new MCP (Model Context Protocol) servers.
3.  Add the following URL:
    `https://mcp.draw.io/mcp`

### Benefits
-   **Inline Diagrams:** Diagrams will appear directly in the conversation, not just as files.
-   **Interactive:** You can pan, zoom, and even edit the diagrams from the chat.
-   **No Installation:** You don't need the draw.io desktop app for this to work.

By setting this up, you are essentially giving the assistant a powerful, persistent tool for all future diagramming tasks.
