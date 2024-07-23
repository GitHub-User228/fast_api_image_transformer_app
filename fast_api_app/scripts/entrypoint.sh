#!/bin/bash
set -e

log() {
    echo "$(date): $1" >&2
}

if [[ -z "${APP_ROOT_PATH}" ]] || [[ -z "${PORT_NUMBER}" ]]; then
    log "Error: APP_ROOT_PATH or PORT_NUMBER is not set"
    exit 1
fi

if ! command -v fastapi &> /dev/null; then
    log "Error: fastapi command not found"
    exit 1
fi


if [ -z "$(ls "${MODEL_PATH}")" ]; then
    log "Model was not found in the volume, downloading it"
    python3 "${APP_ROOT_PATH}/scripts/download_model.py"
    log "Model has been downloaded"
else
    log "Model already exists, skipping download"
fi

log "Starting FastAPI application"
#tail -f /dev/null
fastapi run "${APP_PATH}" --port "${PORT_NUMBER}"
log "FastAPI application exited"