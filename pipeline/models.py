"""Domain objects for the content-audit pipeline."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional

Verdict = Literal["pass", "breach", "unclear"]


@dataclass(frozen=True)
class ContentItem:
    item_id: str
    brand_id: str
    media_url: str
    caption: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    text: str


@dataclass(frozen=True)
class Perception:
    transcript: str
    ocr_text: str
    frame_labels: list[str]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    verdict: Verdict
    evidence: str
    confidence: float


@dataclass
class AuditRun:
    run_id: str
    item: ContentItem
    status: str = "pending"          # pending | running | complete | failed
    started_at: Optional[datetime] = None
    findings: list[Finding] = field(default_factory=list)
