# D1 — Envelope (zero-based) budgeting

**Status:** Accepted · **Area:** D — Money management

---

## Purpose

A monthly spending ceiling per category tells you when you have gone too far. It
does not tell you whether you can afford the thing in front of you, because it
never asked where the money was coming from.

Envelope budgeting does: every unit of income is assigned to a category before
it is spent, balances roll forward, and the question becomes "is there money in
this envelope" rather than "have I exceeded an average".

This replaced both the flat per-category ceiling and category-linked savings
pots — see
[ADR-0017](../../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md).

## Behaviour

### Assign every unit

A monthly grid lists every live expense category with an amount assigned for
that month. Above it sits **ready to assign**: income received minus everything
assigned. The month is budgeted when it reaches zero.

The ready-to-assign figure is never blocking. It can be negative — the user has
assigned more than they have — and the interface says so plainly rather than
refusing the assignment. Refusing would be the tool overriding the person.

### Balances roll forward

An envelope's availability is its assignment, plus what carried in, plus net
money moved in, minus what was spent.

Carryover is computed by walking forward from an **activation anchor** — the
moment the user switched envelopes on — rather than from the beginning of
history. Every input is read fresh from the current ledger on every computation
and nothing is stored incrementally, which is what makes the whole model
idempotent by construction: re-importing an unchanged file, or editing a past
transaction, or splitting one, produces a correct fold rather than a drifting
one.

The walk is bounded so it never runs more than a fixed number of periods past
the present.

### Overspending is a choice

A negative envelope resolves one of two ways, per envelope:

- **Reduce to budget** (default): the shortfall is debited from the
  ready-to-assign pool once, and the envelope starts the next month at zero.
- **Carry negative**: the negative balance rolls forward untouched and the pool
  is not touched.

Both are honest. The default matches what most people mean by "I overspent, I'll
absorb it".

### Moving money between envelopes

A move writes a paired debit and credit sharing a correlation identifier, in one
transaction, so an undo can match them deterministically. Moves never change the
total assigned and never touch the pool.

There is **deliberately no balance guard** on a move: taking a source envelope
negative is a legitimate zero-based budgeting operation, and blocking it would
force the user to do the same thing in two steps.

Recent moves are undoable; an undo hard-deletes both rows of the pair.

### Every live category appears

The grid iterates every live expense category, not only those with an assignment
row. An unassigned category that has spending shows as overspent against zero,
which is the truth, rather than being invisible.

### Copy last month

Where the selected month has no assignments and the previous month has some,
the grid offers to copy them. It is offered, never applied automatically.

### Zero is a deletion

Setting an assignment to zero **deletes** the row rather than storing a zero.
The two converge differently under per-field merge
([E1](../e-sync/e1-change-capture.md)): a deletion and an edit-to-zero are
different intents, and storing the wrong one produces the wrong answer after a
sync.

### Currency scope

Envelopes are single-currency. Spend settled in another currency is surfaced
separately as "spend not shown here" rather than folded in, because folding
would require a conversion the budget did not ask for.

### Activation is a one-way cutover

Switching to envelopes archives every active category-linked pot, releasing each
balance to its account's unallocated pool, and stamps the activation anchor.
Goal-linked pots are untouched.

Activation is idempotent per user: the anchor is claimed atomically before the
pot walk, and a walk that fails part-way un-claims the user so a re-run is safe.

Onboarding seeds a first month's assignments, because an empty grid is not a
useful starting state.

### Over-budget nudges

An hourly pass compares each envelope's spend against its own notify threshold
and raises a nudge ([C8](../c-insight/c8-notifications.md)) when it crosses. The comparison
is integer arithmetic throughout and guards a zero or negative budget base —
nothing can be "over" a budget of nothing.

The pass reads the same live model the grid does, never a legacy path.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Before activation | Every figure is zero; the fold short-circuits. |
| A negative ready-to-assign | Shown plainly; never blocking. |
| A move that takes the source negative | Allowed. |
| A category with spending and no assignment | Shown as overspent against zero. |
| Non-base-currency spend | Surfaced separately, never folded into the envelope total. |
| A zero budget base at nudge time | Guarded; no nudge. |
| A failed activation walk | The user is un-claimed; a re-run is safe. |
| Setting an assignment to zero | The row is deleted, not zeroed. |
| Navigating far into the future | Bounded by the walk ceiling. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **D1-R1** | A monthly grid MUST list every live expense category with its assigned amount. |
| **D1-R2** | A ready-to-assign figure MUST show income minus total assigned for the month. |
| **D1-R3** | Ready-to-assign MUST be allowed to go negative and MUST NOT block assignment. |
| **D1-R4** | Envelope availability MUST be assignment plus carried-in plus net moved minus spent. |
| **D1-R5** | Carryover MUST be computed by walking forward from an activation anchor, not from the beginning of history. |
| **D1-R6** | Every input MUST be read fresh on each computation; no incremental balance may be stored. |
| **D1-R7** | The carryover walk MUST be bounded to a fixed number of periods past the present. |
| **D1-R8** | Each envelope MUST support both reduce-to-budget and carry-negative overspend handling, with reduce-to-budget as the default. |
| **D1-R9** | Reduce-to-budget MUST debit the pool once for the shortfall and reset the carry to zero. |
| **D1-R10** | Carry-negative MUST roll the negative forward and MUST NOT touch the pool. |
| **D1-R11** | A move MUST write a paired debit and credit sharing a correlation identifier in one transaction. |
| **D1-R12** | A move MUST NOT change total assigned and MUST NOT touch the pool. |
| **D1-R13** | A move MUST NOT be blocked by a balance guard. |
| **D1-R14** | Undoing a move MUST remove both rows of the pair. |
| **D1-R15** | The grid MUST include categories that have spending but no assignment. |
| **D1-R16** | Copy-last-month MUST be offered only where the current month has no assignments and the previous month has some, and MUST NOT apply automatically. |
| **D1-R17** | Setting an assignment to zero MUST delete the row rather than storing zero. |
| **D1-R18** | Envelope figures MUST be single-currency; other-currency spend MUST be surfaced separately and never folded in. |
| **D1-R19** | Activation MUST archive every active category-linked pot, releasing balances to unallocated, and MUST leave goal-linked pots untouched. |
| **D1-R20** | Activation MUST stamp an anchor claimed atomically before any pot is touched. |
| **D1-R21** | A failed activation walk MUST un-claim the user so a re-run is safe. |
| **D1-R22** | Onboarding MUST seed a first month's assignments. |
| **D1-R23** | Category identifiers supplied by the client MUST be re-validated server-side before any write. |
| **D1-R24** | Envelope mutations MUST be captured for sync, and assignment deletions MUST be captured as deletions. |
| **D1-R25** | An over-budget nudge MUST use integer arithmetic and MUST guard a zero or negative budget base. |
| **D1-R26** | The nudge pass MUST read the same live model the grid reads. |
| **D1-R27** | The period identity used in nudges MUST be computed identically on every device. |
| **D1-R28** | Cross-user reads and writes MUST return not-found. |

## Related

- [ADR-0017](../../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)
- [B7 Split transactions](../b-ledger/b7-splits.md) — the hard prerequisite
- [D3 Savings pots](d3-pots.md) — what changed
- [A8 Migration importers](../a-ingestion/a8-migration-importers.md) — imports into this model
- [C8 Notifications](../c-insight/c8-notifications.md) · [C1 Dashboard](../c-insight/c1-dashboard.md)
