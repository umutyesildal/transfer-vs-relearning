#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
source_root=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
split_root=/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1
coverage_root=/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_phase2_evidence_v1
test ! -e "$output_root"
test "$(sha256sum "$source_root/control/materialization_v3.json" | cut -d' ' -f1)" = bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10
test "$(sha256sum "$split_root/control/phase1_state.json" | cut -d' ' -f1)" = a09c0c62fffb8536b9917cc9755a40c35eb8c0f862f5b41d044f3de8f4e7d609
test "$(sha256sum "$split_root/splits/train_document_ids.jsonl" | cut -d' ' -f1)" = 90b74fbcfe62107693c35161fc328a6e43b13a830fc9590cc9810d3e99955aac
test "$(sha256sum "$coverage_root/control/final_audit.json" | cut -d' ' -f1)" = 6ce5f1f7b13fa61ae3f9c021b237b0464e4989ae179dc73fe32030049772c177
test "$(sha256sum "$coverage_root/reports/human_review_packet.jsonl" | cut -d' ' -f1)" = 621d8416f120803cc37f75453f0068a5fecaa60562698f11936b22caa3b75c61
test "$(sha256sum artifacts/corpora/vngrs_m2_d0/human_review_decisions_73329e45fd8f.jsonl | cut -d' ' -f1)" = f6e1e2989de4593ca56707db6c3582f5efc7cd0bbd652ca965ef92ceeded7225
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$(squeue -h -n vngrs-m2-oscar-p2-v1 | wc -l)" -eq 0
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/phase2_vngrs_m2_oscar_v1.slurm
job_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/phase2_vngrs_m2_oscar_v1.slurm)"
printf 'job_id=%s\nsource_root=%s\nsplit_root=%s\ncoverage_root=%s\noutput_root=%s\n' \
  "$job_id" "$source_root" "$split_root" "$coverage_root" "$output_root"
