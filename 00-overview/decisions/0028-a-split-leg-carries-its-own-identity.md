# ADR-0028: A split leg carries an identity of its own, and the set conflict stays open

**Status:** Accepted
**Date:** 2026-09-03

## Context

[ADR-0026](0026-an-id-two-devices-cannot-both-compute-is-minted.md) gave every
exposed table an id scheme and left exactly one out, with its reason recorded:

> `transaction_splits` is left exposed **with its reason recorded rather than
> quietly passing**. Its rows are the legs of one transaction and their
> `sort_order` is reassigned on every save, so neither answer fits.

Both answers fail there for the same reason: **the table declares nothing two
devices could agree on**. The primary key is an autoincrement, and `sort_order`
is the leg's position in the list the reader last submitted, rewritten on every
save. A derived id over the position moves whenever a leg moves — and a moved id
orphans the `tax_transaction_tags` row that names it.

## Decision

**A split leg carries a `split_uuid`, minted once by the device that adds the
leg and never rewritten, and its row id is derived from that.**

- The uuid is the leg's identity: an edit, a reorder or a re-save leaves it
  alone, so the derived id is stable where `sort_order` is not, and the tax tag
  naming it stays valid.
- Rows written before this keep their autoincrement id. The backfill gives them
  a `legacy:` uuid derived from `(transaction_id, id)` — columns two devices
  that have synced already agree on, so both compute the same value without
  exchanging one. Their **ids are deliberately not rewritten**: rewriting them
  is what would orphan the tax tags.
- The invariant *id = derived(split_uuid)* therefore holds for legs written from
  here on, and not for legs that predate it. Nothing may assume it for all rows.

**The set-level conflict is not resolved by this, and is not resolved anywhere.**
Two devices that both split one transaction while apart still produce two sets of
legs. With an identity per leg those sets no longer collide by accident, so both
land and the legs sum to twice the transaction; before, whether they collided at
all depended on how far each device's autoincrement had run, so the outcome was
merely undefined rather than consistently wrong.

Resolving it needs a rule about the **set**: one save's legs are one value, and
the later save replaces the earlier one entirely. That is a separate decision
about how a composite value merges, and this ADR does not make it.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Derive from `(transaction_id, sort_order)` | The position is not the identity. A reorder moves the id, which orphans the tax tag naming that leg, and two devices whose sets differ in length still disagree. |
| Leave it exposed | The status quo ADR-0026 recorded. It leaves the table with no identity at all, which is worse than an identity that does not yet resolve the set conflict. |
| Resolve the set first and skip the uuid | The set rule needs a stable per-leg identity to express which legs a batch replaced. This is the piece it would have had to build anyway. |

## Consequences

### Positive

- Every covered table now has a way to tell two devices' rows apart, and the
  list of exposed tables is empty and guarded as empty.
- A leg's id survives a reorder, which it did not before even on one device's
  own data.

### Negative

- **Two devices that both split one transaction now consistently double its
  legs**, where the outcome used to depend on where each autoincrement had
  reached. Consistently wrong is easier to find than intermittently wrong, but
  it is not better for a reader who hits it.
- A table holds two kinds of id: derived for new legs, autoincrement for legs
  that predate this.

### Neutral

- Nothing changes for a transaction split on one device only, which is all of
  them until two devices edit one transaction while apart.

## Revisit if

- The set-level rule is decided. That is the open item, and it is the one that
  makes the doubling above go away.

## Related

- [ADR-0026](0026-an-id-two-devices-cannot-both-compute-is-minted.md) — the
  decision that left this table out, and the reason it did
- [ADR-0025](0025-primary-key-collisions-are-quarantined.md) — what happens
  today when two devices' rows do collide
