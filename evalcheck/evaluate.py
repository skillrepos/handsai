"""
Lab 8 - Trust but Verify: Evaluating Tool Choice
A tiny eval harness: for each golden task, does the model pick the
tool we expect? Run it after every tool or description change.
Note: this file is incomplete -- you'll merge in the working code
during the lab.
"""
import json
import sys
from pathlib import Path

import ollama

sys.path.insert(0, "agent")
from git_tools import TOOLS  # noqa: E402  (the Lab 3 tool schemas)

MODEL = "llama3.2:3b"
GOLDEN = Path("evalcheck/golden_set.jsonl")


def first_tool_choice(task: str) -> str | None:
    """Ask the model once and return the name of the first tool it picks."""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": "You answer questions about this git repository "
                        "using the provided tools."},
            {"role": "user", "content": task},
        ],
        tools=TOOLS,
    )
    calls = response["message"].get("tool_calls") or []
    return calls[0]["function"]["name"] if calls else None


# ---------------------------------------------------------------
# TODO (merge): main - load the golden set, score each case as
# PASS/FAIL, and print a summary the team can track over time.
# ---------------------------------------------------------------
def main() -> None:
    raise NotImplementedError("Merge in main from extra/evaluate_complete.txt")


if __name__ == "__main__":
    main()
