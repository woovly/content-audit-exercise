"""Normalisation stage: strip tracking params, collapse caption whitespace."""
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import ContentItem

_TRACKING_PREFIXES = ("utm_",)
_TRACKING_KEYS = {"igshid", "fbclid", "gclid", "mc_cid"}


def _is_tracking(key: str) -> bool:
    return key in _TRACKING_KEYS or key.startswith(_TRACKING_PREFIXES)


def normalise(item: ContentItem) -> ContentItem:
    parts = urlsplit(item.media_url)
    kept = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
            if not _is_tracking(k)]
    url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(kept), ""))
    caption = re.sub(r"\s+", " ", item.caption).strip()
    return ContentItem(
        item_id=item.item_id,
        brand_id=item.brand_id,
        media_url=url,
        caption=caption,
    )
