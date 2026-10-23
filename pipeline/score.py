"""Scoring stage: ask the model whether this content breaches one rule."""
import json
import logging

from .models import ContentItem, Finding, Perception, Rule
from .provider import call_model

log = logging.getLogger(__name__)

_PROMPT = """You are auditing social content against one brand rule.

RULE {rule_id}: {rule_text}

TRANSCRIPT: {transcript}
ON-SCREEN TEXT: {ocr_text}
VISIBLE: {frame_labels}
CAPTION: {caption}

Reply with JSON: {{"verdict": "pass"|"breach"|"unclear", "evidence": str, "confidence": float}}
"""


def score_rule(item: ContentItem, perception: Perception, rule: Rule) -> Finding:
    prompt = _PROMPT.format(
        rule_id=rule.rule_id,
        rule_text=rule.text,
        transcript=perception.transcript,
        ocr_text=perception.ocr_text,
        frame_labels=", ".join(perception.frame_labels),
        caption=item.caption,
    )
    raw = call_model(prompt)
    payload = json.loads(raw)
    return Finding(
        rule_id=rule.rule_id,
        verdict=payload["verdict"],
        evidence=payload["evidence"],
        confidence=float(payload["confidence"]),
    )
