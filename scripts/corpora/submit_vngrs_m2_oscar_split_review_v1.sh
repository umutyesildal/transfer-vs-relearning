#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?Set the exact authorized implementation commit}"
source_root=/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
prior_root=/vol/tmp2/yesildau/vngrs_m2_oscar_fact_pair_audit_v1
output_root=/vol/tmp2/yesildau/vngrs_m2_oscar_split_review_v1
test ! -e "$output_root"
test "$(sha256sum "$source_root/control/materialization_v3.json" | cut -d' ' -f1)" = bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10
test "$(sha256sum "$prior_root/reports/corpus_label_inventory.json" | cut -d' ' -f1)" = 178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b
test "$(sha256sum "$prior_root/reports/fact_pair_contamination_audit.json" | cut -d' ' -f1)" = bf076ab36fc31b16ab6f47d4a02ff04877177c1562e8bda2f8bb11f1a14091d3
test "$(sha256sum "$prior_root/control/recovery_state.json" | cut -d' ' -f1)" = 381772af2ce8ebca68aa30ee6862e0933689abb88dabafcf499d96603c5dba57
test "$(git rev-parse HEAD)" = "$EXPECTED_COMMIT"
test -z "$(git status --porcelain=v1)"
test "$(squeue -h -n vngrs-m2-oscar-review-v1 | wc -l)" -eq 0
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT}"
sbatch --test-only --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/split_review_vngrs_m2_oscar_v1.slurm
job_id="$(sbatch --parsable --output=/dev/null --error=/dev/null --export="$exports" \
  slurm/m2/split_review_vngrs_m2_oscar_v1.slurm)"
printf 'job_id=%s\nsource_root=%s\nprior_root=%s\noutput_root=%s\n' \
  "$job_id" "$source_root" "$prior_root" "$output_root"
