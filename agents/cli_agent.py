"""Lab 2: Tools from the command line.

Same agent loop as Lab 1, but now the tools are existing CLI programs:
grep, pytest, git, and tail. The agent sees exactly what a human would
see in a terminal — raw stdout, stderr, and an exit code.

Notice as you run this how messy raw CLI output is for a model: no
structure, mixed signal and noise, and output that can be huge.
"""

import json
import os
import subprocess

from llm import chat, extract_json, observation_message, which_backend

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_OUTPUT = 3000  # characters of command output we let into the context


# ---------------------------------------------------------------------------
# A generic runner for CLI commands
# ---------------------------------------------------------------------------

def run_command(cmd):
    """Run a command list, capture everything, and format it for the model."""
    # TODO: Lab 2 merge step — run the command with subprocess, capture
    # stdout/stderr/exit code, enforce a timeout, and truncate long output.
    raise NotImplementedError("merge in the completed code (see labs.md)")


# ---------------------------------------------------------------------------
# Tools: thin wrappers around real CLI programs
# ---------------------------------------------------------------------------

def grep_code(pattern):
    """Search the sample app's source for a pattern using grep."""
    # TODO: Lab 2 merge step — call run_command with the right grep invocation.
    raise NotImplementedError("merge in the completed code (see labs.md)")


def run_tests():
    """Run the sample app's test suite with pytest."""
    # TODO: Lab 2 merge step — call run_command with the right pytest invocation.
    raise NotImplementedError("merge in the completed code (see labs.md)")


def git_history():
    """Show the last five commits using git."""
    # TODO: Lab 2 merge step — call run_command with the right git invocation.
    raise NotImplementedError("merge in the completed code (see labs.md)")


def tail_log(lines):
    """Show the last N lines of the application log using tail."""
    # TODO: Lab 2 merge step — call run_command with the right tail invocation.
    raise NotImplementedError("merge in the completed code (see labs.md)")


TOOLS = {
    "grep_code": {
        "function": grep_code,
        "description": "Search the sample app source code for a pattern (runs grep).",
        "args": {"pattern": "string, text or regex to search for"},
    },
    "run_tests": {
        "function": run_tests,
        "description": "Run the sample app test suite (runs pytest).",
        "args": {},
    },
    "git_history": {
        "function": git_history,
        "description": "Show the last five commits in this repo (runs git log).",
        "args": {},
    },
    "tail_log": {
        "function": tail_log,
        "description": "Show the last N lines of the application log (runs tail).",
        "args": {"lines": "integer, number of lines, e.g. 20"},
    },
}


# ---------------------------------------------------------------------------
# The agent loop (same shape as Lab 1)
# ---------------------------------------------------------------------------

def build_system_prompt():
    lines = [
        "You are a software engineer's assistant that can use tools to investigate a repository.",
        "You have access to these tools:",
        "",
    ]
    for name, tool in TOOLS.items():
        lines.append(f"- {name}: {tool['description']} Args: {json.dumps(tool['args'])}")
    lines += [
        "",
        "To use a tool, reply with ONLY a JSON object like:",
        '  {"tool": "<tool name>", "args": {"<arg>": "<value>"}}',
        "When you have enough information to answer, reply with ONLY:",
        '  {"final": "<your answer>"}',
        "Use one tool at a time. Do not include any other text.",
    ]
    return "\n".join(lines)


def run_agent(task, max_steps=8):
    print(f"[backend: {which_backend()}]")
    print(f"Task: {task}\n")
    messages = [
        {"role": "system", "content": build_system_prompt()},
        {"role": "user", "content": task},
    ]
    for step in range(1, max_steps + 1):
        reply = chat(messages)
        action = extract_json(reply)
        if action is None:
            print(f"--- step {step}: unparseable reply, asking model to retry")
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "Reply with ONLY a valid JSON object as instructed."})
            continue
        if "final" in action:
            print(f"\n=== FINAL ANSWER (after {step - 1} tool calls) ===")
            print(action["final"])
            return action["final"]
        tool_name = action.get("tool")
        args = action.get("args", {})
        if tool_name not in TOOLS:
            observation = f"ERROR: unknown tool '{tool_name}'"
        else:
            try:
                observation = TOOLS[tool_name]["function"](**args)
            except TypeError as e:
                observation = f"ERROR: bad arguments: {e}"
        print(f"--- step {step}: {tool_name}({json.dumps(args)})")
        shown = observation[:200]
        more = " ... [truncated for display - the model receives the full text]" if len(observation) > 200 else ""
        print(f"    observation: {shown}{more}")
        messages.append({"role": "assistant", "content": json.dumps(action)})
        messages.append({"role": "user", "content": observation_message(observation, max_steps - step)})
    print("\n=== Gave up: reached max steps without a final answer ===")
    return None


if __name__ == "__main__":
    import sys

    task = " ".join(sys.argv[1:]) or (
        "Run the test suite and tell me which test fails and why."
    )
    run_agent(task)
