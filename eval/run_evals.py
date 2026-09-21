"""Lab 10: A small evaluation harness for the safe agent.

The same agent can answer differently run to run, so "it worked when
I tried it" is not a
test strategy. This harness runs a set of scenarios through the safe
agent and applies simple checks to each run — plain code, so the same
result always gets the same verdict and no model grades another model:

  final_contains   the final answer mentions an expected string
  final_not_empty  the agent produced a final answer at all
  ticket_created   the ticket store grew during the scenario
  max_tool_calls   the agent stayed within a step budget

Run it with:  python eval/run_evals.py
"""

import asyncio
import io
import json
import os
import sys
from contextlib import redirect_stdout

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "agents"))
sys.path.insert(0, REPO_ROOT)

import safe_agent  # noqa: E402

SCENARIOS_FILE = os.path.join(REPO_ROOT, "eval", "scenarios.json")
TICKETS_FILE = os.path.join(REPO_ROOT, "inventory_service", "tickets.json")

# The harness must run unattended, so approvals are automatic here.
os.environ["SAFE_AGENT_AUTO_APPROVE"] = "yes"


def count_tickets():
    with open(TICKETS_FILE) as f:
        return len(json.load(f))


def run_scenario(scenario):
    """Run one scenario and return (final_answer, tool_calls, tickets_added)."""
    tickets_before = count_tickets()
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            final = asyncio.run(safe_agent.run_agent(scenario["task"]))
    except Exception as e:
        buffer.write(f"\nRUN FAILED: {e}\n")
        final = None
    transcript = buffer.getvalue()
    tool_calls = sum(1 for line in transcript.splitlines() if line.startswith("--- step"))
    tickets_added = count_tickets() - tickets_before
    return final, tool_calls, tickets_added


def run_check(check, final, tool_calls, tickets_added):
    """Apply one check. Plain code, no model involved. Returns (passed, description)."""
    # TODO: Lab 10 merge step — implement the four check types described in
    # the module docstring: final_contains, final_not_empty, ticket_created,
    # and max_tool_calls. Unknown check types should fail loudly.
    raise NotImplementedError("merge in the completed code (see labs.md)")


def main():
    with open(SCENARIOS_FILE) as f:
        scenarios = json.load(f)

    total = passed_count = 0
    for scenario in scenarios:
        print(f"\n=== Scenario: {scenario['name']} ===")
        print(f"    task: {scenario['task']}")
        print("    running (this can take a few minutes on Ollama)...")
        final, tool_calls, tickets_added = run_scenario(scenario)
        for check in scenario["checks"]:
            ok, description = run_check(check, final, tool_calls, tickets_added)
            total += 1
            passed_count += ok
            print(f"    [{'PASS' if ok else 'FAIL'}] {description}")

    print(f"\n=== Results: {passed_count}/{total} checks passed ===")
    if passed_count < total:
        print("Failures are normal with a small local model — that is the point:")
        print("evals tell you HOW OFTEN your agent succeeds, not whether it can.")
        sys.exit(1)


if __name__ == "__main__":
    main()
