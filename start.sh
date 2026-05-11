#!/bin/bash
set -e

# Adiciona a API CodeFlow ao PYTHONPATH
API_DIR="$(dirname "$0")/api_codeflow/api"
export PYTHONPATH="$API_DIR:$PYTHONPATH"

exec gunicorn app:app \
  --bind "0.0.0.0:$PORT" \
  --worker-class sync \
  --threads 4 \
  --timeout 120
