# C8 — Notifications and reminders

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

Before this feature, beatrax's notifications were fire-and-forget: if the user
was not looking when one fired, it was gone. For a payment reminder that is
worse than useless.

This feature replaces that with proactive triggers plus a **persistent,
deduplicated inbox** whose read state syncs across devices — so a notification
seen on the phone is not still shouting on the desktop.

## Behaviour

### Eight kinds, one inbox

| Kind | Fires when |
|------|-----------|
| Payment reminder | A recurring payment is due within the lead window |
| Position digest | On the user's chosen cadence |
| Over-budget nudge | An envelope crosses its notify threshold |
| Savings opportunity | A savings insight is available |
| Drift alert | A subscription's price moved |
| Forecast shortfall | A projected balance crosses a buffer |
| Coalesced import | An import completed |
| Statement ready | A card statement notification arrived |

All eight land in one inbox with a navigation badge, read and dismissed
individually.

### Deduplication is structural

Every notification's identity is derived deterministically from the user, the
trigger kind, the subject, and an **occurrence key** — so the same logical event
computed twice, or on two devices, produces the same identity and the second
write is a no-op.

The occurrence key is chosen per trigger to mean "this instance of this event":
the due date for a reminder, the budget period for a nudge, the insight's own
key for a prompt, the digest's date or week, the alert's own identity for a
drift alert, the window start for a shortfall, the completion time and count for
an import, the arrival day for a statement.

Getting this key right is what stops the inbox filling with the same reminder
every hour.

### A large import is one notification

An import of hundreds of rows produces **one** coalesced notification, not one
per row.

### Persistence and delivery are separate decisions

The row is **always** written. Delivery — whether an operating-system
notification actually appears — is decided separately, in one place, in a fixed
order: a seeding flag, then the per-trigger toggle, then quiet hours.

Nothing about delivery ever prevents the row being written. That separation is
what makes "I was asleep when it fired" recoverable.

Delivery is additionally suppressed when the application window has focus — the
in-app surface is already showing it.

### Preferences are per device

Toggles and quiet hours are per user **and per device**, because a phone and a
desktop want different answers. An unpaired device gets defaults on read and a
no-op on write rather than an error.

### Read state syncs; the notification itself syncs

Both the notification and its read state are merged fields
([E1](../e-sync/e1-change-capture.md)), so the inbox agrees across devices.

### Reminders resolve themselves

A payment reminder for a bill that then arrives is **resolved**, not left
sitting. That is the one lifecycle transition the feature has.

### Links are validated late

A notification's deep link is re-validated at render time, so a notification
whose target no longer exists degrades to a plain entry instead of a broken
link.

### Failures never escape

Every trigger listener wraps its work so a failure in one trigger cannot break
the event that caused it. A notification is a courtesy; it must never take down
an import.

### Retention

Notifications are pruned after a long window. The pruning predicate uses only
plaintext columns, so it runs on a schedule without needing the at-rest key.

## States

`open` → `resolved`, and nothing else. Read and dismissed are separate
timestamps, not states. A single state machine is the only writer, enforced both
in the application and by database trigger.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| An unrecognised trigger kind | Logged and refused, not silently accepted. |
| An unpaired device reading preferences | Defaults returned; writes are no-ops. |
| The same event computed on two devices | Identical identity; the second write is a no-op. |
| A trigger listener throwing | Caught; the causing event completes. |
| A deep link whose target was deleted | Degrades to a plain entry. |
| An import of five hundred rows | One notification. |
| Quiet hours | The row is written; the delivery is suppressed. |
| Retention pruning with no encryption key | Runs anyway — the predicate is plaintext-only. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C8-R1** | All eight trigger kinds MUST land in one inbox with a navigation badge. |
| **C8-R2** | Notification identity MUST be derived deterministically from user, trigger kind, subject, and occurrence key. |
| **C8-R3** | Each trigger MUST define an occurrence key that identifies one instance of its event. |
| **C8-R4** | The same logical event produced twice MUST result in exactly one notification. |
| **C8-R5** | A bulk import MUST produce exactly one coalesced notification. |
| **C8-R6** | The notification row MUST always be written; delivery suppression MUST NOT prevent persistence. |
| **C8-R7** | Delivery MUST be decided in one place, in the order: seeding flag, per-trigger toggle, quiet hours. |
| **C8-R8** | Delivery MUST be suppressed while the application window has focus. |
| **C8-R9** | Preferences MUST be scoped per user and per device. |
| **C8-R10** | An unpaired device MUST receive defaults on read and MUST no-op on write. |
| **C8-R11** | Notifications and their read state MUST be captured for sync and merged across devices. |
| **C8-R12** | A payment reminder whose bill subsequently arrives MUST be resolved. |
| **C8-R13** | The only permitted state transition MUST be open to resolved, enforced in the application and at the database layer. |
| **C8-R14** | Read and dismissed MUST be recorded as timestamps, not as states. |
| **C8-R15** | Deep links MUST be re-validated at render time and MUST degrade gracefully. |
| **C8-R16** | Every trigger listener MUST wrap its work so a failure cannot break the causing event. |
| **C8-R17** | An unrecognised trigger kind MUST be logged and refused. |
| **C8-R18** | Notifications MUST be pruned after a documented retention window. |
| **C8-R19** | The pruning predicate MUST use only plaintext columns so it can run without the at-rest key. |
| **C8-R20** | Notification content MUST be treated as sensitive and encrypted at rest alongside other identifying text. |
| **C8-R21** | Cross-user reads and writes MUST return not-found. |

## Related

- [C1 Dashboard](c1-dashboard.md) — the digest source
- [C2 Recurring](c2-recurring.md) · [C3 Drift](c3-drift-alerts.md) · [C5 Forecasting](c5-forecasting.md) · [D1 Budgeting](../d-money/d1-envelope-budgeting.md) — the trigger sources
- [E1 Change capture](../e-sync/e1-change-capture.md) — read-state sync
- [E4 At-rest encryption](../e-sync/e4-at-rest-encryption.md)
- [F1 Desktop shell](../f-platform/f1-desktop-shell.md) — the delivery adapter
