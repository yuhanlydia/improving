#!/usr/bin/env bash
# Offline official EvalPlus evaluation; no model code executes on the host.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  scripts/evalplus_docker.sh prepare humaneval|mbpp OUTPUT_DIR
  scripts/evalplus_docker.sh evaluate humaneval|mbpp SAMPLES.jsonl OUTPUT_DIR

OUTPUT_DIR must be new or empty. Build docker/EvalPlus.Dockerfile first.
Optional variables (all limits remain enabled):
  IMPROVING_EVALPLUS_IMAGE      improving-evalplus:0.3.1
  IMPROVING_EVALPLUS_PARALLEL   2
  IMPROVING_EVALPLUS_CPUS       2
  IMPROVING_EVALPLUS_MEMORY_MB  4096
  IMPROVING_EVALPLUS_PIDS       256
  IMPROVING_EVALPLUS_WALLTIME   7200 (seconds for the entire container)
  IMPROVING_EVALPLUS_SAMPLE_MB  2048 (EvalPlus per-sample address space)
EOF
}

fail() { printf 'error: %s\n' "$*" >&2; exit 2; }

if [[ ${1:-} == --help || ${1:-} == -h ]]; then
    usage
    exit 0
fi
[[ $# -ge 3 ]] || { usage >&2; exit 2; }
mode=$1
dataset=$2
case "$mode" in
    prepare)
        [[ $# == 3 ]] || fail 'prepare expects DATASET OUTPUT_DIR'
        output_arg=$3
        ;;
    evaluate)
        [[ $# == 4 ]] || fail 'evaluate expects DATASET SAMPLES.jsonl OUTPUT_DIR'
        [[ -f $3 ]] || fail "Samples file does not exist: $3"
        samples_path=$(realpath -- "$3")
        [[ $samples_path != *,* ]] || fail 'Docker bind paths cannot contain commas'
        output_arg=$4
        ;;
    *) fail 'mode must be prepare or evaluate' ;;
esac
[[ $dataset == humaneval || $dataset == mbpp ]] || fail 'dataset must be humaneval or mbpp'

image=${IMPROVING_EVALPLUS_IMAGE:-improving-evalplus:0.3.1}
parallel=${IMPROVING_EVALPLUS_PARALLEL:-2}
cpus=${IMPROVING_EVALPLUS_CPUS:-2}
memory_mb=${IMPROVING_EVALPLUS_MEMORY_MB:-4096}
pids=${IMPROVING_EVALPLUS_PIDS:-256}
walltime=${IMPROVING_EVALPLUS_WALLTIME:-7200}
sample_mb=${IMPROVING_EVALPLUS_SAMPLE_MB:-2048}
for setting in parallel cpus memory_mb pids walltime sample_mb; do
    value=${!setting}
    [[ $value =~ ^[1-9][0-9]*$ && ${#value} -le 8 ]] || fail "$setting must be a positive integer with at most eight digits"
done
(( sample_mb <= memory_mb )) || fail 'Per-sample memory cannot exceed total container memory'
command -v docker >/dev/null || fail 'Docker is required; host execution is not supported'
command -v timeout >/dev/null || fail 'GNU timeout is required for the whole-container time limit'
docker image inspect "$image" >/dev/null 2>&1 || fail "Image is not available locally: $image"

mkdir -p -- "$output_arg"
output_path=$(realpath -- "$output_arg")
[[ $output_path != *,* ]] || fail 'Docker bind paths cannot contain commas'
shopt -s nullglob dotglob
existing=("$output_path"/*)
(( ${#existing[@]} == 0 )) || fail 'Output directory must be empty to prevent stale evaluation results'

run_uid=$(id -u)
run_gid=$(id -g)
if (( run_uid == 0 )); then
    # Keep candidates nonroot even when the caller is root. Only the explicitly
    # requested, empty output directory changes owner.
    run_uid=65534
    run_gid=65534
    chown "$run_uid:$run_gid" -- "$output_path"
fi
[[ -w $output_path ]] || fail 'Output directory is not writable'

container="improving-evalplus-$$-${RANDOM}"
staging_path=""
cleanup() {
    timeout --signal=TERM --kill-after=5s 15s docker rm -f "$container" >/dev/null 2>&1 || true
    if [[ -n $staging_path ]]; then
        rm -rf -- "$staging_path"
    fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

command=(docker run --rm --init --pull never --name "$container"
    --network none --read-only --cap-drop ALL --security-opt no-new-privileges
    --user "$run_uid:$run_gid" --cpus "$cpus"
    --memory "${memory_mb}m" --memory-swap "${memory_mb}m" --pids-limit "$pids"
    --ulimit nofile=256:256 --ulimit core=0:0 --ulimit fsize=1073741824:1073741824
    --tmpfs /tmp:rw,noexec,nosuid,size=1073741824,mode=1777
    --shm-size 64m --workdir /tmp --stop-timeout 1
    --env "EVALPLUS_MAX_MEMORY_BYTES=$((sample_mb * 1024 * 1024))"
    --mount "type=bind,src=$output_path,dst=/output")
if [[ $mode == evaluate ]]; then
    # Atomic JSONL outputs often have mode 0600. Stage bytes with read-only
    # permissions so the nonroot container can read even a root caller's file.
    staging_path=$(mktemp -d -t improving-evalplus.XXXXXXXX)
    chmod 0755 -- "$staging_path"
    install -m 0444 -- "$samples_path" "$staging_path/samples.jsonl"
    command+=(--mount "type=bind,src=$staging_path/samples.jsonl,dst=/input/samples.jsonl,readonly")
fi
command+=("$image" "$mode" "$dataset" --parallel "$parallel")
timeout --foreground --signal=TERM --kill-after=10s "${walltime}s" "${command[@]}"
printf 'EvalPlus output: %s\n' "$output_path"
