#!/usr/bin/env bash
# CPU-only preflight for the 48-slice frozen bilingual Qwen baseline wave.
# This job creates the append-only manifest consumed by the GPU array; it does not evaluate.
#SBATCH --job-name=qwen-pre-m2-base-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1/logs/%x-%j.err
set -euo pipefail

: "${EXPECTED_COMMIT:?EXPECTED_COMMIT must be passed at submission time}"
HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="${BASELINE_SCRATCH_ROOT:-/vol/tmp2/yesildau/qwen_pre_m2_baseline_v1}"
CONTRACT_ROOT="/vol/tmp2/yesildau/qwen_pre_m2_contract_v1"
PREFLIGHT_MANIFEST="${ROOT}/preflight/manifest.json"
HOME_LIMIT_BYTES=30000000000
EXPECTED_JOBS=48
EXPECTED_CHECKPOINTS=0
ESTIMATED_FAMILY_BYTES=$((16 * 1024 * 1024 * 1024))

cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${EXPECTED_COMMIT}"
test -s "${CONTRACT_ROOT}/manifest.json"
test -s "${CONTRACT_ROOT}/evaluation/slice_registry.json"
test ! -e "${PREFLIGHT_MANIFEST}"
test ! -e "${ROOT}/results"

mkdir -p "${ROOT}"/{logs,preflight}
home_du_path="${ROOT}/preflight/home_du_${SLURM_JOB_ID}.txt"
timeout 120s du -xsh "${HOME_ROOT}" > "${home_du_path}"
home_kib=$(timeout 120s du -xsk "${HOME_ROOT}" | awk 'NR == 1 {print $1}')
test -n "${home_kib}"
test $((home_kib * 1024)) -lt "${HOME_LIMIT_BYTES}"
tmp2_available_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
tmp2_available_inodes=$(df -Pi /vol/tmp2 | tail -n 1 | awk '{print $4}')
test $((tmp2_available_kib * 1024)) -ge "${ESTIMATED_FAMILY_BYTES}"
test "${tmp2_available_inodes}" -gt 0
test "$(readlink -f "${REPO_ROOT}/artifacts")" = "/vol/tmp/yesildau/transfer-vs-relearning/artifacts"
test "$(readlink -f "${REPO_ROOT}/runs")" = "/vol/tmp/yesildau/transfer-vs-relearning/runs"

python_bin="${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python"
"${python_bin}" - "${CONTRACT_ROOT}" "${EXPECTED_COMMIT}" "${PREFLIGHT_MANIFEST}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

contract_root = Path(sys.argv[1])
expected_commit = sys.argv[2]
output = Path(sys.argv[3])
manifest = json.loads((contract_root / "manifest.json").read_text(encoding="utf-8"))
registry_path = contract_root / "evaluation/slice_registry.json"
registry = json.loads(registry_path.read_text(encoding="utf-8"))
assert manifest["status"] == "compact_pre_m2_registries_ready"
assert manifest["probe_count"] == 60_000
assert manifest["evaluation_slice_count"] == 24
assert manifest["probes_per_slice"] == 2_500
assert len(registry) == 24
assert {row["probe_count"] for row in registry} == {2_500}
assert len({row["slice_id"] for row in registry}) == 24
assert {row["direction"] for row in registry} == {"en_to_en", "tr_to_en", "tr_to_tr"}
assert {row["form_id"] for row in registry} == {"form_a", "form_b", "form_c", "form_d"}
assert {row["scaffold_id"] for row in registry} == {"direct", "qa"}

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

for item in registry:
    path = Path(item["path"])
    assert path.is_file(), path
    assert sha256(path) == item["sha256"], item["slice_id"]

model_specs = [
    ("qwen_m1_seed42_step75", 42, 75, Path("/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75/selected_artifact_manifest.json")),
    ("qwen_m1_seed43_step50", 43, 50, Path("/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50/selected_artifact_manifest.json")),
]
model_evidence = []
for label, seed, step, path in model_specs:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["status"] == "frozen_selected_model_only"
    assert payload["seed"] == seed and payload["checkpoint_step"] == step
    files = {}
    for name, item in payload["files"].items():
        file_path = Path(item["path"])
        assert file_path.is_file(), file_path
        assert sha256(file_path) == item["sha256"], f"{label}/{name}"
        files[name] = {"path": str(file_path), "sha256": item["sha256"], "size_bytes": item["size_bytes"]}
    model_evidence.append({"label": label, "seed": seed, "checkpoint_step": step, "manifest": str(path), "manifest_sha256": sha256(path), "files": files})

output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({
    "status": "passed",
    "git_commit": expected_commit,
    "contract_root": str(contract_root),
    "contract_manifest_sha256": sha256(contract_root / "manifest.json"),
    "slice_registry_sha256": sha256(registry_path),
    "models": model_evidence,
    "expected_jobs": 48,
    "expected_slices_per_model": 24,
    "expected_probes_per_model": 60_000,
    "expected_new_checkpoints": 0,
    "estimated_family_bytes": 16 * 1024 * 1024 * 1024,
    "retention_policy": "retain per-probe baseline evidence and compact summaries; no checkpoints",
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"status=baseline_preflight_passed manifest={output} jobs=48 probes_per_model=60000")
PY

du -xsh "${HOME_ROOT}" "${ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
printf 'status=baseline_preflight_passed output_root=%s preflight_manifest=%s expected_jobs=%s expected_checkpoints=%s estimated_family_bytes=%s retention=no_checkpoints_retain_per_probe_and_compact_summary\n' \
  "${ROOT}" "${PREFLIGHT_MANIFEST}" "${EXPECTED_JOBS}" "${EXPECTED_CHECKPOINTS}" "${ESTIMATED_FAMILY_BYTES}"
