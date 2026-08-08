# J7 — Migrating from another tool

**Status:** Accepted

> Someone with years of categorised history and a refined category tree in
> another budgeting product. Asking them to start again is asking them not to
> switch.

---

## Precondition

An export from YNAB (either generation) or Actual Budget. A Beatrax install,
either fresh or already in use.

## The path

### 1. Export from the other tool

The user produces an export in that product's own format. Beatrax reads it as it
is — no intermediate conversion, no spreadsheet step.

An Actual export is opened **read-only**, so the source is never modified.

*Exercises: [A8](../features/a-ingestion/a8-migration-importers.md).*

### 2. Parse and stage

The export is parsed into a common intermediate shape and written to staging
tables in bounded chunks. **Nothing touches the live ledger.**

An uploaded archive is opened defensively — guarded against entry-count and
uncompressed-size bombs, absolute paths, traversal, and symlink entries.

*Exercises: [A8](../features/a-ingestion/a8-migration-importers.md).*

### 3. Preview

What will be created, grouped by kind: categories, budget assignments, accounts,
transactions, splits, payees, goals — plus a **summary of anything the importer
could not map**.

That summary matters more than the counts. A user needs to know what will *not*
come across before they commit, not afterwards.

*Exercises: [A8](../features/a-ingestion/a8-migration-importers.md).*

### 4. Promote

In dependency order: categories, then the budget grid, then accounts, then
transactions, then splits, then a transfer-pairing sweep, then goals.

Every step writes through the **same public writers** the rest of the product
uses — there is no privileged path into the ledger, so a migrated transaction is
exactly as valid as an imported one.

Promotion runs outside a wrapping transaction; only the status change and the
counts are wrapped, because a whole-history promotion as one transaction is the
unbounded transaction the import design exists to avoid.

*Exercises: [A8](../features/a-ingestion/a8-migration-importers.md), [B1](../features/b-ledger/b1-transactions.md), [B7](../features/b-ledger/b7-splits.md), [B6](../features/b-ledger/b6-transfers.md), [D1](../features/d-money/d1-envelope-budgeting.md), [D2](../features/d-money/d2-goals.md).*

### 5. What lands where

| From the other tool | In Beatrax |
|---------------------|------------|
| Category tree | Categories |
| Budget assignments, month by month | Envelope assignments ([D1](../features/d-money/d1-envelope-budgeting.md)) |
| Accounts | Accounts, with deterministic synthetic identifiers |
| Transactions | Transactions, at midnight — no source carries a time |
| Splits | Split legs, reconstructed conservatively |
| Cleared status | Reconciliation status ([B8](../features/b-ledger/b8-reconciliation.md)) |
| Payees | Counterparties ([B4](../features/b-ledger/b4-counterparties.md)) |
| Transfers | Paired legs ([B6](../features/b-ledger/b6-transfers.md)) |
| Goals, where the source has them | Goals ([D2](../features/d-money/d2-goals.md)) |

Currencies are preserved as the source recorded them.

A budget assignment's amount is the **assigned amount**, never a carried-forward
balance — confusing the two silently doubles a year of budget history.

### 6. Re-running, and updating

A byte-identical re-run is a **true no-op**: a source map records which source
entity became which Beatrax record, every step consults it first, and a hit
reuses the existing record and writes nothing.

A **newer** export of the same budget performs a three-way merge against the
baseline recorded at the previous import:

| Comparison | Outcome |
|------------|---------|
| Nothing changed in the source | Skip |
| The source changed, Beatrax did not | Apply |
| Both changed | Conflict — the user decides |

Money is compared as money, never as a formatted string.

**Reconciliation is implemented for budget assignments, category names, account
names, transaction descriptions, and non-split transaction amounts. Transaction
date, category, payee, and goal reconciliation are not implemented** — those
fields import on a first run and are not reconciled on a re-run. The documentation
says so rather than letting a user assume otherwise.

*Exercises: [A8](../features/a-ingestion/a8-migration-importers.md).*

### 7. Continue in Beatrax

From here the routine is [J2](j2-daily-use.md) and [J3](j3-monthly-reconcile.md).
Statement imports run alongside migrated history, deduplicating on the
fingerprint where they overlap.

## Features exercised

[A8](../features/a-ingestion/a8-migration-importers.md) ·
[A3](../features/a-ingestion/a3-idempotency.md) ·
[B1](../features/b-ledger/b1-transactions.md) ·
[B4](../features/b-ledger/b4-counterparties.md) ·
[B6](../features/b-ledger/b6-transfers.md) ·
[B7](../features/b-ledger/b7-splits.md) ·
[B8](../features/b-ledger/b8-reconciliation.md) ·
[D1](../features/d-money/d1-envelope-budgeting.md) ·
[D2](../features/d-money/d2-goals.md)

## How this journey fails

| Failure | Why it matters |
|---------|----------------|
| A re-run duplicates history | A user who tries twice has a corrupted ledger. |
| A carried-forward balance is imported as an assignment | A year of budget history is silently doubled. |
| Splits are reconstructed aggressively | Unrelated rows are merged into one transaction. |
| Unmapped items are not surfaced before commit | The user discovers what is missing after committing. |
| An archive bomb is accepted | A hostile export exhausts the machine. |
| Unreconciled fields are implied to reconcile | The user believes an update landed when it did not. |
| Migrated rows use a privileged write path | They behave differently from imported ones, unpredictably. |

## Related

- [J1 First run](j1-first-run.md) — the alternative starting point
- [ADR-0017](../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md) — the model being imported into
