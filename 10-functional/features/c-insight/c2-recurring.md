# C2 — Recurring detection

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

Fixed monthly payments are the part of a household's finances that is both most
predictable and most forgotten. Detecting them is what makes the forecast, the
calendar, the drift alerts, and the payment reminders possible — every one of
those features reads from this one.

## Behaviour

### Always suggest, never auto-apply

Detection produces **suggestions**. A detected series sits in a triage queue
until the user approves it. Nothing is treated as a real recurring commitment on
the system's own say-so.

That posture is deliberate: a false positive that silently becomes a forecast
input distorts every downstream projection, and the user has no obvious place to
notice it.

### Clustering and cadence

Expense series cluster by normalised counterparty and currency, within an
amount-variance tolerance. Income series cluster by account identifier first,
falling back to counterparty name, with a minimum-amount floor so small
irregular credits do not read as salary.

Cadence inference is stateless. It computes the median interval between
occurrences, snaps to a named cadence — weekly, monthly, quarterly, yearly — or
declares the series irregular. Intervals far above the provisional median are
excluded from the refined median and counted as **missed occurrences** rather
than distorting the cadence. A series whose intervals vary widely is flagged
low-confidence.

The next expected date is derived from the inferred cadence.

The five outcomes — weekly, monthly, quarterly, yearly, irregular — are the
whole vocabulary. Nothing else is a cadence a series can hold, and a value
outside the set is a defect rather than a new case to handle, so the set is
named once and both the code and the column are held to it. The digest cadence
in [C8](c8-notifications.md) is a different vocabulary that happens to share
the word and the value `weekly`; the two are not interchangeable.

### Metrics refresh, cadence flips, and re-detection

A new occurrence on an approved series refreshes its metrics without creating a
new suggestion. A cadence that genuinely changes moves the series to a
cadence-changed state, which is audited rather than silent.

A series the user rejected is **not re-suggested**. Rejection is a decision, and
re-asking every import is how a triage queue becomes noise.

### The user's controls

Per series: approve, reject, un-reject, snooze, rename, adjust the variance
tolerance, and set a drift threshold override ([C3](c3-drift-alerts.md)).

The detection window is a per-user setting, so someone with a long thin history
can widen it.

### Detection runs where it can

Detection is dispatched after an import. It runs synchronously in the request
where the at-rest decryption key is available, because clustering compares
counterparty identifiers that are encrypted at rest.

On the scheduled daily run there is no key. In that context the income detector,
which needs to decrypt identifiers, is **skipped with a warning**; the expense
detector, which does not, still runs. Skipping loudly is correct; guessing is
not.

Detection is idempotent on the cluster key, so a redundant run creates nothing.

### The fixed-payments view

The dashboard's fixed-payments summary resolves in a bounded number of queries
regardless of how many series exist. That bound is enforced by test, because it
is the kind of thing that silently regresses into a query per row.

## States

```text
pending ──▶ approved ◀──▶ cadence_changed
   │  │
   │  ├──▶ rejected ──▶ pending   (un-reject)
   │  └──▶ snoozed ──▶ pending | approved | rejected
```

A single state machine is the only writer, and it records every transition in an
append-only audit trail. Transitions take a row lock with a busy timeout.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No recent transactions | Nothing detected; no rows, no events. |
| A cadence that flips between runs | Moves to cadence-changed, audited. |
| One new occurrence on an approved series | Metrics refresh; no new suggestion. |
| A rejected series re-detected | Suppressed permanently for that cluster; the user must un-reject. |
| A snooze that expires | There is no background revival for recurring suggestions; the user sees it when they next open the queue. |
| An outlier occurrence | Gated by the series's variance tolerance. |
| Two detectors producing the same cluster | The key is direction-aware, so they cannot collide. |
| An irregular-cadence series | Detected, but not eligible for drift comparison and excluded from the calendar. |
| The scheduled run with no decryption key | The identifier-dependent detector is skipped with a warning. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C2-R1** | Detection MUST NOT auto-approve a series. |
| **C2-R2** | A single state machine MUST be the sole writer of series state, enforced by architecture test. |
| **C2-R3** | Permitted transitions MUST be: pending to approved, rejected, or snoozed; snoozed to pending, approved, or rejected; approved to and from cadence-changed; rejected to pending. Any other transition MUST raise. |
| **C2-R4** | Every state transition MUST write an append-only audit row. |
| **C2-R5** | Detection MUST be idempotent on the cluster key. |
| **C2-R6** | A new occurrence on an approved series MUST refresh metrics and MUST NOT create a new suggestion. |
| **C2-R7** | A genuine cadence change MUST move the series to a cadence-changed state rather than silently updating. |
| **C2-R8** | A rejected series MUST NOT be re-suggested until the user un-rejects it. |
| **C2-R9** | Cadence inference MUST exclude intervals far above the provisional median from the refined median and MUST count them as missed occurrences. |
| **C2-R10** | A series whose intervals vary widely MUST be flagged low-confidence. |
| **C2-R11** | An irregular-cadence series MUST NOT be eligible for drift comparison. |
| **C2-R12** | Income clustering MUST apply a minimum-amount floor, configurable per user. |
| **C2-R13** | The detection window MUST be a per-user setting. |
| **C2-R14** | Detection MUST run in a context where the at-rest key is available when it needs to decrypt. |
| **C2-R15** | Where the key is unavailable, the identifier-dependent detector MUST be skipped with a warning, not silently produce an empty result. |
| **C2-R16** | The fixed-payments summary MUST resolve in a bounded number of queries regardless of series count, verified by test. |
| **C2-R17** | Approve, reject, un-reject, and snooze MUST each raise exactly one event. |
| **C2-R18** | External reads of series occurrences MUST go through the feature's own public query surface. |
| **C2-R19** | Cross-user reads and writes MUST return not-found. |
| **C2-R20** | The series cadence vocabulary MUST be closed to weekly, monthly, quarterly, yearly, and irregular; it MUST be expressed as one named type rather than as free strings, and the stored column MUST be constrained to that set. |

## Related

- [C3 Subscription drift alerts](c3-drift-alerts.md) — the main consumer
- [C5 Forecasting](c5-forecasting.md) · [C6 Calendar](c6-calendar.md) · [C8 Notifications](c8-notifications.md)
- [B4 Counterparties](../b-ledger/b4-counterparties.md) — the clustering input
- [E4 At-rest encryption](../e-sync/e4-at-rest-encryption.md)
