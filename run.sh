#!/usr/bin/env bash

set -Eeuo pipefail

cd "$(dirname "$0")"

python3 experiments/experiment.py
