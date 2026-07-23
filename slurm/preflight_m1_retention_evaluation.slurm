#!/usr/bin/env bash
#SBATCH --job-name=m1-ret-eval-pre
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:25:00
#SBATCH --output=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_retention_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
ROOT="/vol/tmp2/yesildau/m1_retention_v1"
WAVE="${ROOT}/evaluation_v1"
MANIFEST="${ROOT}/preflight/evaluation_${SLURM_JOB_ID}.json"
RESERVE_BYTES=$((50 * 1024 * 1024 * 1024))

home_kib=$(du -xsk "${HOME_ROOT}" | awk '{print $1}')
available_kib=$(df -Pk /vol/tmp2 | tail -n 1 | awk '{print $4}')
artifacts_resolved=$(readlink -m "${REPO_ROOT}/artifacts")
runs_resolved=$(readlink -m "${REPO_ROOT}/runs")
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr > \
  "${ROOT}/preflight/evaluation_home_large_before.txt"
printf 'home_kib=%s\navailable_kib=%s\n' "${home_kib}" "${available_kib}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
printf 'jobs=22 checkpoint evaluations (11 control + 11 replay), throttle=3, summary, audit\n'
printf 'destinations=%s/{hard_suite,exact_prefix,general_capability,logs,tmp}\n' "${WAVE}"
printf 'expected_new_checkpoints=0\nfamily_reserve_bytes=%s\n' "${RESERVE_BYTES}"
printf 'retention=source checkpoints read-only; compact evaluation outputs retained; no model copy\n'
squeue -u yesildau -o '%.18i %.12T %.10M %.24j %.20N %.30R'

test "${home_kib}" -le $((10 * 1024 * 1024))
test $((available_kib * 1024)) -ge "${RESERVE_BYTES}"
case "${artifacts_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
case "${runs_resolved}" in /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
for path in "${WAVE}/checkpoint_registry.csv" "${WAVE}/wave_manifest.json" \
  "${REPO_ROOT}/slurm/eval_m1_retention_checkpoints.slurm" \
  /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl \
  /vol/tmp2/yesildau/m1_form_generalization_v1/datasets/evaluations/four_form_probe_registry.csv \
  "${REPO_ROOT}/artifacts/datasets/relation_v2_gate_v1/acquisition_100_subjects_direct/exact_prefix_probes_en.csv"; do
  test -f "${path}"
done
for path in "${WAVE}/hard_suite" "${WAVE}/exact_prefix" "${WAVE}/general_capability"; do
  test ! -e "${path}"
  case "$(readlink -m "${path}")" in /vol/tmp2/yesildau/*) ;; *) exit 2 ;; esac
done

"${HOME_ROOT}/.conda/envs/xfer-relearn/bin/python" - \
  "${WAVE}" "${MANIFEST}" "${SLURM_JOB_ID}" "${home_kib}" "${available_kib}" \
  "${RESERVE_BYTES}" "${REPO_ROOT}" <<'PY'
import csv, hashlib, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

wave, output, job_id, home_kib, available_kib, reserve, repo = sys.argv[1:]
wave, repo = Path(wave), Path(repo)
def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()
manifest = json.loads((wave / "wave_manifest.json").read_text())
assert manifest["status"] == "frozen_ready_for_preflight"
assert manifest["tasks"] == 22
assert manifest["conditions"] == ["control", "replay_w0_5"]
assert manifest["checkpoint_steps"] == [25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252]
assert sha(wave / "checkpoint_registry.csv") == manifest["registry_sha256"]
with (wave / "checkpoint_registry.csv").open(newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
assert [int(row["array_index"]) for row in rows] == list(range(22))
assert all(Path(row["model_manifest"]).is_file() for row in rows)
assert all(sha(row["model_manifest"]) == row["model_manifest_sha256"] for row in rows)
commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
payload = {
    "status": "passed", "created_at": datetime.now(timezone.utc).isoformat(),
    "slurm_job_id": job_id, "git_commit": commit, "tasks": 22,
    "task_indices": list(range(22)), "conditions": ["control", "replay_w0_5"],
    "registry_sha256": manifest["registry_sha256"],
    "wave_manifest_sha256": sha(wave / "wave_manifest.json"),
    "home_kib": int(home_kib), "tmp2_available_kib": int(available_kib),
    "family_reserve_bytes": int(reserve), "array_throttle": 3,
    "excluded_nodes": ["gruenau9", "gruenau10"],
}
Path(output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(output)
PY
printf 'status=passed\nmanifest=%s\n' "${MANIFEST}"
