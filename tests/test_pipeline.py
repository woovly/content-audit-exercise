import pytest

from pipeline.models import ContentItem, Rule
from pipeline.normalise import normalise
from pipeline.perceive import perceive
from pipeline.score import score_rule
from pipeline.store import connect, read_findings


ITEM = ContentItem(
    item_id="ig_88213",
    brand_id="brand_7",
    media_url="https://cdn.example.com/v/88213.mp4?utm_source=ig&igshid=abc",
    caption="  loving the  new  summer drop  #ad ",
)
RULE = Rule(rule_id="R-014", text="Logo must appear unobstructed for at least 2 seconds.")


def test_normalise_strips_tracking_params():
    out = normalise(ITEM)
    assert "utm_source" not in out.media_url
    assert "igshid" not in out.media_url


def test_normalise_collapses_caption_whitespace():
    assert normalise(ITEM).caption == "loving the new summer drop #ad"


def test_perceive_returns_all_three_channels():
    p = perceive(ITEM)
    assert p.transcript and p.ocr_text and p.frame_labels


def test_score_rule_returns_a_finding():
    finding = score_rule(normalise(ITEM), perceive(ITEM), RULE)
    assert finding.rule_id == "R-014"
    assert finding.verdict in {"pass", "breach", "unclear"}


def test_read_findings_empty_for_unknown_run():
    conn = connect(":memory:")
    assert read_findings(conn, "run_does_not_exist") == []
