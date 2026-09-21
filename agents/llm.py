"""Shared LLM access for all workshop agents.

Every agent in this workshop talks to a model through the single chat()
function below. By default it uses the local Ollama server (llama3.2:3b).
If the environment variable GROQ_API_KEY is set, it uses Groq's
OpenAI-compatible API with a larger hosted model instead. Both are free.

Groq notes (free tier, verified 09/2026):
  - Default model is qwen/qwen3.8-27b: it follows the labs' "reply with a
    JSON action" convention reliably. (openai/gpt-oss-* models insist on
    native function calling and reject prompt-style JSON actions.)
  - qwen3.8 is a "thinking" model whose reasoning tokens count against the
    free tier's small output-tokens-per-minute limit, so chat() turns
    thinking off and caps max_tokens. Agent replies are short JSON anyway.
  - The free tier also has a daily token budget (200K/day for this model
    when checked). If it runs out mid-workshop, chat() falls back to the
    local Ollama model automatically and says so on stderr.
"""

import json
import os
import re
import sys

from openai import OpenAI, RateLimitError

GROQ_DEFAULT_MODEL = "qwen/qwen3.8-27b"
OLLAMA_DEFAULT_MODEL = "llama3.2:3b"


def which_backend():
    """Return 'groq' or 'ollama' depending on which backend chat() will use."""
    return "groq" if os.environ.get("GROQ_API_KEY") else "ollama"


def get_client_and_model(backend=None):
    """Return an OpenAI-compatible client plus the model name for a backend."""
    backend = backend or which_backend()
    if backend == "groq":
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ["GROQ_API_KEY"],
            max_retries=5,  # free-tier per-minute limits: back off and retry
        )
        model = os.environ.get("GROQ_MODEL", GROQ_DEFAULT_MODEL)
    else:
        client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # required by the client but unused by Ollama
        )
        model = os.environ.get("OLLAMA_MODEL", OLLAMA_DEFAULT_MODEL)
    return client, model


_groq_exhausted = False  # set once Groq reports its daily token budget is spent


def chat(messages, temperature=0.0):
    """Send a list of chat messages to the model and return its reply text.

    Groq's free tier has a per-day token budget as well as per-minute limits.
    Per-minute limits are handled by the client's retries; if the daily budget
    runs out, every later call in this process falls back to the local Ollama
    model so a lab never dies mid-run.
    """
    global _groq_exhausted
    backend = which_backend()
    if backend == "groq" and _groq_exhausted:
        backend = "ollama"
    client, model = get_client_and_model(backend)
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 600,  # agent replies are short JSON; keeps within rate limits
    }
    if backend == "groq":
        kwargs["reasoning_effort"] = "none"  # no hidden thinking tokens
    try:
        response = client.chat.completions.create(**kwargs)
    except RateLimitError as e:
        if backend == "groq" and "per day" in str(e).lower():
            _groq_exhausted = True
            print("[groq: daily token budget used up - falling back to local Ollama]", file=sys.stderr)
            return chat(messages, temperature)
        raise
    return response.choices[0].message.content


def observation_message(observation, steps_left):
    """Wrap a tool observation in the message the model sees next.

    Small models tend to keep calling tools after they already have the
    answer, so every observation ends with a reminder of how to finish —
    and the last one insists on it.
    """
    if steps_left <= 1:
        return (
            f"Observation:\n{observation}\n\n"
            "You have no tool calls left. Reply with ONLY "
            '{"final": "<your answer, based on the observations so far>"}.'
        )
    return (
        f"Observation:\n{observation}\n\n"
        'If you can answer the task now, reply with ONLY {"final": "<answer>"}. '
        "Otherwise call one more tool."
    )


def extract_json(text):
    """Pull the first JSON object out of a model reply.

    Small models often wrap JSON in prose or a Markdown code fence. This
    helper finds the first balanced {...} block and parses it. Returns a
    dict, or None if no valid JSON object is found.
    """
    if text is None:
        return None
    # Strip a Markdown code fence if present
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start : i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None
