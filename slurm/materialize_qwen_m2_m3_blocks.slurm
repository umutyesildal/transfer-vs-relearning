#!/usr/bin/env bash
# CPU materialization of the frozen, token-matched Qwen M2-clean/M3-fact inputs.
#SBATCH --job-name=qwen-m2-m3-blocks
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_m2_m3_v1/logs/%x-%j.err
set -euo pipefail

: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
: "${CONTRACT_PATH:?CONTRACT_PATH is required}"
HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="/vol/tmp2/yesildau/qwen_m2_m3_v1"
BLOCK_ROOT="${ROOT}/blocks"
TMP_ROOT="${ROOT}/tmp/materialize_${SLURM_JOB_ID}"

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${CONTRACT_PATH}"
test ! -e "${BLOCK_ROOT}"

home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
test "${home_kib}" -lt $((30 * 1024 * 1024))
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
readlink -f "${REPO_ROOT}/runs"
readlink -f "${REPO_ROOT}/artifacts"

module load anaconda/3-2024.06
python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
mapfile -t fields < <("${python_bin}" - "${CONTRACT_PATH}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    payload = json.load(handle)
assert payload["status"] == "frozen"
parameters = payload["parameters"]
print(payload["sources"]["generic_train"])
print(payload["sources"]["generic_validation"])
print(payload["sources"]["fact_registry"])
print(payload["sources"]["tokenizer"])
print(parameters["block_size"])
print(parameters["train_blocks"])
print(parameters["validation_blocks"])
print(parameters["fact_cycles"])
PY
)
GENERIC_TRAIN="${fields[0]}"
GENERIC_VALIDATION="${fields[1]}"
FACT_REGISTRY="${fields[2]}"
TOKENIZER="${fields[3]}"
BLOCK_SIZE="${fields[4]}"
TRAIN_BLOCKS="${fields[5]}"
VALIDATION_BLOCKS="${fields[6]}"
FACT_CYCLES="${fields[7]}"
for path in "${GENERIC_TRAIN}" "${GENERIC_VALIDATION}" "${FACT_REGISTRY}" "${TOKENIZER}"; do
  test -e "${path}"
done

mkdir -p "${ROOT}/logs" "${TMP_ROOT}"
export HF_HOME="${ROOT}/cache/huggingface"
export TRANSFORMERS_CACHE="${ROOT}/cache/huggingface"
export XDG_CACHE_HOME="${ROOT}/cache"
export TORCH_HOME="${ROOT}/cache/torch"
export TMPDIR="${TMP_ROOT}"
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
printf 'status=materialization_start\ncommit=%s\ngeneric_train=%s\ngeneric_validation=%s\nfact_registry=%s\ntokenizer=%s\nblock_size=%s\ntrain_blocks=%s\nvalidation_blocks=%s\nfact_cycles=%s\noutput_root=%s\n' \
  "${EXPECTED_COMMIT}" "${GENERIC_TRAIN}" "${GENERIC_VALIDATION}" "${FACT_REGISTRY}" \
  "${TOKENIZER}" "${BLOCK_SIZE}" "${TRAIN_BLOCKS}" "${VALIDATION_BLOCKS}" "${FACT_CYCLES}" "${BLOCK_ROOT}"

PYTHONPATH="${REPO_ROOT}/src" conda run --name xfer-relearn python scripts/materialize_qwen_m2_m3_blocks.py \
  --generic-train "${GENERIC_TRAIN}" \
  --generic-validation "${GENERIC_VALIDATION}" \
  --fact-registry "${FACT_REGISTRY}" \
  --tokenizer "${TOKENIZER}" \
  --output-root "${BLOCK_ROOT}" \
  --block-size "${BLOCK_SIZE}" \
  --train-blocks "${TRAIN_BLOCKS}" \
  --validation-blocks "${VALIDATION_BLOCKS}" \
  --fact-cycles "${FACT_CYCLES}"

"${python_bin}" - "${BLOCK_ROOT}/manifest.json" "${FACT_CYCLES}" <<'PY'
import json
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
audit = payload["audit"]
assert payload["status"] == "matched_m2_m3_blocks_ready"
assert audit["fact_cycles"] == int(sys.argv[2])
assert audit["m2_m3_block_count_equal"]
assert audit["m2_m3_token_budget_equal"]
assert audit["branch_a_fact_exposures"] == 0
assert audit["scheduled_fact_exposures"] == 1_250 * int(sys.argv[2])
print(f"status=materialization_complete manifest={sys.argv[1]} factual_token_share={audit['factual_token_share']}")
PY
