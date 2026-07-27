# J3 — Monthly reconcile

**Status:** Accepted

> Once a month, an hour, on a Sunday. The user checks that what beatrax holds
> matches what their bank says — and then trusts every number in the product for
> the next four weeks on the strength of it.

---

## Precondition

A set-up install. A month has closed and statements are available.

## The path

### 1. Import the month

Download each statement and import it. Where a source is already connected, it
arrived on its own.

The preview shows the verdict per row: new, duplicate, enriched, error. A period
that overlaps one already imported shows mostly duplicates, and **that is the
system working**.

*Exercises: [A1](../features/a-ingestion/a1-source-formats.md), [A2](../features/a-ingestion/a2-import-wizard.md), [A3](../features/a-ingestion/a3-idempotency.md), [A6](../features/a-ingestion/a6-open-banking.md).*

### 2. Let the passes run

After the commit: chain resolution, transfer pairing, recurring detection,
anomaly detection, drift evaluation, and re-projection.

*Exercises: [B5](../features/b-ledger/b5-chain-resolution.md), [B6](../features/b-ledger/b6-transfers.md), [C2](../features/c-insight/c2-recurring.md), [C3](../features/c-insight/c3-drift-alerts.md), [C4](../features/c-insight/c4-anomaly.md), [C5](../features/c-insight/c5-forecasting.md).*

### 3. Clear the queues

Categorise, triage counterparties, confirm or reject chain candidates, approve
or reject recurring suggestions. Split anything that was several things at once
— the supermarket shop that was partly household goods.

*Exercises: [B2](../features/b-ledger/b2-categorisation.md), [B4](../features/b-ledger/b4-counterparties.md), [B5](../features/b-ledger/b5-chain-resolution.md), [B7](../features/b-ledger/b7-splits.md), [C2](../features/c-insight/c2-recurring.md).*

### 4. Reconcile each account

The core of the hour.

Open the reconcile surface, pick an account, enter the closing balance the
statement shows and the date it applies to. beatrax shows its own cleared
balance and **the difference**.

- **Zero.** Complete the reconciliation. Every cleared row up to that date
  becomes reconciled and locks against further change.
- **Not zero.** The difference is shown plainly with the cleared set visible.
  Nothing is auto-corrected — that is the user's investigation, and beatrax's job
  is to make it findable rather than to guess.

Common causes: a transaction not yet cleared, one cleared that should not be, a
missing period, a duplicate that should have been caught but was entered by hand.

*Exercises: [B8](../features/b-ledger/b8-reconciliation.md), [B1](../features/b-ledger/b1-transactions.md), [B9](../features/b-ledger/b9-search.md).*

### 5. Review the month's alerts

Unusual charges: acknowledge, or mark as expected — which creates a narrow,
server-computed suppression band, visible and removable in settings, with an undo
that re-opens the alert.

Drift: acknowledge, snooze, model a cancellation, or mark as already cancelled.

*Exercises: [C4](../features/c-insight/c4-anomaly.md), [C3](../features/c-insight/c3-drift-alerts.md).*

### 6. Assign next month

Ready to assign shows income minus everything assigned. Envelopes roll their
balances forward; overspending resolves per envelope by the chosen rule. Money
moves between envelopes as needed — including into negative, which is a
legitimate operation and is not blocked.

Copy-last-month fills a fresh grid where the previous month has one.

*Exercises: [D1](../features/d-money/d1-envelope-budgeting.md).*

### 7. Check the goals and the runway

Goals show contributed against target and a projected finish — or **no
projection**, honestly, where there is too little history to make one.

The forecast shows the next ninety days with the dips marked.

*Exercises: [D2](../features/d-money/d2-goals.md), [D3](../features/d-money/d3-pots.md), [C5](../features/c-insight/c5-forecasting.md).*

### 8. Back up

A backup, encrypted if the user chose a passphrase, alongside the retention
policy that keeps a bounded set of recent daily and weekly snapshots.

*Exercises: [F4](../features/f-platform/f4-backup-restore.md).*

## Features exercised

[A2](../features/a-ingestion/a2-import-wizard.md) ·
[A3](../features/a-ingestion/a3-idempotency.md) ·
[B5](../features/b-ledger/b5-chain-resolution.md) ·
[B7](../features/b-ledger/b7-splits.md) ·
[B8](../features/b-ledger/b8-reconciliation.md) ·
[C3](../features/c-insight/c3-drift-alerts.md) ·
[C4](../features/c-insight/c4-anomaly.md) ·
[C5](../features/c-insight/c5-forecasting.md) ·
[D1](../features/d-money/d1-envelope-budgeting.md) ·
[D2](../features/d-money/d2-goals.md) ·
[F4](../features/f-platform/f4-backup-restore.md)

## How this journey fails

| Failure | Why it matters |
|---------|----------------|
| Re-importing an overlapping period creates duplicates | Every subsequent figure is wrong and the user cannot tell which. |
| The reconcile difference is auto-corrected | The tool hides the discrepancy it exists to reveal. |
| A reconciled row can still be edited | The assertion means nothing. |
| Split legs are double-counted with the parent | Every category total is inflated. |
| A budget move is blocked for being "invalid" | The tool overrules the person about their own money. |
| A goal projection appears with two days of data | The user plans against a fiction. |
| Reconciliation status is lost on re-import | The whole hour has to be redone. |

## Related

- [J2 Daily use](j2-daily-use.md) · [J4 Tax year end](j4-tax-year-end.md)
