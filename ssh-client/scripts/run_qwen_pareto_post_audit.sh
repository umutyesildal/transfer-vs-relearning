#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

remote_cmd=$(cat <<'EOF'
set -euo pipefail
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
ROOT=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1
REPORT="$ROOT/post_run_storage_audit.txt"
STATUS="$ROOT/post_run_storage_audit.status"
test ! -e "$STATUS"
nohup bash -lc '
set -euo pipefail
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
ROOT=/vol/tmp2/yesildau/m1_qwen_checkpoint_pareto_v1
{
  echo __HOME_DU__
  du -xsh "$HOME_ROOT"
  echo __DF_H__
  df -h "$HOME_ROOT" /vol/tmp /vol/tmp2
  echo __DF_I__
  df -i "$HOME_ROOT" /vol/tmp /vol/tmp2
  echo __RESOLVED__
  readlink -f "$HOME_ROOT/transfer-vs-relearning/runs"
  readlink -f "$HOME_ROOT/transfer-vs-relearning/artifacts"
  readlink -f "$ROOT"
  echo __FAMILY_DU__
  du -sh "$ROOT"
  echo __LARGE_HOME_FILES__
  find "$HOME_ROOT" -xdev -type f -size +500M -printf "%s %p\n" | sort -nr
  echo __SUMMARY_HASHES__
  sha256sum "$ROOT/qwen_checkpoint_pareto_summary.csv" "$ROOT/qwen_checkpoint_pareto_summary.json" "$ROOT/checkpoint_registry.csv" "$ROOT/wave_manifest.json"
} > "$ROOT/post_run_storage_audit.txt" 2>&1
echo COMPLETE > "$ROOT/post_run_storage_audit.status"
' >/dev/null 2>&1 &
echo "AUDIT_PID=$!"
echo "REPORT=$REPORT"
EOF
)

quoted_remote_cmd=$(printf '%q' "$remote_cmd")
exec "$SCRIPT_DIR/hu_ssh_expect" "bash -lc $quoted_remote_cmd"
