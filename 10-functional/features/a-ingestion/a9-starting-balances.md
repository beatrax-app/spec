# A9 — Starting balances and statement metadata

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

A ledger of transactions with no starting point cannot say what an account
holds. Forecasting, net worth, the calendar's projected balance line, and
reconciliation all need an anchor.

Some statement formats carry that anchor; some do not. This feature owns finding
it where it exists, asking for it where it does not, and recording the
statement-level metadata the row-by-row pipeline never sees.

## Behaviour

### Statement metadata is a side channel

CAMT.053 and MT940 carry statement-level facts — opening balance, closing
balance, period start and end — that no individual transaction row contains.
After the rows are processed, the parser is asked for its statement metadata and
the result is recorded as one row per statement period.

CSV formats carry no period boundary and return nothing. Receipt formats are
excluded entirely: each receipt is its own record with no opening or closing
balance.

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
| A format that carries no period boundary | No statement summary written. |
| Two statements for the same account and period | Unique constraint updates rather than duplicating. |
| CAMT.053 and MT940 disagreeing on the same account | Earliest date wins; on a tie CAMT.053 wins; on a full tie both surface as a conflict. |
| PayPal CSV | Always declines to supply a starting balance. |
| An override far from the statement-derived value | Warned, not blocked. |
| A card statement record deleted by hand | Recovered on the next import even if every transaction is a duplicate. |
| A card account with no statement and no user-entered balance | Anchored at zero, to avoid double-counting historical billing events. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A9-R1** | Statement-level metadata MUST be recorded once per statement period, separately from the row pipeline. |
| **A9-R2** | Formats carrying no period boundary MUST record no statement summary. |
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

## Related

- [A1 Source formats](a1-source-formats.md) · [A2 Import preview and confirm](a2-import-wizard.md)
- [C5 Cash-flow forecasting](../c-insight/c5-forecasting.md) — the main consumer
- [C6 Bills and cash-flow calendar](../c-insight/c6-calendar.md)
- [B8 Reconciliation](../b-ledger/b8-reconciliation.md)
- [F2 First-run setup wizard](../f-platform/f2-setup-wizard.md)
