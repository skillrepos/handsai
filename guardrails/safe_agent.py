"""
Lab 7 - Guardrails
The Lab 2 shell agent, now with four layers of protection:
allowlisted commands, parameter validation, a human approval gate,
and an audit log of every action.
Note: this file is incomplete -- you'll merge in the working code
during the lab.
"""
import json
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import ollama
from pydantic import BaseModel, field_validator

MODEL = "llama3.2:3b"
AUDIT_LOG = Path("guardrails/audit_log.jsonl")

# Guardrail 1: only these programs may run at all
ALLOWED_PROGRAMS = {"ls", "wc", "grep", "find", "cat", "head", "git", "echo"}

# Commands matching these need a human "y" before running
NEEDS_APPROVAL = {"git"}


# ---------------------------------------------------------------
# Guardrail 2: parameter validation with pydantic
# ---------------------------------------------------------------
class CommandRequest(BaseModel):
    command: str

    @field_validator("command")
    @classmethod
    def no_shell_tricks(cls, v: str) -> str:
        for bad in [";", "&&", "||", "|", ">", "<", "`", "$("]:
            if bad in v:
                raise ValueError(f"shell operator '{bad}' is not permitted")
        return v


def audit(entry: dict) -> None:
    """Guardrail 4: append every decision to a tamper-evident trail."""
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------
# TODO (merge): safe_run_command - validate, check the allowlist,
# ask a human when required, execute WITHOUT a shell, and audit
# every allow/deny/approve decision.
# ---------------------------------------------------------------
def safe_run_command(command: str) -> str:
    raise NotImplementedError("Merge in safe_run_command from extra/safe_agent_complete.txt")


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run an allowlisted, read-only shell command "
                           "(ls, wc, grep, find, cat, head, git, echo). "
                           "No pipes or redirection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string",
                                "description": "A single simple command"}
                },
                "required": ["command"],
            },
        },
    }
]


def run_agent(task: str) -> None:
    messages = [
        {"role": "system",
         "content": "You are a careful repository assistant. Use simple, "
                    "single commands with no pipes. Answer concisely."},
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
            args = call["function"]["arguments"]
            result = safe_run_command(**args)
            print(f"  <- {result[:200]}")
            messages.append({"role": "tool", "content": result})

    print("Stopped: too many tool iterations.")


if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) or "How many markdown files are here, and what was the last commit?"
    print(f"TASK: {task}\n")
    run_agent(task)
