#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

# If you want to enable reload for local dev only, set ENV DEV_RELOAD=1 in .env
# This script respects DEV_RELOAD. In production do not set it.

APP_MODULE=${APP_MODULE:-main:create_app}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
DEV_RELOAD=${DEV_RELOAD:-1}

echo "Starting uvicorn (module=${APP_MODULE})"

if [ "${DEV_RELOAD}" = "1" ]; then
  # Restrict reload watcher to the app directory to avoid permission errors
  uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}" --reload --reload-dir /src/app
else
  uvicorn "${APP_MODULE}" --host "${HOST}" --port "${PORT}"
fi