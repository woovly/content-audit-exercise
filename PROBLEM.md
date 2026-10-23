# Content audit pipeline — working session

**75 minutes · pairing, not an exam.**

This is a cut-down version of the shape of our production pipeline. It is small
enough to read in ten minutes and real enough to reason about.

    content item ──▶ normalise ──▶ perceive ──▶ score against rules ──▶ write findings

A content item is a social post: a video, a caption, and the brand whose
campaign it belongs to. A brand gives us a guideline document; each rule in it
becomes a `Rule`. For every applicable rule the pipeline produces a `Finding` —
a verdict, the evidence from the content that supports it, and a confidence.
Our customers are large consumer brands, so when we say a post breaches a rule,
someone may ask us why.

## What's real and what isn't

**Stubbed, deliberately** — nothing here costs money or takes thirty seconds:

- `perceive.py` returns a canned transcript, canned OCR text and canned frame
  labels. The real one transcodes, samples frames and runs ASR and OCR.
- `provider.py::_post` returns canned JSON and fails like the real thing. There
  is no network call.

**Real:** everything else. The orchestration, the retry handling, the
persistence and the tests are the code as it would be.

```
pipeline/models.py      ContentItem, Rule, Perception, Finding, AuditRun
pipeline/normalise.py   strip tracking params, tidy the caption
pipeline/perceive.py    stub
pipeline/provider.py    model client — retries transient failures
pipeline/score.py       one rule -> one finding
pipeline/store.py       sqlite
pipeline/run.py         orchestrator — scores a rule set for one item
scripts/demo.py         run one audit end to end
scripts/load_test.py    run several audits against a provider having a bad night
tests/                  five tests, all passing
logs/                   production logs from the incident in Part 1
```

## Run it

    pip install pytest

    pytest -q                      # 5 passed
    python scripts/demo.py         # one audit, end to end
    python scripts/load_test.py    # several audits, under load

`demo.py` stops with a message where Part 2 begins — `write_findings` is the
function you are going to write, so a full run cannot finish until it exists.

The stubbed provider fails a small fraction of calls, the way a real one does.
`AUDIT_FAILURE_RATE` controls it:

    AUDIT_FAILURE_RATE=0.6 RUNS=10 python scripts/load_test.py

---

## Part 1 — something is broken in production

Two nights ago this started failing under load, and we could not reproduce it
locally. Once it starts, **every run after it fails the same way until the
process is restarted**.

The logs from that night are in `logs/incident-2026-10-20.log`, and
`scripts/load_test.py` is roughly how we eventually reproduced it.

**Find it, explain the mechanism, and fix it.**

What we care about, in order:

1. Why it happens — the mechanism, not the symptom.
2. Why it never reproduced on a developer machine.
3. A fix, and some way of demonstrating that the fix works.

---

## Part 2 — add the findings writer

`store.write_findings(conn, run_id, findings)` is a stub that raises
`NotImplementedError`. `run.py` already calls it. Implement it.

It has to be:

- **Safe to run twice.** The pipeline retries, and a step can re-execute after a
  crash. Running it twice must leave one set of findings, not two.
- **Able to handle partial failure.** Some findings written, then the store
  errors. The system must be in a state someone can reason about afterwards.
- **Observable.** When this goes wrong at 3am, whoever is on call should be able
  to tell from the logs what happened and how far it got.
- **Tested.**

You may change the schema in `store.py` if you want to. Say what you're changing
and why.

---

## Ground rules

- **Think out loud.** We are more interested in how you work than in whether you
  finish. An unfinished Part 2 you reasoned about clearly beats a finished one
  we didn't follow.
- **Ask questions.** Anything about the domain, the requirements or what we'd
  want in production — ask. Asking what the identity of a finding should be is a
  better move than guessing silently.
- **Use whatever you normally use.** Search, documentation, an AI assistant —
  Claude Code, Cursor, whatever is open on an ordinary working day. We would
  rather see your real workflow than a performance.
- **There is no unpaid take-home.** This session is the whole exercise.
