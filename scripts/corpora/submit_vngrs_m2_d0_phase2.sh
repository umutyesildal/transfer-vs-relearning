#!/usr/bin/env bash
set -euo pipefail
: "${EXPECTED_COMMIT:?}" "${DECISIONS_JSONL:?}"
test -s /vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1/control/phase1_state.json
test -s "$DECISIONS_JSONL"
exports="ALL,EXPECTED_COMMIT=${EXPECTED_COMMIT},DECISIONS_JSONL=${DECISIONS_JSONL}"
sbatch --test-only --export="$exports" slurm/m2/finalize_vngrs_m2_d0_phase2.slurm
phase2_id="$(sbatch --parsable --export="$exports" slurm/m2/finalize_vngrs_m2_d0_phase2.slurm)"
printf 'phase2_id=%s\ndecisions=%s\n' "$phase2_id" "$DECISIONS_JSONL"
