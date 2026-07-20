#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-resume-preflight
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:15:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
CORPUS_ROOT="${SCRATCH_ROOT}/corpus/trwiki_20260601_bridge_v1"
MIN_TMP2_KIB=$((50 * 1024 * 1024))

mkdir -p "${SCRATCH_ROOT}/logs"

home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
tmp2_available_kib=$(df -k --output=avail /vol/tmp2 | tail -n 1 | tr -d ' ')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")
corpus_resolved=$(readlink -m "${CORPUS_ROOT}")
existing_corpus_kib=$(du -sk "${CORPUS_ROOT}" | awk '{print $1}')

printf 'home_kib=%s\n' "${home_kib}"
printf 'tmp2_available_kib=%s\n' "${tmp2_available_kib}"
printf 'existing_corpus_kib=%s\n' "${existing_corpus_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\n' "${artifacts_resolved}"
printf 'runs_resolved=%s\n' "${runs_resolved}"
printf 'corpus_resolved=%s\n' "${corpus_resolved}"
printf 'jobs=resume_turkish_bridge_contamination_scan_split_report\n'
printf 'expected_checkpoints=0\n'
printf 'incremental_upper_reserve_gib=50\n'
printf 'retention=freeze clean splits, corpus manifest, reports, and SHA-256; preserve completed reusable stages\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N'

test "${home_kib}" -le $((10 * 1024 * 1024))
test "${tmp2_available_kib}" -ge "${MIN_TMP2_KIB}"
test -f "${REPO_ROOT}/slurm/resume_turkish_bridge_corpus_contamination.slurm"
test -f "${REPO_ROOT}/configs/corpora/trwiki_turkish_bridge_v1.yaml"
test -s "${CORPUS_ROOT}/deduplicated/documents.jsonl"
grep -q '"status": "completed"' "${CORPUS_ROOT}/manifests/deduplicate_state.json"
test ! -e "${CORPUS_ROOT}/splits/train_documents.jsonl"
test ! -e "${CORPUS_ROOT}/splits/validation_documents.jsonl"
test ! -e "${CORPUS_ROOT}/manifests/corpus_manifest.json"

case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${corpus_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

printf 'status=passed\n'
