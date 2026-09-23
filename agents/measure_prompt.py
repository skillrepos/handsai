"""Lab 7: How much of every model call is the tool list?

Every time an agent calls the model, it re-sends the whole system prompt,
and most of that prompt is the list of tools. This script builds the
system prompt three ways and prints how big each one is:

  - a bare shell agent: ONE tool, run_command, and the model supplies the
    command line itself
  - the Lab 4 CLI agent: its four hand-written tool descriptions
  - the Lab 6 MCP agent: the tools it discovers from one or more MCP
    servers, each with its full input schema

No model is called. Token counts are estimates at about 4 characters per
token; the exact number depends on the model's tokenizer. compare_agents.py
prints the real totals the model API reports.

Usage:
  python agents/measure_prompt.py                                   # repo_mcp.py
  python agents/measure_prompt.py mcp_server/repo_mcp.py mcp_server/git_mcp.py
"""

import asyncio
import json
import os
import sys

import mcp_agent
import structured_agent
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARS_PER_TOKEN = 4
STEPS = 8  # the agents' max_steps: a run can send the prompt this many times

SHELL_TOOLS = {
    "run_command": {
        "description": "Run a shell command. Returns its stdout, stderr and exit code.",
        "args": {"cmd": "string, the full command line"},
    },
}


def tokens(text):
    return len(text) // CHARS_PER_TOKEN


def shell_prompt():
    """The Lab 4 prompt format, with one generic tool in place of four."""
    saved = structured_agent.TOOLS
    structured_agent.TOOLS = SHELL_TOOLS
    try:
        return structured_agent.build_system_prompt()
    finally:
        structured_agent.TOOLS = saved


async def discover_tools(server_script):
    """Start one MCP server and return the tools it advertises."""
    params = StdioServerParameters(command=sys.executable, args=[server_script], cwd=REPO_ROOT)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.discover()
            return (await session.list_tools()).tools


async def main(servers):
    tools = []
    for server in servers:
        tools += await discover_tools(server)

    rows = [
        ("bare shell (run_command)", 1, shell_prompt()),
        ("Lab 4 CLI agent", len(structured_agent.TOOLS), structured_agent.build_system_prompt()),
        ("Lab 6 MCP agent", len(tools), mcp_agent.build_system_prompt(tools)),
    ]

    print(f"MCP servers: {', '.join(servers)}\n")
    print("The system prompt each agent sends with EVERY model call")
    print(f"{'agent':<26} {'tools':<7} {'characters':<12} {'~tokens':<9} {'x ' + str(STEPS) + ' calls':<10}")
    for label, count, prompt in rows:
        print(f"{label:<26} {count:<7} {len(prompt):<12} {tokens(prompt):<9} {tokens(prompt) * STEPS:<10}")

    print("\nWhat each discovered MCP tool adds to that prompt")
    print(f"{'tool':<18} {'characters':<12} {'~tokens':<9}")
    for tool in tools:
        description = (tool.description or "").strip().splitlines()
        line = f"- {tool.name}: {description[0] if description else ''}\n  input schema: {json.dumps(tool.input_schema)}"
        print(f"{tool.name:<18} {len(line):<12} {tokens(line):<9}")

    print(f"\n~tokens = characters / {CHARS_PER_TOKEN}. The last column is one {STEPS}-step run:")
    print("the tool list is paid for again on every call, before the task gets any room.")


if __name__ == "__main__":
    servers = sys.argv[1:] or ["mcp_server/repo_mcp.py"]
    asyncio.run(main(servers))
