# C1 — Dashboard and current position

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

The dashboard is the answer to "how am I doing", asked every morning in about
four seconds. It is the screen the product is judged on, and its job is to be
calm: a small number of true figures, the things that need attention, and
nothing that demands a decision before coffee.

## Behaviour

### This period at a glance

In, out, and net for the current period, alongside the top spending categories
and the most recent transactions. The period is the **user's** period, not the
calendar month ([B1](../b-ledger/b1-transactions.md)).

The whole aggregate resolves in one read. Income is determined by transaction
type, never by amount sign, and excludes transfers, refunds, fees, and
adjustments — otherwise moving money between your own accounts reads as a
windfall.

### What needs attention comes first

Alerts, unusual charges, drift, forecast shortfalls, and the counts of things
waiting in triage queues are surfaced above the pleasant numbers. A dashboard
that leads with a nice net figure and buries a subscription that doubled is
lying by omission.

Counts for the navigation badges are computed once per render and cached
briefly, rather than one query per badge. A table that does not exist yet counts
as zero rather than raising.

### Glance cards, not a control panel

A small number of summary cards: ready-to-assign for the budget
([D1](../d-money/d1-envelope-budgeting.md)), nearest-finishing goals
([D2](../d-money/d2-goals.md)), the cash-flow highlight
([C5](c5-forecasting.md)), the next card settlement, email-scan health, and up
to three pinned saved reports ([C7](c7-reports.md)).

Each card either shows a figure or renders nothing. A card that says "no data"
is noise. A card with nothing to show is therefore carried as an *absent* value
rather than as a card of zeroes — the absence is what lets the renderer tell it
from a card whose figure is genuinely zero, which is a fact worth showing.

### One definition of "your position"

Net worth, budget status, upcoming recurring charges, and forecast shortfall
risk compose into a single canonical position summary, read from the other
features' own public surfaces rather than from raw queries against their tables.

That composition is byte-for-byte the same figure the dashboard renders, which
is what lets the periodic digest ([C8](c8-notifications.md)) tell the user
something the dashboard would agree with.

A user with no data still gets a fully-populated summary: every figure, count,
and collection present and zero or empty, never null. The card-shaped members are
the one exception, for the reason above — an absent card is how "render nothing"
is expressed, and collapsing it to a zero-valued card would make that rule
unstatable.

### The digest

A position digest can be emitted daily, weekly, or not at all. Its occurrence key
is derived from an injected clock so two devices computing the same digest agree
on which digest it was. It fires unconditionally on its cadence — there is no
"is anything interesting" gate, because a quiet week is itself information.

### Net worth

Assets minus liabilities, per account and in total, in the user's base currency.
Accounts whose currency has no available rate are excluded and named
([B10](../b-ledger/b10-multi-currency.md)). Internal routing constructs are
excluded from the roll-up entirely.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A brand-new install with no data | Every figure is zero; every collection is empty; cards with nothing to show are absent. |
| A period with no transactions | Zero money, not null. |
| A tampered period parameter | Validated by shape and round-trip, so an impossible date is rejected. |
| A badge whose backing table does not exist yet | Counts as zero. |
| An account with no exchange rate | Excluded from net worth and named. |
| A card with nothing to show | Renders nothing rather than an empty state. |
| A failed background pass | Surfaced as an alert scoped by exact user match, never a broad text match. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C1-R1** | The period figures MUST use the user's configured period, not the calendar month. |
| **C1-R2** | The period aggregate MUST resolve in a single read. |
| **C1-R3** | Income MUST be determined by transaction type and MUST exclude transfers, refunds, fees, and adjustments. |
| **C1-R4** | Items needing attention MUST be surfaced above summary figures. |
| **C1-R5** | Navigation badge counts MUST be computed once per render and briefly cached, not one query per badge. |
| **C1-R6** | A missing backing table MUST count as zero rather than raising. |
| **C1-R7** | A summary card with nothing to show MUST render nothing rather than an empty state, and MUST be carried in the position summary as an absent value rather than as a card of zeroes, so the renderer can tell it from a card whose figure is genuinely zero. |
| **C1-R8** | A single canonical position summary MUST compose net worth, budget status, upcoming charges, and shortfall risk. |
| **C1-R9** | The position summary MUST be composed from other features' public surfaces, never from raw queries against their tables. |
| **C1-R10** | The position summary MUST equal the figure the dashboard renders. |
| **C1-R11** | A user with no data MUST receive a fully-populated summary — every figure, count, and collection present and zero or empty, never null. Card-shaped members are the sole exception and MUST be absent when there is nothing to show, because C1-R7 governs them and an absent card is how it expresses "render nothing". |
| **C1-R12** | The digest cadence MUST support daily, weekly, and off. |
| **C1-R13** | The digest occurrence key MUST be derived from an injected clock so devices agree on identity. |
| **C1-R14** | The digest MUST fire on its cadence unconditionally, with no interestingness gate. |
| **C1-R15** | Net worth MUST exclude accounts with no available exchange rate and MUST name the exclusions. |
| **C1-R16** | Internal routing constructs MUST be excluded from the net-worth roll-up. |
| **C1-R17** | A period parameter supplied in a URL MUST be validated by shape and round-trip. |
| **C1-R18** | Pinned saved reports on the dashboard MUST be capped. |

## Related

- [B1 Transactions](../b-ledger/b1-transactions.md) — the period definition and the aggregate
- [B6 Self-transfer pairing](../b-ledger/b6-transfers.md) — why transfers must be excluded
- [C5 Forecasting](c5-forecasting.md) · [C7 Reports](c7-reports.md) · [C8 Notifications](c8-notifications.md)
- [D1 Envelope budgeting](../d-money/d1-envelope-budgeting.md) · [D2 Goals](../d-money/d2-goals.md)
- [J2 Daily use](../../journeys/j2-daily-use.md)
