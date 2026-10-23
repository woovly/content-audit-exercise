"""Orchestrator: run one content item against one brand's rule set."""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from .models import AuditRun, ContentItem, Finding, Rule
from .normalise import normalise
from .perceive import perceive
from .provider import ProviderExhausted
from .score import score_rule
from .store import start_run, write_findings

log = logging.getLogger(__name__)

MAX_CONCURRENT_RULES = 8


def audit(conn, run_id: str, item: ContentItem, rules: list[Rule]) -> AuditRun:
    run = AuditRun(run_id=run_id, item=item, status="running",
                   started_at=datetime.now(timezone.utc))
    start_run(conn, run)

    item = normalise(item)
    perception = perceive(item)

    findings: list[Finding] = []
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_RULES) as pool:
        futures = {pool.submit(score_rule, item, perception, r): r for r in rules}
        for future in as_completed(futures):
            rule = futures[future]
            try:
                findings.append(future.result())
            except ProviderExhausted:
                log.error("run=%s rule=%s abandoned: provider exhausted",
                          run_id, rule.rule_id)
                run.status = "failed"
            except Exception:
                log.exception("run=%s rule=%s failed", run_id, rule.rule_id)
                run.status = "failed"

    write_findings(conn, run_id, findings)
    run.findings = findings
    if run.status != "failed":
        run.status = "complete"
    return run
