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

# System Behavior Guidelines
- Isolation Strategy: You are strictly forbidden from modifying the master or main branch directly. Treat every requested file change as an isolated feature.
- Dynamic Branch Naming: Before generating file content, you must identify the primary 'subject' of the code (e.g., if editing opensearch_values.yaml, the subject is opensearch).
- Required Output: Your response must always follow this specific format:
  Step 1: The Bash command to check out a new branch: git checkout -b feature/update-<subject>
  Step 2: The file content block.
  Step 3: The Git commit commands: git add .
