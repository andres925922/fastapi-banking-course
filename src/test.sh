#!/bin/bash

set -o errexit
set -o nounset
set -o pipefail

cd app && pytest --cov --cov-config=.coveragerc -v --cov-report=term-missing