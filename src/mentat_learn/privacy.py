"""Privacy scope: per-channel consent enforcement + PII redaction."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional

from .models import ConsentFlags, UserProfile

_EMAIL_RX = re.compile(r"\b[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_PHONE_RX = re.compile(r"\b(?:\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]\d{3}[\s\-.]\d{4}\b")
_CC_RX = re.compile(r"\b(?:\d[ -]?){13,16}\b")
_SSN_RX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_JWT_RX = re.compile(r"\beyJ[\w-]+\.[\w-]+\.[\w-]+\b")


@dataclass
class RedactionReport:
    text: str
    redactions: list[tuple[str, str]]    # (kind, original_span)


class PIIRedactor:
    """Regex-based PII redaction. Preserves placeholders so agents can still reason."""

    def redact(self, text: str) -> RedactionReport:
        redactions: list[tuple[str, str]] = []
        out = text

        def sub(kind: str, rx: re.Pattern[str], placeholder: str) -> None:
            nonlocal out
            matches = list(rx.finditer(out))
            for m in matches:
                redactions.append((kind, m.group(0)))
            out = rx.sub(placeholder, out)

        sub("email", _EMAIL_RX, "[EMAIL]")
        sub("phone", _PHONE_RX, "[PHONE]")
        sub("cc", _CC_RX, "[CREDIT_CARD]")
        sub("ssn", _SSN_RX, "[SSN]")
        sub("jwt", _JWT_RX, "[JWT]")
        return RedactionReport(text=out, redactions=redactions)


class PrivacyScope:
    """Enforce per-channel consent before allowing memory writes / cross-channel share."""

    def __init__(self, profile: UserProfile) -> None:
        self.profile = profile
        self._redactor = PIIRedactor()

    def consent_for(self, channel: str) -> ConsentFlags:
        return self.profile.channels_enabled.get(channel, ConsentFlags())

    def set_consent(self, channel: str, flags: ConsentFlags) -> None:
        self.profile.channels_enabled[channel] = flags

    def can_write_memory(self, channel: str) -> bool:
        return self.consent_for(channel).persistent_memory

    def can_share_cross_channel(self, channel: str) -> bool:
        return self.consent_for(channel).cross_channel_share

    def can_model_dialectic(self, channel: str) -> bool:
        return self.consent_for(channel).dialectic_modeling

    def scrub(self, text: str, channel: str) -> RedactionReport:
        """Always redact sensitive patterns on egress to memory/logging."""
        return self._redactor.redact(text)

    def any_consented_channel(self) -> Optional[str]:
        for chan, flags in self.profile.channels_enabled.items():
            if flags.persistent_memory:
                return chan
        return None

    def all_channels(self) -> Iterable[str]:
        return list(self.profile.channels_enabled)
