#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
ENV_FILE="$ROOT_DIR/.env"
HOST="${1:-gruenau10.informatik.hu-berlin.de}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing environment file: $ENV_FILE" >&2
  exit 1
fi

username=$(python3 -c "import re,sys; from pathlib import Path; text=Path(sys.argv[1]).read_text(encoding='utf-8'); m=re.search(r'^\\s*username\\s*[:=]\\s*[\\\"\']?([^\\\"\'\\s,]+)', text, re.M); print(m.group(1) if m else '')" "$ENV_FILE")

if [[ -z "$username" ]]; then
  echo "Could not read username from $ENV_FILE" >&2
  exit 1
fi

mkdir -p "$HOME/.ssh/controlmasters"

SSH_OPTS=(
  -o ControlMaster=auto
  -o ControlPath="$HOME/.ssh/controlmasters/%r@%h:%p"
  -o ControlPersist=60m
  -o ServerAliveInterval=30
  -o ServerAliveCountMax=3
)

if ssh -o BatchMode=yes -o ConnectTimeout=10 "${SSH_OPTS[@]}" "$username@$HOST" true 2>/dev/null; then
  exec ssh "${SSH_OPTS[@]}" "$username@$HOST"
fi

echo "Starting interactive SSH session. If prompted, enter your HU password once." >&2
exec ssh "${SSH_OPTS[@]}" "$username@$HOST"
