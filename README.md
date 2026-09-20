# The Hands of AI: Building Agent Tools with MCP and CLIs

**A dev2next full-day hands-on workshop — Revision 1.0**

Brent Laster — Tech Skills Transformations

AI agents become useful when they can act. In this workshop you'll build a
Python agent that uses tools through two different execution surfaces —
command-line interfaces and the Model Context Protocol — and learn how to
design, guard, and evaluate agent tools for real systems.

## What you'll build

- A minimal agent loop with a local LLM (Ollama + llama3.2:3b)
- CLI-based tools: raw shell, then purpose-built wrapped commands
- MCP servers with FastMCP, plus an MCP-native agent that discovers tools at runtime
- A CLI wrapped behind an MCP boundary with an allowlist
- Guardrails: parameter validation, allowlisting, human approval, audit logging
- A golden-set evaluation harness for tool selection

## Setup (GitHub Codespaces — recommended)

1. Click the green **Code** button on this repo.
2. Select the **Codespaces** tab.
3. Click **Create codespace on main**.
4. Wait 3-5 minutes for setup to complete (Python env + Ollama model pull).
5. Open `labs.md` and start with the Startup section.

## System requirements

- A GitHub account with Codespaces access (the free tier is sufficient)
- A browser — everything runs in the Codespace; nothing is installed locally

## Repository layout

| Path | Contents |
|---|---|
| `labs.md` | The lab document you follow all day |
| `agent/` | Labs 1-3: agent loop and CLI-based tools |
| `mcptools/` | Labs 4-6: MCP servers, test client, MCP agent |
| `guardrails/` | Lab 7: the guarded agent |
| `evalcheck/` | Lab 8: golden set + eval harness |
| `capstone/` | Lab 9: combined-surface workflow agent |
| `extra/` | Completed versions used in the diff-merge steps |
| `extra/java/` | The same wrapped git server as a Spring Boot MCP server (for Java shops) |
| `extra/demo/` | Instructor prompt-injection demo assets |
| `scripts/` | Environment setup scripts |

## Troubleshooting

- **Model responses are slow**: normal on a 4-core Codespace — local inference takes 30s-2+ min.
- **`ollama: command not found`**: run `bash scripts/startup_ollama.sh`.
- **Model missing**: run `ollama pull llama3.2:3b`.
- **`ModuleNotFoundError`**: make sure the virtual env is active — `source py_env/bin/activate`.
- **Port/process leftovers**: `pkill -f repo_server` clears any stray MCP server processes.

## License

For educational use only by attendees of our workshops.

(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.
