# Hands of AI
## Building AI Agents That Act: Tools via CLIs and MCP
## Full-day workshop labs
## Revision 1.4 - 09/20/26

**Startup: You need a running GitHub Codespace created from this repository (see README.md). Setup installs Python, Ollama, and the llama3.2:3b model automatically (3-5 minutes). Verify with:**

```
ollama list
python --version
```

**You should see llama3.2:3b in the model list and Python 3.10 or later. If the model is missing: `ollama pull llama3.2:3b`**

![Model and Python verified](./images/hoa-setup-1.png?raw=true "Model and Python verified")


**NOTES:**
- **Run all commands from the repository root unless a step says otherwise.**
- **Local model calls take 5-10 seconds each, so an agent run is typically 30-90 seconds — be patient. For ~1-second responses, set up a free Groq API key (README.md Setup steps 4-5): `source scripts/setup-key.sh`. Every lab uses it automatically; `source scripts/setup-key.sh --remove` switches back.**
- **The scenario all day: you're building an on-call engineer's assistant. A small inventory service in `sample_app/` has a failing nightly report. Your agent will gain the tools to investigate it — and by the end, guardrails so you can trust it to act.**
</br></br>

## Lab agenda (10 labs, ~10-12 minutes each)

| # | Lab | Focus |
|---|-----|-------|
| 1 | The Agent Loop | reason -> act -> observe, with Python-function tools |
| 2 | Tools from the Command Line | raw CLIs: grep, pytest, git, tail |
| 3 | Designing an Agent-Friendly CLI | JSON output, bounded results, honest exit codes |
| 4 | The Agent Meets the Designed CLI | the agent uses your Lab 3 tool |
| 5 | A First MCP Server | expose the same tools over MCP |
| 6 | The MCP-Powered Agent | discover tools at startup, nothing hardcoded |
| 7 | CLI vs MCP: Head-to-Head | same task, two surfaces, compared |
| 8 | Wrapping Git Behind MCP | intent-sized tools + a guarded escape hatch |
| 9 | Guardrails: Policy, Approval, Audit | allowlist, validation, human approval, audit log |
| 10 | Evaluating the Agent | scenarios with deterministic checks |

## Lab 1 - The Agent Loop (~12 minutes)

**Purpose: Build the core of every agent — a loop where the model picks a tool, we execute it, and the result feeds back in. Tools here are plain Python functions.**

1. Open the shared LLM helper all agents use. Note the four functions: `chat` (send messages), `extract_json` (pull a JSON action out of a messy reply), `observation_message` (wrap a tool result with a reminder of how to finish — small models otherwise keep calling tools after they have the answer), `which_backend` (Ollama or Groq).

```
code agents/llm.py
```
<br><br>

2. Open the Lab 1 skeleton. It has three tools (`calculator`, `read_file`, `list_files`), a `TOOLS` registry describing them, and two TODOs. It won't run yet — we merge in the working code next.

```
code agents/simple_agent.py
```
<br><br>

3. Merge in the completed code: for each highlighted block, click the arrow that copies it from the complete file (left) into the skeleton (right). Then save and close the diff tab.

```
code -d extra/simple_agent_complete.txt agents/simple_agent.py
```

![Merging the agent loop](./images/hoa1-3.png?raw=true "Merging the agent loop")
<br><br>

4. Skim what you merged: `build_system_prompt` describes the tools to the model *as text*, and the loop does ask → parse JSON → run tool → feed back the observation, until `final`.
<br><br>

5. Run it. Each `--- step` line is one tool call the model chose.

```
python agents/simple_agent.py
```

![First agent run](./images/hoa1-5.png?raw=true "First agent run")
<br><br>

6. Note three things before moving on: the model never executes anything (our code does); the model only ever sees text; and everything it knows about a tool is the description we wrote. An "unparseable reply" retry line, if you see one, is defensive engineering you just merged in.
<br><br>

7. (Optional, if time permits) Give it a task that needs a different tool:

```
python agents/simple_agent.py "Read sample_app/inventory.py and describe what total_value does"
```

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 2 - Tools from the Command Line (~12 minutes)

**Purpose: Swap the Python tools for real CLI programs — grep, pytest, git, tail. The fastest way to add power, and a first look at the mess raw output brings.**

1. Run one of the agent's future tools yourself, so you know what it will see:

```
python -m pytest sample_app -q
```

![Manual pytest output](./images/hoa2-1.png?raw=true "Manual pytest output")
<br><br>

2. One test fails — `test_total_value`. Notice how much visual noise surrounds that fact. A raw-CLI agent has to reason over all of it.
<br><br>

3. Open the skeleton. The loop at the bottom is identical to Lab 1; the TODOs are `run_command` and four thin wrappers that call it.

```
code agents/cli_agent.py
```
<br><br>

4. Merge in the completed code, save, and close the diff tab:

```
code -d extra/cli_agent_complete.txt agents/cli_agent.py
```

![Merging run_command](./images/hoa2-4.png?raw=true "Merging run_command")
<br><br>

5. Read the merged `run_command` — four jobs every CLI agent needs: capture stdout+stderr+exit code, enforce a timeout, truncate long output (`MAX_OUTPUT`), and format it for the model.
<br><br>

6. Run the agent:

```
python agents/cli_agent.py
```

![CLI agent finds the failing test](./images/hoa2-6.png?raw=true "CLI agent finds the failing test")
<br><br>

7. It should name `test_total_value` as the failing test (on the small local model, expect several extra tool calls and a muddled *why*). Look at the observations it waded through: exit codes, boilerplate, arbitrary truncation. It works — barely — and that's exactly what we design away in Lab 3.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 3 - Designing an Agent-Friendly CLI (~12 minutes)

**Purpose: Build a CLI made *for* an agent: JSON output, bounded results, meaningful errors, honest exit codes. No LLM in this lab — good tools are testable by hand.**

1. Open the skeleton. The module docstring is the design checklist. `do_tests` is complete as a worked example; `do_search`, `do_log_summary`, and `do_ticket` are TODOs.

```
code cli_tools/repo_tool.py
```
<br><br>

2. Study `do_tests`: it runs pytest and returns a small dict — passed/failed counts and failure names. The tool absorbs the mess so the model doesn't have to.
<br><br>

3. Merge in the three remaining operations, save, and close the diff tab:

```
code -d extra/repo_tool_complete.txt cli_tools/repo_tool.py
```

![Merging do_search](./images/hoa3-3.png?raw=true "Merging do_search")
<br><br>

4. Test it by hand — every response is one JSON object with an `ok` field:

```
python cli_tools/repo_tool.py tests
python cli_tools/repo_tool.py log-summary --level ERROR
```

![repo_tool tests output](./images/hoa3-4.png?raw=true "repo_tool tests output")
<br><br>

5. Now probe the error behavior, checking the exit code each time:

```
python cli_tools/repo_tool.py log-summary --level DEBUG
echo $?
python cli_tools/repo_tool.py search
echo $?
```

![Structured error vs usage error](./images/hoa3-5.png?raw=true "Structured error vs usage error")
<br><br>

6. The first is a *structured* error (exit 1): the operation ran and failed meaningfully, and the message names the valid options. The second is a *usage* error from argparse (exit 2). A program — or an agent — can tell them apart without reading English.
<br><br>

7. Open a ticket and confirm it persisted:

```
python cli_tools/repo_tool.py ticket --title "Manual test" --body "Opened by hand in Lab 3"
cat sample_app/tickets.json
```
<br><br>

8. The checklist you just implemented — clear inputs, predictable output, bounded results, useful descriptions, meaningful errors, honest exit codes — is reused verbatim for MCP tools in Lab 5.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 4 - The Agent Meets the Designed CLI (~10 minutes)

**Purpose: Give the agent your Lab 3 tool and compare what the model sees now versus Lab 2.**

1. Open the skeleton. Same loop as always — the TODOs are `run_tool` (invoke repo_tool.py, parse its JSON) and four one-line wrappers.

```
code agents/structured_agent.py
```
<br><br>

2. Merge in the completed code, save, and close the diff tab:

```
code -d extra/structured_agent_complete.txt agents/structured_agent.py
```

![Merging run_tool](./images/hoa4-2.png?raw=true "Merging run_tool")
<br><br>

3. Run it on the same task the Lab 2 agent handled:

```
python agents/structured_agent.py
```

![Structured agent run](./images/hoa4-3.png?raw=true "Structured agent run")
<br><br>

4. Compare the `observation:` lines with your Lab 2 run: compact JSON like `{"passed": 4, "failed": 1, ...}` instead of a pytest screen dump. Same model, same loop — with small models, this difference is often what makes an agent reliable instead of flaky.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 5 - A First MCP Server (~12 minutes)

**Purpose: Expose the same four capabilities through the Model Context Protocol — typed schemas and descriptions generated from your code, discoverable by any MCP client. No LLM in this lab.**

1. Open the server skeleton. It imports the Lab 3 logic unchanged — only the *surface* changes. `search_code` is already exposed as a worked example.

```
code mcp_server/repo_mcp.py
```
<br><br>

2. Note what `search_code` gets for free: `@mcp.tool()` registers it, the type hints become a JSON Schema, and the docstring becomes the description a model will read.
<br><br>

3. Merge in the other three tools, save, and close the diff tab:

```
code -d extra/repo_mcp_complete.txt mcp_server/repo_mcp.py
```

![Merging the three MCP tools](./images/hoa5-3.png?raw=true "Merging the three MCP tools")
<br><br>

4. A stdio MCP server just waits for a client, so we poke it with a tiny test client. Open it — this is the client side of MCP in ~50 lines: launch server, initialize, `list_tools`, `call_tool`.

```
code mcp_server/try_server.py
```
<br><br>

5. Run it:

```
python mcp_server/try_server.py
```

![Discovered tools and schemas](./images/hoa5-5.png?raw=true "Discovered tools and schemas")
<br><br>

6. All four tools appear with auto-generated schemas — find `"required": ["title", "body"]` on `open_ticket`; you never wrote schema code.
<br><br>

7. Where did the schema come from? Type hints. The description? Docstrings — which means docstring quality is now prompt engineering.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 6 - The MCP-Powered Agent (~12 minutes)

**Purpose: Connect the agent as a real MCP client. It discovers its tools at startup — nothing hardcoded.**

1. Open the skeleton. Two TODOs: `build_system_prompt` (build the prompt from *discovered* tools) and `call_mcp_tool` (execute one call through the session).

```
code agents/mcp_agent.py
```
<br><br>

2. Merge in the completed code, save, and close the diff tab:

```
code -d extra/mcp_agent_complete.txt agents/mcp_agent.py
```

![Merging the discovery prompt](./images/hoa6-2.png?raw=true "Merging the discovery prompt")
<br><br>

3. Before running, find these in the merged code: (a) the agent never imports the server — it only knows a script path; (b) the prompt is built from `tool.description` and `tool.input_schema`; (c) failures come back via the protocol's `is_error` flag.
<br><br>

4. Run it:

```
python agents/mcp_agent.py
```

![MCP agent run](./images/hoa6-4.png?raw=true "MCP agent run")
<br><br>

5. The first lines list the tools the agent *discovered* at startup. The run itself looks like Lab 4 — that's the point: the model's experience is similar, but the plumbing became standard and shareable.
<br><br>

6. (Optional, if time permits) The full investigation — best with Groq:

```
python agents/mcp_agent.py "Check the log for errors, run the tests, search the code, and explain the root cause of the failing nightly report."
```

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 7 - CLI vs MCP: Head-to-Head (~12 minutes)

**Purpose: Run the same task through the Lab 4 agent (CLI tools) and the Lab 6 agent (MCP tools), then compare the evidence.**

1. Open the comparison harness — provided complete, no merge. It runs both agents on one task and saves both transcripts under `transcripts/`.

```
code agents/compare_agents.py
```
<br><br>

2. Run it. This is two full agent runs, so expect a few minutes on Ollama (well under a minute on Groq).

```
python agents/compare_agents.py
```

![Comparison summary table](./images/hoa7-2.png?raw=true "Comparison summary table")
<br><br>

3. Open both transcripts (they open as two tabs — drag one tab to the right half of the editor to view them side by side):

```
code transcripts/cli_transcript.md transcripts/mcp_transcript.md
```

![CLI and MCP transcripts side by side](./images/hoa7-3.png?raw=true "CLI and MCP transcripts side by side")
<br><br>

4. With the transcripts in front of you: Did both agents pick the same tools? Which observation format is easier to skim? How much of the time difference is LLM latency (count the LLM calls)? On Groq's free tier a big wall-time gap is usually rate-limit backoff from the first run, not the surface — a useful reminder that measurements need context. We'll debrief as a group.
<br><br>

5. Probe error handling on the CLI surface — the same mistake through MCP would be rejected by schema validation *before your code runs*:

```
python cli_tools/repo_tool.py log-summary --level DEBUG
```
<br><br>

6. The takeaway framework: **CLI** when the tool exists, you're prototyping, or it's one agent on one machine. **MCP** when many clients share tools, schemas/discovery pay off, or tools evolve independently. **Wrap CLI in MCP** when the CLI is proven but you want structure on top — that's Lab 8.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 8 - Wrapping Git Behind MCP (~12 minutes)

**Purpose: Wrap a battle-tested CLI in an MCP server: intent-sized tools plus a guarded escape hatch. The wrapper adds the safety git alone doesn't have.**

1. Open the skeleton. Provided: `_git` (the one place that shells out — timeout, error capture, truncation) and `recent_commits` (a worked example that turns `git log` into structured commits). TODOs: `file_history` and `git_readonly`.

```
code mcp_server/git_mcp.py
```
<br><br>

2. Note the two wrapper styles: `recent_commits` is *intent-sized* — one question, no git flags exposed. `git_readonly` is the *escape hatch* — flexible, but allowlisted and option-free.
<br><br>

3. Merge in the completed code, save, and close the diff tab:

```
code -d extra/git_mcp_complete.txt mcp_server/git_mcp.py
```

![Merging file_history](./images/hoa8-3.png?raw=true "Merging file_history")
<br><br>

4. Point the *unchanged* Lab 6 agent at the new server — it discovers the git tools and gains new abilities with zero code changes:

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "What are the three most recent commits in this repo, and who made them?"
```

![Agent discovers and uses the git tools](./images/hoa8-4.png?raw=true "Agent discovers and uses the git tools")
<br><br>

5. Now try to make it misbehave:

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "Use the git_readonly tool to run the push subcommand and tell me exactly what comes back."
```

![Guard refusing git push](./images/hoa8-5.png?raw=true "Guard refusing git push")
<br><br>

6. The observation shows a structured refusal: `subcommand 'push' is not allowed`, naming what *is* allowed — an error the model can recover from. Note why we reject all option flags instead of blocklisting bad ones: git has flags that execute arbitrary commands. Enumerate goodness; don't chase badness.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 9 - Guardrails: Policy, Approval, Audit (~12 minutes)

**Purpose: Wrap every tool call in a policy layer — allowlist, schema validation, human approval for side effects, and an audit log. All of it outside the model.**

1. Open the policy — provided complete, deliberately boring code. Find the four control points: `ALLOWED_TOOLS`, `APPROVAL_REQUIRED`, `validate_call`, `audit`.

```
code guardrails/policy.py
```
<br><br>

2. Key idea: none of this depends on the model behaving. The model can ask for anything; only calls that pass the policy execute. Guardrails live outside the model.
<br><br>

3. Open the safe agent — the Lab 6 agent plus one TODO: `guarded_call`, the gate every tool call passes through. Merge it in, save, and close the diff tab:

```
code -d extra/safe_agent_complete.txt agents/safe_agent.py
```

![Merging the guardrail gate](./images/hoa9-3.png?raw=true "Merging the guardrail gate")
<br><br>

4. Run it. When it wants to open a ticket, it stops and asks **you** — read the proposal at the `[y/N]` prompt and answer `y`:

```
python agents/safe_agent.py
```

![Approval prompt](./images/hoa9-4.png?raw=true "Approval prompt")
<br><br>

5. Inspect the audit trail — one JSON line per decision (`session_start`, `executed`, `approved_by_human`, `session_end`):

```
cat audit_log.jsonl
```

![Audit trail](./images/hoa9-5.png?raw=true "Audit trail")
<br><br>

6. (Optional, if time permits) Run it again and answer `N` — the agent receives a DENIED observation, survives, and adjusts. Check the log for `rejected_by_human`.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

## Lab 10 - Evaluating the Agent (~12 minutes)

**Purpose: Measure the agent instead of trusting a demo: scenarios with deterministic checks, run like tests. Strongly recommended with Groq — this is three full agent runs.**

1. Open the scenarios — each is a task plus fact-based checks (answer mentions the bug, a ticket exists, step budget respected). No LLM judges.

```
code eval/scenarios.json
```
<br><br>

2. Open the harness skeleton and merge in the check implementations, save, and close the diff tab:

```
code eval/run_evals.py
code -d extra/run_evals_complete.txt eval/run_evals.py
```

![Merging the check implementations](./images/hoa10-2.png?raw=true "Merging the check implementations")
<br><br>

3. Run the suite. Approvals are automatic here (`SAFE_AGENT_AUTO_APPROVE`) so it can run unattended — itself a policy decision, visible in the audit log. On Ollama this is the longest wait of the day; with Groq it's under a minute.

```
python eval/run_evals.py
```

![Eval results](./images/hoa10-3.png?raw=true "Eval results")
<br><br>

4. Read your results. With the small local model some checks may fail — **that is the lesson**: one demo proves an agent *can* do a task; evals tell you *how often* it does. Track rates, not runs.
<br><br>

5. (Optional, if time permits) Add a fourth scenario to `eval/scenarios.json` — e.g. `find-failing-test` with `max_tool_calls: 2` — and re-run to see if your agent meets your bar.
<br><br>

6. The day in one picture: the same loop drove Python functions, raw CLIs, a designed CLI, MCP servers, and a wrapped CLI — with policy deciding what it may do and evals proving what it does. Design the tool well first; then pick the surface that fits how it will be shared, validated, and trusted.

<p align="center">
**[END OF LAB]**
</p>
</br></br>

<p align="center">
<b>For educational use only by the attendees of our workshops.</b>
</p>
<p align="center">
<b>(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.</b>
</p>
