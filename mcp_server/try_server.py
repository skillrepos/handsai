"""Lab 5 helper: a tiny MCP client for poking at a server by hand.

This launches an MCP server as a subprocess, connects to it over stdio,
lists the tools it advertises (with their auto-generated schemas), and
calls one tool so you can see a result round-trip.

Usage:
  python mcp_server/try_server.py                          # uses repo_mcp.py
  python mcp_server/try_server.py mcp_server/git_mcp.py    # any server script
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def main(server_script):
    params = StdioServerParameters(
        command=sys.executable,
        args=[server_script],
        cwd=REPO_ROOT,
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print(f"=== Tools advertised by {server_script} ===\n")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"* {tool.name}")
                print(f"  description: {(tool.description or '').strip().splitlines()[0]}")
                print(f"  input schema: {json.dumps(tool.inputSchema)}")
                print()

            first = tools.tools[0]
            print(f"=== Calling {first.name} with sample arguments ===\n")
            if first.name == "search_code":
                result = await session.call_tool("search_code", {"pattern": "total_value"})
            else:
                result = await session.call_tool(first.name, {})
            for item in result.content:
                if item.type == "text":
                    print(item.text)


if __name__ == "__main__":
    script = sys.argv[1] if len(sys.argv) > 1 else "mcp_server/repo_mcp.py"
    asyncio.run(main(script))
