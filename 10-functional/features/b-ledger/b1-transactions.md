# B1 — Transactions, accounts and the ledger

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

The ledger is the canonical record. Every other feature reads from it, and
almost nothing writes to it. This feature owns what a transaction is, what an
account is, who is allowed to write, and what the user can do with a row once it
is there.

## Behaviour

### One sanctioned writer per concern

There is exactly one sanctioned path into the transactions table, one into the
category column, and one into each of the columns other features own — the
transfer pair pointer, the reconciliation status, the split legs. Every other
module goes through those paths. This is enforced by architecture test, not by
convention.

The result is that "what can change this row, and under what circumstances" is
an answerable question.

### Imported rows are immutable; user-authored rows are not

An imported transaction is a record of what a statement said, and it is not
editable or deletable. What *is* editable is everything Beatrax layered on top:
its category, its counterparty, its note, its tax tag, its split legs, its
reconciliation status.

Cash-book rows ([A7](../a-ingestion/a7-cash-book.md)) are the exception — the
user wrote them, so the user can delete them.

### Money is exact and dual-currency

Every amount is a minor-unit integer plus a currency code, handled as exact
money ([ADR-0009](../../../00-overview/decisions/0009-brick-money-multi-currency.md)).
A transaction preserves both its native amount and its settled amount, plus the
derived rate at high precision — so a foreign-currency charge can always show
both what it cost and what it cost you.

Reading a money column that is absent raises rather than silently returning
zero. A silent zero in a financial total is worse than a crash.

### Transaction type is first-class

Income is a type, not a negative expense. The type set covers income, expense,
the two transfer directions, refunds, fees, and adjustments, and it is enforced
at the database layer as well as the application layer — so an application-level
typo fails loudly rather than writing an unknown value.

Type classification happens at import: already-classified rows pass through
untouched; cross-account movements are detected by two independent
identifier checks; a payment-processor event map applies where the source has
one; and a positive amount that is none of the above is income.

### The month is the user's month

The period boundary is a per-user setting, not the calendar month. A user whose
salary lands on the 25th can define their month as the 25th to the 24th, and
every period total honours that.

### The dashboard aggregate is one read

The "this period at a glance" figures — in, out, net, top categories,
next settlement, email-scan health — resolve in a single read rather than a
query per tile. The income rule is subtractive: it filters by type, never by
amount sign, and excludes transfers, refunds, fees, and adjustments.

### Browsing

The transaction list defaults to a recent window with an explicit
"show full history" toggle, uses cursor pagination on a stable ordering, and
caps accumulated rows on infinite-scroll surfaces so a phone does not accumulate
an unbounded list.

The detail page offers reclassification, notes, splits, tax tagging, the chain
drawer, and — for user-authored rows — deletion. Reclassifying a paired row to a
non-transfer type breaks the pair, because the pair asserted something that is
no longer true.

### Accounts

An account has a kind — bank, card, payment processor, cash — a currency, a
starting balance, and a display name. Card and processor accounts carry
synthetic identifiers because their source formats have no real one. Account
naming happens inline during import ([A2](../a-ingestion/a2-import-wizard.md)),
and a name is turned into a slug with enough of the identifier appended to make
collisions improbable.

### Categories and merchants

Categories are per-user and seeded from a shared default tree on first install.
A merchant dictionary supports the categoriser's memory layer
([B2](b2-categorisation.md)).

## States

A transaction's reconciliation status is owned by
[B8](b8-reconciliation.md): `uncleared` → `cleared` → `reconciled`, with
un-reconcile returning to cleared.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A row with no category or counterparty | Valid. Both are optional; the row surfaces in the relevant triage queue. |
| Two imports racing on the same fingerprint | The insert-on-conflict path serialises them; one row results. |
| A money column absent when read | Raises. There is no silent zero. |
| An unknown transaction type reaching the database | Rejected at the database layer. |
| An empty period | Totals return zero money, not null. |
| Reclassifying a paired transaction to a non-transfer type | The pair is broken. |
| A reconciled row | Locked against every mutating action. |
| An account with a duplicate display name | The slug carries enough of the identifier to disambiguate. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B1-R1** | Exactly one sanctioned path MUST exist by which a transaction is created, and it MUST be enforced by architecture test. Each column another feature owns — category, counterparty, type, reconciliation status, pair pointer, split legs — MUST have exactly one sanctioned writer of its own, named by that feature's requirements. |
| **B1-R2** | The category column MUST have exactly two sanctioned writers: the category writer for every assignment, and the split writer for the un-split survivor (B7-R9). Every other caller MUST route through the category writer. |
| **B1-R3** | The columns an import took from its source — amounts, currencies, dates, description, source identifiers — MUST NOT be editable, and an imported transaction MUST NOT be deletable. The columns Beatrax layers on top — category, counterparty, note, tax tag, split legs, type, reconciliation status, pair pointer — remain writable through their own sanctioned writers. |
| **B1-R23** | A user-authored transaction MUST be deletable by its owner unless it is reconciled, where deletion is refused like every other edit (B8-R9). |
| **B1-R4** | Every monetary value MUST be stored as a minor-unit integer plus a currency code and handled as exact money. |
| **B1-R5** | A transaction MUST preserve both its native and settled amounts, and the derived rate where they differ. |
| **B1-R6** | Reading an absent money column MUST raise; it MUST NOT return zero. |
| **B1-R7** | Transaction type MUST be a closed set enforced at the database layer as well as the application layer. |
| **B1-R8** | Income MUST be a first-class type determined by classification, never inferred from amount sign alone at aggregation time. |
| **B1-R9** | The period boundary MUST be a per-user setting, and every period total MUST honour it. |
| **B1-R10** | The period-at-a-glance aggregate MUST resolve in a single read. |
| **B1-R11** | The income rule in aggregates MUST filter by type and MUST exclude transfers, refunds, fees, and adjustments. |
| **B1-R12** | The transaction list MUST default to a bounded recent window with an explicit full-history toggle. |
| **B1-R13** | List pagination MUST use a cursor over a stable ordering. |
| **B1-R14** | Infinite-scroll surfaces MUST cap accumulated rows. |
| **B1-R15** | Reclassifying a paired transaction to a non-transfer type MUST break the pair. |
| **B1-R16** | A reconciled transaction MUST refuse every user-initiated edit of its own fields — re-categorising, notes, splitting, tax tagging, reclassification, and deletion. |
| **B1-R17** | An account MUST carry a kind, a currency, a starting balance, and a display name. |
| **B1-R18** | Accounts whose source format carries no real identifier MUST receive a synthetic one. |
| **B1-R19** | An account slug MUST incorporate enough of the account identifier to make collisions improbable. |
| **B1-R20** | Categories MUST be per-user, seeded from a shared default tree on first install. |
| **B1-R21** | Cross-user reads and writes MUST return not-found, never forbidden. |
| **B1-R22** | Every user-scoped query MUST filter by user explicitly where it can run outside an authenticated request. |

## Related

- [A2 Import preview and confirm](../a-ingestion/a2-import-wizard.md) — the main writer
- [A7 Cash book](../a-ingestion/a7-cash-book.md) — the user-authored writer
- [B2 Categorisation](b2-categorisation.md) · [B7 Splits](b7-splits.md) · [B8 Reconciliation](b8-reconciliation.md)
- [B10 Multi-currency](b10-multi-currency.md)
- [ADR-0008](../../../00-overview/decisions/0008-multi-user-belongstouser.md) · [ADR-0009](../../../00-overview/decisions/0009-brick-money-multi-currency.md)
- [20-architecture/data-model.md](../../../20-architecture/data-model.md)
