#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
SCRATCH_ROOT=/vol/tmp2/yesildau/m1_cross_family_screen_v1
echo "__QUEUE__"
squeue -u yesildau -o "%.18i %.12T %.10M %.24j %.20N"
echo "__RECENT_ACCOUNTING__"
sacct -S now-2days -u yesildau -X --name=m1-xfam-preflight,m1-xfam-acquire,m1-xfam-train,m1-xfam-eval -o JobID,JobName,State,ExitCode,Elapsed,NodeList -n -P || true
echo "__ACCESS_RECORDS__"
for path in "$SCRATCH_ROOT"/manifests/access/*.json; do test -f "$path" && grep -E '"(label|status|resolved_revision|error_type)"' "$path" || true; done
echo "__TRAINING_MANIFESTS__"
find "$SCRATCH_ROOT/training" -mindepth 2 -maxdepth 2 -name training_manifest.json -print 2>/dev/null || true
echo "__EVALUATION_MANIFESTS__"
find "$SCRATCH_ROOT/evaluations" -mindepth 2 -maxdepth 2 -name evaluation_manifest.json -print 2>/dev/null || true
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
