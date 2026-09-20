"""
Lab 5 - Agent Meets MCP
The Lab 1 agent loop, but the tools now come from an MCP server.
The agent discovers them at runtime -- add a tool to the server
and the agent can use it with zero agent-code changes.
Note: this file is incomplete -- you'll merge in the working code
during the lab.
"""
import asyncio
import json
import os
import sys

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "llama3.2:3b"
# Point the agent at any MCP server via MCP_SERVER, e.g.
#   MCP_SERVER=mcptools/git_server.py python mcptools/mcp_agent.py "..."
SERVER_PATH = os.environ.get("MCP_SERVER", "mcptools/repo_server.py")
SERVER = StdioServerParameters(command=sys.executable, args=[SERVER_PATH])


# ---------------------------------------------------------------
# TODO (merge): to_ollama_tools - convert the MCP tool list into
# the tool-schema format the Ollama chat API expects.
# ---------------------------------------------------------------
def to_ollama_tools(mcp_tools) -> list:
    raise NotImplementedError("Merge in to_ollama_tools from extra/mcp_agent_complete.txt")


async def run_agent(session: ClientSession, task: str) -> None:
    listing = await session.list_tools()
    tools = to_ollama_tools(listing.tools)
    print(f"Discovered {len(tools)} tools from the MCP server\n")

    messages = [
        {"role": "system",
         "content": "You answer questions about this repository using the "
                    "provided tools. Answer concisely."},
        {"role": "user", "content": task},
    ]

    # -----------------------------------------------------------
    # TODO (merge): the agent loop - same think/act/observe shape
    # as Lab 1, but tool execution goes through session.call_tool.
    # -----------------------------------------------------------
    raise NotImplementedError("Merge in the agent loop from extra/mcp_agent_complete.txt")


async def main() -> None:
    task = " ".join(sys.argv[1:]) or "How many words are in labs.md?"
    print(f"TASK: {task}\n")
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            await run_agent(session, task)


if __name__ == "__main__":
    asyncio.run(main())
