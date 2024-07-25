#!/bin/bash
set -e

log() {
    echo "$(date): $1" >&2
}

if [[ -z "${APP_PATH}" ]]; then
    log "Error: APP_PATH is not set"
    exit 1
fi

log "Starting Flask application"
#tail -f /dev/null
python3 "${APP_PATH}"
log "Flask application exited"