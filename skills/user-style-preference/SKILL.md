---
name: 'user-style-preference'
description: 'Capture per-user style preferences (tone, length, formality) only with explicit opt-in; cascade purge on right-to-erasure.'
version: '0.1.0'
triggers: ['style', 'tone', 'preference', 'verbosity']
tags: ['preference', 'consent', 'right-to-erasure']
---

# Goal
Extract per-user style preferences from dialogue and apply them on
later turns; never persist a preference without active opt-in, and
purge every derived skill on a deletion request.

# Constraints & Style
- Capture is gated on `consent.style_capture == true` in the user's
  consent record; default off.
- Allowed preference fields: `tone` (formal / neutral / playful),
  `length` (terse / standard / detailed), `formality`, `language`.
- Skills land in `Users/<user_id>/style/`; merging respects the existing
  trust tier (`T2-AUTO-EXTRACTED` until reviewed).
- Bright-lines: `BL-MENTAT-SKILL-CONSENT` (opt-in required, deletion
  cascades), `BL-MENTAT-SKILL-MULTI-USER-EXPORT` (one user's prefs may
  not inform another user's responses without explicit consent).

# Workflow
1. Read `consent.style_capture` for the user; abort if false.
2. Run `DialogueExtractor` with the style-shaped `P_ext` template.
3. Validate the output schema is one of the allowed preference fields;
   drop anything outside the closed taxonomy.
4. Propose into `candidates/`; HITL or rule-based review promotes.
5. On deletion request, walk `Users/<user_id>/` and remove every skill,
   appending a tombstone row to `provenance.jsonl`.
