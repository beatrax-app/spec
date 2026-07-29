# C7 — Report builder and saved reports

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

Fixed dashboard cards answer the questions the maintainer thought of. A report
builder answers the ones the user has: where did the money go this quarter, how
has net worth moved over two years, which counterparty has grown the most.

## Behaviour

### Compose a report from five choices

A report is a metric, a grouping, a period, a set of filters, a currency mode,
and a visualisation. It renders live as a chart and a table as the user changes
any of them.

| Choice | Options |
|--------|---------|
| Metric | Spend, income, net, net worth |
| Group by | Category, counterparty, account, time bucket |
| Period | Presets, or an explicit custom range |
| Filters | The same filters search uses |
| Currency | Base-converted, or original currencies |
| Visualisation | Chart type plus the underlying table |

### The metrics are computed honestly

**Net is computed natively**, as a single signed sum over income and expense —
never as spend subtracted from income computed separately. Two separately-rounded
figures subtracted do not reliably equal one signed sum.

**Category aggregation is split-aware** ([B7](../b-ledger/b7-splits.md)): it
counts split legs and unsplit parents, never both. A split whose legs do not sum
rolls up via the parent's own category as a fail-safe. Cross-dimension totals are
checked for consistency by test — the same period grouped two different ways must
produce the same total.

**Net worth over time** is sampled on demand rather than stored as history. Its
most recent point is not guaranteed to be byte-identical to the dashboard's
net-worth card, which resolves through a different anchor path — a documented
limitation rather than a bug to be surprised by.

### Time buckets widen rather than truncate

A range too long for its bucket size auto-widens — monthly to quarterly, weekly
to monthly to quarterly — up to a maximum point count. It never silently
truncates the range, because a chart showing half the period the user asked for
is worse than a coarser chart showing all of it.

The granularity the user chooses is monthly or weekly, and nothing else.
Quarterly is a widening outcome the generator reaches on its own; it is never a
value the user picks and never one a saved report holds, so it is not part of
the vocabulary. A stored granularity outside the set is a defect rather than a
new case to handle, so the set is named once and the code is held to it.

The series cadence in [C2](c2-recurring.md) and the digest cadence in
[C8](c8-notifications.md) also say `weekly`. All three are separate
vocabularies that happen to share a word and a value, and none of them may
share a type — a report is not on a cadence, and widening its buckets has
nothing to do with how often a series recurs or how often a digest is sent.

### Currency modes are explicit

In base mode, values convert and merge, and rows with no available rate are
**excluded and flagged** rather than silently dropped or treated as
one-to-one. In original mode nothing converts and each currency gets its own
row.

### Period comparison

A report can compare against the previous period, computed as an equal-length
span shift rather than "the previous calendar period" — comparing a 45-day range
against a calendar month would be meaningless. The comparison unions the group
keys from both periods and sorts by absolute change.

### Saving and pinning

A report definition can be saved, renamed, deleted, and exported to a file.
Export escapes every free-text column against spreadsheet formula injection and
formats amounts with integer arithmetic.

Up to a fixed number of saved reports can be pinned as dashboard cards. The cap
is checked **inside** the write transaction, so two concurrent pins cannot both
succeed past it. Pin ordering stays dense as reports are pinned and unpinned.

Every write action guards ownership explicitly and returns not-found — never
forbidden — for a report the caller does not own.

### Drilling through

A chart segment drills into the transactions behind it, carrying the report's
filters into the search surface ([B9](../b-ledger/b9-search.md)).

### Custom ranges are parsed strictly

A custom range is parsed in an exact date format, never by a lenient parser
that would accept ambiguous input. An inverted range is rejected.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A group with no available exchange rate in base mode | Excluded from the total and counted separately; the exclusion is shown. |
| A multi-currency group in original mode | One row per currency; never merged. |
| A range too long for its bucket | Widened, never truncated. |
| A split whose legs do not sum | Rolls up via the parent's own category. |
| Two concurrent pins at the cap | The cap check inside the transaction lets exactly one through. |
| An inverted custom range | Rejected. |
| The most recent net-worth point versus the dashboard card | May differ; documented. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C7-R1** | A report MUST be composed of a metric, a grouping, a period, filters, a currency mode, and a visualisation. |
| **C7-R2** | The report MUST render live as both a chart and a table. |
| **C7-R3** | Net MUST be computed as a single signed sum, never as separately computed spend and income subtracted. |
| **C7-R4** | Category aggregation MUST be split-aware, counting legs and unsplit parents and never both. |
| **C7-R5** | A split whose legs do not sum MUST roll up via the parent's own category. |
| **C7-R6** | The same period grouped by different dimensions MUST produce the same total, verified by test. |
| **C7-R7** | Net worth over time MUST be sampled on demand; no net-worth history may be stored. |
| **C7-R8** | The divergence between the sampled net-worth series and the dashboard card MUST be documented. |
| **C7-R9** | A range exceeding the bucket point cap MUST widen the bucket, never truncate the range. |
| **C7-R10** | In base currency mode, rows with no available rate MUST be excluded and flagged, never treated as one-to-one. |
| **C7-R11** | In original currency mode, nothing MUST be converted and each currency MUST occupy its own row. |
| **C7-R12** | Period comparison MUST use an equal-length span shift, not the previous calendar period. |
| **C7-R13** | Comparison MUST union the group keys of both periods and sort by absolute change. |
| **C7-R14** | A report definition MUST be saveable, renameable, deletable, and exportable. |
| **C7-R15** | Export MUST escape every free-text column against formula injection and MUST format amounts with integer arithmetic. |
| **C7-R16** | The number of pinned dashboard reports MUST be capped, and the cap MUST be checked inside the write transaction. |
| **C7-R17** | Pin ordering MUST remain dense as reports are pinned and unpinned. |
| **C7-R18** | Every write action MUST guard ownership explicitly and MUST return not-found for a report the caller does not own. |
| **C7-R19** | A chart segment MUST drill through to the transactions behind it, carrying the report's filters. |
| **C7-R20** | Custom ranges MUST be parsed strictly, and an inverted range MUST be rejected. |
| **C7-R21** | The report granularity vocabulary MUST be closed to monthly and weekly; it MUST be expressed as one named type rather than as free strings, a stored value outside the set MUST be rejected rather than defaulted, and the type MUST NOT be shared with the series cadence of C2 or the digest cadence of C8. |

## Related

- [B7 Split transactions](../b-ledger/b7-splits.md) — why aggregation is split-aware
- [B9 Full-text search](../b-ledger/b9-search.md) — the drill-through target
- [B10 Multi-currency](../b-ledger/b10-multi-currency.md) — the currency modes
- [C1 Dashboard](c1-dashboard.md) — pinned cards
- [C2 Recurring detection](c2-recurring.md) — the series cadence, a separate vocabulary that also says weekly
- [C8 Notifications](c8-notifications.md) — the digest cadence, the third one
