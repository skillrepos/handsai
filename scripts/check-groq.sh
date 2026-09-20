#!/usr/bin/env bash
# Health check for the Groq setup.
# Usage:  bash scripts/check-groq.sh
set -uo pipefail

# The model the labs use on Groq, and what to try if it has been retired.
# Alternates must follow the labs' "reply with a JSON action" convention;
# Groq's openai/gpt-oss-* models do not (they insist on native tool calling).
PRIMARY="${GROQ_MODEL:-qwen/qwen3.8-27b}"
ALTERNATES="qwen/qwen3.6-27b qwen/qwen3-32b moonshotai/kimi-k2-instruct llama-3.3-70b-versatile"

if [ -z "${GROQ_API_KEY:-}" ]; then
  echo "GROQ_API_KEY = MISSING"
  echo
  echo "Run 'source scripts/setup-key.sh' first (README step 5)."
  exit 1
fi
echo "GROQ_API_KEY = set (${#GROQ_API_KEY} chars)"
echo

echo "Models your key can reach right now:"
curl -sS https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY" \
| python3 -c '
import sys, json
try:
    data = json.load(sys.stdin).get("data", [])
except Exception:
    print("  could not read the model list - check your key"); sys.exit(1)
for m in sorted(d["id"] for d in data):
    print("  " + m)
' || { echo "  request failed - check network or key"; exit 1; }
echo

ping_model() {
  local m="$1" code
  code=$(curl -sS -o /dev/null -w '%{http_code}' \
    https://api.groq.com/openai/v1/chat/completions \
    -H "Authorization: Bearer $GROQ_API_KEY" -H "Content-Type: application/json" \
    -d "{\"model\":\"$m\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":5}")
  [ "$code" = "200" ]
}

if ping_model "$PRIMARY"; then
  echo "OK    labs model  ->  $PRIMARY"
  exit 0
fi
echo "FAIL  labs model  ->  $PRIMARY is not available on your key"
for alt in $ALTERNATES; do
  if ping_model "$alt"; then
    echo "      Use this instead (for this and future terminals):"
    echo "          export GROQ_MODEL=$alt"
    echo "          echo 'export GROQ_MODEL=$alt' >> ~/.bashrc"
    exit 0
  fi
done
echo "      No hosted alternative responded. Run the labs on the local model instead:"
echo "          source scripts/setup-key.sh --remove"
exit 1
