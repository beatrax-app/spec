# ADR-0025: A create the primary key refuses is quarantined when the row already there is a different row

**Status:** Accepted
**Date:** 2026-09-02

## Context

[ADR-0024](0024-peer-row-id-aliases.md) split `AlreadyPresent` in two and left
one half explicitly unchanged:

> `AlreadyPresent` **by the primary key** is unchanged: the ids already agree,
> and that is the idempotent re-apply.

The ids agreeing is not the rows agreeing. That sentence holds wherever the
table declares a natural unique key, because then a genuinely different row
would have collided on *that* index and been aliased. It does not hold where the
table declares none.

Measured on a paired desktop and phone rather than reasoned about: a move of
&minus;777 was made on the desktop and one of &minus;888 on the phone while the
two were apart. Each was the ninth `envelope_moves` row on its own device, so
each was id 9. After they synced, every device kept its own row, the peer's
create was classified `AlreadyPresent` and passed over, and `op_log_quarantine`
was **empty on both sides**. Two devices disagreed about money and nothing
anywhere said so. A second pair, ids 5 and 6, had already diverged the same way
earlier the same day and had gone equally unreported.

Thirteen covered tables mint an integer autoincrement primary key and declare no
other unique index, so there is no natural twin for the alias to find:
`categorization_rules`, `rule_conditions`, `rule_actions`, `pot_movements`,
`goals`, `transaction_splits`, `envelope_moves`, `migration_import_baseline`,
`saved_reports`, `chain_links`, `anomaly_suppression_rules`, `system_alerts`,
`forecast_scenario_mutations`.

## Decision

**A create the primary key refuses is quarantined as `primary_key_collision`
when the stored row contradicts it, and passed over in silence only when it does
not.** The alias arm of ADR-0024 is unchanged and is tried first: where a local
twin is found, the content did land under the other id and there is no loss to
report.

The contradiction test is a conjunction:

- the op's `created_at` disagrees with the stored row's, **and**
- at least one other compared column disagrees as well.

Columns excluded from the comparison, each for its own reason: sensitive columns
(the payload is re-sealed for this device before the insert, so a fresh nonce
makes the ciphertext differ on every replay), `id` and `user_id` (seeded by the
applier from the op envelope rather than the wire), and `updated_at` (it moves
whenever anything about the row does).

Both halves are load-bearing. Against a real op log of 320 create groups drawn
from the paired pair above:

| Rule | Groups flagged | Real collisions among them |
| --- | --- | --- |
| Whole payload | 36 | 4 |
| `created_at` alone | 2 | 2 (missed two) |
| **The conjunction** | **4** | **4** |

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Insert the peer's row under a fresh local id and alias the peer's id to it | Repairs instead of reporting, which is better — but it must be *right* to be safe. Mistaking a create replayed after its row was edited for a collision would duplicate the row, turning a loss into a double count. Left open under "Revisit if" once derived ids make the judgement unnecessary. |
| Compare the whole payload | 32 of the 36 differences on a real device were one row whose create replayed after the row had been edited: stale in the edited column by design, and the same row. Quarantine is a signal a person reads, and at eight false entries per real one it stops being one. |
| Compare `created_at` alone | Blind wherever the stored value is null, which is exactly how rows written by peers on older builds landed. It missed two of the four real collisions. |
| Leave it — accept the discard as idempotent | The status quo this finding describes, and its worst property is the one ADR-0024 already named: the device reported no error while a person's money was simply absent. |
| Make ids device-independent across the thirteen tables | The real prevention, and it is the next piece of work — but it is per-table (each needs an identity that cannot merge two legitimately distinct rows, and each exposes its id to a wire that rounds past 2<sup>53</sup>), and it does nothing for the ids already minted. |

## Consequences

### Positive

- Two devices that disagree about money say so, on the device that received the
  losing write, with the table, the pk and the peer that sent it.
- The rule satisfies [E1-R13](../../10-functional/features/e-sync/e1-change-capture.md)
  for a refusal that had been outside it: the entry was refused and not recorded.

### Negative

- A collision is reported, not repaired. The peer's row stays absent until a
  person acts on it.
- `primary_key_collision` is deliberately **not** in
  `QuarantineReason::recoverable()`: the id is held by another row and no op
  arriving later frees it, so a retry pass would refuse it identically forever.

### Neutral

- Nothing changes for the alias path, for tables with a natural unique key, or
  for the idempotent re-apply, which is the overwhelming majority of what
  crosses.

## Revisit if

- Derived ids land for the thirteen tables above. A collision then means a
  genuine identity clash rather than two counters meeting, and inserting the
  peer's row under a fresh id becomes safe enough to prefer over reporting.

## Related

- [ADR-0026](0026-an-id-two-devices-cannot-both-compute-is-minted.md) — the
  prevention this decision named as the next piece of work
- [ADR-0024](0024-peer-row-id-aliases.md) — the alias decision this refines, and
  the sentence it corrects
- [ADR-0014](0014-op-log-crdt-merge-engine.md) — the op log that carries a local
  autoincrement id as a cross-device identity
- [ADR-0015](0015-multi-master-p2p-sync.md) — no central id allocator, which is
  why two devices can mint one id
- [E1 change capture](../../10-functional/features/e-sync/e1-change-capture.md) —
  E1-R13, the rule a silent discard broke
