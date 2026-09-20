"""
Lab 3 - Designing Agent-Friendly Tools
Instead of one raw shell, give the agent a small set of purpose-built
tools with clear names, typed inputs, and predictable JSON outputs.
Note: this file is incomplete -- you'll merge in the working code
during the lab.
"""
import json
import subprocess
import ollama

MODEL = "llama3.2:3b"


def _git(*args: str) -> subprocess.CompletedProcess:
    """Run git with fixed arguments (no shell string parsing)."""
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, timeout=10
    )


def git_status() -> str:
    """Summarize working-tree state as structured data."""
    proc = _git("status", "--porcelain")
    if proc.returncode != 0:
        return json.dumps({"error": proc.stderr.strip()})
    changes = [line[3:] for line in proc.stdout.splitlines()]
    return json.dumps({"changed_files": changes, "clean": not changes})


# ---------------------------------------------------------------
# TODO (merge): git_log - return the last N commits as a list of
# {hash, author, subject} objects instead of raw text.
# ---------------------------------------------------------------
def git_log(count: int = 5) -> str:
    raise NotImplementedError("Merge in git_log from extra/git_tools_complete.txt")


# ---------------------------------------------------------------
# TODO (merge): count_files - count files matching a glob pattern,
# returning {pattern, count} JSON.
# ---------------------------------------------------------------
def count_files(pattern: str = "*.py") -> str:
    raise NotImplementedError("Merge in count_files from extra/git_tools_complete.txt")


FUNCTIONS = {"git_status": git_status, "git_log": git_log, "count_files": count_files}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "git_status",
            "description": "Report which files in the repository have "
                           "uncommitted changes.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "git_log",
            "description": "Get the most recent commits with hash, author, "
                           "and subject line.",
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "integer",
                              "description": "How many commits (default 5)"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "count_files",
            "description": "Count files in the repository matching a glob "
                           "pattern such as '*.py' or '*.md'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string",
                                "description": "Glob pattern, e.g. '*.py'"}
                },
                "required": ["pattern"],
            },
        },
    },
]


def run_agent(task: str) -> None:
    messages = [
        {"role": "system",
         "content": "You answer questions about this git repository using "
                    "the provided tools. Answer concisely."},
        {"role": "user", "content": task},
    ]

    for _ in range(6):
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
        msg = response["message"]
        messages.append(msg)

        if not msg.get("tool_calls"):
            print(f"ANSWER: {msg['content']}")
            return

        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            print(f"  -> model chose tool: {name}({args})")
            fn = FUNCTIONS.get(name)
            result = fn(**args) if fn else json.dumps({"error": f"unknown tool {name}"})
            print(f"  <- {result[:200]}")
            messages.append({"role": "tool", "content": result})

    print("Stopped: too many tool iterations.")


if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) or "What were the last 3 commits in this repo?"
    print(f"TASK: {task}\n")
    run_agent(task)
