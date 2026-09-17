#!/usr/bin/env bash
set -euo pipefail

root="${1:-runs/retention_5round_single_seed_train16_eval16_b128_v1}"
config="configs/retention_5round_single_seed_n16_local.yaml"
python_bin="${PYTHON_BIN:-/root/miniconda3/envs/improving-iclr/bin/python}"
tasks="data/mbpp/eval.jsonl"
output_root="$root/supplemental_eval64"

run_one() {
  local method="$1"
  local checkpoint="$2"
  local output="$output_root/$method"
  mkdir -p "$output"

  if [[ ! -f "$output/evaluation.jsonl" ]]; then
    if [[ -n "$checkpoint" ]]; then
      "$python_bin" -u -m improving generate \
        --config "$config" --checkpoint "$checkpoint" --tasks "$tasks" \
        --samples 64 --output "$output/evaluation.jsonl" --resume
    else
      "$python_bin" -u -m improving generate \
        --config "$config" --tasks "$tasks" \
        --samples 64 --output "$output/evaluation.jsonl" --resume
    fi
  fi

  if [[ ! -f "$output/evaluation.verified.jsonl" ]]; then
    "$python_bin" -u -m improving verify \
      --tasks "$tasks" --samples "$output/evaluation.jsonl" \
      --output "$output/evaluation.verified.jsonl" --backend local \
      --allow-unsafe-local --code-extraction first_fence --workers 8 \
      --timeout 5 --expected-samples 64
  fi

  if [[ ! -f "$output/evaluation.metrics.json" ]]; then
    "$python_bin" -u -m improving metrics \
      --tasks "$tasks" --samples "$output/evaluation.verified.jsonl" \
      --output "$output/evaluation.metrics.json" --expected-samples 64 \
      --ks 1,4,8,16,64 --correct-budget 4 \
      --correct-budgets 4,8,16,64 --bootstrap-samples 2000 --seed 43
  fi
}

run_one base ""
run_one plain "$root/plain/round_5/model"
run_one spd_hard "$root/spd_hard/round_5/model"
run_one spectral_soft "$root/spectral_soft/round_5/model"

"$python_bin" scripts/summarize_final_eval64.py "$root"

printf 'Supplemental 64-sample evaluation completed: %s\n' "$output_root"
