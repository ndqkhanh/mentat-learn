---
name: privacy-redactor
description: PII / secrets redaction at every channel ingest.
---
# Privacy Redactor

Every inbound message passes through the redactor before any
memory write. Catches:

- Email addresses (preserved hash for cross-message linking).
- Phone numbers.
- Credit-card-pattern strings.
- API keys and tokens (heuristic + pattern).
- Names (user-name allow-list; everyone else redacted).

Redaction is **deterministic** — the same input always maps to the
same placeholder, so coreference works across messages.

`LBL-MENTAT-PRIVACY`: un-redacted ingest never reaches memory.
