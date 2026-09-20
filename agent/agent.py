"""
Lab 1 - Your First Agent Loop
A minimal agent: the model reasons over a task, picks a tool,
we execute it, and the model incorporates the result.
Note: this file is incomplete -- you'll merge in the working code
during the lab.
"""
import json
import ollama

MODEL = "llama3.2:3b"


# ---------------------------------------------------------------
# The "hands": plain Python functions the agent can call
# ---------------------------------------------------------------
def calculator(expression: str) -> str:
    """Evaluate a basic math expression like '23 * 7 + 2'."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return json.dumps({"error": "expression contains unsupported characters"})
    try:
        return json.dumps({"result": eval(expression)})
    except Exception as e:
        return json.dumps({"error": str(e)})


def read_file_head(path: str, lines: int = 5) -> str:
    """Return the first N lines of a text file."""
    try:
        with open(path) as f:
            head = [next(f).rstrip() for _ in range(lines)]
        return json.dumps({"path": path, "lines": head})
    except StopIteration:
        return json.dumps({"path": path, "lines": "file has fewer lines"})
    except Exception as e:
        return json.dumps({"error": str(e)})


FUNCTIONS = {"calculator": calculator, "read_file_head": read_file_head}


# ---------------------------------------------------------------
# TODO (merge): TOOLS - the schemas that tell the model what
# hands it has: name, description, and typed parameters.
# ---------------------------------------------------------------
TOOLS = []


def run_agent(task: str) -> None:
    messages = [
        {"role": "system",
         "content": "You are a helpful assistant. Use the provided tools "
                    "when they can answer the question. Answer concisely."},
        {"role": "user", "content": task},
    ]

    # -----------------------------------------------------------
    # TODO (merge): the agent loop -
    #   1. send messages + TOOLS to the model
    #   2. if the model asks for tool calls, run each one
    #   3. append each result and loop so the model can use it
    #   4. otherwise print the model's final answer and stop
    # -----------------------------------------------------------
    raise NotImplementedError("Merge in the agent loop from extra/agent_complete.txt")


if __name__ == "__main__":
    import sys
    task = " ".join(sys.argv[1:]) or "What is 23 * 7 + 2?"
    print(f"TASK: {task}\n")
    run_agent(task)
