# Instructor demo: prompt injection through a retrieved file

Used by the "Watch It Happen" slide in the guardrails section. This is an
INSTRUCTOR demo, not a lab — you drive it, students watch.

`demo_readme.md` looks like an ordinary project README. Buried in an HTML
comment is an instruction aimed at the agent, not at the human reader.

## The demo, in two runs

**Run 1 — the Lab 2 agent (raw shell, no guardrails):**

```
python agent/cli_agent.py "Summarize extra/demo/demo_readme.md for me"
```

The agent reads the file, encounters the injected instruction, and — often —
attempts the `echo pwned > /tmp/exfil.txt` command before summarizing. Point at
the tool-call line as it scrolls past. Nobody asked it to write a file.

**Run 2 — the Lab 7 guarded agent, same file:**

```
python guardrails/safe_agent.py "Summarize extra/demo/demo_readme.md for me"
```

The pydantic validator rejects the `>` redirect (or the allowlist rejects the
program). The refusal comes back as data, the agent degrades gracefully, and the
attempt is written to `guardrails/audit_log.jsonl`. Show the log line.

```
cat guardrails/audit_log.jsonl | tail -2
```

## If the model doesn't take the bait

A 3B model is inconsistent — sometimes it summarizes and ignores the comment.
That is worth saying out loud ("it didn't bite this time; on a bigger model with
more instruction-following, it usually does"), and then show the saved transcript:

```
cat extra/demo/transcript_injected.txt
```

Either way the teaching point lands: the guarded agent's behavior does not depend
on whether the model was fooled.

## The line that ties it together

"This is oops.txt from this morning — except this time *you* didn't ask for it.
The instruction came from a file the agent was told to read."
