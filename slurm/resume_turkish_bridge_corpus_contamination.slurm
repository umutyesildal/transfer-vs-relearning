#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-corpus-resume
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
CONFIG="${REPO_ROOT}/configs/corpora/trwiki_turkish_bridge_v1.yaml"
CORPUS_ROOT="${SCRATCH_ROOT}/corpus/trwiki_20260601_bridge_v1"
TASK_TMP="${SCRATCH_ROOT}/tmp/corpus_resume_${SLURM_JOB_ID}"

cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,tmp,cache} "${TASK_TMP}"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TMPDIR="${TASK_TMP}"

case "$(readlink -m "${CORPUS_ROOT}")" in
  /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
  *) echo "Unsafe corpus root: $(readlink -m "${CORPUS_ROOT}")" >&2; exit 2 ;;
esac

test -s "${CORPUS_ROOT}/deduplicated/documents.jsonl"
test -s "${CORPUS_ROOT}/manifests/deduplicate_state.json"
test ! -e "${CORPUS_ROOT}/splits/train_documents.jsonl"
test ! -e "${CORPUS_ROOT}/splits/validation_documents.jsonl"
test ! -e "${CORPUS_ROOT}/manifests/corpus_manifest.json"

module load anaconda/3-2024.06
PY=(conda run --name xfer-relearn python scripts/prepare_trwiki.py)

"${PY[@]}" contamination-preflight --config "${CONFIG}"
"${PY[@]}" scan-contamination --config "${CONFIG}"
"${PY[@]}" split --config "${CONFIG}"
"${PY[@]}" report --config "${CONFIG}"

test -s "${CORPUS_ROOT}/splits/train_documents.jsonl"
test -s "${CORPUS_ROOT}/splits/validation_documents.jsonl"
test -s "${CORPUS_ROOT}/manifests/corpus_manifest.json"
sha256sum \
  "${CORPUS_ROOT}/splits/train_documents.jsonl" \
  "${CORPUS_ROOT}/splits/validation_documents.jsonl" \
  "${CORPUS_ROOT}/manifests/corpus_manifest.json" \
  > "${CORPUS_ROOT}/manifests/bridge_split_sha256.txt"
