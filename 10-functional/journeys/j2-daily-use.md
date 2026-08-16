# J2 — Daily use

**Status:** Accepted

> Four seconds in the morning, and occasionally five minutes on a Sunday. If the
> daily loop is not this cheap, the product is not used, and an unused finance
> tool is worse than none because its numbers go stale.

---

## Precondition

A set-up install with at least one month of history.

## The path

### The morning glance

Open the application. If the app-lock is on, a code or a biometric releases the
key.

The dashboard shows in, out, and net for the period, the top spending
categories, and — **above them** — anything needing attention: unusual charges,
subscription drift, forecast shortfalls, and queue counts.

That ordering is the whole design. A dashboard that leads with a pleasant net
figure and buries a doubled subscription is lying by omission.

*Exercises: [F3](../features/f-platform/f3-auth-and-app-lock.md), [C1](../features/c-insight/c1-dashboard.md).*

### Something arrived overnight

Email scanning, if enabled, fetched receipts on its schedule and enriched
matching transactions with what they were actually for. An open-banking
connection, if enabled, pulled booked transactions — deduplicating against
anything already imported by file.

Both are optional and both are off until the user turns them on
([G1](../features/g-ux/g1-privacy.md)).

*Exercises: [A4](../features/a-ingestion/a4-email-scanning.md), [A5](../features/a-ingestion/a5-receipt-matching.md), [A6](../features/a-ingestion/a6-open-banking.md), [A3](../features/a-ingestion/a3-idempotency.md).*

### A notification, not a shout

A payment reminder, an over-budget nudge, a savings prompt, or the periodic
digest may be waiting in the inbox. Because the inbox is persistent and
deduplicated, one missed while asleep is still there — and one already read on
the phone is not still shouting on the desktop.

*Exercises: [C8](../features/c-insight/c8-notifications.md), [E1](../features/e-sync/e1-change-capture.md).*

### Cash spent yesterday

A market stall, a coffee, a taxi. Entered in the cash book in a few seconds
against a synthetic cash account, through the same recording path as everything
else — so it categorises, counts toward the month, and participates in
envelopes exactly like an imported row.

*Exercises: [A7](../features/a-ingestion/a7-cash-book.md), [D1](../features/d-money/d1-envelope-budgeting.md).*

### Clearing the queues

The keyboard-first part of the routine.

**Uncategorised transactions** — a number key assigns a category, arrows move,
a batch commits. Each assignment teaches the merchant memory, so next month's
equivalent categorises itself.

**Unknown counterparties** — each shows its identifier, its recent activity, and
a confidence-rated suggestion. Accepting labels every transaction sharing that
identifier at once.

**Chain candidates** — the resolver found a plausible match it was not sure
enough about. Confirming teaches the alias bridge; three confirmations of the
same shape promote every remaining match of that shape automatically.

**Recurring suggestions** — approve, reject, or snooze. Rejected series are not
re-suggested.

*Exercises: [B2](../features/b-ledger/b2-categorisation.md), [B4](../features/b-ledger/b4-counterparties.md), [B5](../features/b-ledger/b5-chain-resolution.md), [C2](../features/c-insight/c2-recurring.md), [G6](../features/g-ux/g6-keyboard.md).*

### Following a thread

Something on the statement is unrecognisable. Search finds it by merchant,
description, or note; the chain drawer shows what funded it; the counterparty
profile shows the whole relationship.

*Exercises: [B9](../features/b-ledger/b9-search.md), [B5](../features/b-ledger/b5-chain-resolution.md), [B4](../features/b-ledger/b4-counterparties.md).*

### A subscription went up

A drift alert names the previous and current amounts and the annualised impact.
The user can model the cancellation — which creates a forecast scenario and
shows the effect **without changing anything** — and then follow a link to the
provider's own cancellation page.

Beatrax never cancels anything ([P7](../../00-overview/vision.md#p7--it-informs-it-never-transacts)).

*Exercises: [C3](../features/c-insight/c3-drift-alerts.md), [C5](../features/c-insight/c5-forecasting.md), [C9](../features/c-insight/c9-community-corpus.md).*

### Checking the month ahead

The calendar shows what is due and the running projected balance. The forecast
shows the same data as a curve with confidence bands and the dips marked.

*Exercises: [C6](../features/c-insight/c6-calendar.md), [C5](../features/c-insight/c5-forecasting.md).*

### On the phone, later

The same surfaces at phone width, from the installed application, holding their
own encrypted copy and syncing peer-to-peer over the local network — or through
a relay that cannot read anything if the desktop is asleep.

*Exercises: [G4](../features/g-ux/g4-pwa.md), [E5](../features/e-sync/e5-mobile-peer.md), [E3](../features/e-sync/e3-transport.md), [E6](../features/e-sync/e6-sync-status.md).*

## Features exercised

Most of the catalogue. The distinctive ones:
[C1](../features/c-insight/c1-dashboard.md) ·
[B2](../features/b-ledger/b2-categorisation.md) ·
[B4](../features/b-ledger/b4-counterparties.md) ·
[B5](../features/b-ledger/b5-chain-resolution.md) ·
[C3](../features/c-insight/c3-drift-alerts.md) ·
[C8](../features/c-insight/c8-notifications.md) ·
[G6](../features/g-ux/g6-keyboard.md) ·
[E5](../features/e-sync/e5-mobile-peer.md)

## How this journey fails

| Failure | Why it matters |
|---------|----------------|
| The dashboard leads with the pleasant number | The user misses the thing they needed to see. |
| Triage requires a pointer per row | Forty rows becomes twenty minutes; the queue stops being cleared. |
| Categorisation does not learn | The same corrections every month; the user gives up. |
| A notification repeats after being read | The inbox becomes noise and gets ignored wholesale. |
| The phone shows different numbers from the desktop | Trust in every number collapses at once. |
| A drift alert offers no next step | The user knows something is wrong and can do nothing about it. |
| Cash entry takes more than a few seconds | Cash stops being entered; every total is quietly wrong. |

## Related

- [J1 First run](j1-first-run.md) · [J3 Monthly reconcile](j3-monthly-reconcile.md)
- [00-overview/vision.md](../../00-overview/vision.md)
