# Hands of AI — Building AI Agents That Act: Tools via CLIs and MCP

**Full-day hands-on workshop — Revision 1.12 — 09/23/26**

AI agents become useful when they can act. In this workshop you build a practical AI agent
that uses tools through two different surfaces — two ways of offering a tool to an agent: command-line interfaces and the
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

![Creating new codespace from button](./images/hoa-1.png?raw=true "Creating new codespace from button")

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


## License

Materials in this repository are for educational use only by attendees of our workshops.

(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.
