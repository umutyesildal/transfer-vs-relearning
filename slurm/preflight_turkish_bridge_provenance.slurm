#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-prov-pre
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
MIN_TMP2_KIB=$((2 * 1024 * 1024))

mkdir -p "${SCRATCH_ROOT}/logs"
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
tmp2_available_kib=$(df -k --output=avail /vol/tmp2 | tail -n 1 | tr -d ' ')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")
corpus_resolved=$(readlink -m "${CORPUS_ROOT}")

printf 'home_kib=%s\n' "${home_kib}"
printf 'tmp2_available_kib=%s\n' "${tmp2_available_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\n' "${artifacts_resolved}"
printf 'runs_resolved=%s\n' "${runs_resolved}"
printf 'corpus_resolved=%s\n' "${corpus_resolved}"
printf 'jobs=refresh_turkish_bridge_corpus_provenance\n'
printf 'expected_checkpoints=0\n'
printf 'existing_scan_read_gib_approx=5.0\n'
printf 'new_compact_output_upper_bound_gib=1\n'
printf 'retention=preserve frozen corpus and split; retain compact provenance and review sample\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N'

test "${home_kib}" -le $((10 * 1024 * 1024))
test "${tmp2_available_kib}" -ge "${MIN_TMP2_KIB}"
test -f "${REPO_ROOT}/slurm/refresh_turkish_bridge_corpus_provenance.slurm"
test -f "${REPO_ROOT}/scripts/sample_contamination_review.py"
test -f "${REPO_ROOT}/configs/corpora/trwiki_turkish_bridge_v1.yaml"
test -s "${CORPUS_ROOT}/contamination/clean_documents.jsonl"
test -s "${CORPUS_ROOT}/contamination/removed_documents.jsonl"
test -s "${CORPUS_ROOT}/contamination/matches.jsonl"
test -s "${CORPUS_ROOT}/splits/train_documents.jsonl"
test -s "${CORPUS_ROOT}/splits/validation_documents.jsonl"

case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${corpus_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

printf 'status=passed\n'
