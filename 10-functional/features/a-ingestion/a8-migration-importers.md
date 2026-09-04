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
   summary of anything the *parser* could not map.
3. **Promote.** Staged rows become real records in dependency order: categories,
   then the budget assignment grid, then accounts, then transactions, then
   splits, then a transfer-pairing sweep, then goals.

Promotion runs **outside** a wrapping transaction — only the status change and
the counts are wrapped — because a whole-history promotion as one transaction is
exactly the unbounded transaction the import path exists to avoid.

Every promotion step writes through the same public writers the rest of the
product uses. There is no privileged path into the ledger.

### Cannot map and cannot parse are different failures

The unmapped-items summary is about **mapping**, and only mapping. An unmapped
item is a source concept with no Beatrax counterpart, or one Beatrax declines to
store as it stands: a saved report, a recurring schedule, a goal with no target
date, a split whose legs do not add up to their transaction. In each case the
file was read and the figure understood; there is simply nowhere to put it. The
run continues, and every item is listed with its reason.

**Where** it is listed follows from when it was found, and the two are not the
same screen. What the parser can see — an Actual schedule, a saved report, a goal
template Beatrax cannot express — is staged with everything else and appears in
the preview. What only promotion can discover — a fingerprint collision, a split
whose legs will not store, a goal with no target date — is recorded as it happens
and appears on the results screen afterwards. A first YNAB import therefore
previews an empty unmapped list whatever the export holds, because the YNAB
parsers stage no unmapped items at all; on a re-import the preview does carry the
three-way merge's conflicts.

A value that **cannot be parsed** is a different failure, and answering it the
same way is how a wrong ledger arrives looking right. A cell whose value cannot
be read refuses the whole file, before a single row is staged.

The reasoning is not squeamishness about one row. A migration reads one product's
entire history against a format assumption made once, so a cell that will not
read is evidence about its **column**, not about its row: if one amount in a
column is not an amount, the column is not the column it was taken for and every
figure in it is suspect. Continuing imports a plausible-looking ledger that is
wrong throughout. Substituting a default is worse — an amount folded to zero puts
a transaction at 0,00 in the ledger with nothing on screen to tell it from a real
one.

This is deliberately the opposite of the import wizard, where a row that fails
processing becomes an error row and the import carries on
([A2-R4](a2-import-wizard.md)). The two are not in conflict. A wizard error row
carries a verdict the user is shown ([A2-R3](a2-import-wizard.md)); a misread
amount carries no verdict at all, because it still looks like a figure.

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
| New equals baseline | Skip — the source has not changed since the last import. |
| New differs from baseline, current equals baseline | Apply — the source changed and Beatrax has not. |
| New differs from baseline, current differs from baseline | Conflict — both changed; ask the user. |

Both questions are asked **against the baseline**, and the first one has to be.
Skipping on "new equals current" instead would hide a genuine source change
whenever the user had already made the same edit by hand: the two values match,
so nothing is recorded and the baseline never advances past what the *previous*
import saw. Beatrax and the source now agree while the baseline disagrees with
both — and the next import, comparing against that stale baseline, reports a
conflict neither side ever had.

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
| A byte-identical re-run | Nothing touches a domain table; a run row and its staging copy are still written. |
| A renamed entity that has a stable identifier | Surfaces as a changed field, not a new record. |
| A fingerprint collision when applying an amount change | The change is refused and reported rather than throwing. |
| An entry the importer cannot map to a Beatrax concept | Recorded in an unmapped-items summary with its reason; in the preview when the parser found it, on the results screen when promotion did. The run continues. |
| A cell whose value cannot be parsed | The whole file is refused before any row is staged; no default is substituted. |
| An archive that is a zip bomb or contains traversal paths | Rejected before extraction. |
| A run abandoned mid-preview | Swept after the age threshold, scoped to its owner. |
| A conflict in a field with no reconciliation support | Not surfaced — the field is simply not reconciled on re-run. |

### Known gap — the refusal names the cell to nobody

The parser composes its refusal around the file, the column and the offending
value. Neither the reader nor the log is told any of it. The screen shows one
fixed line for every unreadable export — deliberately, so that a raw exception
message is never handed to a user — and the log records the exception's class
and nothing else, because the context helper that writes it strips the message
wholesale. That default is sound elsewhere in the product, where an exception
message can carry row data.

The effect here is that the reader is told the file could not be read and given
nothing to act on, while the diagnostic the parser took the trouble to compose is
discarded between the two. The sibling pipeline already states the rule this one
is missing: plain language on screen, full diagnostics in the local log
([A2-R6](a2-import-wizard.md)).

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
| **A8-R14** | The merge MUST skip when new equals baseline, apply when current equals baseline, and raise a conflict otherwise. |
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
| **A8-R26** | A value that cannot be parsed MUST refuse the whole file before any row is staged, and MUST NOT be substituted with a default or recorded as an unmapped item. |
| **A8-R27** | *(Open)* A refusal MUST record the file, the column and the value it could not read in the local log. Not yet satisfied — see [Known gap](#known-gap--the-refusal-names-the-cell-to-nobody). |

## Related

- [D1 Envelope budgeting](../d-money/d1-envelope-budgeting.md) — the model imported into
- [B7 Split transactions](../b-ledger/b7-splits.md) · [B8 Reconciliation](../b-ledger/b8-reconciliation.md)
- [A3 Idempotency](a3-idempotency.md)
- [J7 Migrating from another tool](../../journeys/j7-migrating.md)
