#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git pull --ff-only origin corpus-update
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_cross_family_screen_v1
mkdir -p "$SCRATCH_ROOT/logs"
"$PYTHON" -m pytest -q \
  tests/test_m1_cross_family.py \
  tests/test_m1_canonical_form_diversity.py \
  tests/test_training_core.py \
  tests/test_training_answer_only.py
preflight_id=$(sbatch --parsable \
  --export=ALL,PREFLIGHT_STAGE=acquisition,CANDIDATE_INDICES=0:1:2:3,TARGET_LAUNCHER="$PWD/slurm/m1/acquire_m1_cross_family_models.slurm" \
  slurm/m1/preflight_m1_cross_family.slurm)
acquisition_id=$(sbatch --parsable \
  --dependency="afterok:$preflight_id" \
  --array=0,1,2,3 \
  slurm/m1/acquire_m1_cross_family_models.slurm)
echo "__PREFLIGHT_JOB_ID__=$preflight_id"
echo "__ACQUISITION_ARRAY_JOB_ID__=$acquisition_id"
squeue -h -j "$preflight_id,$acquisition_id" -o "%i %T %M %L %R %j"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
