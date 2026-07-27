# J4 — Tax year end

**Status:** Accepted

> Once a year, under deadline pressure, producing something that has to be right
> because somebody official will read it.

---

## Precondition

A year of reconciled history. Tax tagging has been used through the year, or has
not.

## The path

### 1. Choose the year

The tax surface defaults to the year most people are filing — the previous year
early in the calendar year, the current year later. The user can switch.

*Exercises: [D4](../features/d-money/d4-tax.md).*

### 2. If tagging happened through the year

The best case. Transactions were tagged as they were categorised, from whichever
surface the user happened to be on, and the year is already assembled.

Split transactions were tagged **per leg**, so a partly-deductible purchase
contributes only its deductible legs.

*Exercises: [D4](../features/d-money/d4-tax.md), [B7](../features/b-ledger/b7-splits.md).*

### 3. If it did not

Search the year for the things that should be tagged — by merchant, by
description, by note, filtered by date and category — and tag in batches. This
is the case the search surface exists for.

Already-reconciled rows are filtered out of a batch operation before it applies.

*Exercises: [B9](../features/b-ledger/b9-search.md), [D4](../features/d-money/d4-tax.md), [B8](../features/b-ledger/b8-reconciliation.md).*

### 4. Handle the boundary cases

A payment made in January that belongs to the previous filing year takes a
**year override**, bounded to a sensible window.

A purchase that was partly deductible gets split, and the deductible leg tagged.
An eighty-unit purchase split sixty-and-twenty exports sixty — never eighty,
never zero.

*Exercises: [D4](../features/d-money/d4-tax.md), [B7](../features/b-ledger/b7-splits.md).*

### 5. Review the year

Grouped by deduction category with totals in the settled reporting currency.
Foreign-currency purchases show what they actually cost.

*Exercises: [D4](../features/d-money/d4-tax.md), [B10](../features/b-ledger/b10-multi-currency.md).*

### 6. Export

**CSV** for a spreadsheet or an accountant, with a fixed column order that
includes the audit fields — transaction identifier, source format, import run,
fingerprint — so any row can be traced back to the statement it came from. Every
cell is escaped against formula injection.

**PDF** for a filing record: a summary and grouped tables.

*Exercises: [D4](../features/d-money/d4-tax.md).*

### 7. Archive

A backup taken after the export, so the state the export was produced from is
recoverable.

*Exercises: [F4](../features/f-platform/f4-backup-restore.md), [F7](../features/f-platform/f7-data-locations.md).*

---

## A note on the v2.0 upgrade

A user upgrading from v1.3 to v2.0 meets a **breaking change** in the same
period: category-linked savings pots are retired in favour of envelope
budgeting ([ADR-0017](../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)).

On upgrade, every category-linked pot is archived and its balance released to its
account's unallocated pool. **The user must re-assign that money into envelopes
by hand.** Goal-linked pots are untouched.

This needs release-note prominence, not a changelog line — a user who does not
notice will see money they thought was allocated sitting unallocated, and will
reasonably conclude something is broken.

*Exercises: [D1](../features/d-money/d1-envelope-budgeting.md), [D3](../features/d-money/d3-pots.md).*

## Features exercised

[D4](../features/d-money/d4-tax.md) ·
[B7](../features/b-ledger/b7-splits.md) ·
[B8](../features/b-ledger/b8-reconciliation.md) ·
[B9](../features/b-ledger/b9-search.md) ·
[B10](../features/b-ledger/b10-multi-currency.md) ·
[F4](../features/f-platform/f4-backup-restore.md) ·
[F7](../features/f-platform/f7-data-locations.md) ·
[D1](../features/d-money/d1-envelope-budgeting.md) ·
[D3](../features/d-money/d3-pots.md)

## How this journey fails

| Failure | Why it matters |
|---------|----------------|
| A partly-deductible split exports the whole amount | An incorrect tax return. |
| A partly-deductible split exports nothing | A deduction lost. |
| The export lacks audit fields | A row cannot be traced back when queried. |
| A cell beginning with a formula character | A spreadsheet executes it on open. |
| A year override outside a sensible bound is accepted | A figure lands in the wrong year. |
| A one-tap re-tag wipes an existing note | Work lost silently. |
| The pot retirement is not surfaced on upgrade | The user believes their savings allocation has been lost. |

## Related

- [J3 Monthly reconcile](j3-monthly-reconcile.md) — the routine this depends on
- [ADR-0017](../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)
- [70-operations/releasing.md](../../70-operations/releasing.md)
