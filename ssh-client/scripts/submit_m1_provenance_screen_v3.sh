#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_provenance_screen_v3
REGISTRY=/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/configs/experiments/m1_provenance_screen_v3.yaml
TEMPLATE=/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/configs/training/m1_provenance_screen_v3_seed42_template.yaml
DATASET_ROOT=/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
FROZEN_HOME_REFERENCE_BYTES=14689423360
HOME_LIMIT_BYTES=32212254720

# Preservation-checked ordinary fast-forward only.
git fetch origin corpus-update
local_commit=$(git rev-parse HEAD)
remote_commit=$(git rev-parse origin/corpus-update)
git merge-base --is-ancestor "$local_commit" "$remote_commit" || {
  echo "HU checkout is not an ancestor of origin/corpus-update; refusing sync" >&2
  exit 1
}
dirty_blob=$(git status --porcelain=v1 --untracked-files=all)
dirty_paths=$(printf '%s\n' "$dirty_blob" | sed -E 's/^...//' | sed '/^$/d' | sort -u)
changed_paths=$(git diff --name-only "$local_commit" "$remote_commit" | sort -u)
overlap=$(comm -12 <(printf '%s\n' "$dirty_paths") <(printf '%s\n' "$changed_paths") | sed '/^$/d')
test -z "$overlap" || {
  echo "HU dirty paths overlap the published change set; refusing sync" >&2
  printf '%s\n' "$overlap" >&2
  exit 1
}
before_status_sha=$(git status --porcelain=v1 --untracked-files=all | sha256sum | awk '{print $1}')
git pull --ff-only origin corpus-update
after_status_sha=$(git status --porcelain=v1 --untracked-files=all | sha256sum | awk '{print $1}')
test "$before_status_sha" = "$after_status_sha"
test "$(git rev-parse HEAD)" = "$remote_commit"
printf 'hu_commit=%s dirty_status_sha256=%s\n' "$remote_commit" "$after_status_sha"

# Document 152b freezes one exact measurement. Per-stage recursive du is intentionally
# not repeated; this wave instead fails closed on path routing and scratch capacity.
test "$FROZEN_HOME_REFERENCE_BYTES" -lt "$HOME_LIMIT_BYTES"
registry_home_bytes=$(PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -c 'import sys,yaml; print(yaml.safe_load(open(sys.argv[1]))["home_storage_policy"]["reference_bytes"])' "$REGISTRY")
test "$registry_home_bytes" = "$FROZEN_HOME_REFERENCE_BYTES"
printf 'home_storage_policy=frozen_exact_reference_and_no_home_write\n'
printf 'home_reference_bytes=%s home_limit_bytes=%s recursive_du_per_stage=false\n' "$FROZEN_HOME_REFERENCE_BYTES" "$HOME_LIMIT_BYTES"
df -hP "$HOME_ROOT" /vol/tmp /vol/tmp2
df -iP "$HOME_ROOT" /vol/tmp /vol/tmp2
printf 'runs=%s\n' "$(readlink -f "$HOME_ROOT/transfer-vs-relearning/runs")"
printf 'artifacts=%s\n' "$(readlink -f "$HOME_ROOT/transfer-vs-relearning/artifacts")"
printf 'recursive_large_home_file_scan=not_run_by_design\n'

test ! -e "$SCRATCH_ROOT"
for old_root in \
  /vol/tmp2/yesildau/m1_provenance_screen_v1 \
  /vol/tmp2/yesildau/m1_provenance_screen_retry_v1 \
  /vol/tmp2/yesildau/m1_provenance_screen_retry_v2; do
  if test -e "$old_root"; then printf 'preserved_prior_root=%s\n' "$old_root"; fi
done

test "$(sha256sum "$DATASET_ROOT/dataset_manifest.json" | awk '{print $1}')" = c11f779229af14b196f2063ecdeb956e34444a30bf4086c331168f5cb11d6a26
test "$(sha256sum "$DATASET_ROOT/train.jsonl" | awk '{print $1}')" = 8eb65505b22f5c7f8e67f2d1877efad7503489dd8bdf2608cad08791f7d05a67
test "$(sha256sum "$DATASET_ROOT/validation.jsonl" | awk '{print $1}')" = 495cdcda9049b372159ef167f3da866e4cb82caf1977796efbb3baa9e07973e7
test "$(wc -l < "$DATASET_ROOT/train.jsonl")" -eq 3500
test "$(wc -l < "$DATASET_ROOT/validation.jsonl")" -eq 500

# Authoritative source-side suite before any model access or scratch-root creation.
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -m pytest -q -p no:cacheprovider \
  tests/test_m1_cross_family.py \
  tests/test_model_download_native_tokenizer.py \
  tests/test_training_answer_only.py \
  tests/test_training_core.py \
  tests/test_evaluation_core.py
"$PYTHON" -m py_compile \
  src/transfer_vs_relearning/models/download.py \
  src/transfer_vs_relearning/experiments/m1_cross_family.py \
  scripts/m1/acquire_m1_cross_family_candidate.py \
  scripts/m1/prepare_m1_cross_family_evaluation.py \
  scripts/m1/summarize_m1_provenance_screen_v3.py

queued=$(squeue -u yesildau -h -o '%i|%j|%T|%R')
if printf '%s\n' "$queued" | grep -E '\|m1-pv3-' >/dev/null; then
  echo 'm1-pv3 job namespace is already present; refusing duplicate submission' >&2
  exit 1
fi
printf '%s\n' "$queued"
mkdir -p "$SCRATCH_ROOT/logs"

export_args="ALL,M1_PROVENANCE_SCREEN_ROOT=$SCRATCH_ROOT,M1_PROVENANCE_REGISTRY=$REGISTRY,M1_PROVENANCE_TEMPLATE=$TEMPLATE"
acq_manifest="$SCRATCH_ROOT/preflight/acquisition.json"
acq_pre=$(sbatch --parsable \
  --job-name=m1-pv3-preflight-acq \
  --output="$SCRATCH_ROOT/logs/m1-pv3-preflight-acq-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-pv3-preflight-acq-%j.err" \
  --export="$export_args,PREFLIGHT_STAGE=acquisition,CANDIDATE_INDICES=0:1:2,TARGET_LAUNCHER=$PWD/slurm/m1/acquire_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-pv3-acq,PREFLIGHT_MANIFEST_PATH=$acq_manifest" \
  slurm/m1/preflight_m1_provenance_screen.slurm)

labels=(olmo pythia falcon)
acq_ids=()
train_pre_ids=()
train_ids=()
eval_pre_ids=()
eval_ids=()
for i in 0 1 2; do
  label=${labels[$i]}
  acq=$(sbatch --parsable \
    --job-name="m1-pv3-${label}-acq" \
    --dependency="afterok:$acq_pre" \
    --array="$i-$i" \
    --output="$SCRATCH_ROOT/logs/m1-pv3-${label}-acq-%A_%a.out" \
    --error="$SCRATCH_ROOT/logs/m1-pv3-${label}-acq-%A_%a.err" \
    --export="$export_args,PREFLIGHT_MANIFEST=$acq_manifest" \
    slurm/m1/acquire_m1_provenance_screen.slurm)
  acq_ids+=("$acq")

  train_manifest="$SCRATCH_ROOT/preflight/training_${label}.json"
  train_pre=$(sbatch --parsable \
    --job-name="m1-pv3-${label}-pretrain" \
    --dependency="afterok:$acq" \
    --output="$SCRATCH_ROOT/logs/m1-pv3-${label}-pretrain-%j.out" \
    --error="$SCRATCH_ROOT/logs/m1-pv3-${label}-pretrain-%j.err" \
    --export="$export_args,PREFLIGHT_STAGE=training,CANDIDATE_INDICES=$i,TARGET_LAUNCHER=$PWD/slurm/m1/train_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-pv3-${label}-train,ALLOW_SUBSET_RETRY=1,PREFLIGHT_MANIFEST_PATH=$train_manifest" \
    slurm/m1/preflight_m1_provenance_screen.slurm)
  train_pre_ids+=("$train_pre")
  train=$(sbatch --parsable \
    --job-name="m1-pv3-${label}-train" \
    --dependency="afterok:$train_pre" \
    --array="$i-$i" \
    --output="$SCRATCH_ROOT/logs/m1-pv3-${label}-train-%A_%a.out" \
    --error="$SCRATCH_ROOT/logs/m1-pv3-${label}-train-%A_%a.err" \
    --export="$export_args,PREFLIGHT_MANIFEST=$train_manifest" \
    slurm/m1/train_m1_provenance_screen.slurm)
  train_ids+=("$train")

  eval_manifest="$SCRATCH_ROOT/preflight/evaluation_${label}.json"
  eval_pre=$(sbatch --parsable \
    --job-name="m1-pv3-${label}-preeval" \
    --dependency="afterok:$train" \
    --output="$SCRATCH_ROOT/logs/m1-pv3-${label}-preeval-%j.out" \
    --error="$SCRATCH_ROOT/logs/m1-pv3-${label}-preeval-%j.err" \
    --export="$export_args,PREFLIGHT_STAGE=evaluation,CANDIDATE_INDICES=$i,TARGET_LAUNCHER=$PWD/slurm/m1/eval_m1_provenance_screen.slurm,TARGET_JOB_NAME=m1-pv3-${label}-eval,ALLOW_COMPLETED_SUBSET_EVALUATION=1,PREFLIGHT_MANIFEST_PATH=$eval_manifest" \
    slurm/m1/preflight_m1_provenance_screen.slurm)
  eval_pre_ids+=("$eval_pre")
  eval=$(sbatch --parsable \
    --job-name="m1-pv3-${label}-eval" \
    --dependency="afterok:$eval_pre" \
    --array="$i-$i" \
    --output="$SCRATCH_ROOT/logs/m1-pv3-${label}-eval-%A_%a.out" \
    --error="$SCRATCH_ROOT/logs/m1-pv3-${label}-eval-%A_%a.err" \
    --export="$export_args,PREFLIGHT_MANIFEST=$eval_manifest" \
    slurm/m1/eval_m1_provenance_screen.slurm)
  eval_ids+=("$eval")
done

eval_dependency=$(IFS=:; echo "${eval_ids[*]}")
summary=$(sbatch --parsable \
  --job-name=m1-pv3-summary \
  --dependency="afterany:$eval_dependency" \
  --output="$SCRATCH_ROOT/logs/m1-pv3-summary-%j.out" \
  --error="$SCRATCH_ROOT/logs/m1-pv3-summary-%j.err" \
  --export="$export_args" \
  slurm/m1/summarize_m1_provenance_screen_v3.slurm)

printf '__ACQUISITION_PREFLIGHT_JOB_ID__=%s\n' "$acq_pre"
printf '__ACQUISITION_JOB_IDS__=%s\n' "${acq_ids[*]}"
printf '__TRAINING_PREFLIGHT_JOB_IDS__=%s\n' "${train_pre_ids[*]}"
printf '__TRAINING_JOB_IDS__=%s\n' "${train_ids[*]}"
printf '__EVALUATION_PREFLIGHT_JOB_IDS__=%s\n' "${eval_pre_ids[*]}"
printf '__EVALUATION_JOB_IDS__=%s\n' "${eval_ids[*]}"
printf '__SUMMARY_JOB_ID__=%s\n' "$summary"
all_ids=$(IFS=,; echo "$acq_pre,${acq_ids[*]},${train_pre_ids[*]},${train_ids[*]},${eval_pre_ids[*]},${eval_ids[*]},$summary")
squeue -h -j "$all_ids" -o '%i|%j|%T|%M|%L|%R|%E'
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
cd "${SCRIPT_DIR}/.."
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
