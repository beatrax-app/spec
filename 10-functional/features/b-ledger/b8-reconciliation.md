# B8 — Reconciliation and cleared status

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

Importing a statement tells you what the bank says. Reconciling tells you that
you have *checked* it — that the transactions beatrax holds add up to the
balance the bank printed, and that nothing is missing or invented.

Before this feature, beatrax trusted the import and had no way to express
"I have verified this period". Now it does, and the verification survives
re-import and device sync.

## Behaviour

### Three statuses

| Status | Meaning |
|--------|---------|
| `uncleared` | Recorded, not yet confirmed against a statement. |
| `cleared` | Confirmed as present on the statement. |
| `reconciled` | Part of a completed reconciliation to a statement balance. |

Imported rows default according to their source: a source that is itself a bank
statement is stronger evidence than a hand-entered row, and the default reflects
that. The user can toggle a row between uncleared and cleared at any time from
the list or the detail view.

### Reconciling to a statement balance

The user picks an account and enters the balance their statement shows as of a
date. beatrax shows the cleared balance it computes up to that date and the
difference between the two.

- **Zero difference** — the user completes the reconciliation, and every cleared
  row up to that date becomes reconciled in one operation.
- **Non-zero difference** — the difference is shown plainly, with the cleared
  set visible so the user can find what is missing or wrongly cleared. Nothing
  is auto-corrected.

The bulk transition re-derives the affected set inside the operation, so a row
cleared or uncleared while the screen was open cannot produce a wrong result.
Un-reconciling returns rows to cleared.

### Reconciled rows are locked

Every mutating action refuses a reconciled row: re-categorising, editing notes,
splitting, tax tagging, deleting, re-applying rules. Reconciliation is an
assertion that the row is settled, and the lock is what makes the assertion
mean something.

Unlocking means explicitly un-reconciling.

### It survives re-import

Reconciliation status is beatrax's own state, not something derived from the
source. Re-importing the same statement classifies every row as a duplicate
([A3](../a-ingestion/a3-idempotency.md)) and leaves status untouched.

### It survives sync

Status is a merged field like any other ([E1](../e-sync/e1-change-capture.md)):
clearing a row on the phone shows up on the desktop, resolved last-writer-wins
per field.

### The cleared balance

The account balance query exposes both the full current balance and the cleared
balance — the sum of cleared and reconciled rows only — and the cleared balance
as of a date, which is what the reconciliation screen compares against.

## States

```text
uncleared ──▶ cleared ──▶ reconciled
                 ▲            │
                 └────────────┘
                  un-reconcile
```

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A row cleared while the reconcile screen is open | The bulk operation re-derives the set; the result is correct either way. |
| A difference the user cannot explain | Shown plainly; nothing is auto-corrected and the reconciliation is not completed. |
| Re-importing a reconciled period | Status untouched. |
| A reconciled row targeted by a rule re-apply | Skipped. |
| Clearing a row on one device and un-clearing on another | Resolved by last-writer-wins on the status field. |
| An account with mixed currencies | The cleared balance sums minor units directly and assumes a single currency per account; a mixed-currency account is outside what the figure can express. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B8-R1** | Every transaction MUST carry exactly one of uncleared, cleared, or reconciled. |
| **B8-R2** | The import default MUST depend on the source's strength as evidence. |
| **B8-R3** | The user MUST be able to toggle a row between uncleared and cleared from both the list and the detail view. |
| **B8-R4** | The reconcile flow MUST accept a statement balance and a date and MUST show the computed cleared balance and the difference. |
| **B8-R5** | Completing a reconciliation MUST transition every cleared row up to the date to reconciled in one operation. |
| **B8-R6** | The bulk transition MUST re-derive the affected set inside the operation. |
| **B8-R7** | A non-zero difference MUST be surfaced plainly and MUST NOT be auto-corrected. |
| **B8-R8** | Un-reconciling MUST return rows to cleared. |
| **B8-R9** | Every mutating action MUST refuse a reconciled transaction. |
| **B8-R10** | Reconciliation status MUST survive re-import of the same source unchanged. |
| **B8-R11** | Reconciliation status MUST be captured for sync and merged per field. |
| **B8-R12** | The balance query MUST expose the current balance, the cleared balance, and the cleared balance as of a date. |
| **B8-R13** | Status transitions MUST go through a single sanctioned writer. |
| **B8-R14** | Cross-user reads and writes MUST return not-found. |
| **B8-R15** | The single-currency assumption in the cleared balance MUST be documented rather than silently assumed. |

## Related

- [B1 Transactions and the ledger](b1-transactions.md) · [B7 Splits](b7-splits.md)
- [A3 Idempotency](../a-ingestion/a3-idempotency.md) · [A9 Starting balances](../a-ingestion/a9-starting-balances.md)
- [E1 Change capture and CRDT merge](../e-sync/e1-change-capture.md)
- [J3 Monthly reconcile](../../journeys/j3-monthly-reconcile.md)
