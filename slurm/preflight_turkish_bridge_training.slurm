#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-tr-pre
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
CONTRACT_ROOT="${SCRATCH_ROOT}/contracts/v2"
CONTRACT_MANIFEST="${CONTRACT_ROOT}/manifest.json"
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/training_${SLURM_JOB_ID}.json"
EXPECTED_CONTRACT_SHA256="f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"

mkdir -p "${SCRATCH_ROOT}"/{logs,preflight}
home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
tmp2_available_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")

printf 'home_kib=%s\n' "${home_kib}"
printf 'tmp2_available_kib=%s\n' "${tmp2_available_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'artifacts_resolved=%s\n' "${artifacts_resolved}"
printf 'runs_resolved=%s\n' "${runs_resolved}"
printf 'jobs=qwen,smollm2\n'
printf 'destinations=%s,%s\n' "${SCRATCH_ROOT}/training/qwen" "${SCRATCH_ROOT}/training/smollm2"
printf 'expected_checkpoints_per_model=4\n'
printf 'expected_final_models_per_model=1\n'
printf 'expected_family_reserve_bytes=110721074308\n'
printf 'retention=keep step-32 and final model-only after evaluation/checksums; intermediate optimizer state remains until selection\n'
printf 'expected_training_runtime_after_start=20-45 minutes\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N'

test "${home_kib}" -le $((10 * 1024 * 1024))
test $((tmp2_available_kib * 1024)) -ge 110721074308
test ! -e "${SCRATCH_ROOT}/training/qwen"
test ! -e "${SCRATCH_ROOT}/training/smollm2"
test -f "${REPO_ROOT}/slurm/train_turkish_bridge.slurm"
test -f "${REPO_ROOT}/slurm/audit_turkish_bridge_training.slurm"
test "$(sha256sum "${CONTRACT_MANIFEST}" | awk '{print $1}')" = "${EXPECTED_CONTRACT_SHA256}"
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "$(readlink -m "${SCRATCH_ROOT}/training/qwen")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "$(readlink -m "${SCRATCH_ROOT}/training/smollm2")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${CONTRACT_ROOT}" "${EXPECTED_CONTRACT_SHA256}" "${PREFLIGHT_MANIFEST}" \
  "${home_kib}" "${tmp2_available_kib}" "${SLURM_JOB_ID}" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
expected_hash = sys.argv[2]
output = Path(sys.argv[3])
home_kib = int(sys.argv[4])
available_kib = int(sys.argv[5])
job_id = sys.argv[6]

def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

manifest_path = root / "manifest.json"
assert sha(manifest_path) == expected_hash
manifest = json.loads(manifest_path.read_text())
assert manifest["status"] == "frozen_ready_for_training_preflight"
assert manifest["shared_eligible_count"] == 357
assert manifest["shared_strict_count"] == 196
assert manifest["storage"]["preflight_reserve_bytes"] == 110721074308
assert all(value >= 2048 for value in manifest["dose"]["model_grouped_block_counts"].values())
for relative, expected in manifest["artifact_hashes"].items():
    assert sha(root / relative) == expected, relative
for label in ("qwen", "smollm2"):
    config_path = root / "training_configs" / f"{label}.json"
    config = json.loads(config_path.read_text())
    assert Path(config["training"]["output_root"]).resolve() == Path(
        f"/vol/tmp2/yesildau/turkish_bridge_v1/training/{label}"
    )
    assert config["training"]["max_steps"] == 128
    assert config["training"]["save_steps"] == 32
    assert config["training"]["block_size"] == 512
    assert config["training"]["per_device_train_batch_size"] == 2
    assert config["training"]["gradient_accumulation_steps"] == 8
    model_manifest = json.loads(Path(config["model"]["base_model_manifest"]).read_text())
    for key in ("local_path_absolute", "tokenizer_source_path_absolute"):
        resolved = Path(model_manifest[key]).resolve()
        assert str(resolved).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/")), (label, key, resolved)
        assert resolved.exists(), (label, key, resolved)

payload = {
    "status": "passed",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "slurm_job_id": job_id,
    "contract_manifest": str(manifest_path),
    "contract_manifest_sha256": expected_hash,
    "models": ["qwen", "smollm2"],
    "expected_checkpoints_per_model": 4,
    "expected_final_models_per_model": 1,
    "estimated_family_active_bytes": manifest["storage"]["estimated_family_active_bytes"],
    "preflight_reserve_bytes": manifest["storage"]["preflight_reserve_bytes"],
    "home_kib": home_kib,
    "tmp2_available_kib": available_kib,
    "output_roots": {
        label: f"/vol/tmp2/yesildau/turkish_bridge_v1/training/{label}"
        for label in ("qwen", "smollm2")
    },
}
output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(output)
PY

printf 'status=passed\n'
