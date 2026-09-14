#!/usr/bin/env bash
set -euo pipefail
config=${1:-configs/pilot_16gb.yaml}
improving validate --config "$config"
improving run --config "$config" --resume
