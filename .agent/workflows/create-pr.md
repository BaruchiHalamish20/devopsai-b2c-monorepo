---
description: Drafts a detailed Pull Request description and runs 'gh pr create'.
---
Your task is to:
1. Generate a descriptive title and body for a new GitHub Pull Request.
   - The user's input/context is: {{args}}
   - Use the current Git branch name for context.
   - The body should include sections for:
     - **Summary of Changes**
     - **Related Issue(s)** (if provided in {{args}})
     - **Testing Notes**
2. Format the output as a clean Markdown string.
3. Once the description is generated, use the 'gh pr create' tool to submit it. 
   - Use the generated title and body for the 'gh pr create' command.

Draft the content for the PR title and body first, then provide the final shell command.
