#!/usr/bin/env python3
"""Long-running healthcheck for optimai-cli. Alerts via Telegram on disconnect."""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request


def cli_status(bin_path: str) -> dict:
    out = subprocess.check_output([bin_path, "status", "--json"], text=True, timeout=15)
    return json.loads(out)


def send_tg(bot: str, chat: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot}/sendMessage"
    body = json.dumps({"chat_id": chat, "text": text, "parse_mode": "Markdown"}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print(f"telegram send failed: {e}", file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cli", default=os.getenv("OPTIMAI_CLI_BIN", "/usr/local/bin/optimai-cli"))
    p.add_argument("--interval", type=int, default=60)
    p.add_argument("--device-id", default=os.getenv("OPTIMAI_DEVICE_ID", ""))
    p.add_argument("--tg-bot", default=os.getenv("TG_BOT"))
    p.add_argument("--tg-chat", default=os.getenv("TG_CHAT"))
    p.add_argument("--once", action="store_true", help="check once and exit")
    args = p.parse_args()

    fail_count = 0
    while True:
        try:
            s = cli_status(args.cli)
            connected = s.get("connected") or s.get("online") or s.get("nodeState") == "online"
            ts = s.get("deviceId") or args.device_id
            print(f"[{time.strftime('%H:%M:%S')}] device={ts[:8]}... connected={connected}")
            if not connected:
                fail_count += 1
                if fail_count >= 3 and args.tg_bot and args.tg_chat:
                    send_tg(args.tg_bot, args.tg_chat, f"⚠️ OptimAI node {ts[:8]}... disconnected 3x in a row")
            else:
                fail_count = 0
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] status check failed: {e}")
            fail_count += 1
            if fail_count >= 3 and args.tg_bot and args.tg_chat:
                send_tg(args.tg_bot, args.tg_chat, f"❌ OptimAI status check failed 3x: {e}")
        if args.once:
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
