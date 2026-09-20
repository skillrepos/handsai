"""Lab 9: The guardrail policy used by the safe agent.

A policy is deliberately boring code: small, readable, and testable.
Everything here is enforced OUTSIDE the model — the model can ask for
anything, but only calls that pass these checks are executed.
"""

import json
import os
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_LOG = os.path.join(REPO_ROOT, "audit_log.jsonl")

# Only these tools may be called at all, regardless of what a server offers.
ALLOWED_TOOLS = {"search_code", "run_tests", "summarize_log", "open_ticket"}

# These tools have side effects, so a human must approve each call.
APPROVAL_REQUIRED = {"open_ticket"}

# No single string argument may exceed this many characters.
MAX_STRING_ARG = 500


def validate_call(tool_name, args, schema):
    """Check one proposed tool call against the policy and its schema.

    Returns (True, "ok") if the call may proceed, or (False, reason).
    """
    if tool_name not in ALLOWED_TOOLS:
        return False, f"tool '{tool_name}' is not on the allowlist"
    if not isinstance(args, dict):
        return False, "args must be a JSON object"
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
        if key not in args:
            return False, f"missing required argument '{key}'"
    for key, value in args.items():
        if key not in properties:
            return False, f"unexpected argument '{key}'"
        if isinstance(value, str) and len(value) > MAX_STRING_ARG:
            return False, f"argument '{key}' exceeds {MAX_STRING_ARG} characters"
    return True, "ok"


def needs_approval(tool_name):
    """Does this tool require a human sign-off before executing?"""
    return tool_name in APPROVAL_REQUIRED


def audit(event, **details):
    """Append one event to the audit log as a line of JSON."""
    record = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "event": event}
    record.update(details)
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")
