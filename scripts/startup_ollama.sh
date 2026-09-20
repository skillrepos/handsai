#!/usr/bin/env bash
# Install Ollama and pull the workshop model.
MODEL=${OLLAMA_MODEL:-llama3.2:3b}

if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "Starting Ollama server..."
nohup ollama serve > /tmp/ollama.log 2>&1 &

# Wait for the server to come up
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null; then
        break
    fi
    sleep 1
done

echo "Pulling model $MODEL (this can take a few minutes)..."
ollama pull "$MODEL"
echo "Ollama ready with $MODEL."
