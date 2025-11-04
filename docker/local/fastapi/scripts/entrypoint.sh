#!/usr/bin/env bash
set -o errexit
set -o pipefail
# We handle nounset carefully; set defaults for needed vars
: "${POSTGRES_DB:=postgres}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_PASSWORD:=postgres}"
: "${POSTGRES_HOST:=postgres}"
: "${POSTGRES_PORT:=5432}"

# Wait for Postgres to be ready (psycopg3)
python - <<'PY'
import time, sys, os
import psycopg

RETRY_INTERVAL = 2
MAX_WAIT_TIME = 60
start_time = time.time()

dbname = os.environ.get("POSTGRES_DB", "postgres")
user = os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("POSTGRES_PASSWORD", "postgres")
host = os.environ.get("POSTGRES_HOST", "postgres")
port = os.environ.get("POSTGRES_PORT", "5432")

while True:
    if int(time.time() - start_time) > MAX_WAIT_TIME:
        sys.stderr.write("Timed out waiting for PostgreSQL to become available.\n")
        sys.exit(1)
    try:
        conn = psycopg.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        conn.close()
        sys.stdout.write("PostgreSQL is available!\n")
        break
    except Exception as e:
        sys.stderr.write(f"PostgreSQL is not available yet. Retrying... ({e})\n")
        time.sleep(RETRY_INTERVAL)
PY

# Ensure log dir exists and is writable (when bind-mounted, host ownership takes priority)
if [ ! -d "/src/app/logs" ]; then
  mkdir -p /src/app/logs
  chown -R "${APP_USER:-fastapi}:${APP_GROUP:-fastapi}" /src/app/logs || true
fi

echo "DB up and ready; launching process..."
exec "$@"