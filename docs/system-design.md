# Mentat-Learn — System Design

## Topology

Per-user deployment. Mentat is a small, always-on service that runs cheaply (target: $5-VPS deployable, same envelope Hermes Agent cites). Skill library and memory are per-user; no cross-user sharing unless explicitly opted in.

```
                Slack / iMessage / WhatsApp / Telegram / Email / Web
                                │
                                ▼
                   ┌─────────────────────────┐
                   │    Unified Gateway      │
                   │  (channel-adapter set)  │
                   └─────────────┬───────────┘
                                 │
                                 ▼
                   ┌─────────────────────────┐
                   │       Agent Loop        │◄─── skill dispatch
                   │  (harness_core-backed)  │
                   └──┬────────┬────────┬────┘
                      │        │        │
              ┌───────▼──┐  ┌──▼────┐  ┌▼──────────┐
              │ Memory   │  │ Tools │  │ Skill Lib │
              │ (4-layer)│  │ +MCP  │  │ (cache-   │
              └──┬───────┘  └───────┘  │  aware)   │
                 │                      └─────┬─────┘
                 │                            │
                 ▼                            │
          ┌──────────────┐                    │
          │  Honcho      │                    │
          │ (dialectic)  │                    │
          └──────────────┘                    │
                                              ▼
                                      ┌───────────────┐
                                      │Skill Extractor│
                                      │ (on task end) │
                                      └───────────────┘
             ↕ Cron scheduler  ↕ Session persistence  ↕ Self-eval every 15 tasks
             ↕ Privacy scope   ↕ SOUL.md              ↕ Autogenesis versioning
```

## Data model

```python
class User:
    id: UUID
    soul_md: str                   # canonical persona
    channels_enabled: dict[str, ConsentFlags]
    memory_opt_in: bool

class Session:
    id: UUID
    user_id: UUID
    channel: str
    started_at, last_activity_at
    state: "active" | "idle" | "closed"

class Skill:
    id: UUID
    version: int
    name: str
    description: str              # routing hint
    body_md: str                  # full skill procedure (cache-loaded)
    required_tools: list[str]
    subsumed_by: UUID | None      # for compression
    use_count: int
    success_rate: float

class MemoryEntry:
    id: UUID
    layer: "procedural" | "fact" | "session" | "dialectic"
    content: str
    ttl: datetime | None
    provenance: dict
```

## Public API (for user's own control)

```
GET  /v1/me                                # user record
POST /v1/me/consent                         # update per-channel consent
GET  /v1/me/memory?layer=fact               # list memory in a layer
DELETE /v1/me/memory/{id}                   # forget a specific entry
POST /v1/me/memory/forget-session/{sid}     # purge a session's memory

GET  /v1/skills                             # list skills (user can see them all)
GET  /v1/skills/{id}                        # read a skill's body_md
POST /v1/skills/{id}/disable                # opt out of a specific skill
GET  /v1/skills/history                     # audit of skill patches

POST /v1/cron                               # create a scheduled automation
GET  /v1/cron
DELETE /v1/cron/{id}

POST /v1/soul                               # edit persona (requires confirmation)
GET  /v1/soul/history                       # version history

POST /v1/harness/nlah                       # optional advanced NLAH spec
```

## Channel adapters

Each supported channel is a thin adapter implementing:

```python
class ChannelAdapter:
    channel: str
    def receive() -> Iterable[InboundMessage]: ...
    def send(reply: OutboundMessage) -> None: ...
    def capabilities() -> {"markdown": bool, "files": bool, "buttons": bool}
```

Gateway normalizes channel-specific features to a common internal representation; replies flow back through the adapter for channel-native formatting.

## Skill execution path

1. Turn arrives.
2. Four-layer memory fetched (indexed by user + recent session).
3. Agent loop considers: does any skill description match this turn?
4. If yes: skill body loaded, tools allow-listed per skill manifest, executed.
5. If no: first-principles reasoning; on task completion, skill extractor considers it for new skill.
6. Response streams back through the gateway to the channel.

## Skill extractor path

1. Task end signal.
2. Extractor receives: session transcript summary + tool call sequence + outcome.
3. LLM pass: "is there a reusable procedure here?"
4. If yes: draft SKILL.md; evaluate against last 3 similar turns (from memory); commit if eval passes.
5. If compression triggers (co-occurring skills observed N times): draft composite; evaluate; commit.

## Deployment

- Single containerized process; SQLite-backed FTS5 memory store + on-disk skill library.
- Optional external credential store (Vault-as-service) for channel tokens.
- Channel adapters run in the same process (WhatsApp / Slack webhooks; iMessage bridge like BlueBubbles).
- Nebius Token Factory / Anthropic / OpenAI as model backend (configurable).

## SLOs

| Metric | Target |
|---|---|
| Turn latency on cache-hit skill path (p95) | < 1.2 s |
| Skill extractor runtime (async, per task) | < 30 s |
| Memory-read latency (p95) | < 50 ms |
| Gateway → channel round-trip (not including LLM) | < 300 ms |
| Self-eval pass rate (skill correctness) | ≥ 95 % |

## Failure handling

| Failure | Response |
|---|---|
| Channel webhook down | Adapter retries; user-facing graceful degradation |
| Skill execution fails | Fallback to first-principles; skill's success_rate decreases; if < 0.5 after N uses, skill is flagged for review |
| LLM provider outage | Failover to secondary; if unavailable, graceful "I'm having trouble reaching my model; I'll be back shortly." |
| Memory store corruption | Read-only mode until rebuilt from backups; no writes |
| Extractor produces garbage skill | Self-eval filters; bad skills don't commit |

## Security

- Channel tokens stored encrypted per-user.
- Opt-in memory; purge semantics ("forget that").
- PII scrubber on any egress (e.g., when sending memory to an LLM).
- SOUL.md edits require confirmation step.
- NLAH specs run inside a sandboxed IHR — no arbitrary code execution.

## Roadmap post-v1

- Federated skill gallery (opt-in) — users can share anonymized skill templates.
- Voice channel (bridge with a Harmony-Voice instance).
- Cross-household mode — for families with shared schedules.
- Learned compression thresholds per user.

## Anti-scope

- No team mode — see Syndicate.
- No workplace compliance mode — adds significant complexity.
- No voice-first UX — see Harmony-Voice.
- No cloud-only deployment — privacy bet is on self-hosted.
