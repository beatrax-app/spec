# A8 — Migration from YNAB, nYNAB and Actual

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

Someone arriving from another budgeting tool has years of categorised history,
a category tree they have refined, and a month-by-month budget. Asking them to
start again is asking them not to switch.

This feature imports a full budget export — categories, the whole budget
assignment history, transactions with splits and cleared status, accounts,
transfers, payees, and (where the source has them) goals — into Beatrax's
envelope model.

## Behaviour

### Three sources, one intermediate shape

Exports from the two YNAB generations and from Actual Budget each get their own
parser. Every parser produces the same intermediate representation, so
everything downstream — staging, preview, promotion, reconciliation — is written
once.

The Actual parser reads its export as a **read-only** second database
connection.

### Parse, stage, preview, promote

1. **Parse and stage.** The export is parsed and written to staging tables in
   bounded chunks. Nothing touches the live ledger.
2. **Preview.** The user sees what will be created, grouped by kind, with a
   summary of anything the importer could not map.
3. **Promote.** Staged rows become real records in dependency order: categories,
   then the budget assignment grid, then accounts, then transactions, then
   splits, then a transfer-pairing sweep, then goals.

Promotion runs **outside** a wrapping transaction — only the status change and
the counts are wrapped — because a whole-history promotion as one transaction is
exactly the unbounded transaction the import path exists to avoid.

Every promotion step writes through the same public writers the rest of the
product uses. There is no privileged path into the ledger.

### Re-running the same export is a true no-op

A source-map records, per user, which source entity became which Beatrax record.
Every promotion step consults it first; a hit reuses the existing record and
performs **no further writes**. That is what makes a byte-identical re-run a
genuine no-op rather than merely "safe to call again".

The map records one row per promoted transaction, not one per split leg.

Where a source entity carries no stable identifier, a natural-key fallback
applies **only among entities that have no identifier** — so renaming an entity
that does have one correctly surfaces as a changed field rather than a new
record.

### Updating from a newer export: a three-way merge

Re-importing a newer export of the same budget compares three values per field:
the staged new value, the Beatrax current value, and the baseline recorded at
the last import.

| Comparison | Outcome |
|------------|---------|
| New equals current | Skip — nothing changed. |
| New differs, current equals baseline | Apply — the source changed and Beatrax has not. |
| New differs, current differs from baseline | Conflict — both changed; ask the user. |

Money is compared as money, never as a formatted string.

Reconciliation is implemented for budget assignments (fully worked), category
names, account names, transaction descriptions, and non-split transaction
amounts. **Transaction date, category, payee, and goal reconciliation are not
implemented** — those fields are imported on a first run and not reconciled on a
re-run.

### Details that matter

- Migrated accounts receive a deterministic synthetic account identifier derived
  from the source identifier, because a budget export carries no bank account
  number.
- No source format carries a time of day, so posting dates are midnight. A
  deterministic sub-day offset derived from the staged row is used internally
  for stable ordering; the user-facing date is exact.
- A budget assignment's amount is the **amount assigned**, never a carried-forward
  balance. Confusing the two silently doubles a year of budget history.
- Splits are reconstructed from the source's own split convention,
  conservatively: only adjacent rows sharing account, date, and payee are
  grouped.
- Amount changes applied by reconciliation recompute the fingerprint atomically
  with the amount, so the row stays idempotent afterwards.

### Archives are opened defensively

An uploaded archive is guarded against entry-count and total-uncompressed-size
bombs and against path traversal, absolute paths, and symlink entries.

## States

| State | Meaning |
|-------|---------|
| `parsed` | Staged and previewable. |
| `needs_attention` | A three-way merge produced conflicts. |
| `confirmed` | Promoted. Terminal — cannot be discarded. |
| `discarded` | Abandoned. Cannot be confirmed. |

Abandoned runs are swept after an age threshold.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A byte-identical re-run | No writes at all. |
| A renamed entity that has a stable identifier | Surfaces as a changed field, not a new record. |
| A fingerprint collision when applying an amount change | The change is refused and reported rather than throwing. |
| An entry the importer cannot map | Recorded in an unmapped-items summary shown in the preview. |
| An archive that is a zip bomb or contains traversal paths | Rejected before extraction. |
| A run abandoned mid-preview | Swept after the age threshold, scoped to its owner. |
| A conflict in a field with no reconciliation support | Not surfaced — the field is simply not reconciled on re-run. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A8-R1** | Exports from both YNAB generations and from Actual Budget MUST be supported. |
| **A8-R2** | Every parser MUST produce the same intermediate representation. |
| **A8-R3** | An Actual export MUST be opened read-only. |
| **A8-R4** | Parsing and staging MUST NOT write to the live ledger. |
| **A8-R5** | The preview MUST show what will be created and MUST include a summary of unmapped items. |
| **A8-R6** | Promotion MUST proceed in dependency order: categories, budget assignments, accounts, transactions, splits, transfer pairing, goals. |
| **A8-R7** | Promotion MUST NOT run inside one wrapping transaction; only the status change and counts may be wrapped. |
| **A8-R8** | Every promotion step MUST write through the same public writers the rest of the product uses. |
| **A8-R9** | A source-map MUST record which source entity became which Beatrax record, per user. |
| **A8-R10** | Every promotion step MUST consult the source-map first; a hit MUST reuse the existing record and perform no further writes. |
| **A8-R11** | The source-map MUST record one row per promoted transaction, not one per split leg. |
| **A8-R12** | Natural-key fallback MUST apply only among entities lacking a stable source identifier. |
| **A8-R13** | Re-importing a newer export MUST perform a three-way merge against the baseline recorded at the previous import. |
| **A8-R14** | The merge MUST skip when new equals current, apply when current equals baseline, and raise a conflict otherwise. |
| **A8-R15** | Monetary comparison in the merge MUST compare money values, never formatted strings. |
| **A8-R16** | A budget assignment's imported amount MUST be the assigned amount, never a carried-forward balance. |
| **A8-R17** | Migrated accounts MUST receive a deterministic synthetic identifier derived from the source identifier. |
| **A8-R18** | User-facing posting dates MUST be exactly the source date; any internal ordering offset MUST NOT be surfaced. |
| **A8-R19** | Split reconstruction MUST be conservative, grouping only adjacent rows sharing account, date, and payee. |
| **A8-R20** | An amount change applied by reconciliation MUST recompute the fingerprint atomically with the amount. |
| **A8-R21** | A fingerprint collision during an amount change MUST be reported rather than throwing. |
| **A8-R22** | Uploaded archives MUST be guarded against entry-count and uncompressed-size bombs, absolute paths, traversal paths, and symlink entries. |
| **A8-R23** | A confirmed run MUST NOT be discardable, and a discarded run MUST NOT be confirmable. |
| **A8-R24** | Abandoned runs MUST be swept after an age threshold, scoped to their owner. |
| **A8-R25** | Fields without reconciliation support MUST be documented as unreconciled rather than silently appearing to reconcile. |

## Related

- [D1 Envelope budgeting](../d-money/d1-envelope-budgeting.md) — the model imported into
- [B7 Split transactions](../b-ledger/b7-splits.md) · [B8 Reconciliation](../b-ledger/b8-reconciliation.md)
- [A3 Idempotency](a3-idempotency.md)
- [J7 Migrating from another tool](../../journeys/j7-migrating.md)
