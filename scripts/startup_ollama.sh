#!/usr/bin/env bash
# Install Ollama and pull the workshop model.
MODEL=${OLLAMA_MODEL:-llama3.2:3b}

if ! command -v ollama &> /dev/null; then
    # Ollama's installer extracts a .tar.zst archive and needs zstd, which the
    # base image doesn't ship (verified 09/2026: without it the install fails).
    if ! command -v zstd &> /dev/null; then
        echo "Installing zstd (required by the Ollama installer)..."
        sudo apt-get update -qq > /dev/null 2>&1
        sudo apt-get install -y -qq zstd > /dev/null 2>&1
    fi
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# OLLAMA_KEEP_ALIVE=-1 keeps the model loaded between labs instead of unloading it
# after 5 idle minutes (a reload costs 15s-2min on a 4-core Codespace).
echo "Starting Ollama server..."
OLLAMA_KEEP_ALIVE=-1 nohup ollama serve > /tmp/ollama.log 2>&1 &

# Wait for the server to come up
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        break
    fi
    sleep 1
done

echo "Pulling model $MODEL (this can take a few minutes)..."
ollama pull "$MODEL"
echo "Loading $MODEL into memory..."
curl -s http://localhost:11434/api/generate -d "{\"model\": \"$MODEL\", \"keep_alive\": -1}" > /dev/null
echo "Ollama ready with $MODEL."
