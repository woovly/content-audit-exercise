"""Run one audit end to end and print the findings.

    python scripts/demo.py
"""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.models import ContentItem, Rule
from pipeline.run import audit
from pipeline.store import connect

logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(name)s %(message)s")

ITEM = ContentItem(
    item_id="ig_88213",
    brand_id="brand_7",
    media_url="https://cdn.example.com/v/88213.mp4?utm_source=ig&igshid=abc",
    caption="  loving the  new  summer drop  #ad ",
)

RULES = [
    Rule("R-001", "Disclosure (#ad or equivalent) must appear in the caption."),
    Rule("R-003", "Logo must appear unobstructed for at least 2 seconds."),
    Rule("R-007", "No unsubstantiated efficacy claims."),
    Rule("R-011", "Approved colourway only."),
    Rule("R-014", "Competitor products must not appear in frame."),
]


def main() -> int:
    conn = connect(":memory:")
    try:
        run = audit(conn, "aud_demo", ITEM, RULES)
    except NotImplementedError:
        print("\n" + "=" * 68)
        print("The pipeline ran. store.write_findings() is not implemented yet —")
        print("that is Part 2 of the exercise. See PROBLEM.md.")
        print("=" * 68)
        return 0

    print(f"\nrun={run.run_id} status={run.status} findings={len(run.findings)}")
    for f in run.findings:
        print(f"  {f.rule_id}  {f.verdict:<7} {f.confidence:.2f}  {f.evidence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
