#!/usr/bin/env bash
# monitor.sh — supervise the local OptimAI CLI process and its crawl4ai container.
# Restarts either if either is down. Logs to /var/log/optimai-monitor.log.
set -u
LOG=/var/log/optimai-monitor.log
CLI_BIN=${OPTIMAI_CLI_BIN:-/usr/local/bin/optimai-cli}
CLI_NAME=${OPTIMAI_CLI_NAME:-optimai}
DOCKER_CTN=${OPTIMAI_DOCKER_CTN:-optimai_crawl4ai_0_7_8}
SLEEP=${OPTIMAI_MONITOR_SLEEP:-30}

log() { echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') $*" >> "$LOG"; }

ensure_docker_ctn() {
  if ! command -v docker >/dev/null; then return 0; fi
  if ! docker ps --format '{{.Names}}' | grep -q "^${DOCKER_CTN}\$"; then
    log "container $DOCKER_CTN is not running; trying docker start"
    docker start "$DOCKER_CTN" >> "$LOG" 2>&1 || true
  fi
}

ensure_cli_process() {
  if ! pgrep -f "$CLI_BIN" >/dev/null && ! pgrep -f "$CLI_NAME" >/dev/null; then
    log "optimai-cli not running; starting in a detached screen session"
    if command -v screen >/dev/null; then
      screen -dmS optimai "$CLI_BIN" run
    else
      nohup "$CLI_BIN" run >> "$LOG" 2>&1 &
    fi
  fi
}

log "monitor start (sleep=${SLEEP}s)"
while true; do
  ensure_docker_ctn
  ensure_cli_process
  sleep "$SLEEP"
done
