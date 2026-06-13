# OptimAI Node Operator Toolkit

Real, working tools for operating one or many OptimAI Network nodes from a
single control box. The OptimAI CLI (`optimai-cli`) is the only first-party
binary, but it doesn't help when you want to:

- Run a fleet of nodes
- Watchdog a single node and auto-restart on failure
- Pull rewards history and pretty-print it
- Send a Telegram alert when the device disconnects

This repo provides exactly that. It is **not** a wrapper that hides the
official CLI — it calls it via subprocess and adds missing glue.

## Files

| File | Purpose |
|---|---|
| `monitor.sh` | watch the local `crawl4ai` container and the CLI process; restart on crash; log to syslog |
| `fleet.sh`    | run the same command on N nodes over SSH (deploy a config update) |
| `rewards.py`  | parse the CLI's `--rewards` JSON output, build a CSV, plot a 7-day line |
| `healthcheck.py` | long-running daemon that pings the CLI's status and alerts via Telegram on disconnect |
| `Makefile` | one-liner targets: `install`, `monitor`, `rewards` |
| `systemd/optimai-monitor.service` | systemd unit for the healthcheck |

## Quick start

```bash
make install              # copy scripts to /usr/local/bin and install systemd unit
optimai-monitor --install # tells the CLI to start on boot
make rewards              # prints last 7 days of rewards as a CSV
```

## Requirements

- The official `optimai-cli` already installed (`/usr/local/bin/optimai-cli`)
- An OptimAI account already signed in (run `optimai-cli signin` once)
- Python 3.10+ for the scripts
- Optional: `matplotlib` for the rewards plot

## License

MIT
