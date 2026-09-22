"""Lab 4: The agent, now using the agent-friendly CLI.

Same loop as Labs 1 and 2, but every tool is a subcommand of our
purpose-built repo_tool CLI. The observations the model sees are now
compact, predictable JSON instead of raw terminal output.

Compare a run of this agent with the Lab 2 agent on the same task.
"""

import json
import os
import subprocess
import sys

from llm import chat, extract_json, observation_message, which_backend

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# One runner for the repo_tool CLI
# ---------------------------------------------------------------------------

def run_tool(tool_args):
    """Run repo_tool.py with the given arguments and return its JSON output."""
    # TODO: Lab 4 merge step — invoke repo_tool.py via subprocess, parse its
    # stdout as JSON, and return it (with a structured error if parsing fails).
    raise NotImplementedError("merge in the completed code (see labs.md)")


# ---------------------------------------------------------------------------
# Tools: subcommands of repo_tool
# ---------------------------------------------------------------------------

def search_code(pattern):
    # TODO: Lab 4 merge step — call run_tool with the search subcommand.
    raise NotImplementedError("merge in the completed code (see labs.md)")


def run_tests():
    # TODO: Lab 4 merge step — call run_tool with the tests subcommand.
    raise NotImplementedError("merge in the completed code (see labs.md)")


def summarize_log(level):
    # TODO: Lab 4 merge step — call run_tool with the log-summary subcommand.
    raise NotImplementedError("merge in the completed code (see labs.md)")


def open_ticket(title, body):
    # TODO: Lab 4 merge step — call run_tool with the ticket subcommand.
    raise NotImplementedError("merge in the completed code (see labs.md)")


TOOLS = {
    "search_code": {
        "function": search_code,
        "description": "Search the inventory service source code. Returns JSON matches with file and line.",
        "args": {"pattern": "string, text or regex to search for"},
    },
    "run_tests": {
        "function": run_tests,
        "description": "Run the test suite. Returns JSON with passed/failed counts and failure names.",
        "args": {},
    },
    "summarize_log": {
        "function": summarize_log,
        "description": "Summarize the application log. Returns JSON counts by level and recent messages.",
        "args": {"level": "string, one of INFO, WARNING, ERROR"},
    },
    "open_ticket": {
        "function": open_ticket,
        "description": "Open a ticket in the ticket store. Returns JSON with the new ticket id.",
        "args": {"title": "string, short title", "body": "string, description of the issue"},
    },
}


# ---------------------------------------------------------------------------
# The agent loop (same shape as Labs 1 and 2)
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
    task = " ".join(sys.argv[1:]) or (
        "Run the test suite and tell me which test fails and why."
    )
    run_agent(task)
