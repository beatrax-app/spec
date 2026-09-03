# ADR-0029: The applier enforces the writer's sum invariant, and refuses rather than resolves

**Status:** Accepted
**Date:** 2026-09-03

## Context

[ADR-0028](0028-a-split-leg-carries-its-own-identity.md) gave every split leg a
`split_uuid` and recorded a negative it did not fix:

> Two devices that both split one transaction now **consistently double its
> legs**, where the outcome used to depend on where each autoincrement had
> reached.

That was measured, not predicted. A desktop split of 50/30 and a phone split of
40/40 against one 80,00 charge leave **four legs adding to 160,00**, with an
empty quarantine on both devices. Before the uuid the two sets sometimes
collided on a shared autoincrement and one was discarded; the identity removed
the collision and left nothing in its place.

`SaveTransactionSplit` has always required a transaction's legs to add up to it
**exactly** — it refuses any other split outright. The applier had no such rule,
so an invariant the writer enforces on one device was not enforced on the value
arriving from another.

## Decision

**The applier enforces the writer's invariant: a create whose leg would carry a
transaction's legs past the transaction is refused and quarantined as
`split_would_overfill_transaction`.**

Two things the gate must not do, each with a test of its own:

- It must **not** refuse a peer's split for a transaction this device has not
  split. The legs fit, and they apply.
- It must **not** refuse a leg already applied. The row's own id is excluded
  from what is already there, so the idempotent re-apply stays idempotent.

This **reports** the conflict; it does not resolve it. Two devices that both
split one transaction still disagree — each keeps its own legs, and the peer's
arrive quarantined with a reason a person can act on.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Later set wins the whole transaction | The resolution, and still the right end state. It is a decision about how a composite value merges, and it was explicitly not the one taken; making it here as a side effect of fixing a doubling would be deciding it by default. |
| Let both sets land and raise a user-facing alert | Leaves wrong money on the screen and needs the alert copy in twenty-six locales. Refusing keeps the reader's own device correct, which is the property that matters most. |
| Accept the doubling as a known consequence | It is money, shown wrong, with nothing anywhere saying so — the exact failure [ADR-0025](0025-primary-key-collisions-are-quarantined.md) was written to end. |
| Enforce it in the writer instead | The writer already does. The gap was that the applier is a second writer and did not share the rule. |

## Consequences

### Positive

- A transaction's legs always add up to it, whichever device wrote them.
- ADR-0028's negative is closed: the doubling it recorded no longer happens.

### Negative

- A peer's split of an already-split transaction is **lost until someone acts**
  on the quarantine. That is the reported-not-resolved state, and it is the
  reason the set-level rule is still worth making.

### Neutral

- Nothing changes for a transaction split on one device only.

## Revisit if

- The set-level rule is decided. This gate becomes its refusal path rather than
  the whole answer.

## Related

- [ADR-0028](0028-a-split-leg-carries-its-own-identity.md) — the identity that
  made the doubling deterministic, and the negative this closes
- [ADR-0025](0025-primary-key-collisions-are-quarantined.md) — the refusal
  contract this follows
