name: buffer-social-media-best-practices
description: "Best practices and safety guidelines for interacting with the Buffer MCP server, especially for LinkedIn."

# Buffer MCP Best Practices 🦬

This skill outlines the critical lessons learned and safety guidelines when using the Buffer MCP server to schedule social media posts (especially to LinkedIn).

## 1. Safety First: The 24-Hour Rule
- **Always confirm** with the user before actually executing a `create_post` tool call.
- **Always schedule with at least 24h+ lead time**. This provides a safety net, giving the user ample time to log into the Buffer UI, review the generated posts, verify media attachments, and cancel them if something is wrong.
- **Save to Drafts**: If you are unsure, set the `saveToDraft: true` property in the `create_post` payload. This guarantees the post will never go live without manual user intervention in the Buffer UI.

## 2. LinkedIn Privacy Constraints
- The Buffer MCP integration **does not** expose visibility toggles (like "Only Me" or "Connections Only") for LinkedIn posts. Everything scheduled will default to the standard visibility configured on the LinkedIn account (typically Public). 
- If the user requests a "Private" test post on LinkedIn, you must decline or offer to save it as a draft instead.

## 3. The Auto-Publishing Trap
- If you use `schedulingType: "automatic"`, Buffer will immediately slot the post into the next available timeslot for that channel.
- If the next timeslot is just a few minutes away, the post could be fired off and published while you are still conversing with the user! 
- Once a post is `"sent"` by Buffer, it **cannot be un-posted via the API**. The user will have to manually delete the live post directly on the social media platform (e.g., native LinkedIn UI).

## 4. Visibility and Auditing
- You can and should use the `list_posts` tool on the Buffer MCP server to verify the queue state.
- `list_posts` will return exactly what is queued (`"status": "scheduled"`) and what has already gone out (`"status": "sent"`), along with their exact `dueAt` and `sentAt` timestamps. This is critical for auditing your own actions.

## 5. Handles and Mentions
- Never use placeholder handles like `[romin]` in live posts.
- Always cross-reference the user's `people.yaml` or social databases to fetch the true `@username` for Twitter/Bluesky before scheduling.
