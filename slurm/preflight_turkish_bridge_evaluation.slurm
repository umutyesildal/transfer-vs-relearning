#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-ev-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
EVALUATION_ROOT="${SCRATCH_ROOT}/evaluation_v1"
CONTRACT_ROOT="${SCRATCH_ROOT}/contracts/v2"
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/evaluation_${SLURM_JOB_ID}.json"
CONTRACT_SHA256="f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"
ENGLISH_SHA256="578a0879807f928e423f61631ee697a865af006df21e60e10e25a534c345097a"
TURKISH_SHA256="586e3fd343c8c04fddcd5e9cdfb4a82ae8df221c5ea764500c76e7adf94b8e52"
RESERVE_BYTES=$((10 * 1024 * 1024 * 1024))

cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
tmp2_available_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")
dataset_resolved=$(readlink -f "${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1")

printf 'home_kib=%s\ntmp2_available_kib=%s\n' "${home_kib}" "${tmp2_available_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\nruns_resolved=%s\ndataset_resolved=%s\n' \
  "${artifacts_resolved}" "${runs_resolved}" "${dataset_resolved}"
printf 'jobs=qwen,smollm2\nstates_per_job=m0,m1,low,full\n'
printf 'destinations=%s/results/qwen,%s/results/smollm2\n' "${EVALUATION_ROOT}" "${EVALUATION_ROOT}"
printf 'expected_new_checkpoints=0\nexpected_raw_probe_rows=12000\n'
printf 'expected_output_reserve_bytes=%s\n' "${RESERVE_BYTES}"
printf 'retention=retain per-probe/PPL evidence and compact decisions; no model duplication; evaluate existing read-only endpoints\n'
printf 'expected_runtime_after_gpu_start=60-150 minutes per parallel model task\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N %.30R'

test "${home_kib}" -le $((10 * 1024 * 1024))
test $((tmp2_available_kib * 1024)) -ge "${RESERVE_BYTES}"
test ! -e "${EVALUATION_ROOT}"
test "$(sha256sum "${CONTRACT_ROOT}/manifest.json" | awk '{print $1}')" = "${CONTRACT_SHA256}"
test "$(sha256sum /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl | awk '{print $1}')" = "${ENGLISH_SHA256}"
test "$(sha256sum "${CONTRACT_ROOT}/dose/validation_documents.jsonl" | awk '{print $1}')" = "${TURKISH_SHA256}"
for required in \
  scripts/prepare_turkish_bridge_evaluation.py \
  scripts/evaluate_turkish_bridge.py \
  scripts/evaluate_corpora_perplexity.py \
  scripts/finalize_turkish_bridge_evaluation.py \
  slurm/evaluate_turkish_bridge.slurm \
  slurm/audit_turkish_bridge_evaluation.slurm; do
  test -f "${REPO_ROOT}/${required}"
done
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${dataset_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "$(readlink -m "${EVALUATION_ROOT}")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/prepare_turkish_bridge_evaluation.py \
  --repo-root "${REPO_ROOT}" --output-root "${EVALUATION_ROOT}"
evaluation_manifest="${EVALUATION_ROOT}/contract/evaluation_manifest.json"
evaluation_sha256=$(sha256sum "${evaluation_manifest}" | awk '{print $1}')

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${PREFLIGHT_MANIFEST}" "${evaluation_manifest}" "${evaluation_sha256}" \
  "${home_kib}" "${tmp2_available_kib}" "${RESERVE_BYTES}" "${SLURM_JOB_ID}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

output, evaluation_manifest = Path(sys.argv[1]), Path(sys.argv[2])
payload = json.loads(evaluation_manifest.read_text())
assert payload["status"] == "frozen_ready_to_evaluate"
assert payload["states"] == ["m0", "m1", "low", "full"]
assert set(payload["models"]) == {"qwen", "smollm2"}
for model in payload["models"].values():
    assert set(model) == {"m0", "m1", "low", "full"}
    for endpoint in model.values():
        for key in ("model_path", "tokenizer_path"):
            resolved = str(Path(endpoint[key]).resolve())
            assert resolved.startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")), resolved
payload = {
    "status": "passed",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "slurm_job_id": sys.argv[7],
    "evaluation_manifest": str(evaluation_manifest),
    "evaluation_manifest_sha256": sys.argv[3],
    "models": ["qwen", "smollm2"],
    "states": ["m0", "m1", "low", "full"],
    "home_kib": int(sys.argv[4]),
    "tmp2_available_kib": int(sys.argv[5]),
    "output_reserve_bytes": int(sys.argv[6]),
    "expected_new_checkpoints": 0,
}
output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(output)
PY
printf 'status=passed\nevaluation_manifest=%s\nevaluation_manifest_sha256=%s\n' \
  "${evaluation_manifest}" "${evaluation_sha256}"
