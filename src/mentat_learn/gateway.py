"""Multi-channel gateway: one persona, many channels.

Channel adapters normalize InboundMessage / OutboundMessage shapes. In-memory
channel ships by default for tests and local dev; production plugs in Slack,
iMessage, Telegram, etc. via the adapter protocol.
"""
from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class InboundMessage:
    id: str
    user_id: str
    session_id: str
    channel: str
    text: str
    ts: float = field(default_factory=time.time)


@dataclass
class OutboundMessage:
    in_reply_to: str
    user_id: str
    session_id: str
    channel: str
    text: str
    ts: float = field(default_factory=time.time)


class ChannelAdapter(ABC):
    channel: str = ""

    @abstractmethod
    def receive(self) -> list[InboundMessage]:  # pragma: no cover - abstract
        raise NotImplementedError

    @abstractmethod
    def send(self, message: OutboundMessage) -> None:  # pragma: no cover - abstract
        raise NotImplementedError


class InMemoryChannel(ChannelAdapter):
    """Useful for tests and local dev; round-trip through plain queues."""

    def __init__(self, name: str = "in-memory") -> None:
        self.channel = name
        self._inbound: list[InboundMessage] = []
        self._outbound: list[OutboundMessage] = []

    def push(self, user_id: str, session_id: str, text: str) -> InboundMessage:
        msg = InboundMessage(
            id=uuid.uuid4().hex[:12],
            user_id=user_id,
            session_id=session_id,
            channel=self.channel,
            text=text,
        )
        self._inbound.append(msg)
        return msg

    def receive(self) -> list[InboundMessage]:
        out, self._inbound = self._inbound, []
        return out

    def send(self, message: OutboundMessage) -> None:
        self._outbound.append(message)

    def sent(self) -> list[OutboundMessage]:
        return list(self._outbound)


class Gateway:
    """Holds channel adapters; routes inbound → agent, outbound → correct channel."""

    def __init__(self) -> None:
        self._adapters: dict[str, ChannelAdapter] = {}

    def register(self, adapter: ChannelAdapter) -> None:
        if not adapter.channel:
            raise ValueError("channel adapter must set .channel")
        if adapter.channel in self._adapters:
            raise ValueError(f"channel {adapter.channel!r} already registered")
        self._adapters[adapter.channel] = adapter

    def channels(self) -> list[str]:
        return sorted(self._adapters)

    def get(self, channel: str) -> Optional[ChannelAdapter]:
        return self._adapters.get(channel)

    def drain_inbound(self) -> list[InboundMessage]:
        """Drain every channel's inbound queue in deterministic order."""
        messages: list[InboundMessage] = []
        for name in sorted(self._adapters):
            messages.extend(self._adapters[name].receive())
        return messages

    def send(self, message: OutboundMessage) -> None:
        adapter = self._adapters.get(message.channel)
        if adapter is None:
            raise LookupError(f"no adapter for channel {message.channel!r}")
        adapter.send(message)
