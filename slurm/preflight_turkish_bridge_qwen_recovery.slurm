#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-qw-pre
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
PREFLIGHT_MANIFEST="${SCRATCH_ROOT}/preflight/qwen_recovery_${SLURM_JOB_ID}.json"
EXPECTED_CONTRACT_SHA256="f3248f07839f09665d571c22cf729c548e6c7b6a8a88f12fde2260903c739e5e"
QWEN_RESERVE_BYTES=52527160826

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
printf 'job=qwen_only_recovery\n'
printf 'destination=%s\n' "${SCRATCH_ROOT}/training/qwen"
printf 'preserved_smollm2_root=%s\n' "${SCRATCH_ROOT}/training/smollm2"
printf 'requested_a100_gpus=2\n'
printf 'training_gpu_count=1\n'
printf 'expected_checkpoints=4\n'
printf 'expected_final_models=1\n'
printf 'qwen_recovery_reserve_bytes=%s\n' "${QWEN_RESERVE_BYTES}"
printf 'retention=preserve all Qwen checkpoints through evaluation; do not modify SmolLM2\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N'

test "${home_kib}" -le $((10 * 1024 * 1024))
test $((tmp2_available_kib * 1024)) -ge "${QWEN_RESERVE_BYTES}"
test ! -e "${SCRATCH_ROOT}/training/qwen"
test -d "${SCRATCH_ROOT}/training/smollm2"
test -f "${REPO_ROOT}/slurm/train_turkish_bridge_qwen_recovery.slurm"
test -f "${REPO_ROOT}/slurm/audit_turkish_bridge_training.slurm"
test "$(sha256sum "${CONTRACT_MANIFEST}" | awk '{print $1}')" = "${EXPECTED_CONTRACT_SHA256}"
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "$(readlink -m "${SCRATCH_ROOT}/training/qwen")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${CONTRACT_ROOT}" "${EXPECTED_CONTRACT_SHA256}" "${PREFLIGHT_MANIFEST}" \
  "${SCRATCH_ROOT}/training/smollm2" "${home_kib}" "${tmp2_available_kib}" \
  "${QWEN_RESERVE_BYTES}" "${SLURM_JOB_ID}" <<'PY'
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
expected_hash = sys.argv[2]
output = Path(sys.argv[3])
smollm_root = Path(sys.argv[4])
home_kib = int(sys.argv[5])
available_kib = int(sys.argv[6])
reserve_bytes = int(sys.argv[7])
job_id = sys.argv[8]

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
for relative, expected in manifest["artifact_hashes"].items():
    assert sha(root / relative) == expected, relative

config_path = root / "training_configs/qwen.json"
config = json.loads(config_path.read_text())
assert Path(config["training"]["output_root"]).resolve() == Path(
    "/vol/tmp2/yesildau/turkish_bridge_v1/training/qwen"
)
assert config["training"]["max_steps"] == 128
assert config["training"]["save_steps"] == 32
assert config["training"]["block_size"] == 512
assert config["training"]["per_device_train_batch_size"] == 2
assert config["training"]["gradient_accumulation_steps"] == 8
assert manifest["storage"]["models"]["qwen"]["estimated_active_bytes"] == 40405508328
assert reserve_bytes == int(40405508328 * 1.3)
model_manifest = json.loads(Path(config["model"]["base_model_manifest"]).read_text())
for key in ("local_path_absolute", "tokenizer_source_path_absolute"):
    resolved = Path(model_manifest[key]).resolve()
    assert str(resolved).startswith(("/vol/tmp/yesildau/", "/vol/tmp2/yesildau/"))
    assert resolved.exists()

smollm_manifests = list(smollm_root.glob("*/training_manifest.json"))
assert len(smollm_manifests) == 1
smollm_payload = json.loads(smollm_manifests[0].read_text())
assert smollm_payload["status"] == "complete"
assert len(smollm_payload["result"]["checkpoint_dirs"]) == 4
assert Path(smollm_payload["result"]["final_model_dir"]).is_dir()

payload = {
    "status": "passed",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "slurm_job_id": job_id,
    "model": "qwen",
    "contract_manifest": str(manifest_path),
    "contract_manifest_sha256": expected_hash,
    "qwen_output_root": "/vol/tmp2/yesildau/turkish_bridge_v1/training/qwen",
    "preserved_smollm2_manifest": str(smollm_manifests[0]),
    "expected_checkpoints": 4,
    "expected_final_models": 1,
    "qwen_active_bytes": 40405508328,
    "preflight_reserve_bytes": reserve_bytes,
    "requested_a100_gpus": 2,
    "training_gpu_count": 1,
    "home_kib": home_kib,
    "tmp2_available_kib": available_kib,
}
output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(output)
PY

printf 'status=passed\n'
