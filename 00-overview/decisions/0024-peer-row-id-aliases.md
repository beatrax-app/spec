# ADR-0024: A peer's row id is reconciled by a durable alias, not by making ids device-independent

**Status:** Accepted
**Date:** 2026-09-02

## Context

[ADR-0014](0014-op-log-crdt-merge-engine.md) carries a row's **local
autoincrement id** as its cross-device identity, and
[ADR-0015](0015-multi-master-p2p-sync.md) has no hub to allocate ids centrally.
That holds for rows one device creates and the other only ever receives.

It does not hold for rows **both devices create independently**. A device seeds
its own reference data at signup — tax deduction categories from the country
corpus, among others — so the same six `corpus_key` values exist on both sides
under different autoincrement ids. Measured on a paired Mac and iPhone: ids
109–114 and 13–18 for the same six rows.

The peer's create then arrives, the applier re-scopes `user_id` to the local
user, and the insert collides on the table's *other* unique index —
`(user_id, name)` — not on the primary key:

```text
UNIQUE constraint failed: tax_deduction_categories.user_id, tax_deduction_categories.name
```

That was classified `AlreadyPresent` and passed over in silence, which is
correct for the idempotent re-apply a replay is built on. It is wrong here. The
row **is** present; what was discarded is the peer's *identity* for it, so every
child naming id 109 failed its foreign key and was quarantined.

The cost, measured on the device rather than reasoned about: the whole Tax
feature's data absent on the phone — 19 tag rows — plus `transaction_splits`
8 → 6, `envelope_assignments` 38 → 34 and two transactions, with nothing
anywhere reporting a loss.

## Decision

**A device keeps a durable, peer-scoped record of which local row a peer's id
means, and rewrites foreign keys through it on the way in.**

- `AlreadyPresent` **by the primary key** is unchanged: the ids already agree,
  and that is the idempotent re-apply.
- `AlreadyPresent` **by any other unique index** is a second id for one logical
  row. The local twin is found through the table's own unique indexes, read from
  the schema, and the pair is recorded in `op_log_row_aliases`.
- The alias is keyed by `(user_id, table_name, device_id, remote_id)`. **Peer
  scoping is required, not defensive:** two devices both count from 1, so the
  same remote id names a different row on each of them.
- Every foreign key a replayed row names is rewritten through the alias, derived
  from the live schema rather than a list of columns.

The table is device-local and is not itself covered by sync: the mapping is
between two devices, and the peer already holds its own half.

## Why this rather than device-independent ids for seeded rows

The obvious alternative is to give independently-seeded reference rows an id
both devices compute — the `DerivedRowId` mechanism this codebase already uses
for detector output.

**It cannot work for these rows.** A derived id must be computed identically on
both devices, and the identity tuple for a per-user reference row has to include
the owner. But `user_id` is a per-device autoincrement, and the applier
deliberately re-scopes it to the local user on arrival — it is *precisely* the
column that differs across devices. Folding it into the digest guarantees two
different ids for the same row, which is the defect restated rather than fixed.

There is no stable cross-device user identity to fold in instead. A username is
mutable and is not part of the sync contract.

## Alternatives considered

| Alternative | Why it lost |
|-------------|-------------|
| Derived ids for seeded reference rows | Needs a stable cross-device owner identity. `user_id` is per-device by construction; nothing else identifies the person on the wire. |
| Adopt the peer's id — rewrite the local row's primary key | Every local row already pointing at the old id would have to be rewritten in the same transaction, on a schema where those references are enforced. A wider blast radius than the problem. |
| Stop syncing independently-seeded tables | The parent stops colliding, but the **child** still names the peer's id for it. Translation is unavoidable; this only hides where. |
| Leave it — accept the collision as idempotent | This is the status quo the finding describes. Its worst property is not the loss but the silence: a device reported no error while a feature's data was simply absent. |

## Consequences

### Positive

- A silent, unbounded data loss between independently-set-up devices becomes a
  resolved reference. Verified on the pair that exhibited it: 3 aliases recorded,
  tax tags 0 → 19 against the peer's 19, and the quarantine 89 rows → empty.
- The rule is derived, not enumerated. The twin is found through the table's own
  unique indexes and the foreign keys through the live schema, so a column added
  later is covered without anyone remembering the mechanism exists.

### Negative

- **A new durable table on every device**, holding one row per reconciled id per
  peer. Small and bounded by reference-data volume, but it is state that must be
  migrated and reasoned about.
- **The mapping is local.** Each device holds its own half, so the same logical
  row has two identities that only ever meet inside an applier. Anything reading
  the op log directly sees the peer's id and must translate.
- A create refused for a genuinely duplicate natural key is now indistinguishable
  from a second identity, because at that point they are the same thing.

### Neutral

- Nothing changes for rows one device creates and another receives, which is the
  overwhelming majority of what crosses.

## Revisit if

- A stable cross-device identity for a person appears in the sync contract. That
  would make derived ids viable for seeded reference rows and could retire the
  alias for that class — though not for rows that collide on a natural key for
  any other reason.

## Related

- [ADR-0014](0014-op-log-crdt-merge-engine.md) — the op log whose identity model
  this completes
- [ADR-0015](0015-multi-master-p2p-sync.md) — no central id allocator, which is
  why two devices can mint different ids for one row
- [E1 change capture](../../10-functional/features/e-sync/e1-change-capture.md) —
  E1-R13 and E1-R17, the quarantine this stops filling
