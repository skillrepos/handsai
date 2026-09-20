"""Lab 7: CLI vs MCP, head-to-head.

Runs the SAME task through two agents that have the SAME capabilities:

  - the Lab 4 agent, whose tools are subcommands of a purpose-built CLI
  - the Lab 6 agent, whose tools are discovered from an MCP server

Each run's full transcript is saved under transcripts/ so you can put
them side by side and compare what the model actually saw.
"""

import asyncio
import io
import os
import sys
import time
from contextlib import redirect_stdout

import mcp_agent
import structured_agent

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSCRIPTS = os.path.join(REPO_ROOT, "transcripts")

DEFAULT_TASK = (
    "The nightly report is failing. Check the application log for errors, "
    "run the test suite, and report the most likely root cause."
)


def run_captured(label, runner):
    """Run one agent, capturing its transcript and timing."""
    print(f"Running the {label} agent (this can take a few minutes on Ollama)...")
    buffer = io.StringIO()
    start = time.time()
    try:
        with redirect_stdout(buffer):
            final = runner()
    except Exception as e:
        buffer.write(f"\nRUN FAILED: {e}\n")
        final = None
    elapsed = time.time() - start
    transcript = buffer.getvalue()
    steps = sum(1 for line in transcript.splitlines() if line.startswith("--- step"))
    return {
        "label": label,
        "transcript": transcript,
        "seconds": elapsed,
        "tool_calls": steps,
        "final": final,
    }


def save_transcript(run):
    os.makedirs(TRANSCRIPTS, exist_ok=True)
    path = os.path.join(TRANSCRIPTS, f"{run['label']}_transcript.md")
    with open(path, "w") as f:
        f.write(f"# {run['label']} agent transcript\n\n")
        f.write(f"- tool calls: {run['tool_calls']}\n")
        f.write(f"- wall time: {run['seconds']:.1f}s\n")
        f.write(f"- final answer: {run['final'] or '(none)'}\n\n")
        f.write("```\n" + run["transcript"] + "\n```\n")
    return path


def main():
    task = " ".join(sys.argv[1:]) or DEFAULT_TASK
    print(f"Task: {task}\n")

    cli_run = run_captured("cli", lambda: structured_agent.run_agent(task))
    mcp_run = run_captured("mcp", lambda: asyncio.run(mcp_agent.run_agent(task)))

    print("\n=== Comparison ===")
    print(f"{'surface':<10} {'tool calls':<12} {'wall time':<12} {'got answer?':<12}")
    for run in (cli_run, mcp_run):
        answered = "yes" if run["final"] else "no"
        print(f"{run['label']:<10} {run['tool_calls']:<12} {run['seconds']:<12.1f} {answered:<12}")

    print("\nTranscripts saved:")
    for run in (cli_run, mcp_run):
        print(f"  {os.path.relpath(save_transcript(run), REPO_ROOT)}")
    print("\nOpen both transcripts side by side and compare what the model saw.")


if __name__ == "__main__":
    main()
