from __future__ import annotations

import argparse
import time

from apscheduler.schedulers.background import BackgroundScheduler

from timecapsule.capture import capture_website
from timecapsule.storage import SnapshotStore


def capture_and_store(url: str, db: str) -> None:
    store = SnapshotStore(db)
    snapshot = capture_website(url)
    snapshot_id = store.add(snapshot)
    print(f"Saved snapshot #{snapshot_id} for {snapshot['site_key']} at {snapshot['timestamp']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scheduled website snapshot monitor")
    parser.add_argument("url", help="Public website URL to monitor")
    parser.add_argument("--hours", type=int, default=24, help="Capture interval in hours")
    parser.add_argument("--db", default="data/time_capsule.db", help="SQLite database path")
    args = parser.parse_args()

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        capture_and_store,
        "interval",
        hours=max(args.hours, 1),
        args=[args.url, args.db],
        id="website-monitor",
        max_instances=1,
        coalesce=True,
    )

    capture_and_store(args.url, args.db)
    scheduler.start()
    print(f"Monitoring {args.url} every {max(args.hours, 1)} hour(s). Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
