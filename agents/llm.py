"""Shared LLM access for all workshop agents.

Every agent in this workshop talks to a model through the single chat()
function below. By default it uses the local Ollama server (llama3.2:3b).
If the environment variable GROQ_API_KEY is set, it uses Groq's
OpenAI-compatible API with a larger model instead. Both options are free.
"""

import json
import os
import re

from openai import OpenAI


def get_client_and_model():
    """Return an OpenAI-compatible client plus the model name to use."""
    if os.environ.get("GROQ_API_KEY"):
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ["GROQ_API_KEY"],
        )
        model = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
    else:
        client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # required by the client but unused by Ollama
        )
        model = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
    return client, model


def which_backend():
    """Return 'groq' or 'ollama' depending on which backend chat() will use."""
    return "groq" if os.environ.get("GROQ_API_KEY") else "ollama"


def chat(messages, temperature=0.0):
    """Send a list of chat messages to the model and return its reply text."""
    client, model = get_client_and_model()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content


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
