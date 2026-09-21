"""Lab 8: Wrapping an existing CLI (git) behind an MCP server.

Sometimes the capability you want already exists as a proven
command-line program. Rather than reimplementing it, you can wrap it:
the MCP server gives the agent a clean, discoverable, checked way in,
and the CLI does the real work underneath.

Two kinds of tool are shown here:

  1. Narrow tools (recent_commits, file_history): each one answers ONE
     question an agent might ask, and exposes no git options at all,
     so there is nothing in them to misuse.
  2. A guarded general-purpose tool (git_readonly): for the git command
     nobody anticipated. It accepts only subcommands on the allowlist,
     and it refuses every option flag.

Run it with the test client:
  python mcp_server/try_server.py mcp_server/git_mcp.py
"""

import os
import subprocess

from mcp.server.mcpserver import MCPServer

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

mcp = MCPServer("git-tools")

# Read-only subcommands git_readonly may run — nothing that writes.
ALLOWED_SUBCOMMANDS = {"log", "show", "status", "branch", "shortlog"}


def _git(args, timeout=30):
    """Run git with the given arguments and return a structured result."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"git timed out after {timeout} seconds"}
    if result.returncode != 0:
        return {"ok": False, "error": result.stderr.strip()[:500]}
    output = result.stdout
    if len(output) > 5000:
        output = output[:5000] + "\n...[truncated]"
    return {"ok": True, "output": output}


@mcp.tool()
def recent_commits(count: int = 5) -> dict:
    """Return the most recent commits in this repository.

    Each commit includes its short hash, author, date, and subject line.
    """
    count = max(1, min(count, 50))  # clamp to a sane range
    result = _git(["log", f"-{count}", "--pretty=format:%h|%an|%ad|%s", "--date=short"])
    if not result["ok"]:
        return result
    commits = []
    for line in result["output"].splitlines():
        if not line.strip():
            continue
        commit_hash, author, date, subject = line.split("|", 3)
        commits.append({
            "hash": commit_hash,
            "author": author,
            "date": date,
            "subject": subject,
        })
    return {"ok": True, "commits": commits}


@mcp.tool()
def file_history(path: str, count: int = 5) -> dict:
    """Return the most recent commits that changed a particular file.

    The path must be repo-relative, for example 'inventory_service/inventory.py'.
    """
    # TODO: Lab 8 merge step — validate the path (no leading '-', must stay
    # inside the repo), clamp count, run git log limited to that path with
    # '--', and return the commits as structured dicts.
    return {"ok": False, "error": "not implemented yet — merge in the completed code"}


@mcp.tool()
def git_readonly(subcommand: str, args: list[str] | None = None) -> dict:
    """Run an allowlisted read-only git subcommand.

    Allowed subcommands: log, show, status, branch, shortlog.
    Arguments may only be refs or paths — options (anything starting
    with '-') are rejected.
    """
    # TODO: Lab 8 merge step — enforce the guardrails: reject subcommands
    # not in ALLOWED_SUBCOMMANDS (say what IS allowed in the error), reject
    # any argument that starts with '-', then run the command via _git.
    return {"ok": False, "error": "not implemented yet — merge in the completed code"}


if __name__ == "__main__":
    mcp.run()  # serves the tools over stdio
