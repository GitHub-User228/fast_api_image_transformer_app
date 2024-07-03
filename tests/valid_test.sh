#!/usr/bin/env bash

SCRIPT_DIR=$(dirname "$(dirname "$(realpath "$0")")")
IMAGE_DIR="$SCRIPT_DIR/images/image.png"
TRANSFORMED_IMAGE_DIR="$SCRIPT_DIR/images/transformed.png"
PROMPT="make%image%like%it%is%from%evangelion"

curl -X 'POST' \
  "http://127.0.0.1/images/?prompt=$PROMPT" \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F "file=@$IMAGE_DIR;type=image/png"

curl -X 'GET' 'http://127.0.0.1/images/' --output $TRANSFORMED_IMAGE_DIR