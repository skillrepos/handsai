#!/bin/bash
# Set (or remove) your Groq API key for this terminal AND every future terminal.
#
#   source scripts/setup-key.sh              # prompts for the key
#   source scripts/setup-key.sh gsk_...      # key on the command line
#   source scripts/setup-key.sh --remove     # go back to the local Ollama model
#
# Every lab program checks GROQ_API_KEY: set -> Groq's hosted model, unset -> Ollama.
# Use "source" (not "bash") so the variable lands in the terminal you're using.

if [ "$1" = "--remove" ]; then
  unset GROQ_API_KEY
  sed -i '/^export GROQ_API_KEY=/d' ~/.bashrc 2>/dev/null
  echo "Done! GROQ_API_KEY removed - the labs will use the local Ollama model."
  return 0 2>/dev/null || exit 0
fi

if [ -n "$1" ]; then
  KEY="$1"
else
  read -rp "Enter your Groq API key: " KEY
fi

if [ -z "$KEY" ]; then
  echo "Error: No key provided. Exiting."
  return 1 2>/dev/null || exit 1
fi

# Set for the current terminal
export GROQ_API_KEY="$KEY"

# Set for all future terminals (replace an old line rather than adding a duplicate)
if grep -q "^export GROQ_API_KEY=" ~/.bashrc 2>/dev/null; then
  sed -i "s|^export GROQ_API_KEY=.*|export GROQ_API_KEY=$KEY|" ~/.bashrc
else
  echo "export GROQ_API_KEY=$KEY" >> ~/.bashrc
fi

echo "Done! GROQ_API_KEY is set (${#KEY} chars) for this and all future terminals."
echo "The labs will now use Groq. Run 'bash scripts/check-groq.sh' to confirm the model is reachable."
