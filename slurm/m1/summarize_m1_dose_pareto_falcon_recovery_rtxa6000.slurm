#!/usr/bin/env bash
#SBATCH --job-name=m1-v4-falcon-summary
#SBATCH --account=yesildau
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1/logs/%x-%j.err
set -euo pipefail
REPO_ROOT="${SLURM_SUBMIT_DIR:-$(pwd)}"
ROOT=/vol/tmp2/yesildau/m1_provenance_screen_v4_dose_pareto_v1
REGISTRY="${REPO_ROOT}/configs/experiments/m1_provenance_screen_v4_dose_pareto_v1.yaml"
PYTHON=/vol/tmp2/yesildau/m1_provenance_screen_v3/compat_envs/torch260_cu124_v1/bin/python
SUMMARY_ROOT="${ROOT}/analysis/three_model_dose_pareto_summary_v1"
cd "${REPO_ROOT}"
test "$(git rev-parse HEAD)" = "${M1_V4_EXPECTED_COMMIT:?}"
test -f "${FALCON_RECOVERY_PREFLIGHT:?}"
test "$(sha256sum "${FALCON_RECOVERY_PREFLIGHT}" | awk '{print $1}')" = "${FALCON_RECOVERY_PREFLIGHT_SHA256:?}"
test ! -e "${SUMMARY_ROOT}"
"${PYTHON}" scripts/m1/summarize_m1_dose_pareto.py --registry "${REGISTRY}" --output-root "${SUMMARY_ROOT}" --recovery-contract-sha256 "${FALCON_EVALUATION_RELOCATION_SHA256:?}"
