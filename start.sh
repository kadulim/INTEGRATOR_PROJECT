#!/bin/bash
set -e

API_PORT=$((PORT + 1))

cd api_codeflow
FLASK_PORT=$API_PORT gunicorn app:create_app \
  --bind "0.0.0.0:$API_PORT" \
  --worker-class sync \
  --threads 2 \
  --timeout 60 &
cd ../..

sleep 2

exec gunicorn app:app \
  --bind "0.0.0.0:$PORT" \
  --worker-class sync \
  --threads 4 \
  --timeout 120
