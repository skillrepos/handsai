"""Lab 9: The safe agent — MCP tools behind guardrails.

This is the Lab 6 MCP agent with a policy layer wrapped around every
tool call:

  - allowlist:   only approved tools can run, whatever the server offers
  - validation:  arguments are checked against the tool's schema + limits
  - approval:    side-effecting tools require a human yes/no
  - audit log:   every decision is recorded in audit_log.jsonl

Set SAFE_AGENT_AUTO_APPROVE=yes to skip the interactive prompt (used by
the evaluation harness in this lab).
"""

import asyncio
import json
import os
import sys

from llm import chat, extract_json, which_backend
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from guardrails.policy import audit, needs_approval, validate_call

DEFAULT_SERVER = "mcp_server/repo_mcp.py"


def build_system_prompt(tools):
    """Describe the job and the discovered tools to the model."""
    lines = [
        "You are a software engineer's assistant that can use tools to investigate a repository.",
        "You have access to these tools:",
        "",
    ]
    for tool in tools:
        description = (tool.description or "").strip().splitlines()
        first_line = description[0] if description else "(no description)"
        lines.append(f"- {tool.name}: {first_line}")
        lines.append(f"  input schema: {json.dumps(tool.inputSchema)}")
    lines += [
        "",
        "To use a tool, reply with ONLY a JSON object like:",
        '  {"tool": "<tool name>", "args": {"<arg>": "<value>"}}',
        "Arguments must match the tool's input schema.",
        "When you have enough information to answer, reply with ONLY:",
        '  {"final": "<your answer>"}',
        "Use one tool at a time. Do not include any other text.",
    ]
    return "\n".join(lines)


def ask_human(tool_name, args):
    """Ask the human operator to approve a side-effecting tool call."""
    if os.environ.get("SAFE_AGENT_AUTO_APPROVE", "").lower() in ("yes", "true", "1"):
        return True
    answer = input(f"\n>>> APPROVE {tool_name}({json.dumps(args)})? [y/N] ")
    return answer.strip().lower() in ("y", "yes")


async def guarded_call(session, schemas, tool_name, args):
    """Run one tool call through every guardrail, then (maybe) execute it."""
    # TODO: Lab 9 merge step — the guardrail gate:
    #   1. validate_call against the policy and the tool's schema; if it
    #      fails, audit a 'denied' event and return a DENIED observation
    #   2. if needs_approval, ask_human and audit the decision; a human
    #      'no' returns a DENIED observation without executing
    #   3. execute via session.call_tool, build the observation text, and
    #      audit an 'executed' event with the output size
    raise NotImplementedError("merge in the completed code (see labs.md)")


async def run_agent(task, server_script=DEFAULT_SERVER, max_steps=8):
    params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        cwd=REPO_ROOT,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            tool_names = {tool.name for tool in tools}
            schemas = {tool.name: tool.inputSchema for tool in tools}
            print(f"[backend: {which_backend()}] [server: {server_script}]")
            print(f"[discovered tools: {', '.join(sorted(tool_names))}]")
            audit("session_start", task=task, tools=sorted(tool_names))
            messages = [
                {"role": "system", "content": build_system_prompt(tools)},
                {"role": "user", "content": task},
            ]
            for step in range(1, max_steps + 1):
                reply = chat(messages)
                action = extract_json(reply)
                if action is None:
                    print(f"--- step {step}: unparseable reply, asking model to retry")
                    messages.append({"role": "assistant", "content": reply})
                    messages.append({"role": "user", "content": "Reply with ONLY a valid JSON object as instructed."})
                    continue
                if "final" in action:
                    print(f"\n=== FINAL ANSWER (after {step - 1} tool calls) ===")
                    print(action["final"])
                    audit("session_end", final=str(action["final"])[:300])
                    return action["final"]
                tool_name = action.get("tool")
                args = action.get("args", {})
                if tool_name not in tool_names:
                    observation = f"ERROR: unknown tool '{tool_name}'"
                else:
                    observation = await guarded_call(session, schemas, tool_name, args)
                print(f"--- step {step}: {tool_name}({json.dumps(args)})")
                print(f"    observation: {observation[:200]}")
                messages.append({"role": "assistant", "content": json.dumps(action)})
                messages.append({"role": "user", "content": f"Observation:\n{observation}"})
            print("\n=== Gave up: reached max steps without a final answer ===")
            audit("session_end", final=None)
            return None


if __name__ == "__main__":
    argv = sys.argv[1:]
    server = DEFAULT_SERVER
    if argv and argv[0] == "--server":
        server = argv[1]
        argv = argv[2:]
    task = " ".join(argv) or (
        "Find the root cause of the failing nightly report and open a ticket "
        "titled 'Nightly report failing' describing it."
    )
    asyncio.run(run_agent(task, server))
