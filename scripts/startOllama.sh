#!/usr/bin/env bash
# Re-attach: make sure the Ollama server is running (used by postAttachCommand).
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Starting Ollama server..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 2
fi
echo "Ollama server is running."
