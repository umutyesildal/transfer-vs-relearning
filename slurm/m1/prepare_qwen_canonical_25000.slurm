#!/usr/bin/env bash
#SBATCH --job-name=qwen25k-prepare
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1/logs/%x-%j.err
set -euo pipefail
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT=/vol/tmp2/yesildau/qwen_canonical_25k_seed42_v1
SOURCE_ANCHOR=/vol/tmp2/yesildau/qwen_scale_probe_v3/anchor
test -s "${PREFLIGHT_MANIFEST}"
test ! -e "${ROOT}/prepared"

mkdir -p "${ROOT}"/{cache/huggingface,cache/torch,logs,tmp}
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${ROOT}/tmp"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

cd "${REPO_ROOT}"
module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/build_qwen_canonical_scale_dataset.py \
  --output-dir "${ROOT}/prepared" \
  --replay-train-source "${SOURCE_ANCHOR}/train.jsonl" \
  --replay-validation-source "${SOURCE_ANCHOR}/validation.jsonl"
conda run --name xfer-relearn python - "${ROOT}/prepared/dataset_manifest.json" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text())
assert payload["status"] == "passed"
assert payload["subjects"] == 5000
assert payload["facts"] == 25000
assert payload["train_rows"] == 175000
assert payload["four_form_probes"] == 200000
assert payload["exact_prefix_probes"] == 25000
assert payload["branches"] == {"A": 2500, "B": 2500}
assert payload["audits"]["heldout_c_d_training_rows"] == 0
assert payload["replay"]["cycles"] == 10
assert payload["replay"]["train_rows"] == 175000
assert payload["replay"]["full_population_subject_surface_hits"] == 0
print("status=prepared_and_audited")
PY
