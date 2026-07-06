# COMPLETION CHECKLIST

This checklist must be completed to verify the article's quality and assets before sign-off.

## Opening
- [ ] **Tone & Style Unit Test**: Verify the flow is fun, energetic, and written in Riccardo's relatable developer advocate style.
- [ ] **Readability & Grammar**: Review the entire draft to ensure it reads well, flows naturally, and has no typos.

## Closing
- [ ] **Asset Verification**: Ensure all mentioned external assets (YouTube videos, GitHub repositories) are listed and function.
- [ ] **Publish Draft**: Publish the draft on target platforms (e.g., Medium, Dev.to).
- [ ] **Publicize**: Create social media posts (e.g., LinkedIn post in `PUBLICIZE/LINKEDIN.md`).
- [ ] **Close Bug**: Close the tracking bug in Buganizer.
- [ ] Add rsamborki UTMs thanks to `go/devrel-toolkit:mcp`. If you use the toolkit skill, run it to tag URLs; otherwise, manually append the following `UTM_ADDON` string to supported outbound links:
      `?utm_campaign=CDR_0x89ad3e41_awareness_b<BUG_ID>&utm_medium=external&utm_source=blog`
      (where `<BUG_ID>` is the Buganizer issue ID numbers, e.g., `b123456` if the bug is `123456`).
