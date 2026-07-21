#!/usr/bin/env bash
#SBATCH --job-name=tr-bridge-finalize
#SBATCH --account=yesildau
#SBATCH --partition=std
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:30:00
#SBATCH --output=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.out
#SBATCH --error=/vol/tmp2/yesildau/turkish_bridge_v1/logs/%x-%j.err
set -euo pipefail

HOME_ROOT="/vol/fob-vol6/mi25/yesildau"
REPO_ROOT="${SLURM_SUBMIT_DIR:-${HOME_ROOT}/transfer-vs-relearning}"
SCRATCH_ROOT="/vol/tmp2/yesildau/turkish_bridge_v1"
CONFIG="${REPO_ROOT}/configs/corpora/trwiki_turkish_bridge_v1.yaml"
CORPUS_ROOT="${SCRATCH_ROOT}/corpus/trwiki_20260601_bridge_v1"
TASK_TMP="${SCRATCH_ROOT}/tmp/finalize_${SLURM_JOB_ID}"

cd "${REPO_ROOT}"
mkdir -p "${SCRATCH_ROOT}"/{logs,tmp,cache} "${TASK_TMP}"
export XDG_CACHE_HOME="${SCRATCH_ROOT}/cache"
export TMPDIR="${TASK_TMP}"
case "$(readlink -m "${CORPUS_ROOT}")" in
  /vol/tmp/yesildau/*|/vol/tmp2/yesildau/*) ;;
  *) echo "Unsafe corpus root" >&2; exit 2 ;;
esac

test -s "${CORPUS_ROOT}/manifests/corpus_manifest.json"
test -s "${CORPUS_ROOT}/reports/contamination_review_sample_seed42.json"
test ! -e "${CORPUS_ROOT}/reports/contamination_review_decision_seed42.json"
test ! -e "${CORPUS_ROOT}/manifests/corpus_manifest_final.json"
test ! -e "${CORPUS_ROOT}/manifests/bridge_split_final_sha256.txt"

module load anaconda/3-2024.06
conda run --name xfer-relearn python scripts/finalize_turkish_bridge_corpus.py \
  --config "${CONFIG}" --seed 42 --sample-size 20

test -s "${CORPUS_ROOT}/reports/contamination_review_decision_seed42.json"
test -s "${CORPUS_ROOT}/manifests/corpus_manifest_final.json"
test -s "${CORPUS_ROOT}/manifests/bridge_split_final_sha256.txt"
sha256sum -c "${CORPUS_ROOT}/manifests/bridge_split_final_sha256.txt"

du -xsh "${HOME_ROOT}"
df -h "${HOME_ROOT}" /vol/tmp /vol/tmp2
df -i "${HOME_ROOT}" /vol/tmp /vol/tmp2
find "${HOME_ROOT}" -xdev -type f -size +500M -printf '%s %p\n' | sort -nr
printf 'status=finalized\n'
