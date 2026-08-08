# A5 — Receipt matching and chain hints

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

A fetched or dropped receipt is only useful once it is tied to the transaction
it describes. This feature owns that: recognising which sender a message came
from, extracting its per-line breakdown and merchant detail, enriching the
matching ledger row, and emitting the hints that let
[B5](../b-ledger/b5-chain-resolution.md) work out what funded what.

## Behaviour

### One entry point, a priority-ordered matcher set

Every receipt — whether it arrived through an inbox scan
([A4](a4-email-scanning.md)) or was dropped on the application as a file — goes
through a single entry point. That entry point asks a registry of matchers which
one recognises the message; the highest-priority matcher whose test passes wins.

Matchers ship for the payment processor, the card issuer, and the app store.
Adding one is shipping a class and adding it to a list; nothing else changes.

### A message nobody recognises is not an error

An unmatched message is recorded as a miss. No enrichment is written, no
exception is thrown, and the message stays available for a matcher that may
ship later. Silence here is correct: a receipt for something Beatrax does not
track is not a problem to report.

### What a match produces

- **An enrichment**, applied through the shared enrichment path
  ([A3](a3-idempotency.md)) rather than written directly to the ledger.
- **A statement summary**, where the receipt carries statement-level totals,
  written through the shared statement path rather than directly.
- **Chain hints**, one event per hint extracted — a receipt naming both a
  funding card and a refund reference produces two.

Direct writes to the ledger or to statement summaries from this layer are
forbidden and enforced by architecture test.

### Hints fire after the transaction exists

The hint listener runs after the canonical row has been persisted, so the
reference it writes always resolves. A hint naming a card the user does not own
is stored with an empty target for the user to dismiss or for a later resolver
pass to complete.

### Dropped files

A receipt file dropped onto the application from the operating system is
admitted only after an extension check, a size bound, and path canonicalisation.
If nobody is signed in, the intent is remembered and picked up after sign-in.
Archive files containing several messages are iterated and each message is
processed independently.

### Conflicts

Where a receipt disagrees with what the statement already recorded, the
disagreement is recorded as a conflict rather than applied — the rules and the
user preference that governs them live in [A3](a3-idempotency.md).

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A message matching no registered sender | Recorded as a miss; no enrichment; no exception. |
| An archive containing several receipts | Each is processed independently; one failure does not stop the others. |
| A matcher throwing during matching | Not swallowed — it propagates, so a broken matcher is loud rather than silently skipping every message. |
| An extracted total that disagrees with the matched transaction beyond tolerance | Recorded as a conflict for the user to resolve. |
| A receipt dropped before sign-in | The intent is remembered; the staging page picks it up afterwards. |
| The same inbox message re-fetched | Idempotent; no duplicate enrichment. |
| A chain hint naming a card the user does not own | Stored with an empty target; dismissible, or completed by a later resolver pass. |
| A file whose extension is not admitted | Logged and dropped silently — the operating system never receives an error that would betray the application's presence. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A5-R1** | All receipt processing MUST flow through a single entry point. |
| **A5-R2** | Matchers MUST be consulted in priority order; the first whose test passes MUST win. |
| **A5-R3** | A message matching no matcher MUST be recorded as a miss without raising an error. |
| **A5-R4** | Adding a matcher MUST require only shipping the class and registering it; no change to the entry point or the pipeline. |
| **A5-R5** | Enrichments MUST be applied through the shared enrichment path, never written directly to the ledger. |
| **A5-R6** | Statement summaries MUST be written through the shared statement path, never directly. |
| **A5-R7** | Exactly one chain-hint event MUST fire per extracted hint. |
| **A5-R8** | The hint listener MUST run after the canonical transaction is persisted. |
| **A5-R9** | A hint whose target the user does not own MUST be stored with an empty target and MUST be dismissible. |
| **A5-R10** | A file offered by the operating system MUST be admitted only after an extension allow-list check, a size bound, and path canonicalisation. |
| **A5-R11** | A rejected file path MUST be logged and dropped silently; no error may be returned to the operating system. |
| **A5-R12** | A receipt dropped while signed out MUST be remembered and resumed after sign-in. |
| **A5-R13** | Each message inside an archive MUST be processed independently. |
| **A5-R14** | An exception thrown by a matcher MUST propagate rather than being silently swallowed. |
| **A5-R15** | Re-processing an already-processed message MUST produce no duplicate enrichment. |
| **A5-R16** | Cross-user reads and writes MUST return not-found. |

## Related

- [A4 Email-receipt scanning](a4-email-scanning.md) — where messages come from
- [A3 Idempotency and enrichment](a3-idempotency.md) — how an enrichment lands
- [B5 Funding-chain resolution](../b-ledger/b5-chain-resolution.md) — what hints feed
- [F1 Desktop shell](../f-platform/f1-desktop-shell.md) — the file-drop path
