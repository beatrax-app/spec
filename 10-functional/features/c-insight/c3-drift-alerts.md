# C3 — Subscription drift alerts

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

Subscriptions creep. A streaming service raises its price by a small amount, a
utility adjusts a standing charge, an insurance premium climbs at renewal —
each individually forgettable, collectively the reason a household's fixed costs
drift upward without anyone deciding they should.

Drift alerts notice the change, put a number on it, and make cancelling
something the user can model before they do it.

## Behaviour

### What triggers an alert

For every approved recurring series ([C2](c2-recurring.md)), the latest
occurrence's amount is compared with the previous one **in the series's own
currency**. If the change exceeds the effective threshold, an alert is raised
carrying the previous amount, the current amount, the signed difference, and the
annualised impact.

Comparing in the series's own currency is what stops a foreign-currency
subscription from raising an alert every month because the exchange rate moved.
A genuine price rise in the original currency **is** flagged, currency and all.

### The effective threshold is resolved by precedence

The per-series override wins where one is set; otherwise the user's global
setting; otherwise a documented default. Precedence rather than a maximum,
because taking the greatest would mean an override could only ever make a series
*less* sensitive, and an override that cannot tighten is half a control.

What stops a careless setting silencing drift is not a floor but the option set:
both the global and the override choose from a closed list with a bounded
maximum and no "off" value. A threshold is a minimum movement required to alert,
so a low one is merely noisy — the direction that can actually silence drift is a
high one, and the list is what bounds it.

The per-series override is edited inline wherever the series appears.

### The alert, and what the user can do with it

Each alert offers: acknowledge, snooze, model a cancellation, or mark as already
cancelled. Modelling a cancellation creates a forecast scenario pre-seeded with
that series removed and takes the user to the forecast — **without changing the
alert**, because modelling is not deciding.

Marking as cancelled records that outcome and is deliberately a distinct
transition from acknowledging, so the two do not blur in the history.

Acknowledged alerts flow into a history view. The open view includes snoozed
alerts whose snooze has expired, so an expired snooze is visible immediately
even before the sweep that durably revives it runs.

### The watch overview

A separate overview lists every approved expense series with at least two
observed amounts, showing baseline against latest, cumulative drift, and a
sparkline, sorted by the largest increase. It reads a much deeper occurrence
history than the per-series detail view, because cumulative drift over years is
the point.

### Savings suggestions

A related surface suggests where money could be saved, in priority order:
a cheaper plan where the corpus knows of one, cancellation where an open drift
alert and a cancellation resource both exist, and review where an ongoing charge
is above a floor and a cancellation resource exists.

One suggestion per subscription, each dismissible by a stable key so a dismissal
survives recomputation. Suggestions are cached per user and invalidated on
dismissal.

**Beatrax never acts.** It links to the provider's own page and stops
([P7](../../../00-overview/vision.md#p7--it-informs-it-never-transacts)).

### Boundaries

This feature never decides what "recurring" means and never writes recurring
state — it reads through the recurring feature's public surface, and threshold
edits delegate back to it. That separation is enforced by architecture test.

## States

```text
open ──▶ acknowledged        (terminal)
  │  ├──▶ dismissed_cancelled (terminal)
  │  └──▶ snoozed
  │           └──▶ open | acknowledged | dismissed_cancelled
```

A single state machine is the only writer, enforced at three layers: static
analysis, a runtime transition map, and database triggers. Every transition
writes an append-only audit row.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A series with one occurrence | No comparison possible; nothing raised. |
| Two identical amounts | Zero difference; nothing raised. |
| A previous amount of zero | The ratio is skipped; nothing raised. |
| A cadence change with stable amounts | No drift. |
| An exchange-rate-only swing | Not flagged. |
| A genuine rise in a foreign currency | Flagged, in that currency. |
| A pending or rejected series | Ignored — only approved and cadence-changed series are compared. |
| An irregular-cadence series | Ignored; the comparison would not be meaningful. |
| Several drifts in one refresh | Each gets its own job with its own lock key. |
| A snooze that expires | Visible immediately via the query-time condition; durably revived by an hourly sweep. |
| A user acting on a row mid-sweep | The sweep catches the invalid transition and skips that row. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C3-R1** | Drift MUST be evaluated only for approved and cadence-changed series. |
| **C3-R2** | Comparison MUST be performed in the series's own currency. |
| **C3-R3** | An exchange-rate-only movement MUST NOT raise an alert; a genuine rise in the original currency MUST. |
| **C3-R4** | The effective threshold MUST be resolved by precedence rather than by comparison: the per-series override where one is set, otherwise the user's global setting, otherwise a documented default. An override MUST be able to make one series more sensitive as well as less. |
| **C3-R5** | The values the global setting and the per-series override may take MUST be a closed, documented set with a bounded maximum and no "off" value, so drift cannot be switched off by accident. The threshold that judged a movement, and which of the three sources supplied it, MUST be recorded on the alert. |
| **C3-R6** | An alert MUST carry the previous amount, the current amount, the signed difference, and the annualised impact. |
| **C3-R7** | Evaluation MUST be idempotent for a given series and latest occurrence. |
| **C3-R8** | A previous amount of zero MUST NOT produce a division; no alert MUST be raised. |
| **C3-R9** | A single state machine MUST be the sole writer of alert state, enforced by architecture test, a runtime transition map, and database triggers. |
| **C3-R10** | Permitted transitions MUST be: open to acknowledged, snoozed, or dismissed-as-cancelled; snoozed to open, acknowledged, dismissed-as-cancelled, or snoozed again. Acknowledged and dismissed-as-cancelled MUST be terminal. Snoozed to snoozed is a real move rather than a no-op: C3-R14 returns a lapsed snooze to the open view, from which re-snoozing is reachable. |
| **C3-R11** | Every transition MUST write an append-only audit row. |
| **C3-R12** | Modelling a cancellation MUST create a forecast scenario and MUST NOT modify the alert. |
| **C3-R13** | Marking as already cancelled MUST be a distinct transition from acknowledging. |
| **C3-R14** | The open view MUST include snoozed alerts whose snooze has expired. |
| **C3-R15** | An hourly sweep MUST durably revive expired snoozes and MUST skip rows a user changed concurrently. |
| **C3-R16** | This feature MUST NOT write recurring-series state; threshold edits MUST delegate to the recurring feature's public action. |
| **C3-R17** | The watch overview MUST read a deeper occurrence history than the per-series detail view. |
| **C3-R18** | Savings suggestions MUST be one per subscription, dismissible by a stable key, and cached with invalidation on dismissal. |
| **C3-R19** | Beatrax MUST NOT cancel, switch, or otherwise act on a subscription; it MUST only link to the provider's own page. |
| **C3-R20** | Every action MUST be idempotent and MUST return not-found for a cross-user target. |
| **C3-R21** | The detection job MUST be unique per user and series. |
| **C3-R22** | Snooze idempotency MUST compare absolute instants, not formatted strings. |

## Related

- [C2 Recurring detection](c2-recurring.md) — the input
- [C4 Unusual-charge alerts](c4-anomaly.md) — the sibling alert stream
- [C5 Forecasting](c5-forecasting.md) — the cancellation model
- [C9 Community merchant corpus](c9-community-corpus.md) — where cancellation resources come from
- [C8 Notifications](c8-notifications.md)
