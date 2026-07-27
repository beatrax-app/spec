# B7 — Split transactions

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

A single shop visit is rarely a single category. Eighty units at a supermarket
might be sixty of groceries and twenty of household goods. Counting all eighty
against groceries makes the grocery budget wrong and the household budget
useless.

Splits let one transaction carry several category legs. They are the hard
prerequisite for honest envelope budgeting
([ADR-0017](../../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)),
which is why they shipped first.

## Behaviour

### Legs sum exactly to the parent

A split has two or more legs whose signed amounts sum **exactly** to the parent's
amount. Exactly, with no rounding drift — the arithmetic is exact money
([ADR-0009](../../../00-overview/decisions/0009-brick-money-multi-currency.md)),
so exactness is achievable rather than aspirational.

The invariant is re-checked inside the write transaction, not only at validation
time, so a concurrent edit cannot slip a violating state through the gap.

Every leg must be non-zero and share the parent's sign. A leg of zero is noise;
a leg of the opposite sign is a refund, which is a different thing.

### Roll-ups count legs, never both

Every category roll-up — the dashboard breakdown, budget spend, reports, the tax
export — counts the legs of a split and **not** the parent. A split that counted
both would double the money.

Where a split is somehow broken — legs that do not sum — the roll-up falls back
to the parent's own category rather than reporting a wrong total. Fail-safe
rather than fail-silent.

### Editing preserves identity

Saving a split diffs the existing legs and applies a targeted update, delete,
and insert. It does not delete everything and re-insert, because that would
destroy each leg's identity — and identity is what the merge layer resolves
conflicts against ([E1](../e-sync/e1-change-capture.md)).

### The editor is honest about arithmetic

Amounts are entered as absolute values with the sign implied by the parent. A
live remaining figure shows what is still unallocated, and the save is gated on
it reaching zero. There is no "close enough".

Un-splitting removes every leg and returns the transaction to its own category.

### Legs carry their own metadata

Each leg has its own category, its own note, and its own tax tag. A split where
part is deductible and part is not exports the deductible part only — see
[D4](../d-money/d4-tax.md).

### Scope

Splits apply to non-transfer transactions. A transfer is already two legs of one
movement; splitting one of them is not a meaningful operation.

### Interactions

- **Re-import** of the same source transaction does not disturb the split. The
  parent deduplicates on its fingerprint; the legs are user-authored and are not
  part of it.
- **The rules engine** skips split transactions entirely on re-apply
  ([B3](b3-rules-engine.md)) — the legs carry the categories, so applying a rule
  to the parent would contradict them.
- **Deleting** a user-authored parent tombstones the parent and every leg.
- **Sync** captures leg mutations like any other change.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Legs that do not sum to the parent | Save refused; the remaining figure shows the shortfall. |
| A zero-amount leg | Refused. |
| A leg with the opposite sign to the parent | Refused. |
| A single leg | Refused — that is not a split. |
| Re-importing the split transaction's source | The split survives untouched. |
| A rules re-apply touching a split transaction | Skipped. |
| A broken split at roll-up time | Falls back to the parent's own category. |
| A reconciled transaction | Splitting is locked like every other mutation ([B8](b8-reconciliation.md)). |
| Deleting a user-authored split parent | Parent and legs are tombstoned together. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B7-R1** | A split MUST have two or more legs whose signed amounts sum exactly to the parent amount. |
| **B7-R2** | The sum invariant MUST be re-checked inside the write transaction, not only at validation time. |
| **B7-R3** | Every leg MUST be non-zero and MUST share the parent's sign. |
| **B7-R4** | Category roll-ups MUST count a split's legs and MUST NOT count the parent. |
| **B7-R5** | A split whose legs do not sum MUST roll up via the parent's own category rather than producing a wrong total. |
| **B7-R6** | Saving a split MUST apply an identity-preserving diff, never delete-all-then-reinsert. |
| **B7-R7** | Amounts MUST be entered as absolute values with the sign implied by the parent. |
| **B7-R8** | The save MUST be gated on the unallocated remainder reaching exactly zero. |
| **B7-R9** | Un-splitting MUST remove every leg and restore the parent's own category. |
| **B7-R10** | Each leg MUST support its own category, note, and tax tag. |
| **B7-R11** | Splits MUST apply only to non-transfer transactions. |
| **B7-R12** | Re-importing the source of a split transaction MUST leave the split intact. |
| **B7-R13** | Rule re-application MUST skip split transactions entirely. |
| **B7-R14** | Deleting a user-authored split parent MUST tombstone the parent and every leg. |
| **B7-R15** | Splitting a reconciled transaction MUST be refused. |
| **B7-R16** | Leg mutations MUST be captured for sync like any other change. |
| **B7-R17** | A single split write path MUST exist, and it MUST be the only writer of split legs. |

## Related

- [D1 Envelope budgeting](../d-money/d1-envelope-budgeting.md) — why splits shipped first
- [D4 Tax tagging](../d-money/d4-tax.md) — per-leg deductibility
- [B3 The rules engine](b3-rules-engine.md) · [B8 Reconciliation](b8-reconciliation.md)
- [C7 Report builder](../c-insight/c7-reports.md) — split-aware aggregation
- [ADR-0017](../../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)
