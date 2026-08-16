#!/usr/bin/env bash
#SBATCH --job-name=qwen-pre-m2-build
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1_logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1_logs/%x-%j.err
set -euo pipefail

: "${EXPECTED_COMMIT:?EXPECTED_COMMIT is required}"
: "${PREFLIGHT_MANIFEST:?PREFLIGHT_MANIFEST is required}"

HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
OUTPUT_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1
LOG_ROOT=/vol/tmp2/yesildau/qwen_pre_m2_contract_v1_logs

test -s "${PREFLIGHT_MANIFEST}"
test ! -e "${OUTPUT_ROOT}"
test -f "${REPO_ROOT}/scripts/m2/build_qwen_pre_m2_contract.py"
observed_commit=$(git -C "${REPO_ROOT}" rev-parse HEAD)
test "${observed_commit}" = "${EXPECTED_COMMIT}"
case "$(readlink -m "${OUTPUT_ROOT}")" in
  /vol/tmp2/yesildau/*) ;;
  *) printf 'unsafe_path=%s\n' "${OUTPUT_ROOT}" >&2; exit 2 ;;
esac

module load anaconda/3-2024.06
cd "${REPO_ROOT}"
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"
conda run --name xfer-relearn python scripts/m2/build_qwen_pre_m2_contract.py \
  --repo-root "${REPO_ROOT}" \
  --output-root "${OUTPUT_ROOT}"

conda run --name xfer-relearn python - "${OUTPUT_ROOT}/manifest.json" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
payload = json.loads(manifest_path.read_text(encoding="utf-8"))
assert payload["status"] == "compact_pre_m2_registries_ready"
assert payload["population"] == {
    "subjects": 500,
    "facts": 2500,
    "branch_subjects": {"A": 250, "B": 250},
    "branch_facts": {"A": 1250, "B": 1250},
}
assert payload["probe_count"] == 60_000
assert payload["evaluation_slice_count"] == 24
assert payload["probes_per_slice"] == 2_500
assert payload["m3_branch_b_fact_count"] == 1_250
for item in payload["artifacts"].values():
    path = Path(item["path"])
    assert path.is_file(), path
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    assert observed == item["sha256"], path
print("status=compact_pre_m2_materialized_and_audited")
PY

printf 'status=passed output_root=%s log_root=%s subjects=500 facts=2500 probes=60000 slices=24 branch_b_facts=1250 expected_checkpoints=0 retention=preserve_compact_registry_manifest_and_hashes\n' \
  "$(readlink -m "${OUTPUT_ROOT}")" "$(readlink -m "${LOG_ROOT}")"
