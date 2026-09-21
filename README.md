# Hands of AI — Building AI Agents That Act: Tools via CLIs and MCP

**Full-day hands-on workshop — Revision 1.6 — 09/21/26**

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

These instructions will guide you through configuring a GitHub Codespaces environment
that you can use to run the course labs.

<br><br>

**1. Change your codespace's default timeout from 30 minutes to longer.**

To do this, when logged in to GitHub, go to https://github.com/settings/codespaces and
scroll down on that page until you see the *Default idle timeout* section. Adjust the
value as desired.

![Changing codespace idle timeout value](./images/hoa-setup-timeout.png?raw=true "Changing codespace idle timeout value")

<br><br>

**2. Click on the button below to start a new codespace from this repository.**

Click here ➡️  [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/skillrepos/handsai?quickstart=1)

<br><br>

**3. Then click on the option to create a new codespace.**

![Creating new codespace from button](./images/hoa-setup-create.png?raw=true "Creating new codespace from button")

This will run for several minutes while it gets everything ready.

If VS Code shows a workspace trust prompt, click **Trust Folder & Continue**.

![Trust workspace](./images/hoa-setup-trust.png?raw=true "Trust workspace")

After the initial startup, it will run a script to set up the Python environment, install
Ollama, and download the `llama3.2:3b` model. This takes several more minutes. The
codespace is ready when the terminal shows `Ollama ready with llama3.2:3b.` and a prompt.
Verify with:

```
ollama list
```

![Model and Python verified](./images/hoa-setup-1.png?raw=true "Model and Python verified")

<br><br>

**4. (Recommended) Get a free API key for Groq to use a larger, faster model.**

The labs run entirely on the local `llama3.2:3b` model by default, and everything works
that way. But local model calls take 5-10 seconds each on a codespace, and a small model
occasionally gives a muddled answer — part of what we discuss in the workshop. Groq hosts
a larger model for free (no credit card) that answers in about a second. Labs 7 and 10,
which run several agents back to back, are noticeably nicer with it.

a. In a browser, go to https://console.groq.com and create an account. (If you get an
email with a confirmation button, make sure the link opens in the same browser you used
for Groq. If not, copy the link from the "click here" section and paste it into the right
browser.)

b. In the top right of the Groq screen, click on **API Keys**

![API keys](./images/hoa-groq-1.png?raw=true "API keys")

c. Then click the **Create API Key** button.

![Create API Key](./images/hoa-groq-2.png?raw=true "Create API Key")

d. Fill in the information, verify you're human if asked, and click **Submit**.

![Create API Key](./images/hoa-groq-3.png?raw=true "Create API Key")

e. **Copy the key** (you can't view it again later).

![Copy the key](./images/hoa-groq-4.png?raw=true "Copy the key")

<br><br>

**5. Set up your Groq key in your codespace.**

Back in the codespace **TERMINAL**, run the command below to set your key for this and
all future terminals. Paste your key when prompted and hit *Enter*:

```
source scripts/setup-key.sh
```

You should see `Done! GROQ_API_KEY is set ...`. Every lab program checks that variable:
set means Groq's `qwen/qwen3.8-27b` model, unset means the local Ollama model. The
setting persists across new terminals and codespace restarts.

To confirm the key works and the labs' model is reachable, run:

```
bash scripts/check-groq.sh
```

You should see `OK    labs model  ->  qwen/qwen3.8-27b`. If it reports `FAIL` because
Groq has retired that model, the script checks replacements for you and prints the exact
`export GROQ_MODEL=...` line to run — or tells you to go back to the local model.

To switch back to the local model at any time:

```
source scripts/setup-key.sh --remove
```

*Alternative:* store the key as a **Codespace secret** named `GROQ_API_KEY`
(https://github.com/settings/codespaces) before creating the codespace; it is then set in
every terminal automatically and step 5 isn't needed.

*Daily budget:* Groq's free tier allows about **200,000 tokens per day** per key. A full run
of all ten labs fits, but re-running the longer labs many times can use it up. If that happens
you'll see `[groq: daily token budget used up - falling back to local Ollama]` and the agent
simply continues on the local model — nothing to fix, it just gets slower until the budget
resets the next day.

![Groq daily budget exhausted, run continues on Ollama](./images/hoa-groq-fallback.png?raw=true "Groq daily budget exhausted, run continues on Ollama")

<br><br>

**6. Open `labs.md` and start with Lab 1.**

Right-click `labs.md` in the Explorer and choose **Open Preview** for the rendered version.

<br><br>

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
| `scripts/` | Setup scripts: Ollama install/start, `setup-key.sh` (Groq key), `check-groq.sh` |
| `merge-info.json` | Hover notes and highlights for the Merge Info VS Code extension (installed on attach from `.devcontainer/`) |
| `labs.md` | **The lab guide — start here** |

## Troubleshooting

- **Ollama responses are slow**: on a 4-core Codespace each model call takes 3–10 seconds once
  the model is loaded (an agent run is typically 30–90 seconds; the eval suite ~2 minutes). The
  very first call after a Codespace starts can take up to 2 minutes while the model loads —
  the setup scripts pre-load it and keep it in memory. For ~1 s responses use Groq (Setup step 4).
- **Agent ends with "Gave up: reached max steps"**: the model kept calling tools instead of
  answering. Every observation now carries a finish reminder (`observation_message` in
  `agents/llm.py`); if you still see this on the local model, re-run once or switch to Groq.
- **Groq key not picked up in a new terminal**: run `source scripts/setup-key.sh` again — it
  writes the key to `~/.bashrc` so every new terminal has it. `echo $GROQ_API_KEY` to check.
- **`address already in use` / stuck server**: `pkill ollama` then `bash scripts/startOllama.sh`
- **Model not found**: `ollama pull llama3.2:3b`
- **`ollama: command not found`** after setup: the Ollama installer needs `zstd`, which
  `scripts/startup_ollama.sh` now installs first. Re-run `bash scripts/startup_ollama.sh`.
- **Groq `429` / rate-limit errors**: the free tier has a small per-minute output-token
  budget; the agents cap output and retry with backoff, so a run may pause for a bit.
  Running several agents back-to-back (Labs 7 and 10) is where you'll notice it.
- **`[groq: daily token budget used up - falling back to local Ollama]`**: the key's
  200,000-tokens-per-day allowance is spent. The run finishes on Ollama automatically and
  every later run in that process does the same; new runs try Groq again (and fall back again)
  until the budget resets. To stop the retries, `source scripts/setup-key.sh --remove` for the day.
- **`No module named 'mcp.server.fastmcp'`**: the labs target MCP Python SDK **2.x**
  (`MCPServer`); `requirements.txt` pins `mcp>=2,<3`. Reinstall with
  `pip install -r requirements.txt`.
- **No hover popups / yellow or blue highlights in the editor**: the Merge Info extension installs
  in the background when the codespace attaches. Check `cat /tmp/merge-info-install.log`, or install
  it by hand: `code --install-extension .devcontainer/merge-info-0.3.1.vsix --force`, then reload the
  window. Toggle the highlights with the *Merge Info: Toggle ...* commands in the palette.
- **`ModuleNotFoundError`**: make sure the virtual environment is active — `source py_env/bin/activate`
  from the repo root, or open a new terminal.

## License

Materials in this repository are for educational use only by attendees of our workshops.

(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.
