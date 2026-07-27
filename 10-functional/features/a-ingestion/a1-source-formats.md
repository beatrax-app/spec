# A1 — Source formats and parsers

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

beatrax reads the statement formats European banks and payment processors
already export, so it is not tied to any one institution and needs no
integration agreement with anybody. This feature is the layer that turns each
of those wire formats into one canonical shape.

Everything downstream — categorisation, chain resolution, budgeting, forecasting
— assumes it is looking at one uniform representation. That assumption only
holds if this layer is exhaustive about the quirks of each format and honest
about the ones it cannot handle.

## Behaviour

### The format is declared, never sniffed

The user says which format a file is; beatrax never guesses from content. A
format identifier is chosen from a fixed set, and an unknown one is a typed
error rather than a best-effort attempt.

This is deliberate. Content sniffing across CSV dialects that differ only in
column order produces confident, wrong answers, and a wrong answer here
silently misimports a year of history.

Supported formats:

| Format | Notes |
|--------|-------|
| **CAMT.053** (ISO 20022) | The canonical bank source where a bank offers it. Every sub-version the target banks export is handled. |
| **MT940** | The legacy SWIFT statement format. Fallback where CAMT.053 is unavailable. |
| **Bank CSV** | Per-bank dialects, including ASN and ING. Dialect is declared, never inferred. |
| **Credit-card PDF statements** | ICS statements, parsed positionally. |
| **PayPal CSV** | The activity download, multi-language. |
| **Email receipts** | `.eml` and `.mbox`, handled by [A5](a5-receipt-matching.md). |
| **Open banking** | A remote adapter with the same output shape, [A6](a6-open-banking.md). |

### A pre-parse check runs first

Before the parser touches the file, a lightweight check reads the first chunk
and reports the character set it found, whether the header signature matches the
declared format, and any mismatch. The wizard surfaces a plain-language error at
that point rather than letting a parser produce nonsense from a
correctly-formatted file of the wrong type.

A leading byte-order mark is stripped rather than treated as data.

### Parsers stream, and they never write

Every parser yields rows one at a time so a multi-megabyte file never loads
entirely into memory. No parser writes to the database; parsing is a pure
transformation, which is what makes preview safe to re-run
([A2](a2-import-wizard.md)).

### Each format's quirks are handled explicitly

- **CAMT.053** carries a strong end-to-end reference where the bank populates
  one; weaker references are preserved in the raw payload rather than promoted.
  A date-only booking is normalised to midnight. An entry with neither a booking
  date nor a value date is a parse error, not a guess. External-entity resolution
  is disabled at the XML layer, so a malicious statement cannot reach the
  filesystem or the network.
- **MT940** derives its reference from the structured narrative where present,
  falling back to the customer reference. Debit and credit markers, including
  the reversal variants, map to signs explicitly. Two-digit years resolve through
  a sliding window. The account and opening-balance fields must appear before the
  first transaction line or the file is rejected. Transaction-type codes are
  stripped from counterparty names. Line count and buffer size are capped so a
  malformed file cannot exhaust memory.
- **Bank CSV** validates the column count against the dialect's accepted shapes,
  maps a sequence number to the source reference, and normalises embedded
  carriage returns inside description fields.
- **Credit-card PDF** keeps only the last four digits of a card number and drops
  the cardholder name unconditionally. Long digit runs and masked-card
  placeholders are scrubbed from the retained raw payload. Statement totals are
  persisted with the sign that means "owed to the issuer".
- **PayPal CSV** detects the export language from a column that is stable across
  languages, then rolls up the parent and child rows of a single logical payment
  — the payment, its fee, its currency-conversion legs — into one transaction.
  An unmapped event type is a typed error naming the type, because a genuinely
  unknown event is a data condition the user can act on, not a bug.

### Every failure is a typed error

Callers branch on the kind of failure, never on message text. Unreadable PDF,
unsupported PayPal language, invalid amount, invalid date, unknown event type,
header mismatch, and unsupported format are each distinct.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| File in the wrong character set | The pre-parse check flags the mismatch; the wizard shows a plain-language error before parsing. |
| Empty file | Zero rows. The preview shows "0 transactions" and confirm is a no-op. |
| Repeated header rows mid-file | Skipped. |
| Multi-statement CAMT.053 | Every statement's entries are yielded; each statement's summary metadata is recorded separately ([A9](a9-starting-balances.md)). |
| Unsupported PayPal export language | Typed error naming the language. |
| PDF from which no text can be extracted | Typed error. There is no "best-effort" partial parse — the user re-exports. |
| PayPal row whose amount carries no sign | Sign inferred from the event type; an unmapped type is a typed error. |
| Unbalanced MT940 narrative | Rejected rather than partially parsed. |
| A CSV import with no declared dialect | Refused at the contract boundary, so even a programmatic caller cannot skip it. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A1-R1** | The source format MUST be declared by the caller. beatrax MUST NOT infer a format from file content. |
| **A1-R2** | An unknown format identifier MUST raise a typed error naming the identifier. |
| **A1-R3** | A pre-parse check MUST run before the parser and MUST report character set, header signature, and any mismatch. |
| **A1-R4** | A leading byte-order mark MUST be stripped rather than treated as data. |
| **A1-R5** | Parsers MUST stream their output; a multi-megabyte file MUST NOT be loaded into memory in full. |
| **A1-R6** | No parser may write to the database. |
| **A1-R7** | Every parse failure MUST be a distinct typed error; callers MUST NOT need to inspect message text to distinguish failures. |
| **A1-R8** | XML parsing MUST disable external-entity resolution. |
| **A1-R9** | A CAMT.053 entry carrying neither a booking date nor a value date MUST be a parse error. |
| **A1-R10** | The CAMT.053 parser MUST handle every sub-version the supported banks export. |
| **A1-R11** | The MT940 parser MUST reject a file whose account and opening-balance fields do not precede the first transaction line. |
| **A1-R12** | The MT940 parser MUST cap line count and buffer size so a malformed file cannot exhaust memory. |
| **A1-R13** | The credit-card PDF parser MUST retain at most the last four digits of a card number and MUST discard the cardholder name. |
| **A1-R14** | The credit-card PDF parser MUST scrub long digit runs and masked-card placeholders from any retained raw payload. |
| **A1-R15** | A credit-card PDF from which no text can be extracted MUST raise a typed error. There MUST be no partial-parse fallback. |
| **A1-R16** | The PayPal parser MUST detect export language from a language-stable field, and MUST raise a typed error for an unsupported language. |
| **A1-R17** | The PayPal parser MUST roll up the parent, fee, and currency-conversion rows of one logical payment into a single transaction. |
| **A1-R18** | An unmapped PayPal event type MUST raise a typed error naming the type. |
| **A1-R19** | A CSV import MUST be refused unless a bank dialect is declared, enforced at the contract boundary rather than only in the UI. |
| **A1-R20** | Parser output MUST be the canonical source-row shape; a parser MUST NOT emit a ledger-ready transaction directly. |

## Related

- [A2 Import preview and confirm](a2-import-wizard.md) — what happens to the rows
- [A3 Idempotency and fingerprinting](a3-idempotency.md) — why re-import is safe
- [A9 Starting balances and statement metadata](a9-starting-balances.md)
- [G2 Error and remedy model](../g-ux/g2-error-model.md) — how these errors reach the user
- [20-architecture/data-flow.md](../../../20-architecture/data-flow.md)
- [J1 First run](../../journeys/j1-first-run.md)
