#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote_cmd=$(cat <<'EOF'
set -euo pipefail
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
git status --short
git pull --ff-only origin corpus-update
git rev-parse --short HEAD
PYTHON=/vol/fob-vol6/mi25/yesildau/.conda/envs/xfer-relearn/bin/python
"$PYTHON" -m pytest -q tests/test_general_capability.py
echo __BASE_MANIFEST__
find artifacts/models/HuggingFaceTB__SmolLM2-1.7B -maxdepth 1 -type f -print | sort
echo __FROZEN_MANIFESTS__
find /vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/m1_relation_v2_1_7b_500_frozen -maxdepth 3 -type f -name '*manifest*.json' -print | sort
echo __FROZEN_TREE__
find /vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/m1_relation_v2_1_7b_500_frozen -maxdepth 2 -type f -print | sort
test -f artifacts/datasets/relation_v2_gate_v1/data/canonical_subject_profiles_5000.csv
echo REMOTE_PREFLIGHT_OK
EOF
)
quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
