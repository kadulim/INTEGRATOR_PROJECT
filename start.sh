#!/bin/bash
set -e

# Adiciona a raiz do projeto e a API CodeFlow ao PYTHONPATH
API_DIR="$(dirname "$0")/api_codeflow/api"
PROJECT_ROOT="$(pwd)"
export PYTHONPATH="$PROJECT_ROOT:$API_DIR:$PYTHONPATH"

exec gunicorn app:app \
  --bind "0.0.0.0:$PORT" \
  --worker-class sync \
  --threads 4 \
  --timeout 120
