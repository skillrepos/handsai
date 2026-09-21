# Hands of AI
## Building AI Agents That Act: Tools via CLIs and MCP
## Full-day workshop labs
## Revision 1.9 - 09/21/26

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
- **The scenario all day: you're building an on-call engineer's assistant. A small inventory service in `inventory_service/` has a failing nightly report. Your agent will gain the tools to investigate it — and by the end, guardrails so you can trust it to act.**
- **What's in this repo: `inventory_service/` is the application you are on call for, and the only thing in the repo you do *not* build — `inventory.py` is the service (it has the bug), `test_inventory.py` is its test suite, `logs/app.log` is its log, `tickets.json` is its ticket store. Everything else is what you build today: `agents/` the agents, `cli_tools/` the CLI you design in Lab 3, `mcp_server/` the MCP servers, `guardrails/` the Lab 9 policy, `eval/` the Lab 10 harness. `extra/` holds the finished code you merge from — you never edit those files; they are the left-hand side of every diff.**
- **Expected failures are part of this workshop. Several steps deliberately produce a failing test, an error message, or a refusal — that is how you see the bug, the design, or the guardrail actually working. Every step whose output is *supposed* to look alarming is followed by an `Expected output` note telling you exactly what you should see and why. If a step has no such note, its output should be clean — and if it isn't, something really did go wrong.**
</br></br>

**Assembling Code**

> To learn about the code without getting stuck in syntax and typing, we use a "diff and merge" approach to construct complete code. The starter files you edit live in `agents/`, `cli_tools/` and `mcp_server/`; the finished versions you copy from live in `extra/`.
>
> This involves a side-by-side view with the code to be merged in on the left and an incomplete starter set of code on the right.
>
> Most code to be merged will also have informational comments available describing what the code does. You get to these by hovering over the code or content to be merged when you see the yellow comment icon in the left gutter. See figure below for an example.
>
> When ALL merges are done, you can save your changes and close the view by clicking on the `X` in the tab at the top of the diff.
>
> Two more kinds of highlights help you read code outside the diff view. When you open a starter file on its own, the spots where merged code will land are highlighted in **yellow** (they disappear once you've merged). And in files a lab opens just to *read*, the parts the step calls out are highlighted in **blue** — hover any highlight for the explanation.
> <br><br>

![merge info](./images/merge-info3.png?raw=true "merge info")

</br></br>

## Lab agenda (10 labs, ~10-12 minutes each)

| # | Lab | Focus |
|---|-----|-------|
| 1 | The Agent Loop | reason -> act -> observe, with Python-function tools |
| 2 | Tools from the Command Line | raw CLIs: grep, pytest, git, tail |
| 3 | Designing an Agent-Friendly CLI | answers as JSON, size-limited output, exit codes that mean something |
| 4 | The Agent Meets the Designed CLI | the agent uses your Lab 3 tool |
| 5 | A First MCP Server | expose the same tools over MCP |
| 6 | The MCP-Powered Agent | discover tools at startup, nothing hardcoded |
| 7 | CLI vs MCP: Head-to-Head | same task, offered two different ways, compared |
| 8 | Wrapping Git Behind MCP | one tool per question, plus one guarded general-purpose tool |
| 9 | Guardrails: Policy, Approval, Audit | allowlist, validation, human approval, audit log |
| 10 | Evaluating the Agent | test scenarios checked by plain code, not by another model |

## The story of the day

You are building an **on-call engineer's assistant** for a small inventory service (`inventory_service/`). Its nightly report has been failing since 9:16 this morning. Over ten labs the assistant goes from "can read a file" to "can investigate, act, ask permission, and prove itself":

| Morning — give it hands | Afternoon — make it shareable and trustworthy |
|---|---|
| Lab 1: the agent loop reads the log and checks the math | Lab 6: the agent discovers its tools over MCP |
| Lab 2: real CLI tools — pytest finds the failing test | Lab 7: CLI vs MCP, measured on the same task |
| Lab 3: a CLI designed *for* an agent | Lab 8: a proven CLI (git) wrapped safely |
| Lab 4: the agent uses it — and opens its first ticket | Lab 9: policy, human approval, audit trail |
| Lab 5: the same tools published as an MCP server | Lab 10: evals — does it work, or did it work once? |

Each lab ends with **What just happened** — read it; that's where the point of the lab lives.

</br></br>

## Words we use today

Every one of these is defined again in the lab where you first meet it. This is the one place to look them all up.

| Term | What it means here |
|---|---|
| **agent** | A loop: ask the model what to do, run the tool it asks for, hand the result back, repeat until it says it's done. That's all. You build it in Lab 1. |
| **tool** | A function the agent is allowed to run. The model can only *ask* for a tool; our code decides whether and how to run it. |
| **tool registry** | The plain Python dictionary listing the agent's tools and the one-line description of each. Nothing clever — the model only ever sees those descriptions. |
| **prompt engineering** | Wording text carefully because the model's behavior depends on it. In this workshop the text that matters most is your tool descriptions. |
| **context** | Everything the model can see at once — the conversation so far plus every tool result. It has a size limit, which is why we cap how much output a tool returns. |
| **exit code** | The number a command-line program leaves behind when it finishes: `0` means it worked, anything else means it didn't. `echo $?` prints it. |
| **side effect** | A tool that changes something instead of just reporting — writes a file, opens a ticket, restarts a service. These are the calls worth asking a human about. |
| **size-limited output** | A deliberate cap on how much a tool returns, so one noisy command can't fill the model's context. |
| **surface** | How a tool is *offered* to an agent. The same four capabilities appear on two surfaces today: as a command line (Labs 2-4) and as an MCP server (Labs 5-7). The capability is the same; the surface is the packaging. |
| **MCP** | Model Context Protocol — a standard way to publish tools so any client can discover and call them without being written for your code specifically. |
| **stdio** | How our MCP servers communicate: no network port, no web page. A client launches the server as a subprocess and they talk over its standard input and output. |
| **schema** | The shape a tool's arguments must have — which ones exist, which are required, and what type each is. MCP generates it from your Python type hints. |
| **allowlist** | A list of what *is* permitted, with everything else refused by default. The opposite is a blocklist, which tries to name everything forbidden — a losing game. |
| **audit log** | A file recording one line per decision the agent made: what it asked for, what policy said, what a human answered. |
| **eval** | A test for an agent. A task plus checks that are ordinary code, run repeatedly, so you learn how *often* the agent succeeds rather than that it once did. |
| **harness** | A small script that runs something repeatedly and collects the results — the comparison runner in Lab 7, the eval runner in Lab 10. |

</br></br>

## Lab 1 - The Agent Loop (~12 minutes)

**Purpose: Build the loop at the heart of every agent — the model decides what to do, our code does it, the result goes back to the model — and use it to answer the first on-call question of the day.**

**The situation:** It's 9:16 AM and the nightly inventory report has failed. The application log holds the clue: a `total_value mismatch` — the ledger expected 149.95, the service returned 39.99. Which one is right? A human would read the log and do the arithmetic. We'll build an agent that does exactly that.

**By the end you'll have:** `agents/simple_agent.py` — an agent with three tools (read a file, list a directory, do arithmetic) that reads the log, checks the math, and tells you the ledger is right and the service is wrong. That's the first clue in a bug hunt that runs all day.

1. Look at the evidence yourself first, so you'll know whether the agent gets it right. Lines 3-4 add stock (5 widgets at 19.99, 10 gadgets at 5.00); line 6 is the mismatch:

```
head -8 inventory_service/logs/app.log
```

![The log the agent will read](./images/hoa1-1.png?raw=true "The log the agent will read")

<br><br>

2. Open the model connection every agent in this workshop shares. The four functions the agents import are highlighted in blue (hover for details): `chat` sends messages to the model, `extract_json` pulls a JSON action out of a messy reply, `observation_message` wraps a tool result with a reminder of how to finish, `which_backend` says whether Ollama or Groq is in use. (`get_client_and_model` is the helper that picks the backend; `chat` falls back to Ollama if Groq's daily budget runs out.)

```
code agents/llm.py
```

<br><br>

3. Open the Lab 1 skeleton — this is what "an agent" is in this workshop. Three tools that are plain Python functions (`calculator`, `read_file`, `list_files`); a `TOOLS` registry (blue) — a plain Python dictionary listing the tools — that describes them *in words* — the only thing the model will ever know about them; and two TODOs (yellow) where the missing code will land.

```
code agents/simple_agent.py
```

<br><br>

4. Merge in the completed code: for each highlighted block, click the arrow that copies it from the complete file (left) into the skeleton (right). Then save and close the diff tab.

```
code -d extra/simple_agent_complete.txt agents/simple_agent.py
```

| What you're merging | Why it's there |
|---|---|
| **`build_system_prompt`** — turns every entry in the `TOOLS` registry into one line of description, then spells out the only two replies the model may give: `{"tool": ..., "args": ...}` or `{"final": ...}`. | This text is the *only* thing the model ever learns about your tools. When an agent ignores a tool or calls it wrongly, this is the first place to look. |
| **The reason/act/observe loop** — ask the model, pull the JSON action out of its reply, have *our* code run the tool it chose, hand the result back as the next message, repeat. Unparseable replies get a retry request instead of a crash. | This *is* the agent. Every agent for the rest of the day is this same loop with different tools plugged into it, so it's worth reading line by line. |

![Merging the agent loop](./images/hoa1-3.png?raw=true "Merging the agent loop")

<br><br>

5. Read what you merged, because the division of labor is the whole idea. `build_system_prompt` turns the `TOOLS` descriptions into text and tells the model how to answer: either `{"tool": ..., "args": ...}` to request a tool, or `{"final": ...}` to finish. The loop then repeats: ask the model → parse its JSON → *our code* runs the chosen tool → the result goes back to the model as the next message. The model chooses and interprets; our code executes.

<br><br>

6. Run it. It prints which backend is in use and the task, then one line per decision:

```
python agents/simple_agent.py
```

![First agent run](./images/hoa1-5.png?raw=true "First agent run")

<br><br>

7. Read the transcript top to bottom. `Task:` is the question. Each `--- step N: tool(args)` line is a decision the model made — which tool, with which arguments. The `observation:` line under it is only the *first 200 characters* of what our code handed back — a display convenience so the transcript stays readable. When there's more, the line ends with `... [truncated for display - the model receives the full text]`; the model always gets the whole thing. `=== FINAL ANSWER (after N tool calls) ===` is the model deciding it has enough. Expect: `read_file` on the log, `calculator` on `5*19.99 + 10*5.00` (= 149.95), and a verdict that the ledger is right and the service is wrong. On the small local model the path can wobble — an extra call, a wrong expression first — but it still lands; on Groq it's two or three clean calls. Watch the *mechanics*, not the model's elegance.

<br><br>

8. Now point the same agent at the code, with no other change than the question — the model picks a different tool because the task needs one:

```
python agents/simple_agent.py "Read inventory_service/inventory.py and tell me whether total_value looks correct."
```

![The agent reads the code and spots the bug](./images/hoa1-8.png?raw=true "The agent reads the code and spots the bug")

**A note on what you'll see:** the `observation:` for this step stops partway through the file, on the line `class InventoryError(Exception):`. **That is not an error** — it's the 200-character display cut from step 7 landing in the middle of the source, and `InventoryError` is simply a class defined near the top of `inventory.py`. The agent read the first 2000 characters and answered from all of them; you're just seeing the first tenth of that in the transcript.

<br><br>

9. **What just happened, and why it matters.** The model did the thinking: it chose the tools, wrote the arguments, interpreted a log file and a source file, and decided when it was done. Our code did the doing — and nothing else. That split is what makes it safe to hand an agent real power later, because everything it can *do* is a function we wrote. And notice what it knew: only the one-line descriptions in `TOOLS`. Tool descriptions are prompt engineering: the wording of those one-liners is the only lever you have over which tool the model reaches for, so treat them as code, not comments. You've found the bug (`total_value` adds instead of multiplies) with a file reader and a calculator. Next lab: real engineering tools, so it can prove the bug with the test suite.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 2 - Tools from the Command Line (~12 minutes)

**Purpose: Give the agent the tools engineers already use — pytest, grep, git, tail — exactly as they are, and see both the power and the price of raw terminal output.**

**The situation:** The log says the service's total is wrong. Before anyone touches code, an on-call engineer asks: *do the tests know? Which one fails?* The programs to answer that already exist. The fastest way to make an agent capable is to hand it those programs, unchanged.

**By the end you'll have:** `agents/cli_agent.py` — the Lab 1 loop with four CLI-backed tools — that runs the real test suite and names the failing test, plus a clear picture of what the model had to wade through to do it.

1. Before the agent gets any tools, run one of them yourself. `pytest` is Python's test runner; this command runs every test in the inventory service's own test suite and reports the results (`-q` is "quiet" — the short report instead of the long one). In step 3 this exact command becomes one of the agent's four tools, named `run_tests`, so what appears on your screen now is, character for character, what the model will have to read later:

```
python -m pytest inventory_service -q
```

![Manual pytest output](./images/hoa2-1.png?raw=true "Manual pytest output")

> **Expected output — one test fails, and that failure is the point of the lab.** You should see a red `FAILED` line, an `AssertionError`, and `1 failed, 4 passed`. Nothing is wrong with your setup or your Codespace: this is the service's own test suite confirming the bug that Lab 1's agent suspected from the log.
>
> Read the failure itself. `test_total_value` stocks 5 widgets at 19.99 and 10 gadgets at 5.00, so the correct total is `5 x 19.99 + 10 x 5.00 = 149.95`. The service returned `39.99`, which is what you get when you *add* each price and quantity instead of multiplying them: `(19.99 + 5) + (5.00 + 10)`. That 149.95-versus-39.99 pair is the same mismatch the log reported at 9:16 in Lab 1 — the log said it, and now the tests agree.

<br><br>

2. Now look at the *shape* of that output rather than its meaning. Exactly one fact matters — `test_total_value` is the failing test — and it arrives wrapped in banner characters, a percentage counter, a source excerpt, a file-and-line traceback and a summary block. pytest formats all of that for a human staring at a terminal. In a few minutes the agent will receive this same text as a tool result and will have to locate that one fact inside it on every single run. Count the lines it has to read past.

<br><br>

3. Open the skeleton. The loop at the bottom is the Lab 1 loop, unchanged. What's new is the tools: instead of Python functions, four thin wrappers (`grep_code`, `run_tests`, `git_history`, `tail_log`). The TODOs (yellow) are `run_command` — the one place that actually runs a program — and the single line in each wrapper that calls it.

```
code agents/cli_agent.py
```

<br><br>

4. Merge in the completed code, save, and close the diff tab:

```
code -d extra/cli_agent_complete.txt agents/cli_agent.py
```

| What you're merging | Why it's there |
|---|---|
| **`run_command`** — runs a command-line program and packages its stdout, stderr and exit code into one block of text for the model. Gives up on anything still running after 120 seconds, and cuts output off at `MAX_OUTPUT` characters. | The single place this agent touches the outside world. The timeout and the size cap aren't housekeeping: they're what stops one hung command freezing the agent, and one noisy command filling the model's context. |
| **The four tool wrappers** (`grep_code`, `run_tests`, `git_history`, `tail_log`) — one line each, handing `grep`, `pytest`, `git log` and `tail` to `run_command`. | Four real engineering tools for four lines of code — that's why CLIs are the fastest way to make an agent capable. Notice the cost as you merge them: each returns whatever its program happens to print, in a format that program chose, not you. |

![Merging run_command](./images/hoa2-4.png?raw=true "Merging run_command")

<br><br>

5. Read the merged `run_command` — the four jobs are highlighted in blue. Every CLI-driving agent needs all four: capture stdout, stderr *and* the exit code (the only structure a raw CLI gives you); enforce a timeout so a hung command can't hang the agent; truncate long output (`MAX_OUTPUT`) so one pytest run can't fill the model's context — the limited amount of text it can hold at once; format it as text for the model.

<br><br>

6. Run the agent on the on-call question:

```
python agents/cli_agent.py
```

![CLI agent finds the failing test (end of the run)](./images/hoa2-6.png?raw=true "CLI agent finds the failing test (end of the run)")

> **Expected output:** a long transcript, and `observation:` lines that contain pytest's failure text and `exit code: 1`. Both are expected — the exit code is non-zero *because* a test failed, which is precisely the fact the agent was sent to find. A clean exit code here would mean the bug had vanished.

<br><br>

7. Read the transcript (the screenshot shows the tail of a run — scroll up to see it all). Which tools did it pick, and in what order? It should name `test_total_value` as the failing test. On the local model expect several extra calls and a muddled *why*; on Groq, two to five clean calls. Either way, look at the `observation:` lines — exit codes, pytest boilerplate, arbitrary truncation. Every one of those characters is something the model had to read past to find the one fact.

<br><br>

8. Ask a question that needs a different tool — the model chooses `tail_log` because the task calls for the log, not the tests:

```
python agents/cli_agent.py "Show the last 10 lines of the application log and tell me whether the problem is still happening."
```

![The agent picks tail for a log question](./images/hoa2-8.png?raw=true "The agent picks tail for a log question")

<br><br>

9. **What just happened, and why it matters.** One merge gave the agent four proven programs without writing any connecting code of our own — that is the CLI superpower, and it's why CLIs are the fastest route to a capable agent. The price is that every observation is formatted for a human: screens of text, one exit code as the only structure, and truncation at an arbitrary character count. Small models stumble on exactly this; big models spend tokens on it. The fix is not a bigger model. It's a better tool — which is Lab 3.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 3 - Designing an Agent-Friendly CLI (~12 minutes)

**Purpose: Build a CLI made *for* an agent — every answer as JSON, a cap on how much comes back, error messages that explain themselves, and exit codes that truthfully say whether the command worked — and test it by hand. No LLM in this lab; good tools are testable without one.**

**The situation:** Lab 2 worked, barely. The investigation always needs the same four capabilities — search the code, run the tests, summarize the log, open a ticket — so we build one small program, `repo_tool.py`, with a subcommand for each, and design every response for the consumer that has to read it: a language model.

**By the end you'll have:** a tested CLI whose every answer is one JSON object with an `ok` field, whose output is capped at a sane size, and whose exit codes mean something. Every later lab except Lab 8 runs through this code — Lab 4 as a CLI, Labs 5-7, 9 and 10 behind an MCP server.

1. Open the skeleton. The module docstring (blue) is the design checklist — six properties, each fixing something you watched the Lab 2 agent suffer through. `do_tests` (blue) is complete as the worked example; `do_search`, `do_log_summary` and `do_ticket` are the TODOs.

```
code cli_tools/repo_tool.py
```

<br><br>

2. Study `do_tests`: it runs the very same pytest as Lab 2 but returns a small dict — passed/failed counts and failure names. The tool absorbs the mess so the model doesn't have to. That is the pattern the three TODOs copy.

<br><br>

3. Merge in the three remaining operations, save, and close the diff tab:

```
code -d extra/repo_tool_complete.txt cli_tools/repo_tool.py
```

| What you're merging | Why it's there |
|---|---|
| **`do_search`** — walks the service's `.py` files and returns matches as JSON: file, line, text. Checks the regular expression first, so a bad pattern is a clear message instead of a crash, and `max_results` caps how much comes back, with a `truncated` flag when results were cut. | Same capability as Lab 2's `grep_code`, redesigned around the reader. The `truncated` flag is the detail to notice: Lab 2 cut output silently, so the model couldn't tell a short answer from a clipped one. |
| **`do_log_summary`** — parses the log into counts per level plus the last five messages at the level asked for, and refuses any level other than INFO, WARNING or ERROR with a message naming the valid ones. | The agent now reads a small summary instead of the whole log. The refusal matters as much as the success: an error that names the valid options is one a model can recover from by itself. |
| **`do_ticket`** — appends a ticket to `tickets.json` and returns the id it generated. Title and body lengths are capped. | The tool's only side effect — the one operation that changes something instead of reporting. The lengths are capped because the input is coming from a model. Remember this tool in Lab 9; it's the one we put behind human approval. |

![Merging do_search](./images/hoa3-3.png?raw=true "Merging do_search")

<br><br>

4. Test it by hand — compare the `tests` output with the pytest screen from Lab 2. Same facts, one JSON object. (The tool exits 0 even though a test failed: the exit code says whether the *tool* ran, and pytest's own result is a field, `exit_code`, inside the JSON.)

```
python cli_tools/repo_tool.py tests
python cli_tools/repo_tool.py log-summary --level ERROR
```

![repo_tool tests output](./images/hoa3-4.png?raw=true "repo_tool tests output")

> **Expected output:** one JSON object reporting `"ok": true` alongside `"failed": 1` and the name of the failing test. Those two are not in conflict: `ok` describes the *tool* — it ran and is telling you the truth — while `failed` describes the *tests*. Keeping those two ideas in separate fields is the design point of this lab.

<br><br>

5. Now probe the error behavior. **Both of the commands below are supposed to fail** — making them fail on purpose is how you test that they fail *well*. (`echo $?` prints the exit code of the command immediately before it: `0` means success, anything else means failure.)

```
python cli_tools/repo_tool.py log-summary --level DEBUG
echo $?
python cli_tools/repo_tool.py search
echo $?
```

![Structured error vs usage error](./images/hoa3-5.png?raw=true "Structured error vs usage error")

> **Expected output:** two failures of two different kinds. The first prints a JSON object with `"ok": false` and an explanatory message, and `echo $?` reports `1`. The second prints argparse's usage text to the screen — not JSON — and `echo $?` reports `2`. Step 6 explains why that difference is worth engineering.

<br><br>

6. The first is a *structured* error (exit 1): the operation ran, failed meaningfully, and the message names the valid options — an error a model can recover from. The second is a *usage* error from argparse (exit 2): the caller got the syntax wrong. A program — or an agent — can tell them apart without reading English.

<br><br>

7. Use the tool to do what the agent will do all afternoon — find the bug in the code:

```
python cli_tools/repo_tool.py search --pattern "BUG"
```

![search finds the bug comment](./images/hoa3-7.png?raw=true "search finds the bug comment")

<br><br>

8. Open a ticket and confirm it persisted. This is the tool's one *side effect* — the one place it changes something in the world instead of just reporting on it — remember that when we get to guardrails in Lab 9:

```
python cli_tools/repo_tool.py ticket --title "Manual test" --body "Opened by hand in Lab 3"
cat inventory_service/tickets.json
```

<br><br>

9. **What just happened, and why it matters.** The capabilities are the same as Lab 2; only the design changed, and it changed around the consumer. Clear inputs, predictable JSON output, a cap on how much comes back, useful `--help`, errors that explain themselves, exit codes that tell the truth: that checklist is the most transferable thing you'll take from today, because in Lab 5 you'll see it applies verbatim to MCP tools too. Next: give the agent this tool and watch the same model behave differently.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 4 - The Agent Meets the Designed CLI (~12 minutes)

**Purpose: Repeat the Lab 2 experiment with your designed CLI — same model, same loop, same question — and see what tool design buys you. Then let the agent act on the world for the first time.**

**The situation:** If the design work in Lab 3 was worth it, the transcript should show it: fewer steps, cleaner observations, a straighter path to `test_total_value`. And once the agent has an `open_ticket` tool, the investigation can end the way a real one does — with a ticket.

**By the end you'll have:** `agents/structured_agent.py`, a side-by-side comparison you can point to, and a ticket the agent opened on its own.

1. Open the skeleton. Same loop as always — the TODOs are `run_tool` (invoke `repo_tool.py` and parse its JSON) and four one-line wrappers, one per subcommand.

```
code agents/structured_agent.py
```

<br><br>

2. Merge in the completed code, save, and close the diff tab:

```
code -d extra/structured_agent_complete.txt agents/structured_agent.py
```

| What you're merging | Why it's there |
|---|---|
| **`run_tool`** — runs `repo_tool.py` and parses its stdout as JSON. Output that isn't JSON becomes a structured error the model can react to. | Compare it with Lab 2's `run_command`, which handed raw text straight through. This one can assume a shape, because Lab 3 guaranteed one — that guarantee is what you bought by designing the CLI. |
| **The four subcommand wrappers** (`search_code`, `run_tests`, `summarize_log`, `open_ticket`) — one line each, passing the model's arguments through to `repo_tool.py`'s validated flags. | They are one-liners *because* the CLI is well designed: there is nothing left for the agent to clean up. Wrapper code shrinking is the measurable sign that the design work paid off. |

![Merging run_tool](./images/hoa4-2.png?raw=true "Merging run_tool")

<br><br>

3. Run it on the exact question the Lab 2 agent answered:

```
python agents/structured_agent.py
```

![Structured agent run](./images/hoa4-3.png?raw=true "Structured agent run")

> **Expected output:** compact JSON observations, including `"failed": 1` and `test_total_value`. Same failing test as Lab 2, same bug, same conclusion — the only thing that changed is that the agent now reads it as a fact instead of decoding it from a screen.

<br><br>

4. Compare with your Lab 2 run: the `observation:` lines are compact JSON like `{"ok": true, "passed": 4, "failed": 1, "failures": [...]}` instead of a pytest screen dump. The model may still take several search steps — it is the same model, exploring the same way — but every observation it reads is now a fact rather than a screen to decode. With small models that difference is often the line between flaky and reliable.

<br><br>

5. Now give it a job that ends in an action. It needs two tools it has never been told to combine:

```
python agents/structured_agent.py "Summarize the ERROR lines in the application log, then open a ticket titled 'Nightly report failing' that describes the problem."
```

![The agent summarizes the log and opens a ticket](./images/hoa4-5.png?raw=true "The agent summarizes the log and opens a ticket")

<br><br>

6. Confirm the side effect is real:

```
cat inventory_service/tickets.json
```

<br><br>

7. **What just happened, and why it matters.** The model did not get smarter between Lab 2 and Lab 4; the tool got better, and the agent got more reliable. Reliability is largely a tool-design property, which means it's *yours* to engineer. And note what just happened in step 5: the agent wrote to a ticket store because a sentence asked it to — nobody approved that. Hold on to that feeling; Lab 9 is about it. Next: this tool works for one script on one machine. Making it available to *every* client is what MCP is for.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 5 - A First MCP Server (~12 minutes)

**Purpose: Publish the same four capabilities through the Model Context Protocol, so any MCP client can discover them — with schemas and descriptions generated from your code. No LLM in this lab.**

**The situation:** `repo_tool.py` works for one agent that knows how to spawn it. Tomorrow three teams want the same tools — in an IDE, in a chat client, in a CI bot. Copying a Python file around isn't sharing. MCP is the standard way to publish tools so that clients you've never met can discover and call them.

**By the end you'll have:** `mcp_server/repo_mcp.py` serving the four tools over MCP, and proof from a tiny client that a stranger can discover them, complete with JSON schemas you never wrote.

1. Open the server skeleton. It imports the Lab 3 functions unchanged — only the *surface* changes, meaning the way those same capabilities are offered to a client. The command line was one surface; MCP is another. `search_code` (blue) is already exposed as the worked example.

```
code mcp_server/repo_mcp.py
```

<br><br>

2. Note what `search_code` gets for free: `@mcp.tool()` registers it, its type hints become a JSON Schema — a machine-readable statement of which arguments exist, which are required and what type each must be — and its docstring becomes the description a model will read. The Lab 3 checklist, enforced by the protocol.

<br><br>

3. Merge in the other three tools, save, and close the diff tab:

```
code -d extra/repo_mcp_complete.txt mcp_server/repo_mcp.py
```

| What you're merging | Why it's there |
|---|---|
| **Three more MCP tools** (`run_tests`, `summarize_log`, `open_ticket`) — each exposed exactly like the `search_code` example above it. Every body is a single line that calls the Lab 3 function unchanged. | The point is how little you write. Your type hints become the schema and your docstring becomes the description the model reads, so publishing a tool over MCP is mostly a matter of describing it accurately. The capability itself is still Lab 3's code. |

![Merging the three MCP tools](./images/hoa5-3.png?raw=true "Merging the three MCP tools")

<br><br>

4. Run the server on its own and nothing will happen — that is normal. This server speaks MCP over *stdio*: it doesn't listen on a port and there's no page to visit, a client launches it as a subprocess and the two talk over that process's standard input and output. So it sits silently until a client connects, and we need a client to see anything at all. Open the test client — the entire client side of MCP in about 50 lines, each stage highlighted in blue: launch the server as a subprocess, `initialize`, `list_tools`, `call_tool`.

```
code mcp_server/try_server.py
```

<br><br>

5. Run it against your server:

```
python mcp_server/try_server.py
```

![Discovered tools and schemas](./images/hoa5-5.png?raw=true "Discovered tools and schemas")

<br><br>

6. All four tools appear with generated schemas. Find `"required": ["title", "body"]` on `open_ticket` — a client can now reject a bad call before your code ever runs. Then watch one full call go out and come back: `search_code` (searching for `total_value` this time) returns the same shape of JSON that Lab 3 produced, delivered through the protocol.

<br><br>

7. Where did that schema come from? Type hints. The description? Docstrings — which means docstring quality is now prompt engineering, exactly like `TOOLS` descriptions were in Lab 1.

<br><br>

8. Point the *same* client at a different server (a preview of Lab 8's git server, still a skeleton). Nothing in the client changed; it simply discovers whatever it's given:

```
python mcp_server/try_server.py mcp_server/git_mcp.py
```

![Same client, different server](./images/hoa5-8.png?raw=true "Same client, different server")

> **Expected output:** all three git tools listed, even though two of them are still unfinished skeletons you won't complete until Lab 8. Their `@mcp.tool()` decorators, names and type hints are already in place, so the *catalogue* is complete before the *implementations* are. The tool the client actually calls, `recent_commits`, is the finished one, so real commits come back.

<br><br>

9. **What just happened, and why it matters.** You published tools without writing an API: the protocol turned your functions into a discoverable, typed catalogue, and a 50-line client you've now seen twice can consume *any* server. That's the shareability CLIs lack. What hasn't changed is the checklist — the tools are good because Lab 3 made them good; MCP just makes them portable. Next: teach the agent to be that client.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 6 - The MCP-Powered Agent (~12 minutes)

**Purpose: Turn the agent into a real MCP client that discovers its tools at startup — nothing hardcoded — and run the full investigation through the protocol.**

**The situation:** The server is up. Now the agent should know *nothing* about it in advance: no import, no hand-written tool list. If that works, the same agent can drive any server anyone publishes — which is exactly what Labs 7, 8 and 9 will do with it.

**By the end you'll have:** `agents/mcp_agent.py`, which builds its prompt from discovered tools and finds the root cause of the nightly failure end to end.

1. Open the skeleton. Two TODOs: `build_system_prompt` (build the prompt from *discovered* tools, not a registry) and `call_mcp_tool` (execute one call through the session).

```
code agents/mcp_agent.py
```

<br><br>

2. Merge in the completed code, save, and close the diff tab:

```
code -d extra/mcp_agent_complete.txt agents/mcp_agent.py
```

| What you're merging | Why it's there |
|---|---|
| **`build_system_prompt`** — builds the prompt from the tools the agent *discovered* at startup, using each tool's description and its input schema. Nothing about the server is written into the agent. | This is the whole difference from Lab 1, where the prompt came from a hardcoded registry. Add a tool to the server and it appears in the agent's prompt on the next run, with no code change — which is what makes Lab 8 possible. |
| **`call_mcp_tool`** — runs one call through the MCP session and joins the text that comes back into an observation. The protocol's `isError` flag marks failures as `TOOL ERROR`, and exceptions become error strings. | The loop has to survive bad calls, because the model will make them. Turning a failure into text the model can read — rather than an exception that ends the run — is what lets it correct itself on the next step. |

![Merging the discovery prompt](./images/hoa6-2.png?raw=true "Merging the discovery prompt")

<br><br>

3. Before running, find these three things in the merged code (highlighted in blue): (a) the agent never imports the server — it only knows a script path; (b) the prompt is built from each tool's `description` and `input_schema`, straight from `list_tools`; (c) failures come back through the protocol's `is_error` flag as text the model can react to.

<br><br>

4. Run it on the Lab 4 question:

```
python agents/mcp_agent.py
```

![MCP agent run](./images/hoa6-4.png?raw=true "MCP agent run")

<br><br>

5. The first lines list the tools the agent *discovered* at startup. From there the run looks like Lab 4 — and that is the point: the model's experience didn't change, but the way the tools reach it is now a published standard rather than something we invented.

<br><br>

6. Now the whole investigation in one task. The agent has to chain the log, the tests and a code search, then explain — this is the on-call assistant doing its job:

```
python agents/mcp_agent.py "Check the log for errors, run the tests, search the code, and explain the root cause of the failing nightly report."
```

![The full investigation](./images/hoa6-6.png?raw=true "The full investigation")

<br><br>

7. Read the final answer against what you know: the log's mismatch, the failing `test_total_value`, and the `BUG` line in `inventory.py` where price and quantity are added instead of multiplied. On Groq this is usually a tidy four- or five-step run; on the local model the reasoning is shakier but the tools are the same.

<br><br>

8. **What just happened, and why it matters.** The agent found the root cause of the day's incident using tools it learned about at startup, over a standard protocol, from a server it never imported. Swap the server and the agent gains new abilities with zero code changes — you'll do exactly that in Lab 8. Next: CLI and MCP have now solved the same problem; time to compare them with evidence instead of opinions.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 7 - CLI vs MCP: Head-to-Head (~12 minutes)

**Purpose: Run the identical task through the Lab 4 agent (CLI tools) and the Lab 6 agent (MCP tools), then compare the transcripts and the numbers — so the CLI-versus-MCP decision is an engineering judgment, not a fashion.**

**The situation:** You've built the same four capabilities twice. Leadership will ask "which one should we standardize on?" The honest answer depends on what you measure and what you're building. This lab collects the evidence.

**By the end you'll have:** two transcripts of the same investigation, a comparison table, and a decision framework you can defend.

1. Open the comparison harness — a small script that runs both agents and collects the results. It's provided complete; there's no merge in this step. The three things it does are highlighted in blue: run both agents on one task, count their tool calls and wall time, save both transcripts under `transcripts/`.

```
code agents/compare_agents.py
```

<br><br>

2. Run it. This is two full agent runs back to back, so expect about a minute and a half on Ollama (well under a minute on Groq):

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

4. With the transcripts in front of you: Did both agents pick the same tools in the same order? Which observation format is easier to skim? Did both reach the same root cause?

<br><br>

5. Now the numbers in the table. *Tool calls* is the count of `--- step` lines; wall time is dominated by model calls (one per step, plus the final answer), so if one agent took much longer, first check whether it simply took more steps. If the step counts are close and the times aren't, look elsewhere: on Groq's free tier a gap is usually rate-limit backoff inherited from the first run, and on Ollama the first run may have paid to load the model. Measurements need context before they become verdicts.

<br><br>

6. Now error handling, one surface at a time — first the command line, then MCP. On the command line there is nobody standing between the caller and the tool, so run it by hand (no agent needed) and notice that the tool's own code has to catch the bad value and explain it:

```
python cli_tools/repo_tool.py log-summary --level DEBUG
```

<br><br>

7. Make the same category of mistake through MCP — a wrong *type* — and watch where it gets caught. The schema rejects it before your Python ever runs, and the agent gets a protocol-level error it can recover from:

```
python agents/mcp_agent.py "Call search_code with pattern set to BUG and max_results set to the word ten, then tell me exactly what came back."
```

![Schema validation rejects the call](./images/hoa7-7.png?raw=true "Schema validation rejects the call")

> **Expected output:** an error, and here the error *is* the success condition. The call never reached your Python at all — MCP's generated schema saw a string where an integer was required and rejected it first. Contrast that with step 6, where the CLI tool's own hand-written code had to notice the bad value and explain it.

If your model "helpfully" sends `10` instead of the word, the call just succeeds — run it again, or insist harder in the task; the demonstration needs the bad value to reach the schema.

<br><br>

8. **What just happened, and why it matters.** Same model, same task, offered two different ways — and the transcripts show the model's experience is nearly identical, because the *tool design* was the same. What differs is everything around the tool: MCP gives you discovery, typed validation before execution, and sharing across clients; CLIs give you zero setup and every program that already exists. The framework: **CLI** when the tool exists, you're prototyping, or it's one agent on one machine. **MCP** when many clients share tools, schemas and discovery pay off, or tools evolve independently. **Wrap the CLI in MCP** when the CLI is proven but you want structure and safety on top — which is Lab 8.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 8 - Wrapping Git Behind MCP (~12 minutes)

**Purpose: Put a proven CLI (git) behind an MCP server. You'll build two kinds of tool: narrow ones that each answer a single question, and one flexible tool for everything else that is fenced in with rules. The agent gains git's power without its dangers.**

**The situation:** The investigation needs history: who changed `total_value`, and when? git already knows. But `git` can also push, reset and run arbitrary commands through its flags, and an agent that can run "any git command" is an incident waiting to happen. The wrapper adds the safety git alone doesn't have.

**By the end you'll have:** `mcp_server/git_mcp.py` with three tools, and the *unchanged* Lab 6 agent using them — including watching it get refused.

1. Open the skeleton. Provided, in blue: the allowlist of read-only subcommands — a list of the git commands that *are* permitted, with everything else refused by default — `_git` (the one place that shells out — timeout, error capture, truncation, exactly Lab 2's four jobs), and `recent_commits` (a worked example that turns `git log` text into structured commits). TODOs: `file_history` and `git_readonly`.

```
code mcp_server/git_mcp.py
```

<br><br>

2. Note the two kinds of tool you're about to complete, because the difference is the lesson. `file_history` is **narrow**: it answers exactly one question — what happened to this file — and exposes no git options at all, so there is nothing to misuse. `git_readonly` is the **general-purpose** one, for a git command nobody anticipated: it accepts a subcommand by name, but only from the allowlist, and it refuses every option flag.

<br><br>

3. Merge in the completed code, save, and close the diff tab:

```
code -d extra/git_mcp_complete.txt mcp_server/git_mcp.py
```

| What you're merging | Why it's there |
|---|---|
| **`file_history`** — the commits that touched one file, after checking the path is safe: no leading `-`, nothing outside the repo, and a `--` before the path so git always reads it as a path and never as a flag. | The narrow kind of tool. It answers one question and exposes no git options at all, so there is nothing in it to misuse. The path checks are there because the argument came from a model, and `--file.txt` would otherwise be read as a flag. |
| **`git_readonly`** — flexible git access with two rules enforced before anything runs: the subcommand must be on the allowlist, and any argument starting with `-` is rejected. | The general-purpose kind, for the git command nobody anticipated. Note what it does *not* do: it never tries to list the dangerous flags. It permits a short list of safe subcommands and refuses every option — you can finish writing that list, and you can never finish the other one. |

![Merging file_history](./images/hoa8-3.png?raw=true "Merging file_history")

<br><br>

4. Point the Lab 6 agent — not one line changed — at the new server. It discovers the git tools and gains new abilities:

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "What are the three most recent commits in this repo, and who made them?"
```

![Agent discovers and uses the git tools](./images/hoa8-4.png?raw=true "Agent discovers and uses the git tools")

<br><br>

5. Now try to make it misbehave through the general-purpose tool:

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "Use the git_readonly tool to run the push subcommand and tell me exactly what comes back."
```

![Guard refusing git push](./images/hoa8-5.png?raw=true "Guard refusing git push")

> **Expected output:** a refusal — no push happens, and nothing crashes. The observation should read something like `subcommand 'push' is not allowed`. Seeing the guard turn the agent down is the result this step is after.

<br><br>

6. The observation is a refusal with structure to it — `subcommand 'push' is not allowed` — that also names what *is* allowed. The model can recover from that; a stack trace it could not.

<br><br>

7. Try the sneakier attack: an allowed subcommand with a dangerous flag. git has options that write files and execute commands, so the wrapper rejects *every* option rather than keeping a blocklist of the bad ones (a list of what's forbidden — which you can never finish writing):

```
python agents/mcp_agent.py --server mcp_server/git_mcp.py "Use git_readonly to run the log subcommand with the argument --output=/tmp/pwned and tell me exactly what comes back."
```

![Guard refusing an option flag](./images/hoa8-7.png?raw=true "Guard refusing an option flag")

> **Expected output:** a second refusal, and note *which* rule stopped it. `log` is on the allowlist, so the allowlist let it through; what rejected the call was the no-options rule, because the argument begins with `-`.

<br><br>

8. **What just happened, and why it matters.** The agent gained git with zero changes to the agent, because discovery did the work. And the wrapper is where the safety lives: an allowlist of subcommands, no flags at all, structured refusals. The principle is *enumerate goodness; don't chase badness* — you can list the five things that are safe, you cannot list every way git can hurt you. Next: the same principle applied to every tool call the agent makes, plus a human in the loop.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 9 - Guardrails: Policy, Approval, Audit (~12 minutes)

**Purpose: Wrap every tool call in a policy layer — an allowlist of what may be called, a check that the arguments match the tool's schema, human approval before anything that changes the world, and a log of every decision — all of it in code, outside the model.**

**The situation:** In Lab 4 the agent opened a ticket because a sentence asked it to. Fine in a workshop; not fine when the tool is "restart the service" or "refund the customer". We keep the agent exactly as capable and add a gate every call passes through, so a human decides what has consequences.

**By the end you'll have:** `agents/safe_agent.py`, which stops and asks you before any side effect, refuses what policy forbids, and leaves an audit trail you could hand to a reviewer.

1. Open the policy — provided complete, deliberately boring code. The four control points are highlighted in blue: `ALLOWED_TOOLS` (what may be called at all), `APPROVAL_REQUIRED` (what needs a human), `validate_call` (arguments checked against the tool's own schema), `audit` (one JSON line per decision).

```
code guardrails/policy.py
```

<br><br>

2. The key idea: none of this depends on the model behaving. The model can ask for anything; only calls that pass the policy execute. Guardrails live *outside* the model, in code you can test.

<br><br>

3. Open the safe agent — the Lab 6 agent plus one TODO, `guarded_call`, the gate every tool call now passes through. Merge it in, save, and close the diff tab:

```
code -d extra/safe_agent_complete.txt agents/safe_agent.py
```

| What you're merging | Why it's there |
|---|---|
| **`guarded_call`** — the gate every tool call now passes through, in three checkpoints: check the call against policy and the tool's schema; ask a human if the tool has a side effect; then run it and record what happened in `audit_log.jsonl`. A refusal at any checkpoint comes back as a `DENIED` observation. | Every control in this workshop lives in this one function, and none of it depends on the model behaving. The model may ask for anything; only calls that get through here execute. `DENIED` being an observation rather than an exception is what lets the agent adapt instead of crashing. |

![Merging the guardrail gate](./images/hoa9-3.png?raw=true "Merging the guardrail gate")

<br><br>

4. Run it. The task asks for the root cause *and* a ticket. When the agent wants to open the ticket it stops and asks **you** — read the proposal at the `[y/N]` prompt and answer `y`:

```
python agents/safe_agent.py
```

![Approval prompt](./images/hoa9-4.png?raw=true "Approval prompt")

> **Expected output:** the run pauses at a `[y/N]` prompt and waits for you. It is not hung — the agent has proposed a tool call with a side effect and policy requires a human to approve it. Read the proposal, then type `y` and press Enter.

<br><br>

5. Inspect the audit trail — one JSON line per decision (`session_start`, `executed`, `approved_by_human`, `session_end`). This is the file you'd show a reviewer who asks "what did the agent do, and who let it?":

```
cat audit_log.jsonl
```

![Audit trail](./images/hoa9-5.png?raw=true "Audit trail")

<br><br>

6. Run it again and this time answer `N`. The agent receives a `DENIED` observation, survives, and adjusts its answer instead of crashing:

```
python agents/safe_agent.py
```

![A human says no](./images/hoa9-6.png?raw=true "A human says no")

> **Expected output:** a `DENIED` observation followed by a final answer that works around the missing ticket. No traceback. An agent absorbing a refusal and carrying on is exactly the behavior this step demonstrates — a guardrail that crashed the agent would be a bug, not a guardrail.

<br><br>

7. Find the refusal in the log:

```
grep rejected_by_human audit_log.jsonl
```

<br><br>

8. **What just happened, and why it matters.** The agent is exactly as capable as in Lab 6 — same tools, same model — and now every call is allowlisted, validated, approved when it has consequences, and recorded. All of that is ordinary code, which means it can be reviewed and tested like ordinary code. That is how you earn the right to give an agent real tools. Next: earning the right to *trust* it — with evidence.

<p align="center">
**[END OF LAB]**
</p>

</br></br>

## Lab 10 - Evaluating the Agent (~12 minutes)

**Purpose: Measure the agent instead of trusting a demo. You'll write scenarios whose checks are plain code — the same run always produces the same verdict, and no model grades another model — then run them like a test suite. Strongly recommended with Groq; this lab is several full agent runs.**

**The situation:** Everything today "worked" — once, in front of you. Before this assistant goes on call, someone will ask how often it gets the answer, opens the ticket, and stays within budget. A demo can't answer that. An eval suite can.

**By the end you'll have:** an eval harness (the script that runs the scenarios and collects results), a pass/fail report for three on-call scenarios, and a fourth scenario of your own.

1. Open the scenarios — hover the blue highlights. Each is a task plus fact-based checks: the answer mentions the bug, a ticket exists on disk, the step budget was respected. Every check is code; no model grades another model.

```
code eval/scenarios.json
```

<br><br>

2. Open the harness skeleton. It runs each scenario through the Lab 9 safe agent and then applies the checks; the one TODO (yellow) is `run_check`, the four check implementations.

```
code eval/run_evals.py
```

<br><br>

3. Merge in the four checks, save, and close the diff tab:

```
code -d extra/run_evals_complete.txt eval/run_evals.py
```

| What you're merging | Why it's there |
|---|---|
| **`run_check`** — the four checks: `final_contains` and `final_not_empty` inspect the agent's answer, `ticket_created` inspects the state on disk, and `max_tool_calls` enforces a step budget per scenario. | Every one is ordinary code inspecting an observable fact, so the same run always gets the same verdict and no model is grading another model. `max_tool_calls` is the interesting one — it's how you catch an agent that reaches the right answer the slow, expensive way. |

![Merging the check implementations](./images/hoa10-2.png?raw=true "Merging the check implementations")

<br><br>

4. Run the suite. Approvals are automatic here (`SAFE_AGENT_AUTO_APPROVE` makes `ask_human` say yes) so it can run unattended — itself a policy decision. Notice that the audit log still records those as `approved_by_human`; in production you'd want a distinct event for that. Each scenario is a full agent run, so on Ollama this is about two minutes; on Groq well under one:

```
python eval/run_evals.py
```

![Eval results](./images/hoa10-3.png?raw=true "Eval results")

> **Expected output:** one pass/fail line per check. **Some checks failing here is a normal result**, especially on the small local model — it does not mean you merged the code wrong. Step 5 is about why those failures are the lesson rather than a defect.

<br><br>

5. Read your results check by check. With the small local model some may fail — **that is the lesson**: one demo proves an agent *can* do a task; evals tell you *how often* it does. Track rates, not runs.

<br><br>

6. Add a scenario of your own. Open `eval/scenarios.json` and add this as a fourth entry (after the last `}` inside the list, with a comma before it):

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

7. Re-run (a little longer now, with four scenarios) and see whether your agent meets *your* bar. A tight step budget is a design decision — it's how you catch an agent that gets the right answer the slow, expensive way:

```
python eval/run_evals.py
```

![Four scenarios](./images/hoa10-6.png?raw=true "Four scenarios")

<br><br>

8. **What just happened, and why it matters.** You now have a repeatable answer to "does it work?" that runs like a test suite and can gate a deployment. And step back at the day in one picture: the same loop from Lab 1 drove Python functions, raw CLIs, a designed CLI, MCP servers and a wrapped CLI — with policy deciding what it *may* do and evals proving what it *does*. Design the tool well first; then pick the surface that fits how it will be shared, validated, and trusted. That is the whole course.

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
