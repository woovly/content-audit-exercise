"""Put the pipeline under the kind of load that broke production.

Runs several audits back to back against a provider that is having a bad
night. This is how the incident in logs/ was eventually reproduced.

    python scripts/load_test.py
    AUDIT_FAILURE_RATE=0.6 RUNS=10 python scripts/load_test.py
"""
import logging
import os
import sys
import time

os.environ.setdefault("AUDIT_FAILURE_RATE", "0.4")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from concurrent.futures import ThreadPoolExecutor, as_completed

from pipeline.models import ContentItem, Rule
from pipeline.perceive import perceive
from pipeline.score import score_rule

logging.basicConfig(level=logging.ERROR, format="%(levelname)-5s %(message)s")

RUNS = int(os.environ.get("RUNS", "5"))
ITEM = ContentItem("ig_88213", "brand_7", "https://cdn.example.com/v/88213.mp4", "summer drop #ad")
RULES = [Rule(f"R-{i:03d}", f"rule {i}") for i in range(1, 13)]


def main() -> int:
    perception = perceive(ITEM)
    print(f"failure_rate={os.environ['AUDIT_FAILURE_RATE']}  runs={RUNS}  "
          f"rules_per_run={len(RULES)}\n")
    for n in range(1, RUNS + 1):
        started, scored, failed = time.monotonic(), 0, 0
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(score_rule, ITEM, perception, r) for r in RULES]
            for future in as_completed(futures):
                try:
                    future.result()
                    scored += 1
                except Exception:
                    failed += 1
        print(f"run {n}:  scored={scored:>2}  failed={failed:>2}  "
              f"elapsed={time.monotonic() - started:5.1f}s")
    print("\nIf the later runs look nothing like the first one, that is the bug.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
