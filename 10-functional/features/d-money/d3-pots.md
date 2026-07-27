# D3 — Savings pots

**Status:** Accepted · **Area:** D — Money management

---

## Purpose

One savings account often holds several intentions: the emergency fund, next
year's holiday, the boiler that will eventually fail. Opening a bank account per
intention is administrative overhead nobody wants.

Pots carve one real account balance into named virtual sub-balances, without
moving a unit of real money, and always reconcile back to the real balance.

## Behaviour

### A pot has no stored balance

A pot's balance is the signed sum of its movement rows, computed at read time.
Nothing is stored and incrementally updated, which is precisely why a pot
balance cannot drift out of agreement with its own history.

### The reconciliation invariant

For any account: **real balance equals allocated plus unallocated**, where
allocated is the sum of active pots. Unallocated is computed at read time.

Unallocated can go negative — the user has allocated more than the account
holds. That is surfaced as an over-allocation flag and **never auto-corrected**.
Silently rebalancing someone's savings intentions would be the tool overruling
the person.

### Every operation is a movement row

| Operation | Effect |
|-----------|--------|
| **Fund** | A positive movement. The available unallocated amount is re-read inside the same transaction, so two concurrent funds cannot both consume it. |
| **Withdraw** | A negative movement, checked against the pot's balance. |
| **Transfer** | An atomic pair of movements, within one account only. Both pots must be active, owned, and on the same account. |
| **Archive** | A final releasing movement plus a status change, in the same transaction. An archived pot always reads as zero. |
| **Restore** | No movements. The pot returns empty — and may have lost its goal link if another pot claimed it meanwhile. |

The append-only movement model means a pot's history is its balance, and an
archive genuinely releases the money rather than hiding it.

### Linking

A pot may back a savings goal ([D2](d2-goals.md)), or nothing.

**A pot may no longer be linked to a budget category.** Category-linked pots
were retired when envelope budgeting arrived — see
[ADR-0017](../../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md).
A write that supplies a category link is rejected outright, and the retirement
is a user-visible breaking change requiring the user to re-assign released money
into envelopes.

One pot per goal, enforced on both create and edit.

### Ownership

Every write filters on the explicitly passed user and bypasses the ambient
scope, because the ambient scope is a no-op outside a request. A missing or
foreign pot raises from a write action and silently no-ops from a lifecycle
action.

## States

`active` ↔ `archived`.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Over-allocation | Flagged, never auto-corrected. |
| Two concurrent funds against the same unallocated amount | The in-transaction re-read prevents both succeeding. |
| A withdrawal exceeding the pot balance | Refused. |
| A transfer between pots on different accounts | Refused. |
| Archiving a funded pot | The balance is released to unallocated in the same transaction. |
| Restoring an archived pot | It returns empty, and its goal link may be gone. |
| A write supplying a category link | Rejected. |
| A missing pot on a write | Raises. On a lifecycle action, silent no-op. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **D3-R1** | A pot MUST NOT have a stored balance column; its balance MUST be the signed sum of its movements at read time. |
| **D3-R2** | For any account, the real balance MUST equal allocated plus unallocated, where allocated counts active pots only. |
| **D3-R3** | Unallocated MUST be computed at read time and MUST be allowed to go negative. |
| **D3-R4** | Over-allocation MUST be surfaced and MUST NOT be auto-corrected. |
| **D3-R5** | Every operation MUST be expressed as a movement row; no balance column may be updated. |
| **D3-R6** | Funding MUST re-read the available unallocated amount inside the same transaction. |
| **D3-R7** | A withdrawal MUST be checked against the pot's balance. |
| **D3-R8** | A transfer MUST write an atomic pair of movements and MUST be confined to one account. |
| **D3-R9** | A transfer MUST require both pots to be active, owned by the caller, and on the same account. |
| **D3-R10** | Archiving MUST write a final releasing movement and change status in the same transaction; an archived pot MUST read as zero. |
| **D3-R11** | Restoring MUST write no movements; the pot MUST return empty. |
| **D3-R12** | A pot MUST NOT be linkable to a budget category; such a write MUST be rejected. |
| **D3-R13** | A pot MUST back at most one goal, enforced on both create and edit. |
| **D3-R14** | Every write MUST filter on the explicitly passed user and MUST NOT rely on an ambient scope. |
| **D3-R15** | A missing or foreign pot MUST raise from a write action and MUST silently no-op from a lifecycle action. |
| **D3-R16** | The retirement of category-linked pots MUST be surfaced to upgrading users as a breaking change requiring manual re-assignment. |

## Related

- [ADR-0017](../../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)
- [D1 Envelope budgeting](d1-envelope-budgeting.md) — what replaced the category link
- [D2 Savings goals](d2-goals.md) — the surviving link target
- [J4 Upgrading to v2.0](../../journeys/j4-tax-year-end.md) — the released-balance step
