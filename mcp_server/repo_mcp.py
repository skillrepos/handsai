"""Lab 5: The same capabilities, exposed as an MCP server.

The Model Context Protocol gives tools a standard, discoverable way in:
each tool has a name, a description (from the docstring), and a typed
input schema (from the type hints) — all generated for us by MCPServer.

Note what we did NOT have to write: no argument parser, no JSON
formatting conventions, no help text. The protocol carries all of that.
The actual logic is imported, unchanged, from the Lab 3 CLI tool.

Run it with:  python mcp_server/repo_mcp.py
(then press Ctrl+C to stop — normally a client launches it for you)
"""

import os
import sys

# Make the repo root importable so we can reuse the Lab 3 logic
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.mcpserver import MCPServer

from cli_tools.repo_tool import do_log_summary, do_search, do_tests, do_ticket

mcp = MCPServer("repo-tools")


@mcp.tool()
def search_code(pattern: str, max_results: int = 20) -> dict:
    """Search the inventory service source code for a regex pattern.

    Returns the match count and a length-capped list of matches, each with
    file, line number, and the matching text.
    """
    return do_search(pattern, max_results)


# TODO: Lab 5 merge step — expose three more tools the same way search_code
# is exposed above: run_tests, summarize_log (with a level argument), and
# open_ticket (with title and body arguments). Each one is a decorated
# function with type hints, a docstring, and a one-line call into the
# imported Lab 3 logic.


if __name__ == "__main__":
    mcp.run()  # serves the tools over stdio
