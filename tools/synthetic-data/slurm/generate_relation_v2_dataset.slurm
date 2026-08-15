#!/usr/bin/env bash
#SBATCH --job-name=relation-v2-generate
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out
#SBATCH --error=logs/%x-%j.err

set -euo pipefail

REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
cd "${REPO_ROOT}"
mkdir -p logs

module load anaconda/3-2024.06

echo "hostname=$(hostname)"
echo "slurm_job_id=${SLURM_JOB_ID:-none}"
conda run --name xfer-relearn python generate_relation_v2_dataset.py

sha256sum \
  output/relation_v2/manifest.json \
  output/relation_v2/acquisition_10_subjects_direct/train.jsonl \
  output/relation_v2/acquisition_10_subjects_direct/validation.jsonl \
  output/relation_v2/acquisition_10_subjects_direct/exact_prefix_probes_en.csv \
  output/relation_v2/acquisition_100_subjects_direct/train.jsonl \
  output/relation_v2/acquisition_100_subjects_direct/validation.jsonl \
  output/relation_v2/acquisition_100_subjects_direct/exact_prefix_probes_en.csv \
  output/relation_v2/acquisition_500_subjects_direct/train.jsonl \
  output/relation_v2/acquisition_500_subjects_direct/validation.jsonl \
  output/relation_v2/acquisition_500_subjects_direct/exact_prefix_probes_en.csv
