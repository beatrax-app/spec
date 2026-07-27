# C5 — Cash-flow forecasting and scenarios

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

"Will I be fine until payday" is the question a household actually asks, and no
statement answers it. Forecasting projects the balance forward across every
account, shows where it dips below the line, and lets the user model a change
before making it.

## Behaviour

### Three horizons, per account and combined

Thirty, sixty, and ninety days. The chart shows an aggregate line or per-account
range areas, with confidence bands rather than a single confident line.

The forecast is a **snapshot artefact**. It is computed by a background job,
stored as the result of a run, and read from there. It is never computed inside
a page request — a projection in the request path would make the dashboard's
performance depend on history size.

While a run is in progress the surface says so rather than showing a stale
number as if it were current.

### How a projection is built

1. **Anchor.** The starting balance, resolved per account kind: from the most
   recent statement's closing balance for a bank account, from the most recent
   card statement for a card, from the user-entered opening balance otherwise.
   An account with no anchor at all sums its history from the beginning.
2. **Project.** Each approved recurring series contributes at its expected dates.
   A series with modest variance contributes an envelope around its typical
   amount. A series with high variance **and** enough history contributes
   percentile bands instead, spread across a small jitter window to model timing
   uncertainty.
3. **Route through chains.** A contribution whose series is linked to a funder
   ([B5](../b-ledger/b5-chain-resolution.md)) is re-attributed to the funding
   account, and the next bulk card settlement is synthesised onto the funding
   account. This is what makes the forecast reflect where the money actually
   leaves.
4. **Apply the scenario**, if one is selected.
5. **Fold.** Contributions combine per day into a low, median, and high curve.
   Spreads combine in quadrature, which is correct for independent series and
   understates when several share an underlying cause — a documented limitation.
   Cross-currency contributions convert through the rate the transaction
   recorded; a missing rate **raises** rather than leaking a foreign-currency
   figure into the total.
6. **Detect shortfalls.** Where the projected balance crosses the account's
   buffer, a shortfall window is recorded and an event fires. The buffer is per
   account; zero means any negative balance counts.

Percentiles use linear interpolation between closest ranks — the method every
mainstream statistical tool defaults to — rather than nearest-rank, which
collapses to a single observation on small samples.

The projection is deterministic: the same inputs produce the same curve, jitter
included, because the jitter is derived from a stable per-series seed rather
than randomness.

### Scenarios never touch the ledger

A scenario is a named set of mutations applied **in memory** during projection.
Five kinds are supported: cancel a series, add a one-off, add a recurring item,
change a series's amount, and shift a series's date — the last with a choice of
next occurrence only or all subsequent.

Scenarios read recurring series only to learn cadence and variance. They never
join onto transactions, occurrences, chain links, or card statements, and that
isolation is enforced by architecture test. Deleting a scenario removes it and
its runs and changes nothing else.

A one-off with no account named lands on whichever account carries the most
baseline traffic, with a deterministic tie-break.

Launchpad actions — model this cancellation, model this price change — create
the scenario and its mutation in one transaction, so a half-applied scenario
cannot exist.

### Re-projection is event-driven

Approving, rejecting, or re-detecting a recurring series, dismissing a drift
alert as cancelled, and any scenario change all trigger re-projection. A
scenario change re-projects the baseline and that scenario only, not every
scenario.

### Net worth

Assets minus liabilities per account, using the same anchor resolution, in the
user's base currency. Accounts with no available rate are excluded and named
([B10](../b-ledger/b10-multi-currency.md)).

### Opening-balance overrides warn, they do not block

Setting an opening balance materially different from the statement-derived
anchor raises a warning the user can accept or decline. It is their number to
override.

## States

A forecast run moves `pending` → `running` → `complete` | `failed`, with a
single sanctioned writer.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No recurring series and a zero opening balance | A flat curve at zero; no shortfall windows. |
| A scenario with no mutations | Identical to the baseline. |
| A scenario cancelling everything | The curve stays at the anchor. |
| A worker crash mid-run | The run moves to failed; the next dispatch starts fresh. |
| Re-projection while a run is in progress | A new run is dispatched and replaces the result once complete. |
| A cross-currency contribution with no recorded rate | Raises rather than silently mixing currencies. |
| A card account with no statement and no entered balance | Anchored at zero, avoiding double-counted history. |
| An override far from the statement anchor | Warned, not blocked. |
| A completed run with no series | A flat curve at the anchor for the whole horizon. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C5-R1** | Horizons of thirty, sixty, and ninety days MUST be supported. |
| **C5-R2** | Projection MUST run as a background job; it MUST NOT be computed inside a page request. |
| **C5-R3** | A run in progress MUST be shown as computing rather than displaying a stale figure as current. |
| **C5-R4** | The starting anchor MUST be resolved per account kind, falling back to summing history where no anchor exists. |
| **C5-R5** | A card account with neither a statement nor an entered opening balance MUST anchor at zero. |
| **C5-R6** | A high-variance series with sufficient history MUST contribute percentile bands; others MUST contribute an envelope. |
| **C5-R7** | Percentiles MUST use linear interpolation between closest ranks. |
| **C5-R8** | Contributions MUST be routed to the funding account where a chain link establishes one, and the next bulk settlement MUST be synthesised onto it. |
| **C5-R9** | Daily spreads MUST combine in quadrature, and the independence assumption MUST be documented. |
| **C5-R10** | A cross-currency contribution with no recorded rate MUST raise rather than being folded in. |
| **C5-R11** | Shortfall detection MUST compare against a per-account buffer, where zero means any negative balance. |
| **C5-R12** | Each detected shortfall window MUST be recorded and MUST raise exactly one event. |
| **C5-R13** | Re-detection MUST replace the previous windows for the same account and scenario atomically. |
| **C5-R14** | The projection MUST be deterministic; jitter MUST derive from a stable per-series seed. |
| **C5-R15** | Scenarios MUST be applied in memory and MUST NOT write to the ledger. |
| **C5-R16** | Scenario mutations MUST NOT be joined onto transactions, occurrences, chain links, or card statements, enforced by architecture test. |
| **C5-R17** | The five mutation kinds MUST be supported, including a date shift scoped to the next occurrence or all subsequent. |
| **C5-R18** | A one-off with no account named MUST land on the account with the most baseline traffic, with a deterministic tie-break. |
| **C5-R19** | Launchpad actions MUST create the scenario and its mutation in one transaction. |
| **C5-R20** | Scenario names MUST be unique per user. |
| **C5-R21** | Every scenario lifecycle action MUST raise exactly one event. |
| **C5-R22** | A scenario change MUST re-project the baseline and that scenario only. |
| **C5-R23** | Recurring approval, rejection, re-detection, and drift-dismissed-as-cancelled MUST each trigger re-projection. |
| **C5-R24** | A single state machine MUST be the sole writer of run state. |
| **C5-R25** | An opening-balance override diverging materially from the anchor MUST warn and MUST NOT block. |
| **C5-R26** | Net worth MUST exclude accounts with no available rate and MUST name them. |
| **C5-R27** | Cross-user reads and writes MUST return not-found. |

## Related

- [C2 Recurring detection](c2-recurring.md) — the contribution source
- [C3 Drift alerts](c3-drift-alerts.md) — the cancellation launchpad
- [B5 Chain resolution](../b-ledger/b5-chain-resolution.md) — funder routing
- [C6 Calendar](c6-calendar.md) — the day-level view of the same data
- [A9 Starting balances](../a-ingestion/a9-starting-balances.md) · [B10 Multi-currency](../b-ledger/b10-multi-currency.md)
