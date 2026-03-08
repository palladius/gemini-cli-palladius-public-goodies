---
name: Ruby Coding Best Practices
description: (💛) Opinionated Ruby coding practices and standards.
tags: ruby, development, best-practices
version: 0.1
---

## Ruby Best Practices

- **RVM/rbenv:** Use a version manager for Ruby.
- **StandardRB:** Prefer StandardRB for linting and formatting.
- **Bundler:** Always use Bundler for dependency management.

(Add your opinionated ideas here)

## Riccardo opinionations

1. I really love the =begin/=end even if nobody uses it. In python, I love a big '''....''' Multiline at the beginning of a file explain what this file is for, and same with ruby, so I can survive this ugly =begin/=end to reach the same goal: \*\*Add a big multiline at the beginning of everything, just after the shebang and an empty line with what the app does!
2. **Minimalism** is important.
3. **Beauty** is important. If your code is minimal and beautiful, it's easier to read and to maintain.
4. Do not monkey patch unless it's the ONLY way or unless it's incredibly minimalistic/beautiful to do.
5. Riccardo likes it colorful and emojiful. I like `lolcat` and `rainbow` gems.
6. Use env ruby as shebang.
7. I don't speak JavaScirpt and friends => reduce JS to a minimum, use Ruby whenever you can, in doubt. If you have to use JS, make sure to document throughly like I was a 13yr old.

### Versions

- Ruby 3.4+
- Rails 8.1+

### CLIs

I also love powerful CLIs with multiple options, particularly:

- `-h|--help`
- `-n|--dryrun` (usually disabled unless the script is DANGEROUS then should be enabled by default)
- A default invocation should be SAFE, like listing, and only a further knowledgeable invocation should allow me to damage/mutate the system.
