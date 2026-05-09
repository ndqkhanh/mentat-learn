---
name: dialectic-user-model
description: Honcho-style structured user model — preferences, style, patterns.
---
# Dialectic User Model

Per-user structured model:

```yaml
user_model:
  identity: alice@example.com
  preferences:
    - "vegan"
    - "no-meetings-friday"
    - "concise-responses"
  communication_style:
    formality: medium
    detail_level: high
    humor: dry
  decision_patterns:
    - intent: travel-planning
      pattern: "always asks about cancellation policy first"
    - intent: code-review
      pattern: "wants security implications surfaced"
  updated_at: 2026-05-09T11:00:00Z
```

Updates happen on confidence-gated promotion (L311-8). The model
is **queryable** — agent prompts include relevant slices, not the
whole model.
