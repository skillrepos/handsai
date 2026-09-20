"""
Lab 4 - MCP Test Client (provided complete; nothing to merge)
Starts repo_server.py over stdio, lists its tools, and calls two
of them -- proving the server works before any LLM is involved.
"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=["mcptools/repo_server.py"])


async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("TOOLS DISCOVERED:")
            for t in tools.tools:
                print(f"  {t.name}: {t.description}")

            print("\nCALL file_info('labs.md'):")
            result = await session.call_tool("file_info", {"path": "labs.md"})
            print(" ", result.content[0].text)

            print("\nCALL recent_commits(3):")
            result = await session.call_tool("recent_commits", {"count": 3})
            print(" ", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
