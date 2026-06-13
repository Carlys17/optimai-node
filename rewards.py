#!/usr/bin/env python3
"""Fetch OptimAI rewards history and print a CSV (and optional plot)."""
from __future__ import annotations
import argparse
import csv
import json
import os
import subprocess
import sys
from typing import List, Dict


def get_rewards(cli: str) -> List[Dict]:
    """Call `optimai-cli rewards --json` and parse."""
    out = subprocess.check_output([cli, "rewards", "--json"], text=True, timeout=30)
    data = json.loads(out)
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    if isinstance(data, list):
        return data
    raise RuntimeError(f"unexpected rewards JSON shape: {type(data)}")


def write_csv(rows: List[Dict], path: str) -> None:
    if not rows:
        print("no rows")
        return
    keys = sorted({k for r in rows for k in r.keys()})
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {len(rows)} rows to {path}")


def plot(rows: List[Dict], out: str) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping plot", file=sys.stderr)
        return
    by_date: Dict[str, float] = {}
    for r in rows:
        d = r.get("date") or r.get("ts", "")[:10]
        amt = float(r.get("amount", 0))
        by_date[d] = by_date.get(d, 0.0) + amt
    if not by_date:
        print("no dates to plot")
        return
    xs = sorted(by_date.keys())
    ys = [by_date[x] for x in xs]
    plt.figure(figsize=(8, 4))
    plt.plot(xs, ys, marker="o")
    plt.title("OptimAI rewards (last 7 days)")
    plt.xlabel("date")
    plt.ylabel("PEARL")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(out)
    print(f"plot saved to {out}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cli", default=os.getenv("OPTIMAI_CLI_BIN", "/usr/local/bin/optimai-cli"))
    p.add_argument("--csv", default="rewards.csv")
    p.add_argument("--plot", default="rewards.png")
    args = p.parse_args()
    rows = get_rewards(args.cli)
    write_csv(rows, args.csv)
    plot(rows, args.plot)


if __name__ == "__main__":
    main()
