# B6 — Self-transfer pairing

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

Moving money between your own accounts is not spending. Shown as two unrelated
rows it inflates both income and expenditure, corrupts every category total, and
makes a month look like it had a windfall and a disaster in the same week.

This feature pairs the two legs so the dashboard treats them as one internal
movement.

## Behaviour

### A deterministic matcher

Two legs pair when all of the following hold:

- Same user.
- Equal and opposite amounts, in the same currency.
- Booking dates within a fixed window of each other.
- Both typed as transfer, in opposite directions.
- Neither already paired.

The matcher has no per-instance state and no dependence on the time of day
beyond the calendar-day comparison, so the same inputs always produce the same
decision.

### Identifier reconciliation walks both ways

The firing leg may carry the identifier of one of the user's own accounts —
the forward case. Or it may carry none, in which case the partner's identifier
is resolved through the alias bridge — the reverse case. Both directions are
walked, because which leg fires first depends on file order, which the user
controls and beatrax does not.

Under at-rest encryption the forward arm decrypts the firing leg's identifier
once; the reverse arm narrows candidates on plaintext dimensions first and
decrypts only the survivors.

### Both legs are written, atomically

A successful pair writes the pointer on each leg pointing at the other, inside
one transaction. A partial pair cannot land.

Re-running the matcher for an already-paired row is a no-op.

### Two contexts, one matcher

The matcher runs per-row as transactions are imported, and as a bulk
orphan sweep during the chain-resolution pass. The sweep exists because the
per-row pass necessarily misses the case where the partner account did not exist
yet.

The sweep runs **after** the retyping healing pass in
[B5](b5-chain-resolution.md), so it operates on a corrected ledger.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Legs in different currencies | No pair. An accepted trade-off: the amounts are not equal-and-opposite in any single currency. |
| Dates outside the window | No pair. |
| Three legs of the same amount inside the window | A deterministic order picks the closest in time; the third stays unpaired. |
| A re-imported row whose fingerprint already exists | The per-row listener never fires, because no row was recorded. |
| Account A uploaded before account B exists | The per-row pass misses; the orphan sweep catches it afterwards. |
| A paired row later reclassified to a non-transfer type | The pair is broken — the assertion is no longer true ([B1](b1-transactions.md)). |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B6-R1** | The matcher MUST be deterministic: the same inputs MUST produce the same decision. |
| **B6-R2** | The matcher MUST be the only sanctioned writer of the transaction pair pointer for self-transfers. |
| **B6-R3** | Pairing MUST require the same user, equal and opposite amounts in the same currency, booking dates within the window, both legs typed as opposite transfer directions, and neither already paired. |
| **B6-R4** | Both legs MUST be written bidirectionally inside one transaction; a partial pair MUST NOT be able to land. |
| **B6-R5** | Re-running the matcher for an already-paired row MUST be a no-op. |
| **B6-R6** | Identifier reconciliation MUST walk both the forward and the reverse direction. |
| **B6-R7** | Under at-rest encryption, candidate narrowing MUST use plaintext dimensions before decrypting survivors. |
| **B6-R8** | The bulk orphan sweep MUST run after the retyping healing pass. |
| **B6-R9** | A partner lookup for an unpaired row MUST return nothing rather than a guess. |
| **B6-R10** | Cross-user rows MUST be invisible to the matcher. |
| **B6-R11** | Legs in different currencies MUST NOT pair, and the limitation MUST be documented rather than silently absent. |

## Related

- [B1 Transactions and the ledger](b1-transactions.md) — the pair pointer's owner
- [B5 Funding-chain resolution](b5-chain-resolution.md) — the other pointer writer, and the sweep's host
- [C1 Dashboard](../c-insight/c1-dashboard.md) — why this matters to the totals
