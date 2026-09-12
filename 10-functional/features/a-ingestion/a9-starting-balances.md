# A9 — Starting balances and statement metadata

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

A ledger of transactions with no starting point cannot say what an account
holds. Forecasting, net worth, the calendar's projected balance line, and
reconciliation all need an anchor.

Some statement formats carry that anchor; some do not. This feature owns finding
it where it exists, asking for it where it does not, and recording the
statement-level metadata no single transaction row carries.

## Behaviour

### Statement metadata is a side channel

CAMT.053 and MT940 carry statement-level facts — opening balance, closing
balance, period start and end — that no individual transaction row contains.
After the rows are processed, the parser is asked for its statement metadata and
the result is recorded as one row per statement period.

**The side channel is the recording path, not the origin of the figures.** A
format that ships no balance rows of its own may still answer that question, by
summing the rows it just yielded — the PayPal export is the one that does. It is
still asked once, after the rows, and still written once through the same path,
which is what "separately from the row pipeline" was ever protecting. What a
derived figure costs is a condition the read ones do not carry: it is only true
if everything it summed was in one denomination and nothing was lost, so it is
withheld entirely where either fails, and it never anchors an account. That last
part is about the figure and not about the seam carrying it: a derived balance is
not offered to the reader as a starting balance, and no other path may write it
as one either. A balance that reaches an account without being offered has
skipped the step that would have caught it, which is not the same as avoiding
the harm.

**A period is established the same way.** Where a format prints no header saying
which dates it covers, the earliest and latest booked dates of the rows it
yielded are that period — worked out rather than asserted, and enough to record a
summary against. What A9-R2 refuses a summary to is the format that can
establish no period at all, not the one that derives the period it was never
given.

Bank CSV presets carry no period boundary and derive none either: they return
nothing at all. Receipt formats are excluded entirely: each receipt is its own
record with no opening or closing balance.

Statement summaries are unique per user, account, and period, so re-importing
the same statement updates rather than duplicates.

### Starting-balance detection, in preference order

Detectors are consulted in a fixed order and the first non-empty result wins:

1. **CAMT.053** — canonical.
2. **MT940** — legacy.
3. **Card PDF statements.**
4. **PayPal CSV** — which always declines, because its running-balance column
   resets after every funding sweep and is therefore meaningless as an anchor.

Where two detectors disagree for the same account, the earliest opening-balance
date wins; on a date tie CAMT.053 is preferred over MT940; if both still tie,
**both are returned** and the wizard renders a conflict card for the user to
choose.

### Where nothing is detected, the user is asked

An account with no detected starting balance gets a manual-entry card. A
detected balance gets a confirmation card the user can edit. Cards appear only
for accounts the import actually touched.

### A wildly divergent override warns, but does not block

If the user enters a starting balance far from what the statements imply, the
system says so and lets them proceed. It is their money and their ledger; the
system's job is to notice, not to refuse.

### Card statements are promoted

Card-kind statement summaries are promoted into card-statement records after the
import commits. The promotion is idempotent and deliberately decoupled from
whether any transaction was inserted, so it also recovers a manually deleted
record on a re-import where every row is a duplicate.

## States

A starting-balance card is in one of:

| State | Meaning |
|-------|---------|
| `detected` | A detector found a value; awaiting confirmation. |
| `conflict` | Two detectors disagree; awaiting a choice. |
| `editing` | The user is overriding. |
| `manual-entry` | No detector fired; awaiting input. |
| `confirmed` | Settled. |

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A format that neither carries a period boundary nor can work one out from its rows | No statement summary written. |
| A format that prints no period but whose rows carry booked dates | Summary written against the period those dates span. |
| A derived balance on any path to an account's starting balance | Not used. Declining to offer it is not enough on its own: a figure nobody read is not an anchor whichever seam reaches the account. |
| A derived closing balance over rows in more than one currency | No balance recorded. The period and the entry count still are: a figure summed across two denominations is not money, and offering it as a reconcile target asks the reader to close a gap no row can close. |
| A derived closing balance where a row of the source could not be read | The same. Summed over what was left, the total moves with the loss, and nothing on the screen would say by how much. |
| Two statements for the same account and period | Unique constraint updates rather than duplicating. |
| CAMT.053 and MT940 disagreeing on the same account | Earliest date wins; on a tie CAMT.053 wins; on a full tie both surface as a conflict. |
| PayPal CSV | Always declines to supply a starting balance. |
| An override far from the statement-derived value | Warned, not blocked. |
| A card statement record deleted by hand | Recovered on the next import even if every transaction is a duplicate. |
| A card account with no statement and no user-entered balance | Anchored at zero, to avoid double-counting historical billing events. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A9-R1** | Statement-level metadata MUST be recorded once per statement period, through a channel separate from the row pipeline: the parser is asked for it once the rows have been yielded, and it is written once rather than once per row. Where a format carries no balance rows of its own, the figures MAY be derived from the rows that format yielded, under A9-R16. |
| **A9-R2** | Formats that neither carry a period boundary nor can derive one MUST record no statement summary. Where a format states no period of its own, the boundary MAY be derived from the booked dates of the rows that format yielded; a summary over a period that was neither carried nor derived MUST NOT be recorded. |
| **A9-R3** | Receipt formats MUST be excluded from statement-summary recording. |
| **A9-R4** | Statement summaries MUST be unique per user, account, and period. |
| **A9-R5** | Starting-balance detectors MUST be consulted in a fixed, documented order, and the first non-empty result MUST win. |
| **A9-R6** | Where detectors disagree for one account, the earliest opening-balance date MUST win. |
| **A9-R7** | On a date tie, the ISO 20022 source MUST be preferred over the legacy one. |
| **A9-R8** | Where both date and preference tie, both results MUST surface as a user-resolvable conflict. |
| **A9-R9** | The PayPal source MUST always decline to supply a starting balance. |
| **A9-R10** | An account with no detected starting balance MUST offer manual entry. |
| **A9-R11** | Starting-balance cards MUST appear only for accounts the import touched. |
| **A9-R12** | An override diverging materially from the statement-derived value MUST warn and MUST NOT block. |
| **A9-R13** | Card-statement promotion MUST be idempotent and MUST NOT be gated on whether any transaction was inserted. |
| **A9-R14** | A card account with neither a statement nor a user-entered balance MUST anchor at zero. |
| **A9-R15** | Confirming a starting balance MUST be idempotent. |
| **A9-R16** | Where a statement summary's balances are derived from the rows rather than read from the source, those balances MUST be withheld unless every row summed is denominated in one currency and every row of the source was readable; and a derived balance MUST NOT anchor an account — neither offered to the reader as a starting-balance candidate, nor written as an account's starting balance by any other path. |

## Open questions

**Whether a derived zero is a balance at all.** A format that prints no opening
balance and works its figures out by summing its own rows has to start that sum
somewhere, and where the conditions A9-R16 sets are met that starting point is
recorded as an opening balance of **zero** — not null, dated at the period start,
in the account's own currency, and indistinguishable in the record from a
statement that genuinely opened at nothing. A9-R16 keeps that figure from
anchoring an account. It does not say whether a figure the format never printed
should be recorded as a balance in the first place, or withheld the way a
multi-currency sum already is. Nobody has decided, and the question is recorded
in
[90-appendix/open-questions.md](../../../90-appendix/open-questions.md#is-a-derived-opening-balance-of-zero-a-balance-anybody-measured).

**Whether a summary is one per period or one per import run.** A9-R1 records
statement metadata once per statement period and A9-R4 requires it unique per
user, account and period. The product keys the row on the user and the import
run instead, and writes at most one row per run: two runs over the same
statement period leave two rows, and one run spanning two periods leaves one.
Which of the two is right is a product question — re-importing the same
statement under a new run is the case that decides it — and it is recorded in
[90-appendix/open-questions.md](../../../90-appendix/open-questions.md#is-a-statement-summary-one-per-period-or-one-per-import-run).

## Related

- [A1 Source formats](a1-source-formats.md) · [A2 Import preview and confirm](a2-import-wizard.md)
- [C5 Cash-flow forecasting](../c-insight/c5-forecasting.md) — the main consumer
- [C6 Bills and cash-flow calendar](../c-insight/c6-calendar.md)
- [B8 Reconciliation](../b-ledger/b8-reconciliation.md)
- [F2 First-run setup wizard](../f-platform/f2-setup-wizard.md)
