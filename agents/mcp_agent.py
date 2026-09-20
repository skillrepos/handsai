"""Lab 6: The agent, powered by MCP.

The agent loop is the same one you have built three times now. What is
different is where the tools come from: nothing about them is hardcoded.
The agent launches an MCP server, DISCOVERS what tools exist (names,
descriptions, and typed schemas), builds its prompt from that, and
executes every action through the protocol.

Point it at a different server and the agent gains different abilities
without a single code change. That is the reuse story of MCP.
"""

import asyncio
import json
import os
import sys

from llm import chat, extract_json, which_backend
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SERVER = "mcp_server/repo_mcp.py"


def build_system_prompt(tools):
    """Describe the job and the DISCOVERED tools to the model."""
    # TODO: Lab 6 merge step — build the system prompt from the discovered
    # tools: for each tool include its name, the first line of its
    # description, and its JSON input schema, then the action format rules.
    raise NotImplementedError("merge in the completed code (see labs.md)")


async def call_mcp_tool(session, tool_name, args):
    """Execute one tool call through the MCP session and return observation text."""
    # TODO: Lab 6 merge step — call the tool through the MCP session, join
    # the text content parts into an observation string, and flag errors
    # using the result's isError field.
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
            print(f"[backend: {which_backend()}] [server: {server_script}]")
            print(f"[discovered tools: {', '.join(sorted(tool_names))}]")
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
                    return action["final"]
                tool_name = action.get("tool")
                args = action.get("args", {})
                if tool_name not in tool_names:
                    observation = f"ERROR: unknown tool '{tool_name}'"
                else:
                    observation = await call_mcp_tool(session, tool_name, args)
                print(f"--- step {step}: {tool_name}({json.dumps(args)})")
                print(f"    observation: {observation[:200]}")
                messages.append({"role": "assistant", "content": json.dumps(action)})
                messages.append({"role": "user", "content": f"Observation:\n{observation}"})
            print("\n=== Gave up: reached max steps without a final answer ===")
            return None


if __name__ == "__main__":
    argv = sys.argv[1:]
    server = DEFAULT_SERVER
    if argv and argv[0] == "--server":
        server = argv[1]
        argv = argv[2:]
    task = " ".join(argv) or (
        "Run the test suite and tell me which test fails and why."
    )
    asyncio.run(run_agent(task, server))
