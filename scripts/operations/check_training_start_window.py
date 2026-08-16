#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from transfer_vs_relearning.training.operational import start_is_on_time


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", required=True, help="Timezone-aware ISO-8601 start cutoff")
    args = parser.parse_args()
    cutoff = datetime.fromisoformat(args.cutoff)
    if cutoff.tzinfo is None:
        raise ValueError("--cutoff must include a UTC offset")
    now = datetime.now(ZoneInfo("Europe/Berlin"))
    print(f"current_time={now.isoformat()}")
    print(f"start_cutoff={cutoff.isoformat()}")
    if not start_is_on_time(cutoff=cutoff, now=now):
        print("start_window=closed")
        raise SystemExit(75)
    print("start_window=open")


if __name__ == "__main__":
    main()
