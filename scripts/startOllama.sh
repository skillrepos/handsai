#!/usr/bin/env bash
# Make sure the Ollama server is running and the workshop model is loaded.
#
# Safe to run as often as you like: when everything is already up it costs one
# local HTTP call and exits. Run it any time Ollama looks unresponsive:
#
#     bash scripts/startOllama.sh
#
# --quiet prints only when something was actually wrong (used by the ~/.bashrc
# check that runs in every new terminal).
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/ollama-lib.sh
source "$SCRIPT_DIR/ollama-lib.sh"

QUIET=""
case "${1:-}" in
    -q | --quiet) QUIET="quiet" ;;
esac

if ! ollama_installed; then
    # The Codespace setup step never finished - finish it now instead of
    # handing the student a command to run.
    [ -z "$QUIET" ] && echo "Ollama is not installed yet - running the full setup..."
    exec bash "$SCRIPT_DIR/startup_ollama.sh"
fi

ollama_ensure_server 60 "$QUIET" || exit 1

if ollama_have_model "$OLLAMA_MODEL"; then
    ollama_warm_model_detached "$OLLAMA_MODEL"
    [ -z "$QUIET" ] && echo "Ollama server is running with $OLLAMA_MODEL."
elif [ -n "$QUIET" ]; then
    # Don't block a new terminal on a multi-minute download.
    echo "Ollama is running, but model $OLLAMA_MODEL is not downloaded."
    echo "Run: bash $SCRIPT_DIR/startup_ollama.sh"
else
    ollama_ensure_model "$OLLAMA_MODEL" || exit 1
    ollama_warm_model_detached "$OLLAMA_MODEL"
    echo "Ollama server is running with $OLLAMA_MODEL."
fi
exit 0
