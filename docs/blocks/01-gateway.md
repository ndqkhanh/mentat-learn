# Mentat-Learn Block 01 — Unified Gateway

## Responsibility

One process fronts every channel (Slack, iMessage, WhatsApp, Telegram, Signal, email, web UI). Normalizes inbound messages, routes replies back to the originating channel with channel-native formatting. One persona, one agent loop, many surfaces.

Reference: [docs/52 Dive into OpenClaw](../../../docs/52-dive-into-open-claw.md) — OpenClaw's gateway pattern is the dominant multi-channel approach; Mentat adopts it and adds cache-aware skill routing.

## Channel adapters

Each channel implements a thin adapter:

```python
class ChannelAdapter:
    channel: str
    def receive(self) -> Iterable[InboundMessage]: ...
    def send(self, reply: OutboundMessage) -> None: ...
    def capabilities(self) -> ChannelCaps: ...
    def auth_info(self) -> AuthContext: ...
```

Inbound normalization turns channel-specific payloads into a common `InboundMessage(user_ref, session_ref, text, attachments, channel, capabilities)` shape. Outbound rendering applies channel-native formatting (emoji / mentions / rich cards / HTML / plain).

## Session identity across channels

A single user across channels resolves to **one user record** via linked identities (e.g., same phone number on WhatsApp + iMessage; same email on Slack + Web). Cross-channel linkage is explicit (user confirms at first use on each new channel) — never silent.

Consent flags per channel independently control memory persistence ([block 08 Privacy Scope](08-privacy-scope.md)).

## Routing modes

- **Direct** — one user turn → one agent loop invocation.
- **Grouped** (WhatsApp/Slack group) — user's messages within a group are addressed to the group, not the agent; Mentat only responds when mentioned or when it holds a scheduled automation posting to the group.
- **Scheduled** — cron-triggered output (morning summary, weekly review); uses the channel the automation was configured for.

## Graceful degradation

- If a channel webhook is down: queue outbound messages; retry; alert the user via an alternate channel if available.
- If the LLM provider is temporarily unavailable: "I'm having trouble reaching my model; I'll be back in a moment" response; no silence.

## Rate control

- Per-channel rate caps derived from platform limits (WhatsApp Business, Telegram, Slack) plus per-user sending-rate caps to prevent runaway scheduled automations.

## Security

- Channel tokens encrypted per-user with per-user derived keys.
- Inbound redaction: PII-shape values in user uploads are optionally stripped before entering memory (per consent flags).
- No cross-user bleed: the gateway runs per-user-process; user A's webhooks never see user B's state.

## Failure modes

| Mode | Defense |
|---|---|
| Channel adapter crash | Watchdog + restart |
| Cross-channel identity confusion | Explicit link confirmation at first use |
| Webhook signature mismatch | Reject |
| Duplicate message delivery | Idempotency key on `InboundMessage.id` |
| Cascading auto-replies in a group | Mute mode after N consecutive turns from the agent |

## Metrics

- `gateway.messages_per_channel`
- `gateway.p95_end_to_first_reply_ms`
- `gateway.cross_channel_resolutions`
- `gateway.auth_failures` per channel
- `gateway.outbound_retries`
