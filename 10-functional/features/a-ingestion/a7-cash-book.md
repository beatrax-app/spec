# A7 — Cash book: manual entry

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

Cash spending is invisible to every statement. So is money handed to a friend,
a market stall, or a machine that does not issue a receipt. If those never enter
the ledger, the month's totals are wrong and every budget built on them is wrong
too.

The cash book is a hand-entry surface that lands manual entries in **the same
ledger, through the same recording pipeline**, so they categorise, participate
in recurring detection, and count toward the month exactly like an imported row.

## Behaviour

### One ledger, not a parallel one

A manual entry is recorded through the canonical write path against a synthetic
per-user cash account and a manual source marker. It is not a separate table, a
separate view, or an annotation — it is a transaction.

That is the whole point: a parallel store would need its own categorisation, its
own budget integration, its own reporting, and would drift.

### Manual rows are the user's to delete

Imported rows are immutable — they are a record of what a statement said.
Manual rows are user-authored and therefore user-deletable. This is the one
place the ledger's immutability is relaxed, and it is relaxed deliberately.

### Amount entry is forgiving

The amount field accepts both plain and grouped notation, resolving the decimal
separator by a last-separator-wins rule so both European and Anglophone
conventions work without a setting.

### Two identical entries are two entries

Two genuinely distinct entries of the same amount, on the same day, to the same
counterparty both record. The fingerprint would otherwise collapse them, and for
cash that is the wrong answer — two coffees are two coffees.

### The chosen category is validated

A category identifier supplied by the client is validated as belonging to the
requesting user before it is written.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Two identical same-day entries | Both record. |
| A category identifier the user does not own | Rejected. |
| An amount in grouped notation | Parsed by the last-separator-wins rule. |
| A manual row later reconciled | Locked against mutation like any reconciled row ([B8](../b-ledger/b8-reconciliation.md)). |
| No cash account yet | Created on first use. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A7-R1** | A manual entry MUST be recorded through the canonical transaction write path, not a parallel store. |
| **A7-R2** | Manual entries MUST land against a synthetic per-user cash account with a manual source marker. |
| **A7-R3** | A manual entry MUST participate in categorisation, recurring detection, and period totals identically to an imported row. |
| **A7-R4** | Manual entries MUST be deletable by their owner; imported rows MUST NOT be. |
| **A7-R5** | The amount field MUST accept both plain and grouped notation, resolving the decimal separator by a last-separator-wins rule. |
| **A7-R6** | Two genuinely distinct identical same-day entries MUST both record. |
| **A7-R7** | A client-supplied category identifier MUST be validated as owned by the requesting user before any write. |
| **A7-R8** | The synthetic cash account MUST be created on first use rather than requiring setup. |
| **A7-R9** | Cross-user reads and writes MUST return not-found. |

## Related

- [B1 Transactions and the ledger](../b-ledger/b1-transactions.md) — the write path
- [A3 Idempotency](a3-idempotency.md) — and why it is bypassed here
- [D1 Envelope budgeting](../d-money/d1-envelope-budgeting.md) — cash counts against envelopes
- [J2 Daily use](../../journeys/j2-daily-use.md)
