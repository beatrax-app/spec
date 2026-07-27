# B5 — Funding-chain resolution

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

This is the capability that makes beatrax different from a per-account ledger
viewer, and it is the one the [vision](../../../00-overview/vision.md) is
written around.

A single monthly subscription can touch four accounts: billed to the payment
processor, funded from a credit card, settled to the bank in one bulk monthly
transfer. Each account's own app shows one leg and calls it the picture. Chain
resolution links them, so from any leg the user can see the whole chain.

## Behaviour

### Two chain shapes

**Funding chains.** A payment-processor charge is two transactions: the
merchant-side debit from the processor balance, and the funding-side debit from
whichever bank account or card the processor pulled from. The resolver links
them.

**Bulk settlements.** A card issuer bills a whole month's card spend as one
transfer from the bank. The bank side shows one anonymous debit for a figure
that matches nothing; the card side shows dozens of merchant lines. The resolver
matches the two and then decomposes the settlement into the individual card
transactions it covered.

### Funding chains resolve in three arms

Each candidate is tried against three arms in order, first match wins:

1. **Deterministic.** The processor's own event record names a withdrawal to an
   account identifier the user owns, and an equal, opposite movement exists on
   that account inside a short date window. Written as confirmed with full
   confidence.
2. **Direct.** The withdrawal record is missing from the export entirely —
   because the user exported only outgoing payments, not the incoming funding
   sweeps. The processor-side charge is matched directly against a bank-side
   transfer whose counterparty identifier resolves, through the alias bridge, to
   the user's processor account, on equal settled amount inside the same window.
   Exactly one match is confirmed; two or more is a candidate with the closest by
   date proposed, so the user resolves the ambiguity. A bank row already cited by
   another chain is excluded, so two same-day same-amount charges cannot both
   claim one debit.
3. **Fuzzy.** A weighted blend of name similarity, amount closeness, and date
   proximity. A score above the floor surfaces as a candidate with a confidence
   **deliberately capped below full**, so the deterministic arm remains the only
   path to a certain link.

Each arm computes the same signature over the pair's identifying properties, so
the learning loop below counts confirmations consistently regardless of which
arm found the match.

### Bulk settlements decompose arithmetically

For each unresolved bank-side transfer whose counterparty identifier resolves to
a card account:

1. Find the card statement whose period end is closest to the transfer's date,
   inside a window, measuring distance precisely rather than in whole days.
2. Take every card charge in that statement's period not already settled.
3. Subtract any credit already carried into the statement.
4. Compute the unaccounted difference between the charges, the carried credits,
   and the transfer.
5. If the difference is inside tolerance — the greater of a small absolute
   amount or a small percentage of the statement — write one confirmed link per
   charge and advance the statement's state. An overpayment records a credit
   carried forward.
6. If it is outside tolerance, write a **candidate with no partner** and a marker
   saying the tolerance was exceeded, for the review queue.

A second pass handles refunds that posted after their statement closed: it
chains each back to the original purchase and carries the credit forward to the
next open statement.

### The learning loop

Confirming a candidate counts against its signature. After three confirmations
of the same signature, every remaining candidate with that signature is promoted
automatically and marked as resolved by the learnt rule.

The user interface distinguishes the three provenances — deterministic,
resolver-suggested-then-confirmed, and learning-loop — so the user knows what
they are looking at. When one confirmation remains before the threshold, the
review queue says so.

Rejecting a pair is per-pair. It does not demote confirmed links and does not
block the counter — but the rejected pair is never proposed again.

### A healing pass, because file order is not controllable

During setup a user may upload a bank export before the account it references
exists. The classifier finds no destination account, the row falls through to a
plain expense or income, and that type persists. Without a healing pass those
rows stay mistyped forever and every resolver iterates an empty set.

A dedicated resolver re-applies the cross-account rule against the now-complete
account graph, retyping affected rows by amount sign. It is idempotent — a
retyped row leaves the candidate set — and self-healing: adding an alias retypes
matching historical rows on the next pass. It runs **before** the two chain
resolvers so they see a corrected ledger.

This is the one documented exception to the read-only contract below.

### Read-mostly by contract

The resolver reads the ledger and writes only its own records, plus the pair
pointer it is explicitly permitted to set. Amounts, dates, descriptions, and
categories are never touched. That is what makes the whole pass safe to re-run,
and it is enforced by architecture test.

### Resolution runs synchronously after import

The pass is dispatched after the import transaction commits, and it runs in the
request rather than on the queue — because it matches against encrypted
identifier columns and the decryption key is only reachable from an unlocked
session. Handing it to a background worker would hand it to a context with no
key.

Running the pass twice is redundant but harmless: it is idempotent.

Every run writes an audit record with its outcome and counts, so a crashed run
is visible rather than silently absent.

### The chain drawer

From any transaction, a drawer shows the chain it belongs to. The walk is
bidirectional — an earlier forward-only walk found nothing half the time,
because clicking the bank-side leg of a funding chain follows the reverse edge —
bounded in depth, and cycle-guarded. Only confirmed and candidate links are
followed. A node with several outgoing settlement links renders as a fan-out
parent with its children paginated.

## States

| Record | States |
|--------|--------|
| Chain link | `candidate` → `confirmed` \| `rejected` |
| Card statement | `open` → `partially_settled` → `settled` \| `overpaid` |
| Resolution run | `pending` → `running` → `complete` \| `failed` |

Each state column has exactly one sanctioned mutator, enforced by architecture
test and by database trigger.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Nothing to resolve | The pass is a no-op; the audit record completes with a zero count. |
| Tolerance exceeded on a settlement | A candidate with no partner and an explicit marker, for review. |
| Two same-amount same-day charges | Exclusion of already-cited rows prevents both claiming one debit. |
| A worker crash mid-run | The audit record stays running; the surface shows the orphan; a manual retry re-dispatches. |
| A linked transaction deleted | The link is removed with it. |
| A hint referencing a not-yet-imported transaction | The hint listener runs after persistence, so the reference always resolves. |
| A hint-shaped record with no partner | Cannot be confirmed; a typed error rather than a database constraint violation. Dismissible. |
| A previously rejected pair | Never re-proposed. |
| An import after a failed pass | A fresh run record is created; the failed one stays as an audit trail. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B5-R1** | The resolver MUST NOT write to the transactions table except the pair pointer and the documented retyping pass, and this MUST be enforced by architecture test. |
| **B5-R2** | Every resolver pass MUST be idempotent: re-running against the same data MUST produce the same links. |
| **B5-R3** | Funding-chain resolution MUST try the deterministic, direct, and fuzzy arms in that order, first match wins. |
| **B5-R4** | Only the deterministic arm may produce a link at full confidence; the fuzzy arm MUST be capped below it. |
| **B5-R5** | A bank-side row already cited as the partner of another non-rejected funding link MUST be excluded from further matches. |
| **B5-R6** | Where the direct arm finds more than one match, the result MUST be a candidate, not a confirmed link. |
| **B5-R7** | All arms MUST compute the same signature over a pair's identifying properties. |
| **B5-R8** | Bulk-settlement decomposition MUST choose the candidate statement by precise date distance, not whole-day truncation. |
| **B5-R9** | A settlement whose unaccounted difference is inside tolerance MUST write one confirmed link per covered charge and advance the statement state. |
| **B5-R10** | A settlement outside tolerance MUST write a candidate with no partner and an explicit tolerance marker. |
| **B5-R11** | An overpayment MUST record a credit carried forward to the next open statement. |
| **B5-R12** | Refunds posting after a statement closes MUST chain to the original purchase and carry a credit forward. |
| **B5-R13** | Three confirmations of one signature MUST promote every remaining candidate with that signature, marked as resolved by the learnt rule. |
| **B5-R14** | The interface MUST distinguish deterministic, confirmed-from-suggestion, and learning-loop provenance. |
| **B5-R15** | Rejecting a pair MUST NOT demote confirmed links and MUST NOT block the confirmation counter, but the pair MUST never be proposed again. |
| **B5-R16** | The retyping healing pass MUST run before the chain resolvers, MUST be idempotent, and MUST NOT touch the pair pointer. |
| **B5-R17** | Resolution MUST be dispatched only after the import transaction commits. |
| **B5-R18** | Resolution MUST run in a context where the at-rest decryption key is available. |
| **B5-R19** | Every run MUST write an audit record; a final-retry failure MUST record the failure with a truncated error. |
| **B5-R20** | Card-statement state MUST have exactly one sanctioned mutator, enforced by architecture test. |
| **B5-R21** | Link state and kind MUST be enforced at the database layer as well as the application layer. |
| **B5-R22** | A link with no partner MUST NOT be promotable; the attempt MUST raise a typed error. |
| **B5-R23** | The chain walk MUST follow edges in both directions, MUST be depth-bounded, and MUST guard against cycles. |
| **B5-R24** | Only confirmed and candidate links MUST be followed by the walk. |
| **B5-R25** | Cross-user reads and writes MUST return not-found. |

## Related

- [ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md) — why identifier columns need decrypting before matching
- [A5 Receipt matching](../a-ingestion/a5-receipt-matching.md) — the source of hints
- [B4 Counterparties](b4-counterparties.md) — the alias bridge
- [B6 Self-transfer pairing](b6-transfers.md) — the other user of the pair pointer
- [C5 Forecasting](../c-insight/c5-forecasting.md) — routes contributions through chains
- [20-architecture/data-flow.md](../../../20-architecture/data-flow.md)
