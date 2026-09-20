#!/usr/bin/env bash
# Re-attach: make sure the Ollama server is running and the model is loaded
# (used by postAttachCommand). OLLAMA_KEEP_ALIVE=-1 keeps the model in memory
# between labs; the curl below loads it now so the first lab doesn't pay for it.
MODEL=${OLLAMA_MODEL:-llama3.2:3b}
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed (the Codespace setup step did not finish)."
    echo "Run:  bash scripts/startup_ollama.sh"
    exit 1
fi
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Starting Ollama server..."
    OLLAMA_KEEP_ALIVE=-1 nohup ollama serve > /tmp/ollama.log 2>&1 &
    for i in {1..30}; do
        curl -s http://localhost:11434/api/tags > /dev/null && break
        sleep 1
    done
fi
curl -s http://localhost:11434/api/generate -d "{\"model\": \"$MODEL\", \"keep_alive\": -1}" > /dev/null &
echo "Ollama server is running."
