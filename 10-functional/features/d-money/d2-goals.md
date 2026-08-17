# D2 — Savings goals

**Status:** Accepted · **Area:** D — Money management

---

## Purpose

A savings goal is a target amount by a target date. The value Beatrax adds is
not the target — anyone can write that down — but the honest answer to "will I
make it", derived from what the user is actually saving rather than what they
intended to.

## Behaviour

### A goal is a name, an amount, a date

Optionally backed by a savings pot ([D3](d3-pots.md)). Lifecycle: create, edit,
mark complete, archive, restore.

A goal is **not** linked to an account. It once was, and the link was withdrawn
because it could not answer the question it appeared to answer — see
[Contribution progress](#contribution-progress-belongs-to-one-goal).

### The currency is fixed at creation

A goal's currency is set when it is created and **never changes** — deliberately
not the user's current base currency, which they may change later. Both the
contribution total and the target are always expressed in that same fixed
currency, so the percentage complete stays internally consistent even if the
base currency diverges afterwards.

### Contribution progress belongs to one goal

**A linked pot**, preferred: the pot's current balance, converted into the
goal's currency where they differ. Pot balances for all of a user's goals are
loaded in one batch, never one query per goal.

**Otherwise**, the sum of the transactions the user explicitly attributed to
that goal, converted into the goal's currency.

Progress was once the sum of credits on a linked account posted on or after the
goal's start date. That figure belonged to no goal in particular: two goals over
one account reported the same number, and any target below a month's income read
as reached the moment a salary landed. Both sources above name a single goal,
which is the property the account sum lacked.

A goal with neither a pot nor an attribution reports zero contributed. That is
honest — nothing has been designated as going toward it.

The completion fraction is a ratio of two integer minor-unit amounts, never a
conversion of money to a floating-point number.

### Attribution is explicit, and recorded beside the transaction

A transaction is attributed to a goal on the transaction detail screen, beside
the category, split and counterparty pickers — the one screen where a
transaction is assigned to anything.

The attribution is a row in a pivot, not a column on the transaction: the
transactions table is hot and heavily synced and stays untouched, and one
transaction may fund more than one goal without a further schema change.

The pivot carries **no amount of its own**. The funded figure is always read
back through the joined transaction, so an edited or FX-restated amount can
never drift from its attribution.

An attribution is idempotent — unique on the goal and the transaction together —
so a double submission, or the same operation replayed from a peer device,
inserts once rather than twice.

Attribution is the one mutator on that screen **not** behind the reconciled
lock. It writes a separate row and leaves the reconciled transaction untouched,
and a reconciled row is exactly the confirmed money a goal wants to count.

Attributions are covered by change capture
([E1](../e-sync/e1-change-capture.md)) as an append-only table — created and
deleted, never updated — so an attribution made on the desktop reaches the
phone. The rows carry no content of their own, so they add nothing to the
sensitive-field registry.

### The projection is deliberately cautious

A projected finish date is derived from a trailing contribution run-rate. The
rate measures pot movements for a pot-backed goal, and attributed transactions
otherwise — the same two sources as the progress figure, never an account's
overall credits:

- The trailing window is clamped to the goal's own start date if the goal is
  younger than the window, and the rate divides by the **actual** elapsed
  observation window rather than the nominal one — otherwise a young goal is
  systematically understated.
- With fewer than a week of observation history the projection is **suppressed
  entirely**. Extrapolating a one-day deposit produces a misleadingly soon
  finish, and a wrong date is worse than no date.
- A zero or negative rate — no history, or net outflow — suppresses it too.
- Beyond the forecast horizon the projection is reported as extrapolated and
  lower-confidence rather than presented as equivalent to a near-term one.
- Within the horizon, the forecast is consulted as a **sanity signal only**,
  never as the source of the contribution figure — a forecast point is an overall
  balance trajectory, not goal-specific saving.

A goal already at or past its target has no projected date.

### Writes re-assert ownership

Every mutation checks ownership against the explicitly passed user rather than
relying on an ambient scope, because the ambient scope is a no-op in background
and command-line contexts.

A missing or foreign goal identifier resolves to nothing: an edit raises, and the
three lifecycle actions silently no-op — the background-safe convention.

Attaching or detaching an attribution checks **both** sides against that user:
a goal belonging to someone else is not offered and not accepted, and neither is
a transaction belonging to someone else.

### Status has exactly one write surface

The three lifecycle actions are the only things that set status. Create and edit
never accept a status from the caller, so a form field can never smuggle an
arbitrary value.

Creating always creates a fresh record rather than upserting on a natural key: a
same-name, same-day goal must not silently collapse into one.

### Linking is atomic

A create or edit that touches the pot link performs the goal write and the pot
link in **one transaction**. A failed link — a pot already claimed, a pot
belonging to another user, a pot linked to a category — rolls the goal write
back too.

A pot may back at most one goal. The pot picker excludes pots already claimed,
except the one currently linked to the goal being edited, resolved through a
single shared query so the two branches cannot drift apart. It is no longer
narrowed by a chosen account, because a goal no longer has one.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A goal with no pot and no attributions | Zero contributed; no projection. |
| A goal carried over from the account-linked model | Zero contributed. The old figure was never meaningful, so it is not backfilled. |
| The same transaction attributed twice | One attribution. |
| An attributed transaction later edited or FX-restated | The goal follows the new amount; the pivot holds none. |
| An attributed transaction deleted | The attribution goes with it. |
| A reconciled transaction | Still attributable. |
| A goal or transaction belonging to another user | Neither offered nor accepted. |
| A goal at or past target | No projected date. |
| Fewer than a week of history | Projection suppressed. |
| A zero or negative contribution rate | Projection suppressed. |
| A projection beyond the horizon | Reported as extrapolated and lower-confidence. |
| A missing goal on a lifecycle action | Silent no-op. |
| A missing goal on an edit | Raises. |
| A same-name, same-day goal | Two goals. |
| An account identifier the user does not own | Rejected. |
| A pot already backing another goal | Rejected; the goal write rolls back with it. |
| The base currency changed after creation | The goal keeps its own currency. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **D2-R1** | A goal MUST carry a name, a target amount, and a target date. |
| **D2-R3** | A goal's currency MUST be fixed at creation and MUST NOT follow later changes to the base currency. |
| **D2-R4** | Both the contribution total and the target MUST be expressed in the goal's own currency. |
| **D2-R5** | Where a pot backs the goal, its balance MUST be the contribution source, converted where currencies differ. |
| **D2-R6** | Pot balances MUST be loaded in one batch for all of a user's goals. |
| **D2-R8** | A goal with neither a pot nor an attribution MUST report zero contributed. |
| **D2-R9** | The completion fraction MUST be a ratio of integer minor-unit amounts, never derived from a floating-point money conversion. |
| **D2-R10** | The projection MUST divide by the actual elapsed observation window, not a nominal one. |
| **D2-R11** | Fewer than a week of observation history MUST suppress the projection entirely. |
| **D2-R12** | A zero or negative contribution rate MUST suppress the projection. |
| **D2-R13** | A goal at or past its target MUST have no projected date. |
| **D2-R14** | A projection beyond the forecast horizon MUST be reported as extrapolated and lower-confidence. |
| **D2-R15** | The forecast MUST be consulted only as a sanity signal, never as the contribution figure. |
| **D2-R16** | Every mutation MUST re-assert ownership against the explicitly passed user rather than an ambient scope. |
| **D2-R17** | An edit against a missing or foreign goal MUST raise; a lifecycle action MUST silently no-op. |
| **D2-R18** | Status MUST be settable only by the three lifecycle actions; create and edit MUST NOT accept a caller-supplied status. |
| **D2-R19** | Creating a goal MUST always create a new record; a same-name, same-day goal MUST NOT collapse into one. |
| **D2-R21** | A goal write and its pot link MUST commit as one transaction; a failed link MUST roll the goal write back. |
| **D2-R22** | A pot MUST back at most one goal. |
| **D2-R23** | A pot already linked to a category MUST be rejected as a goal target. |
| **D2-R24** | The pot picker MUST exclude already-claimed pots except the one currently linked to the goal being edited, resolved through a single shared query. |
| **D2-R25** | A goal MUST NOT carry an account link, and MUST support being optionally backed by a savings pot. |
| **D2-R26** | Without a pot, contributions MUST be the sum of the transactions explicitly attributed to that goal. |
| **D2-R27** | An attribution MUST be recorded in a pivot rather than a column on the transaction, leaving the transactions table unchanged. |
| **D2-R28** | The attribution record MUST carry no amount; the funded figure MUST be read back through the joined transaction, so a later edit or FX restatement cannot drift from it. |
| **D2-R29** | Attaching or detaching an attribution MUST validate that both the goal and the transaction belong to the passed user. |
| **D2-R30** | An attribution MUST be unique on the goal and transaction together, so a double submission or a replayed peer operation inserts once. |
| **D2-R31** | Attribution MUST remain available on a reconciled transaction, unlike the other mutators on that screen. |
| **D2-R32** | Attributions MUST be covered by change capture as an append-only table — created and deleted, never updated — and MUST add no sensitive fields. |
| **D2-R33** | The projection run-rate MUST measure pot movements for a pot-backed goal and attributed transactions otherwise, never an account's overall credits. |

## Related

- [D3 Savings pots](d3-pots.md) — the preferred contribution source
- [B1 Transactions](../b-ledger/b1-transactions.md) — where attribution happens
- [E1 Change capture](../e-sync/e1-change-capture.md) — attributions sync
- [C5 Forecasting](../c-insight/c5-forecasting.md) — the sanity signal
- [B10 Multi-currency](../b-ledger/b10-multi-currency.md)
- [C1 Dashboard](../c-insight/c1-dashboard.md) — the nearest-finishing card
