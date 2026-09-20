"""
Lab 9 (Optional Capstone) - The Full Workflow
Provided complete; nothing to merge. One agent, two execution
surfaces: local CLI-backed tools AND tools discovered from the
Lab 4 MCP server, with an approval gate before the final write.
The task: produce a short "repo health report" and save it.
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "llama3.2:3b"
SERVER = StdioServerParameters(command=sys.executable, args=["mcptools/repo_server.py"])
REPORT = Path("capstone/repo_health.md")


# ----- local CLI-backed tool ------------------------------------
def count_files(pattern: str = "*.py") -> str:
    proc = subprocess.run(["git", "ls-files", pattern],
                          capture_output=True, text=True, timeout=10)
    return json.dumps({"pattern": pattern,
                       "count": len(proc.stdout.splitlines())})


LOCAL_TOOLS = {
    "count_files": {
        "fn": count_files,
        "schema": {
            "type": "function",
            "function": {
                "name": "count_files",
                "description": "Count repository files matching a glob "
                               "pattern such as '*.py' or '*.md'.",
                "parameters": {
                    "type": "object",
                    "properties": {"pattern": {"type": "string"}},
                    "required": ["pattern"],
                },
            },
        },
    }
}


def to_ollama_tools(mcp_tools) -> list:
    return [{"type": "function",
             "function": {"name": t.name,
                          "description": t.description or "",
                          "parameters": t.inputSchema}}
            for t in mcp_tools]


async def run(task: str) -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_tools()
            mcp_names = {t.name for t in listing.tools}
            tools = to_ollama_tools(listing.tools) + \
                    [t["schema"] for t in LOCAL_TOOLS.values()]
            print(f"Tools available: {sorted(mcp_names | set(LOCAL_TOOLS))}\n")

            messages = [
                {"role": "system",
                 "content": "You are a repo analyst. Use tools to gather "
                            "facts, then write a 5-line markdown repo "
                            "health report as your final answer."},
                {"role": "user", "content": task},
            ]

            for _ in range(8):
                response = ollama.chat(model=MODEL, messages=messages, tools=tools)
                msg = response["message"]
                messages.append(msg)

                if not msg.get("tool_calls"):
                    report = msg["content"]
                    print(f"\nDRAFT REPORT:\n{report}\n")
                    # Approval gate before the only write action
                    if input("Save report to capstone/repo_health.md? [y/N] ").strip().lower() == "y":
                        REPORT.write_text(report + "\n")
                        print(f"Saved {REPORT}")
                    else:
                        print("Not saved.")
                    return

                for call in msg["tool_calls"]:
                    name = call["function"]["name"]
                    args = dict(call["function"]["arguments"])
                    print(f"  -> {name}({args})")
                    if name in LOCAL_TOOLS:                    # CLI surface
                        result = LOCAL_TOOLS[name]["fn"](**args)
                    elif name in mcp_names:                    # MCP surface
                        r = await session.call_tool(name, args)
                        result = r.content[0].text if r.content else "{}"
                    else:
                        result = json.dumps({"error": f"unknown tool {name}"})
                    print(f"  <- {result[:150]}")
                    messages.append({"role": "tool", "content": result})

            print("Stopped: too many tool iterations.")


if __name__ == "__main__":
    task = ("Gather: number of Python files, number of markdown files, "
            "and the 3 most recent commits. Then write the report.")
    asyncio.run(run(task))
