# Mentat-Learn Block 07 — Session Persistence

## Responsibility

Conversations survive process restarts, channel switches, device changes. The user can leave mid-thread on iMessage, resume it on Slack an hour later, and Mentat still knows where they are.

Reference: [docs/10 multi-session-continuity](../../../docs/10-multi-session-continuity.md), [docs/55 Hermes](../../../docs/55-hermes-agent-self-improving.md).

## Session identity

A "session" is a coherent thread of user intent. In practice:

- One channel thread = one session.
- On cross-channel user identity resolution, related threads can be linked (explicit user confirmation).
- Sessions have idle timeouts; after N hours of inactivity, session marks `idle` but is resumable.

## Persisted state

Each session persists:

```yaml
session_id: UUID
user_id: UUID
channel: str
last_activity_at: datetime
context_window:
  recent_turns: [Turn]     # last N turns, raw
  compacted_history: str   # older turns, compacted via [docs/08]
  pinned_refs: [MemoryRef] # memory entries pinned to this session
working_state:
  todos: [Todo]            # scratchpad state
  open_questions: [str]
  in_flight_tool_calls: [ToolCall]
```

On restart, the agent loop rehydrates from this state; the user sees continuity.

## Storage

- SQLite per-user (default) with write-ahead logging for durability.
- Redis sidecar for hot sessions (LRU-capped; cold sessions go back to SQLite).
- Optional: external managed store (tenant-specific).

## Compaction on long sessions

Triggered when session token count exceeds threshold:

1. Keep SOUL.md, last N raw turns, pinned memory refs.
2. Summarize everything else via a structured compactor preserving "goal, decisions, findings, failed approaches, open questions".
3. Re-inject compacted summary in place of older raw turns.

Same pattern as [docs/08 context compaction](../../../docs/08-context-compaction.md).

## Cross-channel continuity

If a session is linked across channels:

- User on iMessage: session visible as iMessage-thread.
- User on Slack: same session visible; last messages from iMessage inlined at top as "continuing from your iMessage thread".
- Channel switch is explicit: user says "continue on Slack" or "see this thread in Slack", Mentat creates/resumes the linked session.

## Recovery from crashes

- Write-ahead log means we never lose turns in flight.
- Recovery pass on startup: verify invariants (referenced memory entries exist, in-flight tool calls resolved or timed out, session state coherent).
- If recovery finds an incoherent session, flag it; don't silently overwrite.

## User controls

- `DELETE /v1/sessions/{id}` — purge one session.
- `POST /v1/sessions/{id}/forget` — keep session for resumption but forget everything else about it.
- `GET /v1/sessions` — list sessions with metadata.

## Failure modes

| Mode | Defense |
|---|---|
| Session state corruption | Invariant checks on rehydrate; flag not overwrite |
| Hot session goes cold mid-turn | Redis sidecar; SQLite fallback |
| Cross-channel linkage surprise | Always explicit user confirmation |
| Zombie sessions (never closed) | Idle timeout + periodic GC |
| In-flight tool call orphaned | Recovery pass re-queries tool or marks call failed |

## Metrics

- `session.active_count`
- `session.compaction_events`
- `session.rehydration_latency_ms` p95
- `session.cross_channel_links`
- `session.recovery_invariant_failures` (hot alarm)
