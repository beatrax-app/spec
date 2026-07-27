# C6 — Bills and cash-flow calendar

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

A forecast curve answers "will I be fine". A calendar answers "what is due on
the 28th, and what will I have left after it". Same data, different question,
and for most people the calendar is the one they act on.

## Behaviour

### A month grid of expected payments

Each day shows the recurring-series entries expected on it, with amount,
direction, account, and counterparty, plus a start-of-day and end-of-day
projected balance.

The calendar is a **read-only composition**. It writes nothing.

### Occurrences are computed by index, not by walking

The k-th occurrence of a series is computed directly from its anchor —
anchor plus k intervals — rather than by stepping a cursor forward or backward
one interval at a time.

Chained stepping permanently loses an end-of-month anchor after the first short
month: the 31st becomes the 28th and never recovers. Index stepping is symmetric,
invertible, and preserves the anchor.

Series with no expected next date — irregular cadence — are excluded entirely.
Occurrences are floored at the series's inception with a small slack, so a
payment expected slightly before its first observed occurrence is not dropped
while phantom pre-inception entries are.

### The balance line is honest about what it knows

**Past days** never depend on a forecast run. Their balance is the real
cumulative sum of transactions, carried forward day by day from a base computed
once for everything before the visible grid.

**Future days** use the forecast ([C5](c5-forecasting.md)). Each included
account's forecast is fetched once, not once per grid day, summed per day and
currency, and converted to the base currency **before** summing across accounts —
minor units are never added across currencies.

A day's start-of-day balance is the previous day's end-of-day, chained forward
**only where the previous value was actually known**. A day following a
data-less day reports its start-of-day as unknown rather than fabricating a
zero.

Internal transfers appear on the grid and net to zero automatically, because
each account's own forecast already contains both legs.

### Past days show what happened

An expected entry on a past day is marked paid when a matching occurrence landed
inside a tolerance window, and missed otherwise. The window is clamped by
cadence: a sub-monthly series uses half its interval, so one payment cannot mark
several adjacent entries paid; monthly and longer keep a full week.

### Two independent account controls

Which accounts' **entries** appear, and which accounts' balances **sum** into
the line, are separate settings. The distinction between never-configured and
explicitly-empty is preserved: never-configured falls back to sensible defaults —
all accounts for entries, spendable accounts for the balance, with card accounts
excluded because their liability already appears via the settlement leg — while
an explicitly empty selection is honoured literally.

Every account identifier supplied by the client is intersected against the
user's own accounts on both read and write.

### Drilling through

A calendar entry drills to its recurring series or its counterparty.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A series with no expected next date | Excluded. |
| A day after a data-less day | Start-of-day shown as unknown, never zero. |
| A month parameter outside the sensible range | Clamped, including against the forecast horizon ceiling. |
| A malformed date in a day selection | Validated by shape and by calendar validity — a shape-only check still admits impossible dates. |
| An end-of-month anchor across a short month | Preserved by index stepping. |
| A payment slightly before a series's first observed occurrence | Included, via the inception slack. |
| Accounts in several currencies | Converted before summing; minor units never added across currencies. |
| A never-configured account preference | Defaults applied and materialised explicitly on first load. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C6-R1** | Each calendar day MUST show its expected entries and a start-of-day and end-of-day projected balance. |
| **C6-R2** | The calendar MUST write nothing. |
| **C6-R3** | Occurrences MUST be computed by index from the series anchor, never by chained stepping. |
| **C6-R4** | Series with no expected next date MUST be excluded. |
| **C6-R5** | Occurrences MUST be floored at the series's inception with a small tolerance slack. |
| **C6-R6** | Past-day balances MUST derive from actual transactions and MUST NOT depend on a forecast run. |
| **C6-R7** | Each included account's forecast MUST be fetched once per render, not once per day. |
| **C6-R8** | Amounts MUST be converted to the base currency before being summed across accounts. |
| **C6-R9** | A day's start-of-day balance MUST chain from the previous day only where that value was known; otherwise it MUST be shown as unknown. |
| **C6-R10** | Internal transfers MUST net to zero on the balance line without special-casing. |
| **C6-R11** | A past-day entry MUST be marked paid or missed against a cadence-clamped tolerance window. |
| **C6-R12** | The tolerance window for a sub-monthly series MUST be at most half its interval. |
| **C6-R13** | Which accounts contribute entries and which contribute balance MUST be independent settings. |
| **C6-R14** | A never-configured preference MUST fall back to a documented default; an explicitly empty selection MUST be honoured literally. |
| **C6-R15** | Card accounts MUST be excluded from the default balance set. |
| **C6-R16** | Client-supplied account identifiers MUST be intersected against the user's own accounts on both read and write. |
| **C6-R17** | Month and year parameters MUST be clamped to a valid range and to the forecast horizon ceiling. |
| **C6-R18** | A date supplied for day selection MUST be validated for calendar validity, not only shape. |
| **C6-R19** | A calendar entry MUST drill through to its recurring series or counterparty. |
| **C6-R20** | Every query MUST be scoped to the requesting user. |

## Related

- [C2 Recurring detection](c2-recurring.md) — the entry source
- [C5 Forecasting](c5-forecasting.md) — the future balance source
- [C8 Notifications](c8-notifications.md) — payment reminders come from the same series
- [B10 Multi-currency](../b-ledger/b10-multi-currency.md)
