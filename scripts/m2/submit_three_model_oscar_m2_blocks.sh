#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
source_root=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
split_root=/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_v1
test ! -e "$output_root"
test "$(sha256sum "$source_root/control/materialization_v3.json" | cut -d' ' -f1)" = bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10
test "$(sha256sum "$split_root/splits/train_document_ids.jsonl" | cut -d' ' -f1)" = 90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac
test "$(sha256sum "$split_root/splits/heldout_document_ids.jsonl" | cut -d' ' -f1)" = dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$(squeue -h -n vngrs-m2-oscar-blocks-v1 | wc -l)" -eq 0
available_bytes="$(df -PB1 /vol/tmp2/yesildau | awk 'NR==2 {print $4}')"
available_inodes="$(df -Pi /vol/tmp2/yesildau | awk 'NR==2 {print $4}')"
test "$available_bytes" -ge 10737418240
test "$available_inodes" -ge 4096
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_three_model_oscar_m2_blocks.slurm
job_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/materialize_three_model_oscar_m2_blocks.slurm)"
printf 'job_id=%s\noutput_root=%s\n' "$job_id" "$output_root"
