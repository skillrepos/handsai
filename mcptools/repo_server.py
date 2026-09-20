"""
Lab 4 - Your First MCP Server
The same kind of capabilities as before, but exposed through the
Model Context Protocol: discoverable, schema-described, and usable
by ANY MCP client -- not just our Python agent.
Note: this file is incomplete -- you'll merge in the working code
during the lab.
"""
import json
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("repo-tools")


@mcp.tool()
def file_info(path: str) -> str:
    """Get the size in bytes and line count of a text file in the repo."""
    p = Path(path)
    if not p.is_file():
        return json.dumps({"error": f"{path} is not a file"})
    text = p.read_text(errors="replace")
    return json.dumps({
        "path": path,
        "bytes": p.stat().st_size,
        "lines": text.count("\n") + 1,
    })


# ---------------------------------------------------------------
# TODO (merge): word_count tool - count words in a text file.
# ---------------------------------------------------------------


# ---------------------------------------------------------------
# TODO (merge): recent_commits tool - last N commits as JSON,
# reusing the subprocess pattern from Lab 3.
# ---------------------------------------------------------------


if __name__ == "__main__":
    # stdio transport: the client starts this process and speaks
    # MCP with it over stdin/stdout.
    mcp.run()
