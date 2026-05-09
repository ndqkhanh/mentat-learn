---
name: multi-channel-gateway
description: Slack / WhatsApp / Telegram / email gateway with canonical envelope.
---
# Multi-Channel Gateway

Every inbound message converts to a canonical envelope:

```yaml
inbound:
  channel: slack | whatsapp | telegram | email
  user_identity: <opaque>
  text: <redacted-payload>
  attachments: [...]
  metadata: {...}     # channel-specific bits
  ts: 2026-05-09T11:00:00Z
```

Outbound messages render per-channel from the same canonical
response. The agent never crafts channel-specific text; channel
adapters do the rendering.

`LBL-MENTAT-CHANNEL-NEUTRAL`: the canonical envelope is the truth;
channel rendering is view-only.
