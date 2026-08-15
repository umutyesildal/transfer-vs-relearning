#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update

PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
"$PYTHON" -m pytest -vv tests/test_relation_v2_binding_control.py tests/test_training_answer_only.py tests/test_training_core.py

JOB_ID=$(sbatch --parsable \
  --export=ALL,TRAIN_CONFIG=configs/training/m1_smollm2_360m_relation_v2_binding_control_10_subjects_lr1e-4_ep36.yaml \
  slurm/train_m1_gpt2_english_facts.slurm)
echo "__JOB_ID__=$JOB_ID"
squeue -h -j "$JOB_ID" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
