# ADR-0026: An id two devices cannot both compute is minted, not derived

**Status:** Accepted
**Date:** 2026-09-03

## Context

[ADR-0025](0025-primary-key-collisions-are-quarantined.md) made a primary-key
collision visible and named the prevention as the next piece of work: give the
exposed tables an id that is not "the next number on this device". Thirteen
covered tables mint an autoincrement and declare no other unique index.

[ADR-0024](0024-peer-row-id-aliases.md) already had one answer —
`DerivedRowId::for()`, which folds the columns that identify a row into its id
so two devices compute the same number without exchanging a message. It was
built for detector output, where both devices genuinely derive the same row from
the same ledger.

Applied to the exposed tables, that answer is wrong for most of them, and wrong
in the worse direction. Two deposits of the same amount into one pot on one day
are **two deposits**. An id computed from their content gives them one row, and
the second is refused as a duplicate — losing money rather than duplicating it.
The same holds for a second goal of the same name, or a second saved report.

## Decision

**A row gets a derived id when every device would compute the same identity for
it, and a minted one when they would not.**

`DeviceMintedRowId::mint()` returns a random 63-bit integer. Nothing about the
row is folded in, so two devices never agree — which is the point: they were
never writing the same row.

The test is not "does this row have columns that identify it", but **"are those
columns the same on every device"**:

| Table | Answer | Why |
| --- | --- | --- |
| `envelope_moves` | derived | `move_group_id` is a uuid minted once and carried by both rows of the move |
| `system_alerts` | derived | every device polls the same feed; the kind and the version are the same strings everywhere |
| `anomaly_suppression_rules` | derived | keyed on the alert it was dismissed from, and `anomaly_alerts` ids are themselves derived |
| `pot_movements` | minted | a second deposit of the same amount is a second deposit |
| `goals` | minted | the writer deliberately never upserts: two goals of one name are two goals |
| `saved_reports` | minted | likewise |
| `forecast_scenario_mutations` | minted | hangs off a scenario whose id is a local autoincrement on each device |
| `migration_import_baseline` | minted | hangs off a source-map row matched by natural key, so its id is this device's |

The trap that decides several of these: **a foreign key is not a
device-independent value** unless the parent's own id is derived. A scenario or
a source-map row is reconciled by [ADR-0024](0024-peer-row-id-aliases.md)'s
alias, which means the two devices hold it under *different* ids — so an id
derived from that foreign key differs per device and derives nothing.

Three tables are exempt because they never travel in either direction:
`categorization_rules`, `rule_conditions`, `rule_actions`. The backfill excludes
them and no writer captures them; the rules screen tells the reader so.

`transaction_splits` is left exposed **with its reason recorded rather than
quietly passing**. Its rows are the legs of one transaction and their
`sort_order` is reassigned on every save, so neither answer fits: a minted id
lets both devices' legs land and the legs then sum to twice the transaction,
while a derived one moves a leg's id whenever the leg moves. It needs a decision
about the *set* of legs, not about one row's id, and that decision is not this
one.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Derive every exposed table's id | Merges rows that were never the same row. On `pot_movements` and `goals` that silently deletes a deposit or a goal, which is worse than the collision it fixes. |
| Mint every exposed table's id | Duplicates rows two devices genuinely both compute — one "update available" banner per device, one suppression rule per device. |
| Give each device an id range (a device ordinal in the high bits) | Uniform and needs no per-table thought, but it hands out an id that encodes which device wrote the row, and the ordinal has to be allocated by something. There is no allocator: [ADR-0015](0015-multi-master-p2p-sync.md) has no hub. |
| Add a uuid column to each exposed table and derive from it | The honest general answer, and it is what `envelope_moves` already has in `move_group_id`. Rejected for now as a migration per table plus a merge-rule change per table, for a property a random id gives without either. |

## Consequences

### Positive

- The collision stops happening on eight of the nine tables that could reach it,
  rather than only being reported.
- `system_alerts` gains a dedupe it never had: the poll runs on a schedule and a
  plain insert wrote one banner row per poll.

### Negative

- Both id kinds run past 2<sup>53</sup>, so every id in those modules must reach
  the browser **quoted**. This is enforced, not remembered: the guard that
  already covered derived ids now covers minted ones, and it is deliberately
  coarse — it flags every bare id in a module that mints any, including ids that
  are still small autoincrements.
- Rows written before this keep the ids they were given. Nothing is rewritten,
  so a table holds both kinds side by side.

### Neutral

- A random 63-bit id is not sequential, so nothing may infer creation order from
  it. Nothing did: the tables that carry an order carry a timestamp for it.

## Revisit if

- `transaction_splits` gets its set-level decision, which may also be the moment
  to give the exposed tables a uuid column and retire the minted id.

## Related

- [ADR-0024](0024-peer-row-id-aliases.md) — the alias that reconciles a peer's
  id, and the reason a foreign key is not device-independent
- [ADR-0025](0025-primary-key-collisions-are-quarantined.md) — the collision this
  prevents, and which named this work
- [ADR-0015](0015-multi-master-p2p-sync.md) — no central allocator
