#!/usr/bin/env bash
# One-time setup (devcontainer postCreateCommand): install Ollama, start the
# server, download the workshop model, and install the check that keeps the
# server up for the life of the Codespace.
#
# Re-running this is safe - every step is skipped if it is already done.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/ollama-lib.sh
source "$SCRIPT_DIR/ollama-lib.sh"

if ! ollama_installed; then
    # Ollama's installer extracts a .tar.zst archive and needs zstd, which the
    # base image doesn't ship (verified 09/2026: without it the install fails).
    if ! command -v zstd > /dev/null 2>&1; then
        echo "Installing zstd (required by the Ollama installer)..."
        sudo apt-get update -qq > /dev/null 2>&1
        sudo apt-get install -y -qq zstd > /dev/null 2>&1
    fi
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

if ! ollama_installed; then
    echo "Ollama did not install. Check the output above, then re-run:" >&2
    echo "  bash scripts/startup_ollama.sh" >&2
    exit 1
fi

ollama_install_shell_hook
ollama_ensure_server 60 || exit 1
ollama_ensure_model "$OLLAMA_MODEL" || exit 1

echo "Loading $OLLAMA_MODEL into memory..."
ollama_warm_model "$OLLAMA_MODEL"
echo "Ollama ready with $OLLAMA_MODEL."
