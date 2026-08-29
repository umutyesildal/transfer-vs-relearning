#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
source_root=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
prior_root=/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1
test ! -e "$output_root"
test "$(sha256sum "$source_root/control/materialization_v3.json" | cut -d' ' -f1)" = bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10
test "$(sha256sum "$prior_root/control/final_audit.json" | cut -d' ' -f1)" = 3add7667d202cb5547dc0847c9ad302a47e7e57cd7fb8f2f43fd4211dba86e7e
test "$(sha256sum "$prior_root/control/phase1_state.json" | cut -d' ' -f1)" = a09c0c62fffb8536b9917cc9755a40c35eb8c0f862f5b41d044f3de8f4e7d609
test "$(sha256sum "$prior_root/manifests/output_artifact_manifest.jsonl" | cut -d' ' -f1)" = 8a9c9dfaeba7b25a699c7f380492e54ba5595622d23bf428e66aeceee03c2061
test "$(sha256sum "$prior_root/reports/human_review_packet.jsonl" | cut -d' ' -f1)" = e0175029e17d9aaccb8a6c3c73c9322befe069e955539f2126c27cbb42053ac1
test "$(sha256sum "$prior_root/reports/human_review_sample.jsonl" | cut -d' ' -f1)" = cb294c2b4588619b19073dd5bbc8fa82337880f3d1adaf60488101b2095ebd33
test "$(sha256sum "$prior_root/splits/heldout_document_ids.jsonl" | cut -d' ' -f1)" = dc30629fe76ca722745fcd0148021de6c042218ed2994281d52d13c06011dc91
test "$(sha256sum "$prior_root/splits/train_document_ids.jsonl" | cut -d' ' -f1)" = 90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$(squeue -h -n vngrs-m2-oscar-cover-v1 | wc -l)" -eq 0
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/review_coverage_vngrs_m2_oscar_v1.slurm
job_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/review_coverage_vngrs_m2_oscar_v1.slurm)"
printf 'job_id=%s\nsource_root=%s\nprior_root=%s\noutput_root=%s\n' \
  "$job_id" "$source_root" "$prior_root" "$output_root"
