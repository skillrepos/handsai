"""
Lab 6 - Wrapping a CLI Behind MCP
An MCP server whose tools shell out to git -- the wrap pattern:
keep the battle-tested CLI, add a typed, governed protocol surface.
Note: this file is incomplete -- you'll merge in the working code
during the lab.
"""
import json
import subprocess

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("git-wrapped")

# Only these git subcommands may ever run -- the wrap boundary is
# where policy lives.
ALLOWED_SUBCOMMANDS = {"status", "log", "diff", "branch", "show"}


# ---------------------------------------------------------------
# TODO (merge): run_git - validate the subcommand against the
# allowlist, run git with fixed args (no shell), and return
# structured JSON including errors the model can act on.
# ---------------------------------------------------------------
def run_git(subcommand: str, args: list[str]) -> str:
    raise NotImplementedError("Merge in run_git from extra/git_server_complete.txt")


@mcp.tool()
def git_command(subcommand: str, args: list[str] = []) -> str:
    """Run a read-only git subcommand (status, log, diff, branch, show)
    with optional arguments and get structured output back."""
    return run_git(subcommand, args)


@mcp.tool()
def diff_summary() -> str:
    """Summarize how many files changed and how many lines were
    added/removed in the working tree."""
    return run_git("diff", ["--shortstat"])


if __name__ == "__main__":
    mcp.run()
