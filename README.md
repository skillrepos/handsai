# Hands of AI — Building AI Agents That Act: Tools via CLIs and MCP

**Full-day hands-on workshop — Revision 1.3 — 09/20/26**

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/skillrepos/handsai?quickstart=1)

AI agents become useful when they can act. In this workshop you build a practical AI agent
that uses tools through two different execution surfaces — command-line interfaces and the
Model Context Protocol (MCP) — and learn when each one is the right engineering choice.

Over ten short labs (10–12 minutes each) you will:

- Build a Python agent that can reason over a task, choose a tool, execute it, and use the result
- Give the agent tools implemented as local CLI commands
- Design agent-friendly tools with clear inputs, predictable outputs, and meaningful errors
- Build an MCP server and connect your agent to it as an MCP client
- Compare the CLI and MCP approaches head-to-head on the same task
- Wrap an existing CLI (git) behind an MCP server
- Add guardrails: allowlists, parameter validation, human approval, logging, and evaluation checks

## Setup

The easiest way to run the labs is with **GitHub Codespaces**:

1. Click the **Open in GitHub Codespaces** button above (or the **Code** button → **Codespaces** tab → **Create codespace on main**).
2. Wait for the environment to build (3–5 minutes). The setup installs Python dependencies,
   installs Ollama, and pulls the `llama3.2:3b` model automatically.
3. When the terminal shows `Ollama ready with llama3.2:3b.`, you're set. Open `labs.md`
   and start with Lab 1.

## Optional: using a larger model via Groq (free)

The labs run entirely on the local `llama3.2:3b` model by default. Small models occasionally
make formatting mistakes when choosing tools — that's part of what we discuss in the workshop.
If you'd like faster and more reliable responses, you can use a **free Groq API key**:

1. Create a free account at https://console.groq.com and generate an API key.
2. In your Codespace terminal:

```
export GROQ_API_KEY=<your key>
```

Every lab program automatically uses Groq's `qwen/qwen3.8-27b` model when
`GROQ_API_KEY` is set, and the local Ollama model otherwise. That model was chosen
because it reliably follows the labs' "reply with a JSON action" convention; Groq's
`openai/gpt-oss-*` models insist on native function calling and reject it. (You can
pick a different Groq model by also setting `GROQ_MODEL`.) In a Codespace you can
store the key as a **Codespace secret** named `GROQ_API_KEY` instead of exporting it.
To switch back:

```
unset GROQ_API_KEY
```

## System requirements (local alternative)

If you prefer to run locally instead of in a Codespace, you need:

- Docker Desktop and VS Code with the Dev Containers extension (open the repo folder and
  choose "Reopen in Container"), or
- Python 3.10+, `pip install -r requirements.txt`, and Ollama installed from https://ollama.com
  with `ollama pull llama3.2:3b`

## Repository layout

| Directory | Contents |
|---|---|
| `agents/` | The agents you build: simple loop, CLI-tool agent, MCP agent, safe agent |
| `cli_tools/` | The agent-friendly CLI tool you design in Lab 3 |
| `mcp_server/` | MCP servers: repo tools server, git wrapper server, test client |
| `guardrails/` | Guardrail policy used by the safe agent in Lab 9 |
| `eval/` | Evaluation harness and scenarios for Lab 10 |
| `sample_app/` | The small application (with a bug!) that your agent investigates all day |
| `extra/` | Completed versions of lab code used in the diff-merge steps |
| `scripts/` | Environment setup scripts |
| `labs.md` | **The lab guide — start here** |

## Troubleshooting

- **Ollama responses are slow**: on a 4-core Codespace each model call takes 3–10 seconds once
  the model is loaded (an agent run is typically 30–90 seconds; the eval suite ~2 minutes). The
  very first call after a Codespace starts can take up to 2 minutes while the model loads —
  the setup scripts pre-load it and keep it in memory. For instant responses use Groq (above).
- **Agent ends with "Gave up: reached max steps"**: the model kept calling tools instead of
  answering. Every observation now carries a finish reminder (`observation_message` in
  `agents/llm.py`); if you still see this on the local model, re-run once or switch to Groq.
- **`address already in use` / stuck server**: `pkill ollama` then `bash scripts/startOllama.sh`
- **Model not found**: `ollama pull llama3.2:3b`
- **`ollama: command not found`** after setup: the Ollama installer needs `zstd`, which
  `scripts/startup_ollama.sh` now installs first. Re-run `bash scripts/startup_ollama.sh`.
- **Groq `429` / rate-limit errors**: the free tier has a small per-minute output-token
  budget; the agents cap output and retry with backoff, so a run may pause for a bit.
  Running several agents back-to-back (Labs 7 and 10) is where you'll notice it.
- **`No module named 'mcp.server.fastmcp'`**: the labs target MCP Python SDK **2.x**
  (`MCPServer`); `requirements.txt` pins `mcp>=2,<3`. Reinstall with
  `pip install -r requirements.txt`.
- **`ModuleNotFoundError`**: make sure the virtual environment is active — `source py_env/bin/activate`
  from the repo root, or open a new terminal.

## License

Materials in this repository are for educational use only by attendees of our workshops.

(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.
