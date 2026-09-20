# The Hands of AI: Building Agent Tools with MCP and CLIs
## A hands-on workshop
## Revision 1.2 - 09/15/26

**Startup: Setting up your environment**

**Purpose: To get a GitHub Codespace running with our local LLM ready to go. (~5 minutes active, plus background setup)**

1. Open the workshop repository on GitHub (your instructor will share the URL), click the green **Code** button, select the **Codespaces** tab, and click **Create codespace on main**.

<br><br>

2. Wait for the Codespace to finish building (3-5 minutes). The terminal will show the Python environment installing and Ollama pulling the `llama3.2:3b` model.

![Codespace ready](./images/handson-setup-1.png?raw=true "Codespace ready")

<br><br>

3. Verify the model is ready. In the terminal, run:

```
ollama list
```

You should see `llama3.2:3b` in the list. If not, run `ollama pull llama3.2:3b` and wait for it to finish.

<br><br>

<p align="center">
**[END OF SETUP]**
</p>
<br><br>

**Lab 1 - Your First Agent Loop**

**Purpose: To build the core of every agent - a loop where the model reasons, picks a tool, and incorporates the result. (10-12 minutes)**

1. Open the starting file to see its overall structure. Note: this file is incomplete - we'll merge in the working code next.

```
code agent/agent.py
```

<br><br>

2. Open a diff view against the completed version and merge each highlighted change over into `agent.py` using the arrow controls. Look at the `TOOLS` schemas and the loop as you merge - the schemas are all the model ever sees of your code.

```
code -d extra/agent_complete.txt agent/agent.py
```

![Merging the agent loop](./images/handson-lab1-1.png?raw=true "Merging the agent loop")

<br><br>

3. Save the file (Ctrl+S / Cmd+S) and close the diff tab. Run the agent with its default task:

```
python agent/agent.py
```

The first inference can take 30 seconds to 2 minutes on a Codespace - be patient.

<br><br>

4. Watch the output: the model chose the `calculator` tool, your code executed it, and the model turned the result into an answer.

![Agent tool call output](./images/handson-lab1-2.png?raw=true "Agent tool call output")

<br><br>

5. Now give it a task that needs the other tool:

```
python agent/agent.py "What are the first 3 lines of README.md?"
```

<br><br>

6. Try a task no tool covers and observe what the model does:

```
python agent/agent.py "What is the capital of France?"
```

<br><br>

**What just happened**

- You built the think -> act -> observe loop that sits inside every agent product you've used.
- The model never runs code. It emits a *request* to call a tool; your code executes and returns the result.
- Tool schemas (name, description, parameters) are the model's only view of your functions - they are prompt engineering.
- The loop has a safety cap on iterations - a guardrail you'll see much more of later.
- Yes, the calculator uses `eval` behind a character allowlist. Hold that thought - it is the first guardrail of the day, and Lab 7 is where we do it properly.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 2 - CLI as Hands**

**Purpose: To give the agent a real shell and see both the power and the risk of CLI-based execution. (10-12 minutes)**

1. Open the starting file and look at the single tool it defines - one schema, unlimited reach. Note: this file is incomplete until the next step.

```
code agent/cli_agent.py
```

<br><br>

2. Merge in the completed `run_command` function:

```
code -d extra/cli_agent_complete.txt agent/cli_agent.py
```

<br><br>

3. Save and run the default task:

```
python agent/cli_agent.py
```

The model composes its own shell command (something like `find . -name "*.py" | wc -l`) - nobody taught it that; it's in the training data.

<br><br>

4. Ask something harder and watch it chain knowledge it already has:

```
python agent/cli_agent.py "Which markdown file in this repo has the most lines?"
```

If a command fails, watch the model read stderr and retry - errors returned as data become course corrections.

<br><br>

5. Now the uncomfortable part. Ask:

```
python agent/cli_agent.py "Create a file named oops.txt containing the word pwned"
```

<br><br>

6. Check what happened:

```
cat oops.txt
```

The agent wrote to your filesystem because nothing said it couldn't. Delete the file:

```
rm oops.txt
```

<br><br>

**What just happened**

- One tiny tool schema unlocked every CLI the model knows: `find`, `grep`, `wc`, `git` - zero integration code per tool.
- That's the CLI advantage: enormous capability for a few dozen schema tokens, with training-data familiarity doing the work.
- It's also the risk: the same schema that lets it count files lets it write, delete, or exfiltrate. Capability and permission arrived as one unit.
- Labs 7-8 fix exactly this; first we'll see the alternatives.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 3 - Designing Agent-Friendly Tools**

**Purpose: To replace one raw shell with purpose-built tools that have typed inputs and predictable JSON outputs. (10-12 minutes)**

1. Open the starting file and skim the three tool schemas near the bottom - narrow names, one job each. Note: this file is incomplete until the merge.

```
code agent/git_tools.py
```

<br><br>

2. Merge in the two missing tool implementations (all three schemas are already in place):

```
code -d extra/git_tools_complete.txt agent/git_tools.py
```

Notice as you merge: `git_log` parses git's output into `{hash, author, subject}` objects instead of passing raw text through.

<br><br>

3. Save and run:

```
python agent/git_tools.py
```

<br><br>

4. Compare tool choice quality with a few tasks:

```
python agent/git_tools.py "Do we have any uncommitted changes?"
```

```
python agent/git_tools.py "How many shell scripts are in this project?"
```

<br><br>

5. Now sabotage a description to see how much it matters. In `agent/git_tools.py`, change the `count_files` description to just `"A tool."`, save, and re-run the shell-scripts question. Watch the model flounder or pick the wrong tool.

<br><br>

6. Restore the description (undo with Ctrl+Z / Cmd+Z, then save) and re-run to confirm it recovers.

<br><br>

**What just happened**

- Purpose-built tools trade raw power for predictability: fixed argv (no shell injection surface), structured output, narrow blast radius.
- The description is the interface. You just watched tool selection break from one lazy sentence - descriptions deserve code review.
- Errors returned as JSON let the model self-correct; exceptions that crash the loop don't.
- This is the design discipline MCP will formalize in the next lab.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 4 - Your First MCP Server**

**Purpose: To expose tools through the Model Context Protocol, making them discoverable by any MCP client. (10-12 minutes)**

1. Open the server file. One `FastMCP` object, functions decorated with `@mcp.tool()` - the docstring and type hints become the published schema. Note: this file is incomplete until the merge.

```
code mcptools/repo_server.py
```

<br><br>

2. Merge in the two missing tools:

```
code -d extra/repo_server_complete.txt mcptools/repo_server.py
```

<br><br>

3. Save the file. There's nothing to "start" - with stdio transport, the client launches the server itself. Open the provided test client to see how:

```
code mcptools/test_client.py
```

<br><br>

4. Run the test client:

```
python mcptools/test_client.py
```

You should see all three tools discovered with their descriptions, then live results from two calls - no LLM involved yet.

![MCP test client output](./images/handson-lab4-1.png?raw=true "MCP test client output")

<br><br>

5. Prove discoverability. Add a fourth tool to `repo_server.py` yourself - copy the `word_count` function, rename it `line_count`, and make it return the number of lines instead (hint: `len(p.read_text(errors="replace").splitlines())`). Save.

<br><br>

6. Re-run the test client:

```
python mcptools/test_client.py
```

You should now see four tools listed — `file_info`, `word_count`, `recent_commits`, and your `line_count` — with the client code unchanged.

<br><br>

**What just happened**

- MCP separates the tool provider from the tool consumer with a protocol: list the tools, read their schemas, call them.
- FastMCP generated the JSON Schema from your function signature - the "schema is the interface" idea from Lab 3, now enforced by a standard.
- The test client proved the server works before adding LLM nondeterminism - always debug in that order.
- Any MCP client - Claude Desktop, an IDE, your agent in the next lab - could now use this server as-is.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 5 - Agent Meets MCP**

**Purpose: To connect our agent loop to the MCP server so tools are discovered at runtime instead of hardcoded. (10-12 minutes)**

1. Open the MCP-powered agent. Note the shape: same loop as Lab 1, but no `TOOLS` list anywhere in the file. Note: this file is incomplete until the merge.

```
code mcptools/mcp_agent.py
```

<br><br>

2. Merge in the completed code:

```
code -d extra/mcp_agent_complete.txt mcptools/mcp_agent.py
```

The whole "integration" is `to_ollama_tools` - reshaping schemas the server already publishes.

<br><br>

3. Save and run:

```
python mcptools/mcp_agent.py
```

<br><br>

4. Try a task that needs the tool YOU added in Lab 4:

```
python mcptools/mcp_agent.py "How many lines are in README.md?"
```

The agent uses `line_count` - a tool that didn't exist when the agent code was written.

<br><br>

5. Ask a two-step question and watch it chain MCP calls:

```
python mcptools/mcp_agent.py "Which has more words, README.md or labs.md?"
```

<br><br>

**What just happened**

- The agent discovers its hands at runtime - `list_tools` then `call_tool` - so servers and agents can evolve independently.
- Adding a capability meant editing the SERVER only. In the CLI world that was also true; the difference is the schema came with it.
- The conversion function is ~10 lines because both sides speak JSON Schema - this is the portability argument for MCP.
- Cost note: every discovered tool's schema rides along in each model call. More tools = more context. Remember this for the decision framework.
- `ClientSession` is a client-side object, not a protocol session: the 2026-07-28 spec removed sessions from the wire, not from the SDK.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 6 - Wrapping a CLI Behind MCP**

**Purpose: To combine both surfaces - a battle-tested CLI on the inside, a typed and governed MCP boundary on the outside. (10-12 minutes)**

1. Open the wrapper server and look at `ALLOWED_SUBCOMMANDS` - policy lives at the wrap boundary. Note: this file is incomplete until the merge.

```
code mcptools/git_server.py
```

<br><br>

2. Merge in the completed `run_git`:

```
code -d extra/git_server_complete.txt mcptools/git_server.py
```

Validation order as you merge: allowlist first, then fixed-argv execution, then errors returned as data.

<br><br>

3. Save the file. Point the Lab 5 agent at this server instead - no agent changes, just an environment variable:

```
MCP_SERVER=mcptools/git_server.py python mcptools/mcp_agent.py "What branches exist in this repo?"
```

<br><br>

4. Give the working tree something to diff (a fresh Codespace has no changes yet):

```
echo "workshop scratch note" >> README.md
```

<br><br>

5. Ask for something inside the allowlist:

```
MCP_SERVER=mcptools/git_server.py python mcptools/mcp_agent.py "Summarize the current diff"
```

The agent should report one changed file with one added line. Undo the scratch change:

```
git checkout -- README.md
```

<br><br>

6. Now ask for something the allowlist forbids:

```
MCP_SERVER=mcptools/git_server.py python mcptools/mcp_agent.py "Delete the most recent commit"
```

Watch the refusal come back as structured data - and the model explain the limitation instead of crashing.

<br><br>

**What just happened**

- The wrap pattern gets both halves: git's 20 years of reliability underneath, MCP's discovery, typing, and policy on top.
- The allowlist turned "what can the agent do" from an emergent property into a config line you can code-review.
- The same agent binary drove two different servers via one env var - execution surfaces became swappable.
- This is the pattern for your internal CLIs at work: don't rewrite them, wrap them.
- Java shop? `extra/java/` has this same server as a Spring Boot MCP server - same allowlist, same fixed-argv execution, same structured returns.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 7 - Guardrails**

**Purpose: To retrofit the dangerous Lab 2 shell agent with allowlisting, validation, human approval, and an audit trail. (10-12 minutes)**

1. Open the guarded agent and skim the four guardrail markers: `ALLOWED_PROGRAMS`, the pydantic `CommandRequest`, `NEEDS_APPROVAL`, and `audit`. Note: this file is incomplete until the merge.

```
code guardrails/safe_agent.py
```

<br><br>

2. Merge in `safe_run_command`:

```
code -d extra/safe_agent_complete.txt guardrails/safe_agent.py
```

Note the order as you merge: validate -> allowlist -> approve -> execute, and every branch writes to the audit log.

<br><br>

3. Save and run the default task:

```
python guardrails/safe_agent.py
```

When the agent reaches for `git`, you'll get an approval prompt. Type `y` and press Enter.

![Approval gate prompt](./images/handson-lab7-1.png?raw=true "Approval gate prompt")

<br><br>

4. Re-run the Lab 2 attack:

```
python guardrails/safe_agent.py "Create a file named oops.txt containing the word pwned"
```

The model may try `echo` with redirection - the pydantic validator rejects `>` - or an unlisted program - the allowlist rejects that. Either way, no file.

<br><br>

5. Verify nothing was written, then read the audit trail:

```
ls oops.txt
```

```
cat guardrails/audit_log.jsonl
```

Every attempt, denial, and approval is a timestamped JSON line.

<br><br>

6. Run one more task, and this time answer `n` at an approval prompt to confirm a human "no" sticks:

```
python guardrails/safe_agent.py "What was the last commit?"
```

The denial goes back to the model as data — expect it to either apologize that it can't check, or try an allowed command instead. Both are correct behavior.

<br><br>

**What just happened**

- Four independent layers: validation (shape), allowlist (capability), approval (judgment), audit (accountability). Any one alone has holes.
- Denials went back to the model as data, so it degraded gracefully instead of crashing - guardrails and good tool design are the same discipline.
- The audit log is what your security team will ask for on day one of any agent deployment.
- Note these guardrails live in agent code. In Lab 6 they lived in the server. Where policy lives is an architecture decision - that's the afternoon discussion.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 8 - Trust but Verify: Evaluating Tool Choice**

**Purpose: To build a golden-set eval that catches tool-selection regressions before your users do. (10-12 minutes)**

1. Look at the golden set - each line is a task plus the tool we expect the model to choose:

```
code evalcheck/golden_set.jsonl
```

<br><br>

2. Open the harness. It reuses the Lab 3 tool schemas and asks one question per case: which tool did the model pick first? Note: this file is incomplete until the merge.

```
code evalcheck/evaluate.py
```

<br><br>

3. Merge in the scoring loop:

```
code -d extra/evaluate_complete.txt evalcheck/evaluate.py
```

<br><br>

4. Save and run the eval:

```
python evalcheck/evaluate.py
```

Eight model calls take 2-4 minutes on a Codespace. Expect most cases to pass - a small local model won't be perfect, and that's part of the lesson.

![Eval results](./images/handson-lab8-1.png?raw=true "Eval results")

<br><br>

5. Break it on purpose: in `agent/git_tools.py` (the Lab 3 file - note you're editing outside `evalcheck/`), swap the descriptions of `git_log` and `git_status`, save, and re-run the eval. Expect roughly 6-8/8 normally and noticeably lower - often around half - with the swapped descriptions. Same code, same model, worse tools.

<br><br>

6. Restore the descriptions (Ctrl+Z / Cmd+Z in that file, then save) and re-run to confirm the score recovers.

<br><br>

**What just happened**

- Tool descriptions are load-bearing, and now you have a regression test for them - run it in CI like any other test.
- The eval tests one narrow thing (first tool choice) so failures point at one cause. Resist mega-evals that fail mysteriously.
- A golden set of 8 is a starting point; real teams grow theirs from production failures, one case per incident.
- This same harness works no matter which surface executes the tool - CLI, MCP, or wrapped.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

**Lab 9 (Optional Capstone) - The Full Workflow**

**Purpose: To run one agent that combines both execution surfaces plus an approval gate to produce a deliverable. (10-12 minutes)**

1. Open the capstone agent - this one is provided complete; nothing to merge. Skim how it merges local tools and MCP-discovered tools into one tool list:

```
code capstone/workflow_agent.py
```

<br><br>

2. Run it:

```
python capstone/workflow_agent.py
```

The agent gathers facts across both surfaces (watch which tool comes from where), then drafts a repo health report. Multiple inferences - allow 2-3 minutes.

<br><br>

3. When prompted, approve the save with `y`, then view the deliverable:

```
code capstone/repo_health.md
```

Expect a short markdown report quoting a Python file count, a markdown file count, and the three latest commit subjects — exact wording will vary run to run.

<br><br>

4. Stretch goal, if time permits: add a `disk_usage` local CLI tool (wrap `du -sh` with fixed argv) to `LOCAL_TOOLS`, and extend the task string to include it in the report.

<br><br>

**What just happened**

- One agent, two surfaces, chosen per capability: local CLI for cheap simple facts, MCP for shared, schema'd services.
- The approval gate sat exactly where the risk was - the single write - not on every read. Guardrail placement is proportional to blast radius.
- This is the architecture most production agent systems converge on: mixed surfaces behind one loop, policy at the boundaries.

<p align="center">
**[END OF LAB]**
</p>
<br><br>

<p align="center">
**THANKS!**
</p>
<br><br>

<p align="center">
<b>For educational use only by the attendees of our workshops.</b>
</p>
<p align="center">
<b>(c) 2026 Tech Skills Transformations and Brent C. Laster. All rights reserved.</b>
</p>
