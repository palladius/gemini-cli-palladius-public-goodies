# Google Docs AI-Editing Best Practices (`ai-coding`) 📄🤖

When an AI agent edits or maintains a Google Doc (via Google Docs / Workspace MCP servers or APIs), it operates on a **live, collaborative human document** rather than an isolated source file. Follow these non-destructive editing invariants at all times.

---

## 1. 🛡️ Protect the Human Header Zone & Respect the `<hr>` (`---`) Fence

Many collaborative Google Docs begin with a human-authored metadata and instruction header at the very top of the page, often followed by a horizontal rule (`<hr>` / `---`):

```markdown
Self: https://docs.example.com/my-doc
Owner: Alice Smith
Folder: Team Architecture
🤖 This is managed by AI on behalf of Alice 🤖 — ⚠️ Keep strictly within 1 PAGE!

---

# Document Title (AI-Managed Zone Starts Below <hr>)
```

- **The `<hr>` Boundary Rule:** If a horizontal rule (`<hr>` or `---`) exists near the top of the document, treat **everything above the first `<hr>`** as the **Human Header Zone (Strictly Read-Only for AI)**.
- **Write Only After `<hr>`:** Never delete, modify, reorder, or overwrite any text above the `<hr>`. All AI-generated updates must occur **strictly after** the `<hr>` separator.
- **No `<hr>` Present?** If there is no explicit `<hr>`, treat the top metadata lines (`Self:`, `Owner:`, `Author:`, `Date:`, `Status:`, `Folder:`, and any introductory human notes or banners above the first `#` / `##` heading) as an implicit Human Header Zone and preserve them verbatim.

---

## 2. ✏️ Scoped Heading Ownership (`H2` / `##` or Deeper)

- **Never Alter Human-Authored Content:** In a shared document containing human-written sections, never rewrite, summarize, or delete human-authored paragraphs, comments, or top-level (`H1`) structure unless the user explicitly asks you to edit that specific text.
- **Modify Only AI-Owned `H2+` Sections:** Scope autonomous AI additions and refreshes to sections created and owned by the agent at heading level **`H2` (`##`) or deeper (`###`, `####`)**.
- **Explicit Delegation Exception:** If the Human Header Zone explicitly delegates the post-`<hr>` body to the agent (e.g., `🤖 This is managed by AI on behalf of <user> 🤖`), the agent may maintain the full post-`<hr>` structure while still keeping the pre-`<hr>` header untouched and honoring any constraints declared in that header.

---

## 3. 🔄 Read-Immediately-Before-Write (Anti-Race Condition)

Google Docs is a real-time multiplayer surface—the user may be typing a new instruction in the header or tweaking a paragraph while the agent is thinking.

- **Never Trust Stale Context:** Do not rely on a document snapshot read several turns earlier.
- **Mandatory Fresh Read Before Every Write:** Immediately before calling any write tool (`update_doc`, `update_document`, `replace_paragraph`, or `batchUpdate`), **re-read the live document in the same turn**.
- **Splice Live Header Verbatim:** When using a full-document replacement tool (such as `update_document`), dynamically copy the freshly read Human Header Zone (everything up to and including `---`) and prepend it verbatim to your updated post-`<hr>` body so concurrent human edits are never clobbered.
- **Prefer Surgical Updates When Available:** When using index-aware tools (`batchUpdate` / `replace_paragraph`), target only the specific AI-owned `H2+` section range (applying edits in reverse index order from bottom to top so character offsets do not shift).

---

## 4. 📏 Honor Header Directives (Page Budget & Density)

Always parse the Human Header Zone for editorial and layout directives before drafting your update:

- **Page-Length Constraints (e.g., *"Keep within 1 page"*):**
  - Replace verbose prose and deep bullet trees with **compact Markdown tables**.
  - Limit vertical whitespace and avoid redundant introductory/concluding filler paragraphs.
  - Consolidate related items into single table rows (`~35–45 lines` maximum for a 1-page Google Doc with a top header and 1–2 tables).
- **Confidentiality & Audience Scope:** Verify who the document is shared with and never leak restricted or private project keywords into a broadly shared doc.
