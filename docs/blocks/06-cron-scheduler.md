# Mentat-Learn Block 06 — Cron Scheduler

## Responsibility

First-class scheduled automations. User says "every Monday 9am draft my weekly review" or "on the 1st of each month summarize last month"; scheduler fires the matching skill at the right time and delivers through the configured channel.

Reference: [docs/55 Hermes Agent](../../../docs/55-hermes-agent-self-improving.md) cron-style scheduler — Mentat formalizes it and ties it to the skill library.

## Schedule schema

```yaml
id: UUID
user_id: UUID
name: "Weekly review Friday 5pm"
cron_expr: "0 17 * * FRI"
timezone: "America/Los_Angeles"
skill_id: UUID                # which skill to invoke
inputs: {}                    # static inputs the skill takes
channel: "slack://@me"        # where to deliver
enabled: true
last_run_at: datetime | null
last_result: "success" | "failure" | "skipped" | null
```

## Trigger flow

1. Scheduler ticks every minute.
2. For each due schedule: enqueue a `ScheduledTurn`.
3. Agent loop consumes queue entries as if they were user turns, but:
   - Source = `scheduled`.
   - Targeting = `channel` field, not the originating channel.
4. Skill fires; output delivered through the channel adapter; result recorded.

## User interactions

Natural-language creation:

> User: "Every Monday at 9 draft my weekly review and send it here"
> Mentat: "OK — I'll run the `weekly-review` skill every Monday at 9 AM Pacific, and post the draft here in Slack. You can cancel anytime by saying 'cancel weekly review'."

Under the hood: Mentat asks the `cron-create` skill; it emits a `Schedule` record; user confirms.

## Safety

- Destructive actions (sending emails, making API calls that modify external state) cannot be scheduled without explicit per-schedule approval at creation time.
- "Silent failure" alerting: 3 consecutive failures → notify user through primary channel.
- Schedules can be paused globally (e.g. user is on vacation).

## Time zones

- Schedules carry timezone; cron evaluated in local TZ.
- User preference defaults to the TZ they set at onboarding.
- Travel mode (user toggled): schedules respect travel-TZ for the travel window.

## Failure modes

| Mode | Defense |
|---|---|
| Schedule fires while user is on DND | DND-aware delivery; queue for post-DND window |
| Cron-expression typo from user | Parser validates at creation; shows human-readable interpretation for confirmation |
| Skill retired but schedule still points at it | On schedule execution, if skill missing → skip + notify user |
| User opt-out mid-run | Schedule respects instant-pause; can be purged anytime |
| Runaway scheduled automation (loop-of-scheduled-turns) | Per-user-per-hour scheduled-turn cap; excess are dropped + notified |

## Metrics

- `cron.schedules_active`
- `cron.fires_per_day`
- `cron.skip_rate` (DND, paused, etc.)
- `cron.failure_rate`
- `cron.destructive_approvals`
