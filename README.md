# content-audit (cut-down)

**Candidates: read [`PROBLEM.md`](PROBLEM.md).** It has the context, the two
tasks and the ground rules.

A small version of the shape of our production pipeline.

    content item  ->  normalise  ->  perceive  ->  score against rules  ->  write findings

Perception and the model call are **stubbed**, so nothing costs money or takes
thirty seconds.

    pipeline/models.py      domain objects
    pipeline/normalise.py   strip tracking params, tidy the caption
    pipeline/perceive.py    stub: canned transcript / OCR / frame labels
    pipeline/provider.py    model client, retries transient failures
    pipeline/score.py       one rule -> one finding
    pipeline/store.py       sqlite
    pipeline/run.py         orchestrator, scores a rule set for one item
    scripts/demo.py         run one audit end to end
    scripts/load_test.py    run several audits under load
    tests/                  five tests, all passing
    logs/                   production logs from the incident

## Run it

    pip install pytest

    pytest -q                      # 5 passed
    python scripts/demo.py         # one audit, end to end
    python scripts/load_test.py    # several audits, under load
