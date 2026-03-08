---
name: TypeScript Coding Best Practices
description: (💛) Opinionated TypeScript coding practices and standards for those who prefer Ruby.
tags: typescript, javascript, development, best-practices
version: 0.1
---

## TypeScript Best Practices

- **Strict Mode:** Always enable `strict` in `tsconfig.json`.
- **ESLint & Prettier:** Use for consistent styling and identifying potential bugs.
- **Type Safety:** Prefer explicit types over `any`.
- **Modern Syntax:** Utilize latest ECMAScript features compatible with the target environment.

## Riccardo's TypeScript Opinionations

Riccardo is primarily a Ruby and Python developer and finds TypeScript/JavaScript complex. Therefore:

1. **Avoid if possible:** Only use TypeScript/JavaScript when it's the only viable option (e.g., frontend development with React/Angular or specific Node.js-only libraries). If a task can be done in Ruby or Python, prefer those.
2. **Extreme Documentation:** Document the code thoroughly, as if explaining it to someone with no prior JavaScript experience (or a 13-year-old). Explain the *why* and *how* of every non-trivial block.
3. **Minimalism:** Keep the code as simple and flat as possible. Avoid complex design patterns that are common in large JS codebases but hard to follow for outsiders.
4. **Maintainability:** Since this is not Riccardo's primary language, the code must be exceptionally clear so he can understand and maintain it months later without a deep dive into JS documentation.
5. **No "Magic":** Avoid clever tricks or obscure JS features. Stick to well-understood, standard patterns.
6. **Beauty & Emojis:** Even in TypeScript, keep the CLI outputs (if any) beautiful, colorful, and emoji-friendly.
