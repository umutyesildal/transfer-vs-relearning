#!/usr/bin/env bash
#SBATCH --job-name=qwen-scale-eval-prep
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/qwen_scale_probe_v3/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/qwen_scale_probe_v3/logs/%x-%j.err
set -euo pipefail
ROOT=/vol/tmp2/yesildau/qwen_scale_probe_v3
cd "${SLURM_SUBMIT_DIR}"; module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/m1/prepare_qwen_scale_probe_evaluation.py --root "${ROOT}" --source-manifest /vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json --general-corpus /vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl
