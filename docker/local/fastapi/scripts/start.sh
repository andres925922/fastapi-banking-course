#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

exec uvicorn src.app.main:create_app --host 0.0.0.0 --port 8000 --reload

set +o errexit
set +o nounset
set +o pipefail