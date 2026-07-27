# D4 — Tax tagging and per-year export

**Status:** Accepted · **Area:** D — Money management

---

## Purpose

Once a year a household has to produce the subset of its spending that a tax
authority cares about. Doing that from statements, in a spreadsheet, in the week
before the deadline, is how deductions get missed.

Tagging as you go — from wherever you happen to be looking at a transaction —
and exporting a clean year at the end is what this feature is for.

## Behaviour

### Tag from anywhere

A transaction can be tagged as tax-relevant from the transaction list, the
detail view, a counterparty profile, or the cash book. The same badge, picker,
and batch affordance appear on all four.

A tag optionally carries a deduction category, a note, and a **year override**
for the case where a payment made in January belongs to the previous year's
filing.

### Split legs tag individually

A split transaction ([B7](../b-ledger/b7-splits.md)) tags per leg. An
eighty-unit purchase split sixty deductible and twenty not **exports sixty** —
never eighty, never zero.

Once any leg-level tag exists on a transaction, the whole-transaction tag is
excluded from every result rather than deleted, so the leg-level intent wins
without destroying what came before.

A leg's deduction category always comes from the tag, never from the leg's own
spending category — they are different taxonomies.

### The effective year

The effective tax year is the override where one exists, otherwise the year of
the booking date. An override is bounded to a sensible window around the present.

### The year cockpit

A single page for a chosen year, grouped by deduction category, with totals in
the settled reporting currency. It defaults to the year most people are filing:
the previous year early in the calendar year, the current year later.

### Export

CSV and PDF.

**CSV** has a fixed column order covering the year, date, account, counterparty,
counterparty identifier, description, deduction category, note, settled amount,
original amount and currency, transaction type, and the audit fields that let a
row be traced back to its source: the transaction identifier, source format,
import run, and fingerprint. Every cell is escaped against spreadsheet formula
injection, and amounts are formatted with integer arithmetic rather than float
conversion.

**PDF** is a summary plus grouped tables, rendered with remote content disabled
and all interpolation escaped.

### Country corpus

Deduction categories are seeded from a bundled per-country corpus covering
several jurisdictions. Switching country is **additive** — it seeds the new
corpus and never deletes what is there, because a user who has tagged a year
under one set must not lose those tags.

Seeding is insert-only on the corpus key, so re-running preserves any edits.

### Tagging semantics

Re-tagging an already-tagged row with an empty payload — the one-tap tag button —
is **non-destructive**: the existing category, note, and year override are left
alone and the first-tagged timestamp is never rewritten, because it is the audit
signal for when the decision was made.

Any non-empty field means the whole payload is written together, so partial
state cannot accumulate.

Untagging is fire-and-forget: a miss or a cross-user target is a silent no-op.

A lost race on the uniqueness constraint is caught and retried rather than
surfacing as an error.

### Reconciled rows

Tagging respects the reconciliation lock ([B8](../b-ledger/b8-reconciliation.md)):
a batch operation filters out already-reconciled candidates before applying.

### Search integration

Tax notes are part of the full-text index ([B9](../b-ledger/b9-search.md)), so
"find that thing I noted last March" works.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A partially deductible split | Exports the deductible legs' amounts only. |
| A whole-transaction tag plus a leg tag | The whole-transaction tag is excluded from results, not deleted. |
| A year override outside the sensible window | Rejected. |
| A one-tap re-tag on a tagged row | Nothing changes; the first-tagged timestamp is preserved. |
| A cross-user untag | Silent no-op. |
| A concurrent duplicate tag | The lost race is caught and retried. |
| A reconciled row in a batch | Filtered out before applying. |
| Switching tax country | The new corpus seeds; nothing is deleted. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **D4-R1** | A transaction MUST be taggable from the transaction list, the detail view, a counterparty profile, and the cash book. |
| **D4-R2** | A tag MUST optionally carry a deduction category, a note, and a year override. |
| **D4-R3** | Split legs MUST be taggable individually. |
| **D4-R4** | A partially deductible split MUST export only the deductible legs' amounts. |
| **D4-R5** | Once a leg-level tag exists, the whole-transaction tag MUST be excluded from results rather than deleted. |
| **D4-R6** | A leg's deduction category MUST come from the tag, never from the leg's spending category. |
| **D4-R7** | The effective tax year MUST be the override where present, otherwise the booking date's year. |
| **D4-R8** | A year override MUST be bounded to a sensible window around the present. |
| **D4-R9** | The year view MUST group by deduction category with totals in the settled reporting currency. |
| **D4-R10** | The year view MUST default to the year most users are filing, based on the current date. |
| **D4-R11** | CSV export MUST use a fixed column order including the audit fields needed to trace a row to its source. |
| **D4-R12** | Every exported cell MUST be escaped against spreadsheet formula injection. |
| **D4-R13** | Exported amounts MUST be formatted with integer arithmetic, never float conversion. |
| **D4-R14** | PDF rendering MUST disable remote content and MUST escape all interpolated values. |
| **D4-R15** | Deduction categories MUST be seeded from a bundled per-country corpus. |
| **D4-R16** | Switching country MUST be additive and MUST NOT delete existing categories or tags. |
| **D4-R17** | Corpus seeding MUST be insert-only so re-running preserves user edits. |
| **D4-R18** | A re-tag with an empty payload MUST leave existing values untouched and MUST NOT rewrite the first-tagged timestamp. |
| **D4-R19** | A re-tag with any non-empty field MUST write the whole payload together. |
| **D4-R20** | Untagging MUST be a silent no-op on a miss or a cross-user target. |
| **D4-R21** | A lost race on the tag uniqueness constraint MUST be caught and retried. |
| **D4-R22** | Batch tagging MUST filter out reconciled transactions before applying. |
| **D4-R23** | Tax notes MUST be included in the full-text index. |
| **D4-R24** | Tax notes MUST be treated as sensitive and encrypted at rest. |
| **D4-R25** | A cross-user tag target MUST return not-found. |

## Related

- [B7 Split transactions](../b-ledger/b7-splits.md) — per-leg deductibility
- [B8 Reconciliation](../b-ledger/b8-reconciliation.md) · [B9 Search](../b-ledger/b9-search.md)
- [E4 At-rest encryption](../e-sync/e4-at-rest-encryption.md)
- [J4 Tax year end](../../journeys/j4-tax-year-end.md)
