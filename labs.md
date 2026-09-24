# Hands of AI
## Building AI Agents That Act: Tools via CLIs and MCP
## Workshop labs
## Revision 1.18 - 09/23/26

**Startup: You need a running GitHub Codespace created from this repository (see README.md). Setup installs Python, Ollama, and the llama3.2:3b model automatically (3-5 minutes). Verify with:**

```
ollama list
python --version
```

**You should see llama3.2:3b in the model list and Python 3.10 or later. If the model is missing: `ollama pull llama3.2:3b`**

![Model and Python verified](./images/hoa-setup-1.png?raw=true "Model and Python verified")


**NOTES:**
- **Run all commands from the repository root.**
- **A local model call takes 5-10 seconds, so an agent run takes 30-90 seconds. For ~1-second responses, use a free Groq API key (README.md Setup steps 4-5): `source scripts/setup-key.sh`. Every lab then uses it automatically; `source scripts/setup-key.sh --remove` switches back. The local model often takes extra or wrong steps before it gets to the answer; that is expected.**
- **Some steps are supposed to fail (a failing test, an error, a refusal). Each of those has an `Expected output` note. Any other step should run clean.**
- **Terms are listed in [Appendix A](#appendix-a); the repo layout is in [Appendix B](#appendix-b).**
</br></br>

**Assembling Code**

> We build code with "diff and merge": the finished code from `extra/` is on the left, your starter file is on the right. Click the arrow on each highlighted block to copy it across. Hover the yellow comment icon in the left gutter for a note on what the block does. When all merges are done, save and close the diff tab.
>
> Outside the diff view, **yellow** highlights mark where merged code will land, and **blue** highlights mark the parts of a file a step asks you to read. Hover any highlight for its explanation.
> <br><br>

![merge info](./images/merge-info3.png?raw=true "merge info")

</br></br>

## The labs

You are building an **on-call engineer's assistant** for a small inventory service (`inventory_service/`). Its nightly report has been failing since 9:16 this morning. Each lab gives the assistant one more capability.

| # | Lab | What the assistant gains |
|---|-----|-------|
| 1 | [The Agent Loop](#lab1) | reads the log and checks the math |
| 2 | [Tools from the Command Line](#lab2) | runs pytest and finds the failing test |
| 3 | [Designing an Agent-Friendly CLI](#lab3) | a CLI built for an agent to read (no LLM in this lab) |
| 4 | [The Agent Uses the Designed CLI](#lab4) | uses that CLI, and opens its first ticket |
| 5 | [A First MCP Server](#lab5) | the same tools published over MCP (no LLM in this lab) |
| 6 | [The MCP-Powered Agent](#lab6) | finds its tools at startup instead of having them written in |
| 7 | [CLI vs MCP: Head-to-Head](#lab7) | the two measured on the same task |
| 8 | [Wrapping Git Behind MCP](#lab8) | git access with safety rules |
| 9 | [Guardrails: Policy, Approval, Audit](#lab9) | an allowlist, human approval, an audit log |
| 10 | [Evaluating the Agent](#lab10) | repeatable pass/fail checks |

</br></br>

<a id="lab1"></a>
## Lab 1 - The Agent Loop (~12 minutes)

**Purpose: Build the loop at the center of every agent — the model picks a tool, our code runs it, the result goes back to the model — and use it to answer the first on-call question.**

**The situation:** The application log shows a `total_value mismatch`: the ledger expected 149.95, the service returned 39.99. A person would read the log and do the arithmetic to see which is right. We'll build an agent that does the same.

1. Look at the evidence first, so you can judge the agent's answer. Lines 3-4 add stock (5 widgets at 19.99, 10 gadgets at 5.00); line 6 is the mismatch:

```
head -8 inventory_service/logs/app.log
```

![The log the agent will read](./images/hoa1-1.png?raw=true "The log the agent will read")

<br><br>

2. Open the skeleton. The three tools are plain Python functions (`calculator`, `read_file`, `list_files`). The `TOOLS` registry (blue) describes each tool in one sentence, and that sentence is all the model ever knows about it. The two TODOs (yellow) are where code will land; scroll down to line 56 to see both. (The model connection every agent uses is in `agents/llm.py`.)

```
code agents/simple_agent.py
```

![Blue TOOLS registry and yellow TODO](./images/hoa1-2.png?raw=true "Blue TOOLS registry and yellow TODO")

<br><br>

3. Merge in the completed code, then save and close the diff tab:

```
code -d extra/simple_agent_complete.txt agents/simple_agent.py
```

| What you're merging | Why |
|---|---|
| **`build_system_prompt`** — turns each `TOOLS` entry into a line of text and tells the model it may reply only with `{"tool": ..., "args": ...}` or `{"final": ...}`. | This text is all the model learns about your tools. If an agent misuses a tool, look here first. |
| **The loop** — ask the model, parse its JSON, run the tool it chose, send the result back, repeat. A reply that isn't JSON gets a retry request. | This is the agent. Every later lab reuses this loop with different tools. |

![Merging the agent loop](./images/hoa1-3.png?raw=true "Merging the agent loop")

<br><br>

4. Run it:

```
python agents/simple_agent.py
```

![First agent run](./images/hoa1-5.png?raw=true "First agent run")

<br><br>

5. Read the transcript. Each `--- step N: tool(args)` line is a choice the model made. The `observation:` line under it shows the first 200 characters of what our code returned; the model gets the full text. Expect `read_file` on the log, `calculator` on `5*19.99 + 10*5.00` (= 149.95), and a final answer saying the ledger is right.

<br><br>

6. Ask about the code instead. Only the question changes, and the model picks a different tool:

```
python agents/simple_agent.py "Read inventory_service/inventory.py and tell me whether total_value looks correct."
```

![The agent reads the code and spots the bug](./images/hoa1-8.png?raw=true "The agent reads the code and spots the bug")

The `observation:` stops at `class InventoryError(Exception):`. That is the 200-character display limit, not an error.

<br><br>

7. **What just happened.** The model chose the tools and interpreted the results; our code did all the running. Everything the agent can *do* is a function we wrote, and everything it *knows* about those functions is the text in `TOOLS`, so tool descriptions need the same care as code. The agent found the bug: `total_value` adds price and quantity instead of multiplying them.

![The loop you just built](./diagrams/agent-loop.png?raw=true "The loop you just built")

*The full loop, including two exits the transcript doesn't show: a reply that isn't JSON goes back for a retry, and the step budget stops a run that never finishes. Other diagrams are in [`diagrams/`](./diagrams/README.md).*

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab2"></a>
## Lab 2 - Tools from the Command Line (~9 minutes)

**Purpose: Give the agent tools engineers already use — pytest, grep, git, tail — unchanged, and see what raw terminal output costs the model.**

**The situation:** Before anyone changes code, the on-call engineer asks: do the tests catch this, and which one fails? Programs that answer that already exist.

1. Run the test suite yourself. In step 3 this exact command becomes the agent's `run_tests` tool, so this is the text the model will read:

```
python -m pytest inventory_service -q
```

> **Expected output: one test fails. That is the bug, not a problem with your setup.** You'll see `FAILED`, an `AssertionError`, and `1 failed, 4 passed`. `test_total_value` expects 149.95 and gets 39.99, the same mismatch the log showed in Lab 1.

![Manual pytest output](./images/hoa2-1.png?raw=true "Manual pytest output")

<br><br>

2. Look at how much of that output is formatted for a person at a terminal: banners, a progress counter, a source excerpt, a traceback. The one fact that matters is the name of the failing test, and the agent has to find it inside all of that.

<br><br>

3. Merge in the completed code, then save and close the diff tab. The loop is the Lab 1 loop; what's new is `run_command` and four one-line tool wrappers:

```
code -d extra/cli_agent_complete.txt agents/cli_agent.py
```

| What you're merging | Why |
|---|---|
| **`run_command`** — runs a program and returns its stdout, stderr and exit code as text. Stops after 120 seconds and cuts output at `MAX_OUTPUT` characters. | The only place this agent touches the system. The timeout keeps a hung command from freezing the agent; the cap keeps a noisy one from filling the model's context. |
| **Four wrappers** (`grep_code`, `run_tests`, `git_history`, `tail_log`) — one line each, passing `grep`, `pytest`, `git log` and `tail` to `run_command`. | Four real tools for four lines of code. Each returns whatever its program prints, in that program's format. |

![Merging run_command](./images/hoa2-4.png?raw=true "Merging run_command")

<br><br>

4. Run the agent:

```
python agents/cli_agent.py
```

> **Expected output:** `observation:` lines containing pytest's failure text and `exit code: 1`. The non-zero exit code comes from the failing test the agent was sent to find.

![CLI agent finds the failing test (end of the run)](./images/hoa2-6.png?raw=true "CLI agent finds the failing test (end of the run)")

<br><br>

5. Read the transcript (scroll up for the start). The answer should name `test_total_value`. Look at how much text the model had to read in each `observation:` line to find it.

<br><br>

6. Ask a question that needs a different tool:

```
python agents/cli_agent.py "Show the last 10 lines of the application log and tell me whether the problem is still happening."
```

![The agent picks tail for a log question](./images/hoa2-8.png?raw=true "The agent picks tail for a log question")

<br><br>

7. **What just happened.** Four lines of wrapper code gave the agent four proven programs, which is why CLIs are the fastest way to make an agent capable. The cost: every observation is formatted for a person, the exit code is the only structure, and output is cut at an arbitrary point. Lab 3 fixes the tool, not the model.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab3"></a>
## Lab 3 - Designing an Agent-Friendly CLI (~12 minutes)

**Purpose: Build a CLI designed for an agent — JSON answers, capped output, clear error messages, meaningful exit codes — and test it by hand. No LLM in this lab.**

**The situation:** The investigation keeps needing four things: search the code, run the tests, summarize the log, open a ticket. We put them in one program, `repo_tool.py`, with a subcommand for each, and design every response for a model to read.

**`repo_tool.py` supplies the agent's tools for the rest of the workshop.** You build it once, here, and never rewrite it. Lab 4 runs it as a command; from Lab 5 on, an MCP server publishes the same four functions.

1. Open the skeleton. The docstring at the top (blue) is the design checklist. `do_tests` (blue) is finished: it runs the same pytest as Lab 2 but returns a small dict of passed and failed counts plus failure names. The three TODOs follow the same pattern.

```
code cli_tools/repo_tool.py
```

![Blue design checklist and yellow TODO](./images/hoa3-1.png?raw=true "Blue design checklist and yellow TODO")

<br><br>

2. Merge in the three remaining operations, then save and close the diff tab:

```
code -d extra/repo_tool_complete.txt cli_tools/repo_tool.py
```

| What you're merging | Why |
|---|---|
| **`do_search`** — returns matches as JSON (file, line, text). Rejects a bad regex with a message; `max_results` caps the count and sets `truncated` when results were cut. | Lab 2 cut output silently, so the model couldn't tell a short answer from a clipped one. `truncated` tells it. |
| **`do_log_summary`** — counts log lines per level and returns the last five messages for the level requested. Any level other than INFO, WARNING or ERROR is refused with the valid list. | An error that names the valid options is one the model can correct by itself. |
| **`do_ticket`** — adds a ticket to `tickets.json` and returns its id. Title and body lengths are capped. | The one operation that changes something. Lab 9 puts it behind human approval. |

![Merging do_search](./images/hoa3-3.png?raw=true "Merging do_search")

<br><br>

3. Run two subcommands, and compare the `tests` output with Lab 2's pytest screen:

```
python cli_tools/repo_tool.py tests
python cli_tools/repo_tool.py log-summary --level ERROR
```

> **Expected output:** `"ok": true` alongside `"failed": 1`. `ok` says the *tool* worked; `failed` reports the *tests*. That is why the exit code is 0 even though a test failed.

![repo_tool tests output](./images/hoa3-4.png?raw=true "repo_tool tests output")

<br><br>

4. Check the error behavior. **Both commands below are supposed to fail:**

```
python cli_tools/repo_tool.py log-summary --level DEBUG
echo $?
python cli_tools/repo_tool.py search
echo $?
```

> **Expected output:** The first prints JSON with `"ok": false` and a message listing the valid levels, and exit code `1`: the command ran and failed for a stated reason. The second prints argparse's usage text and exit code `2`: the command was called wrong. A program can tell the two cases apart from the exit code alone.

![Structured error vs usage error](./images/hoa3-5.png?raw=true "Structured error vs usage error")

<br><br>

5. Use the tool to track down the bug, the same way the agent will. Step 3 reported `test_total_value` as the failing test, so search for the function it tests, then for the line inside it that builds the total:

```
python cli_tools/repo_tool.py search --pattern "total_value"
python cli_tools/repo_tool.py search --pattern "total \+="
```

> **Expected output:** The first search finds `def total_value` in `inventory.py` and the failing test in `test_inventory.py`. The second finds the one line that adds to the total: `total += item["price"] + item["quantity"]`. The docstring of `total_value` says the total is price *times* quantity, so the `+` between them is the bug.

![search narrows down to the buggy line](./images/hoa3-7.png?raw=true "search narrows down to the buggy line")

<br><br>

6. Open a ticket:

```
python cli_tools/repo_tool.py ticket --title "Manual test" --body "Opened by hand in Lab 3"
```

> **Expected output:** `"ok": true` and the new ticket, including the id the tool assigned (`TICKET-0001` if this is your first ticket). This is the tool's *reply*, the part the agent will read.

<br><br>

7. Confirm the ticket was saved to the ticket store:

```
cat inventory_service/tickets.json
```

> **Expected output:** a JSON list holding the same ticket. Step 6 showed what the tool *said* it did; this shows what it actually wrote.

<br><br>

8. **What just happened.** The capabilities are the same as Lab 2; the design changed for the reader. JSON output, a size cap, errors that explain themselves, exit codes that tell the truth: this checklist is the main thing to take from the workshop. In Lab 4 the agent runs `repo_tool.py` in place of Lab 2's raw programs.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab4"></a>
## Lab 4 - The Agent Uses the Designed CLI (~8 minutes)

**Purpose: Give the agent `repo_tool.py` from Lab 3 in place of Lab 2's raw programs, repeat Lab 2's run — same model, same loop, same question — and compare. Then have the agent open a ticket.**

1. Merge in the completed code, then save and close the diff tab. The loop is unchanged; the TODOs are `run_tool` and one wrapper per subcommand:

```
code -d extra/structured_agent_complete.txt agents/structured_agent.py
```

| What you're merging | Why |
|---|---|
| **`run_tool`** — runs `repo_tool.py` and parses its output as JSON. Output that isn't JSON becomes a structured error. | Lab 2's `run_command` passed raw text through. This can parse JSON because Lab 3 guarantees it. |
| **Four wrappers** (`search_code`, `run_tests`, `summarize_log`, `open_ticket`) — one line each, passing the model's arguments to `repo_tool.py`. | There is nothing left to clean up, because the CLI already returns clean data. |

![Merging run_tool](./images/hoa4-2.png?raw=true "Merging run_tool")

<br><br>

2. Run it on Lab 2's question:

```
python agents/structured_agent.py
```

![Structured agent run](./images/hoa4-3.png?raw=true "Structured agent run")

<br><br>

3. Compare with your Lab 2 run. The `observation:` lines are now short JSON such as `{"ok": true, "passed": 4, "failed": 1, "failures": [...]}` instead of pytest screens. The model may still search a few times, but each result is a fact it can use directly. With small models, that is often the difference between flaky and reliable.

<br><br>

4. Give it a task that ends in an action. It needs two tools it hasn't been told to combine:

```
python agents/structured_agent.py "Summarize the ERROR lines in the application log, then open a ticket titled 'Nightly report failing' that describes the problem."
```

![The agent summarizes the log and opens a ticket](./images/hoa4-5.png?raw=true "The agent summarizes the log and opens a ticket")

<br><br>

5. Confirm the ticket was saved:

```
cat inventory_service/tickets.json
```

<br><br>

6. **What just happened.** The model didn't change between Lab 2 and Lab 4; the tool did, and the agent became more reliable. Reliability depends heavily on tool design. Note also that in step 4 the agent wrote to the ticket store because a sentence asked it to, with no one approving it. Lab 9 deals with that.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab5"></a>
## Lab 5 - A First MCP Server (~10 minutes)

**Purpose: Publish `repo_tool.py`'s four functions through an MCP server, so any MCP client can discover and call them. No LLM in this lab.**

**The situation:** `repo_tool.py` works for one agent that knows how to start it. Other teams want the same tools in an IDE, a chat client and a CI bot. MCP is the standard way to publish tools so that clients you didn't write can use them. We don't rewrite anything: the server is a second way to reach the same code, and `repo_tool.py` keeps working as a command.

1. Open the server skeleton. Line 23 imports `do_search`, `do_tests`, `do_log_summary` and `do_ticket` from `cli_tools/repo_tool.py` unchanged; only the way they are offered changes. `search_code` (blue) is the finished example: `@mcp.tool()` registers it, its type hints become its JSON schema, and its docstring becomes the description the model reads.

```
code mcp_server/repo_mcp.py
```

![Blue worked example and yellow TODO](./images/hoa5-1.png?raw=true "Blue worked example and yellow TODO")

<br><br>

2. Merge in the other three tools, then save and close the diff tab:

```
code -d extra/repo_mcp_complete.txt mcp_server/repo_mcp.py
```

| What you're merging | Why |
|---|---|
| **`run_tests`, `summarize_log`, `open_ticket`** — each exposed like `search_code`, with a one-line body that calls the matching `repo_tool.py` function. | Publishing a tool over MCP is mostly a matter of describing it accurately. The type hints and docstring do the rest. |

![Merging the three MCP tools](./images/hoa5-3.png?raw=true "Merging the three MCP tools")

<br><br>

3. Open the test client. The server communicates over stdio, so it does nothing until a client starts it. The client's four stages are in blue: start the server as a subprocess, `discover` (ask which versions of MCP the server supports), `list_tools`, `call_tool`.

```
code mcp_server/try_server.py
```

![The four client stages in blue](./images/hoa5-4.png?raw=true "The four client stages in blue")

<br><br>

4. Run the client against your server:

```
python mcp_server/try_server.py
```

![Discovered tools and schemas](./images/hoa5-5.png?raw=true "Discovered tools and schemas")

<br><br>

5. Read the output from top to bottom. The client did two things: it asked the server which tools it has, then it called one of them.

| Look at | What it tells you |
|---|---|
| **`Protocol version: 2026-07-28`** | Client and server agreed on the 2026-07-28 version of MCP. There was no opening handshake and no session: every later request carries the version and the client's details with it, so any running copy of a server can answer any request. |
| **The four `*` entries** (`search_code`, `run_tests`, `summarize_log`, `open_ticket`) | The server reported its own tools. The client had no list of them in advance. |
| **`description:`** under each tool | The first line of that function's docstring. The model reads the full docstring to decide when to use the tool. |
| **`input schema:`** under `open_ticket` | A description of the arguments the tool accepts, built from the Python line `def open_ticket(title: str, body: str)`. `"type": "string"` comes from `str`. `"required": ["title", "body"]` is there because neither argument has a default value. You didn't write any of it. |
| **`input schema:`** under `search_code` | `max_results` has `"default": 20` and is not in `required`, because the Python parameter has a default (`max_results: int = 20`). |
| **The last line**, under `=== Calling search_code ===` | The client called `search_code` with the pattern `total_value`. The reply is the same JSON that `repo_tool.py search --pattern "total_value"` gave you in Lab 3, because both run the same `do_search` function. |

![open_ticket's generated schema and the search_code result](./images/hoa5-6.png?raw=true "open_ticket's generated schema and the search_code result")

Why the schema matters: the MCP layer checks every call against it before your function runs. A call that leaves out `body`, or sends a number where text belongs, is turned away without reaching your code. You'll see this happen in Lab 7.

<br><br>

6. Point the same client at a different server, Lab 8's git server, which is still a skeleton:

```
python mcp_server/try_server.py mcp_server/git_mcp.py
```

> **Expected output:** all three git tools listed, although two are unfinished until Lab 8. Their names and type hints already exist, so they can be discovered. The call goes to `recent_commits`, which is complete, so real commits come back.

![Same client, different server](./images/hoa5-8.png?raw=true "Same client, different server")

<br><br>

7. **What just happened.** You published tools without writing an API: MCP turned your functions into a typed list that any client can discover, and one small client can use any server. CLIs don't give you that kind of sharing. The tools are still good because of the Lab 3 checklist; MCP makes them portable. There is now one set of tool code, `repo_tool.py`, with two ways in: the command line (Lab 4) and MCP (this server).

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab6"></a>
## Lab 6 - The MCP-Powered Agent (~9 minutes)

**Purpose: Make the agent an MCP client that discovers its tools at startup, with nothing hardcoded, and run the full investigation through MCP.**

**The situation:** The agent should know nothing about the server in advance: no import, no tool list. If that works, it can use any server, which Labs 7, 8 and 9 rely on. Its tools are still `repo_tool.py`'s four functions, now reached through `repo_mcp.py` instead of the command line.

1. Merge in the completed code, then save and close the diff tab. The two TODOs are `build_system_prompt` and `call_mcp_tool`:

```
code -d extra/mcp_agent_complete.txt agents/mcp_agent.py
```

| What you're merging | Why |
|---|---|
| **`build_system_prompt`** — builds the prompt from each discovered tool's `description` and `input_schema`, as returned by `list_tools`. | In Lab 1 the prompt came from a hardcoded registry. Now a tool added to the server shows up in the prompt on the next run, with no code change. |
| **`call_mcp_tool`** — runs one call through the MCP session and returns the text. Failures (the protocol's `isError` flag, or an exception) come back as `TOOL ERROR` text. | The model will make bad calls. Returning the failure as text lets it correct itself instead of ending the run. |

![Merging the discovery prompt](./images/hoa6-2.png?raw=true "Merging the discovery prompt")

![What happens over stdio](./diagrams/mcp-stdio-sequence.png?raw=true "What happens over stdio")

*The agent starts the server, asks which tools exist, builds its prompt from the answer, then runs the Lab 1 loop with `call_tool` in place of a Python function call.*

<br><br>

2. Run it on Lab 4's question:

```
python agents/mcp_agent.py
```

![MCP agent run](./images/hoa6-4.png?raw=true "MCP agent run")

<br><br>

3. The first lines list the tools the agent discovered. After that the run looks like Lab 4: the model sees the same tools, now delivered through a standard protocol.

<br><br>

4. Now the whole investigation in one task: log, tests, code search, then an explanation:

```
python agents/mcp_agent.py "Check the log for errors, run the tests, search the code, and explain the root cause of the failing nightly report."
```

![The full investigation](./images/hoa6-6.png?raw=true "The full investigation")

<br><br>

5. Check the answer against what you know: the log's mismatch, the failing `test_total_value`, and the line in `total_value` (`inventory.py`) where price and quantity are added instead of multiplied.

<br><br>

6. **What just happened.** The agent found the root cause using tools it discovered at startup, from a server it never imported. Point it at another server and it gains new tools with no code change, which you'll do in Lab 8.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab7"></a>
## Lab 7 - CLI vs MCP: Head-to-Head (~12 minutes)

**Purpose: Run one task through the Lab 4 agent (reaches `repo_tool.py` as a command) and the Lab 6 agent (reaches it through MCP), then compare the transcripts, the token cost and the error handling.**

**The situation:** The agent now has two ways to reach the same `repo_tool.py` code: as a command (Lab 4) and through MCP (Lab 6). Which should a team standardize on? That depends on what you measure.

1. Open the comparison script (complete, no merge). The blue highlights show its three jobs: run both agents on one task, count tool calls, tokens and time, save both transcripts to `transcripts/` (scroll down to see them). A **token** is the unit a model reads and bills by: roughly four characters of English text.

```
code agents/compare_agents.py
```

![The comparison script with its three jobs in blue](./images/hoa7-1.png?raw=true "The comparison script with its three jobs in blue")

<br><br>

2. Run it. It makes two agent runs back to back: about 90 seconds on Ollama, under a minute on Groq:

```
python agents/compare_agents.py
```

![Comparison summary table](./images/hoa7-2.png?raw=true "Comparison summary table")

<br><br>

3. Open both transcripts, then drag one tab to the right half of the editor to see them side by side:

```
code transcripts/cli_transcript.md transcripts/mcp_transcript.md
```

![CLI and MCP transcripts side by side](./images/hoa7-3.png?raw=true "CLI and MCP transcripts side by side")

<br><br>

4. Compare: Did both agents call the same tools in the same order? Which observations are easier to read? Did both reach the same root cause? In the table, time mostly follows the number of steps. If the step counts match but the times don't, the usual cause is Groq rate limiting or Ollama loading the model on the first run.

| Column | What it counts |
|---|---|
| **tool calls** | Tools the agent ran. |
| **model calls** | Times the agent asked the model for its next action: one per tool call, plus the final answer and any retries. |
| **prompt tokens** | Everything sent to the model, added up over the run, as reported by the model API. The whole conversation, tool list included, is re-sent on every call, so this grows faster than the step count. |

<br><br>

5. For the same number of steps, the MCP agent usually sends more prompt tokens. This script shows why: it builds each agent's system prompt (the part re-sent on every call) without calling a model:

```
python agents/measure_prompt.py
```

![The system prompt each agent sends, measured](./images/hoa7-5.png?raw=true "The system prompt each agent sends, measured")

| Row | What it shows |
|---|---|
| **bare shell (run_command)** | One tool that runs any command line. The model already knows `git`, `grep` and `pytest`, so one line is enough: the cheapest option, and the riskiest, since that tool can run anything. |
| **Lab 4 CLI agent** | Four tools, each described in one line that you wrote. |
| **Lab 6 MCP agent** | The same four tools, each with the full input schema the server published: more to check arguments against, and more tokens. |
| **x 8 calls** | The same prompt sent on every call of an 8-step run. |

<br><br>

6. Now connect the MCP agent's prompt to both servers, as an agent that uses the repo tools and the git tools together would be:

```
python agents/measure_prompt.py mcp_server/repo_mcp.py mcp_server/git_mcp.py
```

> **Expected output:** 7 tools, and the MCP prompt about two-thirds larger. Every connected server adds its whole tool list to every call, used or not. With dozens of servers that is tens of thousands of tokens per call, which is why MCP clients now load tool descriptions only when needed.

![Two servers: the MCP prompt grows](./images/hoa7-6.png?raw=true "Two servers: the MCP prompt grows")

<br><br>

7. Now error handling. In Lab 3 step 4, `repo_tool.py`'s own code caught `--level DEBUG`. Make the same kind of mistake through MCP (a wrong *type*) and see where it's caught:

```
python agents/mcp_agent.py "Call search_code with pattern total_value and max_results set to the string 'ten' exactly as written - do not convert it to a number. Then tell me exactly what came back."
```

> **Expected output:** a `TOOL ERROR` saying `max_results` must be a valid integer. The schema rejected the call before your Python ran; in Lab 3 your own code had to catch the bad value. The local model may then retry with `10`, which succeeds.

![Schema validation rejects the call](./images/hoa7-7.png?raw=true "Schema validation rejects the call")

<br><br>

8. **What just happened.** The model behaved almost the same with both, because the tools were designed the same way. The differences are in what surrounds the tool: MCP's schemas cost tokens on every call but catch bad arguments before your code runs, and the cost grows with every server you connect. When to pick each:
- **CLI:** the tool already exists, you're prototyping, or it's one agent on one machine.
- **MCP:** many clients share the tools, schemas and discovery matter, or tools change independently.
- **CLI wrapped in MCP:** the CLI is proven, but you want structure and safety on top (Lab 8).

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab8"></a>
## Lab 8 - Wrapping Git Behind MCP (~11 minutes)

**Purpose: Put git behind an MCP server with two kinds of tool: narrow ones that each answer one question, and one general tool restricted by rules.**

**The situation:** The investigation needs history: who changed `total_value`, and when? git knows. But git can also push, reset and write files through its options, so an agent that can run any git command is dangerous. The wrapper supplies the safety.

1. Open the skeleton. Provided (blue): the allowlist of read-only subcommands; `_git`, which runs git with a timeout, error capture and truncation as in Lab 2; and `recent_commits`, a finished example that returns `git log` as structured data. The TODOs are `file_history` and `git_readonly`.

```
code mcp_server/git_mcp.py
```

![Blue allowlist, _git and recent_commits](./images/hoa8-1.png?raw=true "Blue allowlist, _git and recent_commits")

<br><br>

2. Merge in the completed code, then save and close the diff tab:

```
code -d extra/git_mcp_complete.txt mcp_server/git_mcp.py
```

| What you're merging | Why |
|---|---|
| **`file_history`** — the commits that touched one file. Rejects a path that starts with `-` or points outside the repo, and puts `--` before the path so git never reads it as an option. | The narrow kind: one question, no git options exposed, nothing to misuse. The path checks exist because a model supplies the argument. |
| **`git_readonly`** — runs any subcommand on the allowlist, and rejects every argument that starts with `-`. | The general kind, for questions nobody anticipated. It lists what is safe instead of trying to list every dangerous option, a list you could never finish. |

![Merging file_history](./images/hoa8-3.png?raw=true "Merging file_history")

<br><br>

3. Point the unchanged Lab 6 agent at the git server:

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "What are the three most recent commits in this repo, and who made them?"
```

![Agent discovers and uses the git tools](./images/hoa8-4.png?raw=true "Agent discovers and uses the git tools")

<br><br>

4. Try to make it push:

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "Use the git_readonly tool to run the push subcommand and tell me exactly what comes back."
```

> **Expected output:** a refusal, with no push and no crash: something like `subcommand 'push' is not allowed`, followed by the allowed list. The model can act on that; it couldn't act on a stack trace. The local model may leave out `subcommand` here and get schema errors instead (as in step 5); with Groq the refusal shows every time.

![Guard refusing git push](./images/hoa8-5.png?raw=true "Guard refusing git push")

<br><br>

5. Try an allowed subcommand with a dangerous option (`--output` writes a file):

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "Use git_readonly to run the log subcommand with the argument --output=/tmp/pwned and tell me exactly what comes back."
```

> **Expected output:** another refusal. `log` is on the allowlist; the no-options rule stopped the call because the argument starts with `-`. The local model often can't build this call (it leaves out `subcommand`) and gets schema errors instead; with Groq the refusal shows every time.

![Guard refusing an option flag](./images/hoa8-7.png?raw=true "Guard refusing an option flag")

<br><br>

6. **What just happened.** The agent gained git with no code changes, because it discovers its tools. All the safety is in the wrapper: an allowlist of subcommands, no options, and refusals the model can read. Listing what is allowed works; listing everything that is dangerous doesn't. Lab 9 applies the same idea to every tool call.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab9"></a>
## Lab 9 - Guardrails: Policy, Approval, Audit (~11 minutes)

**Purpose: Put every tool call through a policy check — an allowlist, argument validation, human approval for anything that changes something, and a log of each decision — all in code, outside the model.**

**The situation:** In Lab 4 the agent opened a ticket because a sentence asked it to. For a tool like "restart the service", that isn't acceptable. The agent keeps the same tools (`repo_tool.py`'s functions, through `repo_mcp.py`), and a human decides on anything with consequences.

1. Open the policy (complete). The four controls are in blue: `ALLOWED_TOOLS`, `APPROVAL_REQUIRED`, `validate_call` (checks arguments against the tool's schema), and `audit` (writes one JSON line per decision). None of it depends on the model behaving.

```
code guardrails/policy.py
```

![Blue policy control points](./images/hoa9-1.png?raw=true "Blue policy control points")

![Every branch one tool call can take](./diagrams/guardrail-decision-path.png?raw=true "Every branch one tool call can take")

*Every path a tool call can take, and the audit line each one writes. `guarded_call`, merged next, is the middle of this picture.*

<br><br>

2. `safe_agent.py` is the Lab 6 agent plus one function, `guarded_call`. Merge it in, then save and close the diff tab:

```
code -d extra/safe_agent_complete.txt agents/safe_agent.py
```

| What you're merging | Why |
|---|---|
| **`guarded_call`** — checks the call against policy and schema, asks you if the tool has side effects, then runs it and records the result in `audit_log.jsonl`. A refusal at any point returns a `DENIED` observation. | Every control is in this one function. `DENIED` comes back as an observation, not an exception, so the agent can adjust instead of crashing. |

![Merging the guardrail gate](./images/hoa9-3.png?raw=true "Merging the guardrail gate")

<br><br>

3. Run it. The task asks for the root cause and a ticket:

```
python agents/safe_agent.py
```

> **Expected output:** the run pauses at a `[y/N]` prompt. It isn't hung: the agent wants to open a ticket, and policy requires your approval. Read the proposal, type `y`, and press Enter.

![Approval prompt](./images/hoa9-4.png?raw=true "Approval prompt")

<br><br>

4. Read the audit trail, one line per decision (`session_start`, `executed`, `approved_by_human`, `session_end`):

```
cat audit_log.jsonl
```

![Audit trail](./images/hoa9-5.png?raw=true "Audit trail")

<br><br>

5. Run it again and answer `N`:

```
python agents/safe_agent.py
```

> **Expected output:** a `DENIED` observation, then a final answer without the ticket. No traceback.

![A human says no](./images/hoa9-6.png?raw=true "A human says no")

<br><br>

6. Find the refusal in the log:

```
grep rejected_by_human audit_log.jsonl
```

<br><br>

7. **What just happened.** Same tools and model as Lab 6, but now every call is allowlisted, validated, approved when it has consequences, and logged. It is ordinary code, so it can be reviewed and tested like any other code.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="lab10"></a>
## Lab 10 - Evaluating the Agent (~11 minutes)

**Purpose: Measure the agent instead of trusting one demo. Each scenario's checks are plain code, so the same run always gets the same verdict. This lab makes several agent runs; Groq is strongly recommended.**

**The situation:** Everything so far worked once, in front of you. Before the assistant goes on call, someone will ask how often it finds the answer, opens the ticket, and stays within its step budget.

1. Open the scenarios. Each is a task plus checks (hover the blue highlights): the answer names the bug, a ticket exists on disk, the step budget held.

```
code eval/scenarios.json
```

![Blue highlights on a task and its checks](./images/hoa10-1.png?raw=true "Blue highlights on a task and its checks")

<br><br>

2. Merge in the checks, then save and close the diff tab:

```
code -d extra/run_evals_complete.txt eval/run_evals.py
```

| What you're merging | Why |
|---|---|
| **`run_check`** — four checks: `final_contains` and `final_not_empty` look at the answer, `ticket_created` looks at the ticket file, `max_tool_calls` enforces the step budget. | Each check is code looking at a fact, so no model grades another model. `max_tool_calls` catches an agent that gets the right answer the slow, expensive way. |

![Merging the check implementations](./images/hoa10-2.png?raw=true "Merging the check implementations")

<br><br>

3. Add a scenario of your own. In `eval/scenarios.json` (still open), add this as a fourth entry, after the last `}` in the list with a comma before it, then save:

```
{
  "name": "quick-check",
  "task": "Run the test suite and tell me which test fails, in one sentence.",
  "checks": [
    { "type": "final_contains", "value": "test_total_value" },
    { "type": "max_tool_calls", "value": 2 }
  ]
}
```

<br><br>

4. Run the suite. Approvals are automatic here (`SAFE_AGENT_AUTO_APPROVE`) so it can run unattended; the audit log still records them as `approved_by_human`, which production code should distinguish. About 3 minutes on Ollama, under 1 on Groq:

```
python eval/run_evals.py
```

> **Expected output:** one pass/fail line per check. **Some failures are normal**, especially on the local model, and don't mean your merge is wrong.

![Four scenarios](./images/hoa10-6.png?raw=true "Four scenarios")

<br><br>

5. Read the results check by check, including your `quick-check` and its 2-call budget. One demo shows the agent *can* do a task; evals show *how often* it does. Track pass rates, not single runs.

<br><br>

6. **What just happened.** You have a repeatable answer to "does it work?" that runs like a test suite and could gate a deployment. Across the workshop, the same Lab 1 loop drove Python functions, raw CLIs, a designed CLI, MCP servers and a wrapped CLI, with policy controlling what it may do and evals measuring what it does. Design the tool well first, then choose the surface that fits how it will be shared.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

<a id="appendix-a"></a>
## Appendix A - Terms

The deck defines these where they come up; this is the one place to look them all up.

| Term | Meaning in this workshop |
|---|---|
| **agent** | A loop: ask the model what to do, run the tool it asks for, give it the result, repeat until it says it's done. Built in Lab 1. |
| **tool** | A function the agent may run. The model can only *ask* for a tool; our code decides whether and how to run it. |
| **tool registry** | The Python dictionary listing the agent's tools with a one-line description of each. The model sees only those descriptions. |
| **prompt engineering** | Choosing wording carefully because the model's behavior depends on it. Here, the wording that matters most is the tool descriptions. |
| **context** | Everything the model can see at once: the conversation so far plus every tool result. It has a size limit, which is why tools cap their output. |
| **exit code** | The number a command-line program returns when it finishes: `0` means success, anything else means failure. `echo $?` prints it. |
| **side effect** | A change a tool makes instead of only reporting: writing a file, opening a ticket, restarting a service. These are the calls to ask a human about. |
| **surface** | How a tool is offered to an agent. The same four capabilities appear as a command line (Labs 2-4) and as an MCP server (Labs 5-7). |
| **MCP** | Model Context Protocol: a standard way to publish tools so any client can discover and call them. |
| **stdio** | How our MCP servers communicate. There is no network port: the client starts the server as a subprocess and they talk over its standard input and output. |
| **schema** | The required shape of a tool's arguments: which exist, which are required, and each one's type. MCP generates it from Python type hints. |
| **allowlist** | A list of what is permitted; everything else is refused. The opposite, a blocklist, tries to name everything forbidden and can never be complete. |
| **audit log** | A file with one line per decision the agent made: what it asked for, what the policy said, what a human answered. |
| **eval** | A test for an agent: a task plus checks written as ordinary code, run repeatedly to learn how *often* the agent succeeds. |
| **token** | The unit a model reads, and the unit model use is measured and billed in: roughly four characters of English. Lab 7 counts them. |
| **system prompt** | The instructions at the start of every model call: the agent's role, its tool list and the reply format. It is sent again on every call. |
| **harness** | A script that runs something repeatedly and collects the results, such as the comparison script in Lab 7 and the eval runner in Lab 10. |

</br></br>

<a id="appendix-b"></a>
## Appendix B - What's in this repo

| Folder | Contents |
|---|---|
| `inventory_service/` | The application you are on call for, and the only part you don't build: `inventory.py` (the service, with the bug), `test_inventory.py` (its tests), `logs/app.log` (its log), `tickets.json` (its ticket store). |
| `agents/` | The agents (Labs 1, 2, 4, 6, 9) and the Lab 7 comparison and prompt-measuring scripts. `llm.py` is the shared model connection. |
| `cli_tools/` | `repo_tool.py`, the CLI you build in Lab 3. It supplies the agent's tools in every later lab except Lab 8: as a command in Lab 4, and through `mcp_server/repo_mcp.py` in Labs 5-7, 9 and 10. |
| `mcp_server/` | The MCP servers: `repo_mcp.py` (Lab 5, publishes `repo_tool.py`'s functions) and `git_mcp.py` (Lab 8), plus the test client. |
| `guardrails/` | The Lab 9 policy. |
| `eval/` | The Lab 10 scenarios and eval runner. |
| `extra/` | The finished code you merge from. You never edit these files; they are the left side of every diff. |
| `diagrams/` | Diagrams of the agent loop, the MCP exchange and the guardrail paths. |

</br></br>

<p align="center">
<b>For educational use only by the attendees of our workshops.</b>
</p>

<p align="center">
<b>(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.</b>
</p>
