#!/usr/bin/env bash
# Install Ollama and pull the workshop model
curl -fsSL https://ollama.com/install.sh | sh
(ollama serve > /tmp/ollama.log 2>&1 &)
sleep 5
ollama pull ${OLLAMA_MODEL:-llama3.2:3b}
