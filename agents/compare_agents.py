"""Lab 7: CLI vs MCP, head-to-head.

Runs the SAME task through two agents that have the SAME capabilities:

  - the Lab 4 agent, whose tools are subcommands of a purpose-built CLI
  - the Lab 6 agent, whose tools are discovered from an MCP server

Each run's full transcript is saved under transcripts/ so you can put
them side by side and compare what the model actually saw. The table also
shows how many tokens each agent sent to the model over the whole run.
"""

import asyncio
import io
import os
import sys
import time
from contextlib import redirect_stdout

import mcp_agent
import structured_agent
from llm import USAGE, reset_usage

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
    reset_usage()
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
        "model_calls": USAGE["model_calls"],
        "prompt_tokens": USAGE["prompt_tokens"],
        "estimated": USAGE["estimated"],
        "final": final,
    }


def save_transcript(run):
    os.makedirs(TRANSCRIPTS, exist_ok=True)
    path = os.path.join(TRANSCRIPTS, f"{run['label']}_transcript.md")
    with open(path, "w") as f:
        f.write(f"# {run['label']} agent transcript\n\n")
        f.write(f"- tool calls: {run['tool_calls']}\n")
        f.write(f"- model calls: {run['model_calls']}\n")
        f.write(f"- prompt tokens sent: {run['prompt_tokens']}\n")
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
    print(f"{'offered as':<12} {'tool calls':<12} {'model calls':<13} {'prompt tokens':<15} {'wall time':<11} {'got answer?':<12}")
    for run in (cli_run, mcp_run):
        answered = "yes" if run["final"] else "no"
        print(
            f"{run['label']:<12} {run['tool_calls']:<12} {run['model_calls']:<13} "
            f"{run['prompt_tokens']:<15} {run['seconds']:<11.1f} {answered:<12}"
        )
    if cli_run["estimated"] or mcp_run["estimated"]:
        print("(prompt tokens estimated at ~4 characters per token: the backend did not report usage)")
    print("\nprompt tokens = everything sent to the model, added up over every call in the run.")
    print("The tool list is re-sent on every call. See: python agents/measure_prompt.py")

    print("\nTranscripts saved:")
    for run in (cli_run, mcp_run):
        print(f"  {os.path.relpath(save_transcript(run), REPO_ROOT)}")
    print("\nOpen both transcripts side by side and compare what the model saw.")


if __name__ == "__main__":
    main()
