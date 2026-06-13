#!/usr/bin/env bash
# fleet.sh — run a single optimai-cli command on many hosts over SSH.
#
# Usage:
#   fleet.sh "optimai-cli status" hosts.txt
#   fleet.sh "systemctl restart optimai" hosts.txt
#
# hosts.txt: one host per line, optionally user@host.
set -uo pipefail
CMD="$1"
HOSTS_FILE="${2:-hosts.txt}"
[ -z "$CMD" ] && { echo "usage: $0 <cmd> <hosts.txt>"; exit 1; }
[ -f "$HOSTS_FILE" ] || { echo "no $HOSTS_FILE"; exit 1; }

while IFS= read -r HOST; do
  [[ -z "$HOST" || "$HOST" =~ ^# ]] && continue
  echo "=== $HOST ==="
  ssh -o ConnectTimeout=5 -o BatchMode=yes "$HOST" "$CMD" 2>&1 || echo "  [failed]"
  echo ""
done < "$HOSTS_FILE"
