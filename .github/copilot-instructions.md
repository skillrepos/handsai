# Instructions for AI assistants in this repo

When a student asks you to explain a code file in this repository, use the
"Explain this app" format below. Keep explanations student-friendly: assume
solid Python knowledge but no prior experience with agents or MCP.

## Explain-this-app format

1. **What it does** — one or two sentences describing the program's purpose in the workshop.
2. **High-level flow** — a short numbered list of what happens from start to finish.
3. **Key building blocks** — the important functions/classes and what each is responsible for.
4. **Data flow** — what goes into the LLM, what comes back, and how tool results feed the next step.
5. **Safe experiments** — two or three small changes the student can try without breaking the lab.
6. **Debug checklist** — the first things to check if it doesn't work (environment active,
   Ollama running, model pulled, correct directory, merge step completed).

## Repo-specific notes

- Skeleton files in `agents/`, `cli_tools/`, `mcp_server/`, and `eval/` are intentionally
  incomplete. The completed versions live in `extra/` as `.txt` files. Do not "fix" a skeleton
  by rewriting it — point the student to the lab's `code -d` merge step instead.
- All LLM access goes through `agents/llm.py`, which uses local Ollama by default and Groq
  when `GROQ_API_KEY` is set.
- Do not write students' lab code for them. Guide them through the steps in `labs.md`.
