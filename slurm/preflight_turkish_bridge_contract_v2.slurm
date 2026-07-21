#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-v2-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:20:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
CORPUS_ROOT="${SCRATCH_ROOT}/corpus/trwiki_20260601_bridge_v1"
OUTPUT_ROOT="${SCRATCH_ROOT}/contracts/v2"

mkdir -p "${SCRATCH_ROOT}/logs"
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
tmp2_available_kib=$(df -k --output=avail /vol/tmp2 | tail -n 1 | tr -d ' ')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")

printf 'home_kib=%s\n' "${home_kib}"
printf 'tmp2_available_kib=%s\n' "${tmp2_available_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\n' "${artifacts_resolved}"
printf 'runs_resolved=%s\n' "${runs_resolved}"
printf 'output_resolved=%s\n' "$(readlink -m "${OUTPUT_ROOT}")"
printf 'jobs=materialize_turkish_bridge_contract_v2\n'
printf 'expected_checkpoints=0\n'
printf 'new_contract_output_upper_bound_gib=1\n'
printf 'retention=append-only v2 contract; preserve v1 and frozen corpus\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N'

test "${home_kib}" -le $((10 * 1024 * 1024))
test "${tmp2_available_kib}" -ge $((2 * 1024 * 1024))
test -f "${REPO_ROOT}/scripts/prepare_turkish_bridge_contract_v2.py"
test -f "${REPO_ROOT}/slurm/materialize_turkish_bridge_contract_v2.slurm"
test -s "${CORPUS_ROOT}/manifests/corpus_manifest_final.json"
test "$(sha256sum "${CORPUS_ROOT}/manifests/corpus_manifest_final.json" | awk '{print $1}')" = "108c72375bb253742831da3fafb9e4b4b7b736974cb3cf6ef13f9b0f167502f7"
test ! -e "${OUTPUT_ROOT}"
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "$(readlink -m "${OUTPUT_ROOT}")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
printf 'status=passed\n'
