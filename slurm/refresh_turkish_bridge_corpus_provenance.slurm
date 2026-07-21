#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-provenance
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
CONFIG="${REPO_ROOT}/configs/corpora/trwiki_turkish_bridge_v1.yaml"
CORPUS_ROOT="${SCRATCH_ROOT}/corpus/trwiki_20260601_bridge_v1"
TASK_TMP="${SCRATCH_ROOT}/tmp/provenance_${SLURM_JOB_ID}"

cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,tmp,cache} "${TASK_TMP}"
export HF_HOME="${SCRATCH_ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${SCRATCH_ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TORCH_HOME="${SCRATCH_ROOT}/cache/torch"
export TMPDIR="${TASK_TMP}"

case "$(readlink -m "${CORPUS_ROOT}")" in
  /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
  *) echo "Unsafe corpus root: $(readlink -m "${CORPUS_ROOT}")" >&2; exit 2 ;;
esac

test -s "${CORPUS_ROOT}/manifests/scan-contamination_state.json"
test -s "${CORPUS_ROOT}/splits/train_documents.jsonl"
test -s "${CORPUS_ROOT}/splits/validation_documents.jsonl"

module load anaconda/3-2024.06
PY=(conda run --name xfer-relearn python)
"${PY[@]}" scripts/prepare_trwiki.py contamination-preflight --config "${CONFIG}" --force
"${PY[@]}" scripts/sample_contamination_review.py --config "${CONFIG}" --seed 42 --sample-size 20
"${PY[@]}" scripts/prepare_trwiki.py report --config "${CONFIG}" --force

"${PY[@]}" - "${CORPUS_ROOT}" "$(git rev-parse HEAD)" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
commit = sys.argv[2]
preflight = json.loads((root / "manifests/contamination-preflight_state.json").read_text())
review = json.loads((root / "reports/contamination_review_sample_seed42.json").read_text())
manifest = json.loads((root / "manifests/corpus_manifest.json").read_text())

assert preflight["status"] == "completed"
assert preflight["processing_git_commit"] == commit
assert preflight["document_counters"]["pattern_count"] == 65717
assert preflight["document_counters"]["pattern_count_by_channel"]["canonical_object"] == 713
assert review["review_status"] == "pending_manual_review"
assert review["observed_bucket_counts"] == {"removed": 729, "flagged_only": 285303, "clean": 218984}
assert {key: len(value) for key, value in review["samples"].items()} == {"removed": 20, "flagged_only": 20, "clean": 20}
assert manifest["stage_states"]["contamination-preflight"]["document_counters"]["pattern_count"] == 65717
assert "report" not in manifest["stage_states"]
assert manifest["finalized"] is False
assert manifest["completion_status"] == "phase1_not_finalized"
PY

sha256sum \
  "${CORPUS_ROOT}/splits/train_documents.jsonl" \
  "${CORPUS_ROOT}/splits/validation_documents.jsonl" \
  "${CORPUS_ROOT}/manifests/corpus_manifest.json" \
  "${CORPUS_ROOT}/reports/contamination_review_sample_seed42.json" \
  > "${CORPUS_ROOT}/manifests/bridge_split_candidate_sha256.txt"

printf 'post_run_storage_audit\n'
du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
du -sh "${CORPUS_ROOT}"
printf 'status=passed_pending_manual_review\n'
