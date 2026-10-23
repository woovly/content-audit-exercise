"""Perception stage. Stubbed: returns canned transcript / OCR / frame labels.

The real implementation transcodes, samples frames, runs ASR and OCR. None of
that runs here, so the round costs nothing and takes no time.
"""
from .models import ContentItem, Perception

_CANNED = {
    "transcript": "So this is the new summer line, I've been using it for about a week now...",
    "ocr_text": "SUMMER DROP 24 | #ad | swipe up",
    "frame_labels": ["person", "bottle", "logo-partial", "text-overlay"],
}


def perceive(item: ContentItem) -> Perception:
    return Perception(
        transcript=_CANNED["transcript"],
        ocr_text=_CANNED["ocr_text"],
        frame_labels=list(_CANNED["frame_labels"]),
    )
