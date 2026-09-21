#!/usr/bin/env bash
# Shared helpers for getting the Ollama server up and the workshop model loaded.
#
# Sourced by:
#   scripts/startup_ollama.sh  - one-time setup (devcontainer postCreateCommand)
#   scripts/startOllama.sh     - every attach, every new terminal, manual runs
#
# The important detail in here is ollama_start_detached: the server is started
# in its OWN session (setsid). A plain "nohup ollama serve &" stays in the
# process group of whatever started it, so it dies when the devcontainer
# lifecycle command that launched it is cleaned up, and it dies again if anyone
# presses Ctrl-C in the terminal that ran the script. A new session is in
# neither, so the server survives both.

OLLAMA_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2:3b}"
OLLAMA_LOG="${OLLAMA_LOG:-/tmp/ollama.log}"
OLLAMA_LOCK="${OLLAMA_LOCK:-/tmp/ollama-start.lock}"

ollama_installed() {
    command -v ollama > /dev/null 2>&1
}

# Is the server answering right now?
ollama_up() {
    curl -sf --max-time 3 "$OLLAMA_URL/api/tags" > /dev/null 2>&1
}

ollama_start_detached() {
    if command -v setsid > /dev/null 2>&1; then
        OLLAMA_KEEP_ALIVE=-1 setsid ollama serve > "$OLLAMA_LOG" 2>&1 < /dev/null &
    else
        OLLAMA_KEEP_ALIVE=-1 nohup ollama serve > "$OLLAMA_LOG" 2>&1 < /dev/null &
        disown 2> /dev/null || true
    fi
}

# Wait for the server, printing progress so nobody thinks it has hung.
# $1 = seconds to wait, $2 = "quiet" to skip the progress lines
ollama_wait_up() {
    local timeout="${1:-60}" quiet="${2:-}" waited=0
    while [ "$waited" -lt "$timeout" ]; do
        ollama_up && return 0
        sleep 1
        waited=$((waited + 1))
        if [ -z "$quiet" ] && [ $((waited % 5)) -eq 0 ]; then
            echo "  ...still starting (${waited}s)"
        fi
    done
    ollama_up
}

# Start the server if it isn't already up. Safe to call from several terminals
# at once - the lock means only one of them actually starts a server.
# $1 = seconds to wait, $2 = "quiet"
ollama_ensure_server() {
    local timeout="${1:-60}" quiet="${2:-}" locked=""

    ollama_up && return 0

    # Note the braces: "exec 9>file 2>/dev/null" would redirect this shell's
    # stderr to /dev/null permanently, swallowing every later error message.
    if command -v flock > /dev/null 2>&1; then
        if { exec 9> "$OLLAMA_LOCK"; } 2> /dev/null; then
            flock -w "$((timeout + 30))" 9 && locked="yes"
        fi
    fi

    # Another terminal may have won the race while we waited for the lock.
    if ollama_up; then
        [ -n "$locked" ] && exec 9>&-
        return 0
    fi

    [ -z "$quiet" ] && echo "Starting the Ollama server (a few seconds - please don't Ctrl-C)..."
    ollama_start_detached
    ollama_wait_up "$timeout" "$quiet"
    local rc=$?
    [ -n "$locked" ] && exec 9>&-

    if [ "$rc" -ne 0 ]; then
        echo "The Ollama server did not come up. Last lines of $OLLAMA_LOG:" >&2
        tail -n 15 "$OLLAMA_LOG" >&2 2> /dev/null
        return 1
    fi
    return 0
}

# Has the model been downloaded? (an untagged name means the :latest tag)
ollama_have_model() {
    local want="${1:-$OLLAMA_MODEL}"
    case "$want" in
        *:*) ;;
        *) want="$want:latest" ;;
    esac
    ollama list 2> /dev/null | awk 'NR > 1 { print $1 }' | grep -qxF "$want"
}

ollama_ensure_model() {
    local model="${1:-$OLLAMA_MODEL}"
    ollama_have_model "$model" && return 0
    echo "Downloading model $model (1-3 minutes on Codespace bandwidth)..."
    ollama pull "$model"
}

# Load the model into memory so the first lab doesn't pay for it.
# OLLAMA_KEEP_ALIVE=-1 on the server keeps it there instead of unloading it
# after 5 idle minutes (a reload costs 15s-2min on a 4-core Codespace).
ollama_warm_model() {
    local model="${1:-$OLLAMA_MODEL}"
    curl -sf --max-time 900 "$OLLAMA_URL/api/generate" \
        -d "{\"model\": \"$model\", \"keep_alive\": -1}" > /dev/null 2>&1
}

# Same, but detached, for callers that must not block (attach hook, shell hook).
# setsid for the same reason as the server: the caller exiting must not kill it.
ollama_warm_model_detached() {
    local model="${1:-$OLLAMA_MODEL}"
    local cmd="curl -sf --max-time 900 '$OLLAMA_URL/api/generate' -d '{\"model\": \"$model\", \"keep_alive\": -1}'"
    if command -v setsid > /dev/null 2>&1; then
        setsid bash -c "$cmd" > /dev/null 2>&1 < /dev/null &
    else
        nohup bash -c "$cmd" > /dev/null 2>&1 < /dev/null &
        disown 2> /dev/null || true
    fi
}

# Every new terminal re-checks the server. postAttachCommand does not fire on
# every reconnect (reattaching from the CLI, an extension-host restart), so
# this is what actually makes "it is running when I need it" true.
ollama_install_shell_hook() {
    local rc_file="$HOME/.bashrc"
    local marker="# >>> hands-of-ai: keep the Ollama server up >>>"

    grep -qF "$marker" "$rc_file" 2> /dev/null && return 0

    cat >> "$rc_file" <<EOF_HOOK

$marker
# Costs one local HTTP call when the server is already running; restarts it
# quietly when it isn't. Remove this block to opt out.
if [ -f "$OLLAMA_SCRIPT_DIR/startOllama.sh" ]; then
    bash "$OLLAMA_SCRIPT_DIR/startOllama.sh" --quiet
fi
# <<< hands-of-ai: keep the Ollama server up <<<
EOF_HOOK
    echo "Added the Ollama startup check to ~/.bashrc."
}
