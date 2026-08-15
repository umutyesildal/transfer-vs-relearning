#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python - <<'PY'
import json
from pathlib import Path

import yaml

repo = Path("/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning")
run_dir = repo / "runs/training/m1_smollm2_360m_english_biographies_stage_a/20260707T171129Z_m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_fa548873"
source_manifest = repo / "artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json"
manifest_dir = repo / "runs/local_model_manifests/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1"
config_dir = repo / "runs/local_configs/m1_checkpoint_eval_smollm2_360m_stage_a_lr5e-5_ep1"
manifest_dir.mkdir(parents=True, exist_ok=True)
config_dir.mkdir(parents=True, exist_ok=True)

checkpoints = ["checkpoint-146", "checkpoint-292", "checkpoint-438", "checkpoint-583"]
relations = ["profession", "born_in", "lives_in", "studied_at", "works_at"]
runtime = {
    "bf16": True,
    "device": "cuda",
    "candidate_batch_size": 64,
    "checkpoint_interval": 25,
    "seed": 42,
}
scoring = {
    "primary": "mean_logprob",
    "secondary": "total_logprob",
    "tie_breaker": "canonical_object_id",
}

for checkpoint in checkpoints:
    manifest_path = manifest_dir / f"{checkpoint}_model_manifest.json"
    subprocess_args = [
        "/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python",
        "scripts/create_local_model_manifest.py",
        "--source-manifest",
        str(source_manifest),
        "--local-model-dir",
        str(run_dir / "checkpoints" / checkpoint),
        "--output-manifest",
        str(manifest_path),
        "--model-id",
        f"m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1/{checkpoint}",
        "--training-checkpoint",
        checkpoint,
        "--training-run-dir",
        str(run_dir),
    ]
    import subprocess
    subprocess.run(subprocess_args, check=True)

    direct_cfg = {
        "dataset_version": "synthetic_v1",
        "dataset_dir": "artifacts/datasets/synthetic_v1",
        "pilot_subject_file": "artifacts/datasets/synthetic_v1/pilot_100_subjects.json",
        "model_manifest": str(manifest_path.relative_to(repo)),
        "languages": ["en", "tr"],
        "relations": relations,
        "prompt": {
            "format": "direct",
            "template": "{question}",
            "answer_separator": " ",
        },
        "scoring": scoring,
        "runtime": runtime,
        "output": {
            "run_root": f"runs/evaluation/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_{checkpoint}_direct",
        },
    }
    qa_cfg = {
        "dataset_version": "synthetic_v1",
        "dataset_dir": "artifacts/datasets/synthetic_v1",
        "pilot_subject_file": "artifacts/datasets/synthetic_v1/pilot_100_subjects.json",
        "model_manifest": str(manifest_path.relative_to(repo)),
        "languages": ["en", "tr"],
        "relations": relations,
        "prompt": {
            "format": "qa_matched",
            "templates_by_language": {
                "en": "Question: {question}\nAnswer:",
                "tr": "Soru: {question}\nCevap:",
            },
            "answer_separator": " ",
        },
        "scoring": scoring,
        "runtime": runtime,
        "output": {
            "run_root": f"runs/evaluation/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_{checkpoint}_qa_matched",
        },
    }

    (config_dir / f"m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_{checkpoint}_direct.yaml").write_text(
        yaml.safe_dump(direct_cfg, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (config_dir / f"m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_{checkpoint}_qa_matched.yaml").write_text(
        yaml.safe_dump(qa_cfg, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

print(manifest_dir)
print(config_dir)
for path in sorted(config_dir.glob("*.yaml")):
    print(path.relative_to(repo))
PY

for cfg in runs/local_configs/m1_checkpoint_eval_smollm2_360m_stage_a_lr5e-5_ep1/*.yaml; do
  sbatch --export=ALL,EVAL_CONFIG="$cfg" slurm/eval_m0_gpt2_pilot.slurm
  sleep 1
done

echo __QUEUE__
squeue -h -u yesildau -o "%i %T %M %L %R %j" | grep m0-gpt2-pilot || true
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
