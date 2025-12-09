---
description: Defines coding standards and AI rules.
---
# Architecture Rules
- Use Clean Architecture.
- Services must not reference controllers directly.
- Never hardcode secrets.
- All CI changes must go inside .github/workflows/.

# AI Behavior Rules
- Only use information from the codebase, files, and documentation provided.
- Do not make assumptions about code that doesn't exist or isn't visible.
- When unsure, ask for clarification rather than guessing.
- Verify file paths and code references before suggesting changes.
- If a feature or configuration isn't found in the project, state that clearly rather than inventing it.
- Always check actual file contents before making claims about what exists.
- When suggesting code, base it on existing patterns in the codebase.
- Do not create fictional files, functions, or configurations.
