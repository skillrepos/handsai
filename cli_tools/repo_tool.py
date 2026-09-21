"""Lab 3: An agent-friendly CLI tool.

In Lab 2 the agent used raw CLI programs and had to wade through
unstructured output. This program is a CLI designed *for an agent*:

  - clear inputs:       named arguments with types and defaults
  - predictable output: always a single JSON object on stdout
  - capped output:      results are limited on purpose, so one noisy
                        command can't fill the model's context
  - useful help:        --help text doubles as the tool description
  - errors that explain themselves: failures are JSON too, same shape
  - exit codes that tell the truth: 0 = success, 1 = the operation
                        failed, 2 = the caller got the syntax wrong

Try it yourself before giving it to the agent:
  python cli_tools/repo_tool.py search --pattern total_value
  python cli_tools/repo_tool.py tests
  python cli_tools/repo_tool.py log-summary --level ERROR
  python cli_tools/repo_tool.py ticket --title "Demo" --body "Opened by hand"
"""

import argparse
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(REPO_ROOT, "inventory_service", "logs", "app.log")
TICKETS_FILE = os.path.join(REPO_ROOT, "inventory_service", "tickets.json")


# ---------------------------------------------------------------------------
# The operations (pure functions that return dicts)
# ---------------------------------------------------------------------------

def do_search(pattern, max_results=20):
    """Search the sample app source for a pattern. Returns structured matches."""
    # TODO: Lab 3 merge step — validate the pattern, walk inventory_service/*.py,
    # collect structured matches (file, line, text), and bound the results.
    return {"ok": False, "error": "not implemented yet — merge in the completed code"}


def do_tests():
    """Run the sample app's tests and return a structured summary."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "inventory_service", "-q", "-rf", "--tb=no"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    failed = []
    for line in result.stdout.splitlines():
        if line.startswith("FAILED "):
            failed.append(line[len("FAILED "):].strip())
    counts = {"passed": 0, "failed": 0}
    for number, word in re.findall(r"(\d+) (failed|passed)", result.stdout):
        counts[word] = int(number)
    return {
        "ok": True,
        "exit_code": result.returncode,
        "passed": counts["passed"],
        "failed": counts["failed"],
        "failures": failed,
    }


def do_log_summary(level="ERROR"):
    """Summarize the application log: counts by level plus recent messages."""
    # TODO: Lab 3 merge step — validate the level, parse each log line,
    # count entries per level, and return the last few messages at the
    # requested level.
    return {"ok": False, "error": "not implemented yet — merge in the completed code"}


def do_ticket(title, body):
    """Open a ticket: append it to the ticket store and return its id."""
    # TODO: Lab 3 merge step — validate inputs, load the ticket store,
    # append a new ticket with a generated id, save, and return the ticket.
    return {"ok": False, "error": "not implemented yet — merge in the completed code"}


# ---------------------------------------------------------------------------
# The command-line interface
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="repo_tool",
        description="Agent-friendly repo operations. All output is a single JSON object.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("search", help="Search sample app source code for a regex pattern.")
    p.add_argument("--pattern", required=True, help="text or regex to search for")
    p.add_argument("--max-results", type=int, default=20, help="limit matches returned")

    sub.add_parser("tests", help="Run the sample app test suite and summarize results.")

    p = sub.add_parser("log-summary", help="Summarize the application log by level.")
    p.add_argument("--level", default="ERROR", help="INFO, WARNING, or ERROR")

    p = sub.add_parser("ticket", help="Open a ticket in the ticket store.")
    p.add_argument("--title", required=True, help="short ticket title")
    p.add_argument("--body", required=True, help="ticket description")

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "search":
        result = do_search(args.pattern, args.max_results)
    elif args.command == "tests":
        result = do_tests()
    elif args.command == "log-summary":
        result = do_log_summary(args.level)
    elif args.command == "ticket":
        result = do_ticket(args.title, args.body)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
