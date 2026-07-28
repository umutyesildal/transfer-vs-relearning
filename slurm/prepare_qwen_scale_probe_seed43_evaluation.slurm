#!/usr/bin/env bash
#SBATCH --job-name=qwen-s43-eval-prep
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1/logs/%x-%j.err
set -euo pipefail
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_seed43_v1
cd "${SLURM_SUBMIT_DIR}"; module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/prepare_qwen_scale_probe_evaluation.py --root "${ROOT}" --training-relative training/replay_w0_5_seed43 --label-prefix qwen_scale_seed43_step --resolved-revision-prefix qwen-scale-probe-seed43-update --source-manifest /vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json --general-corpus /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl
