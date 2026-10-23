"""Model provider client.

Wraps the HTTP call to the scoring model and retries transient failures.
"""
import logging
import os
import random
import time

log = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT_SECONDS = 45

# Retry budget for the provider.
_retries_remaining = MAX_RETRIES


class TransientError(Exception):
    """429, 5xx, connection reset, read timeout."""


class TerminalError(Exception):
    """4xx that will never succeed."""


class ProviderExhausted(Exception):
    """Retry budget gone."""


def call_model(prompt: str, *, timeout: int = TIMEOUT_SECONDS) -> str:
    """Call the scoring model, retrying transient failures."""
    global _retries_remaining
    while True:
        try:
            return _post(prompt, timeout=timeout)
        except TransientError as exc:
            if _retries_remaining <= 0:
                log.error("provider retry budget exhausted: %s", exc)
                raise ProviderExhausted(str(exc)) from exc
            _retries_remaining -= 1
            delay = 2 ** (MAX_RETRIES - _retries_remaining)
            log.warning("transient provider error, retrying in %ss: %s", delay, exc)
            time.sleep(delay)


# How often the stubbed provider throws a transient error. Override with
# AUDIT_FAILURE_RATE to simulate a bad night at the provider.
_FAILURE_RATE = float(os.environ.get("AUDIT_FAILURE_RATE", "0.05"))


def _post(prompt: str, *, timeout: int) -> str:
    """Stubbed HTTP call. Returns canned JSON; fails like the real thing."""
    if random.random() < _FAILURE_RATE:
        raise TransientError("503 Service Unavailable")
    return (
        '{"verdict": "breach", '
        '"evidence": "Logo appears at 0:04 cropped on the right edge.", '
        '"confidence": 0.81}'
    )
