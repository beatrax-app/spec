# A2 — Import preview and confirm

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

Importing a statement is the single most consequential thing a user does in
Beatrax, and the one they will do most often. A bad import is expensive to
notice and expensive to undo, so the flow is built around one rule: **the user
sees exactly what will happen before anything happens**.

## Behaviour

### Two phases, one write boundary

**Preview** runs every processing stage — parse, account resolution,
normalisation, transaction-type classification, payment-type classification,
auto-categorisation, counterparty resolution, and fingerprinting — and writes
nothing to the ledger. Its output is a per-row verdict plus any questions the
user must answer.

**Confirm** is the only write. Reviewers and architecture tests both rely on
there being no other path into the ledger from the import layer.

### Every row gets a verdict

| Verdict | Meaning |
|---------|---------|
| **New** | No existing row matches. Will be inserted. |
| **Duplicate** | An identical row already exists. Will be skipped. |
| **Enriched** | A row already exists and this source is stronger. Will update it in place, appending provenance. |
| **Error** | This row could not be processed. Shown with the reason. |

Verdicts are explained in [A3](a3-idempotency.md), which owns the rules.

### One bad row never kills an import

Per-row processing is guarded: a row that throws becomes an Error row with its
message shown, and the rest of the file proceeds. A failure at the file level —
a bad header, an encoding mismatch, malformed XML — produces a single Error
covering the whole file so the wizard still renders a preview screen rather than
failing hard.

The user-facing message is plain language; the full diagnostic goes to the local
log where [F5](../f-platform/f5-dev-console.md) can read it.

### Unknown accounts are a question, not a failure

When a row belongs to an account Beatrax has not seen, the preview does not
fail. It collects the unknown identifiers, de-duplicates them across the whole
file, and asks the user to name each one. Naming creates the account and the
preview re-runs.

Card and PayPal sources have the same shape with a synthetic identifier, because
those formats carry no bank account number.

### Nothing is committed until the user says so

Preview results are held in a short-lived cache — long enough for a considered
review, short enough that a tab left open overnight cannot replay stale data.
The cache round-trips through a plain data encoding rather than native object
deserialisation, so a schema change produces a loud failure instead of silently
dropping rows.

### Confirm is bounded, not one giant transaction

A full year of history must not commit as a single unbounded database
transaction. Confirm therefore splits:

1. **Recording** commits in bounded chunks, each idempotent on the fingerprint.
   A crash part-way leaves committed rows that a re-run safely completes.
2. **Enrichment and status** commit together in one transaction, so a run
   marked confirmed always implies its enrichment writes landed.

Re-confirming an already-confirmed run short-circuits before either phase and
reports the original counts, so a refresh or a back-button can never
double-import.

### Downstream work is dispatched after the commit, in order

Once the write has committed — never inside it — the confirm step promotes any
card-statement metadata, then dispatches chain resolution and recurring
detection. The ordering matters: the chain resolver needs the statement rows to
exist. Dispatching inside the transaction would let a worker observe state that
has not committed.

Callers that batch several confirms inside their own transaction suppress the
dispatch and fire it once themselves afterwards.

### Re-importing the same file is free

A file whose content hash matches one the user already imported and confirmed
short-circuits to an empty preview. Even without that, every row would classify
as Duplicate — the hash check just saves the work.

### The consolidated first-import view

During first-run setup the user may stage several files across several formats
before committing anything. A consolidated preview groups the staged runs by
format, shows a sample of each, and commits them together. It drops runs older
than a two-week window and runs already confirmed, so a forgotten tab cannot
resurface weeks-old data or replay a committed run.

## States

An import run moves through:

| State | Meaning |
|-------|---------|
| `previewed` | Parsed, classified, cached. Nothing written. |
| `confirmed` | Committed. Terminal. |
| `discarded` | Abandoned by the user. Re-usable. |

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Empty file | Preview shows zero rows; confirm is a no-op. |
| Two previews racing on the same file | The unique constraint on content hash resolves it; the loser re-reads the winner's run and proceeds with identical semantics. |
| A file dropped from the OS while nobody is logged in | The path is remembered, the user is sent to sign in, and the staging page picks it up afterwards. |
| Preview cache expired before confirm | The user is told to re-run the preview rather than shown a partial commit. |
| Enrichment targets a transaction deleted since preview | That enrichment is dropped and logged; the import continues. |
| Interrupted mid-confirm | Recorded rows are committed and idempotent; re-confirming completes the run. |
| A file over the per-format size cap | Rejected before parsing, with the cap named. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A2-R1** | Preview MUST NOT write to the ledger. |
| **A2-R2** | Confirm MUST be the only path from the import layer into the ledger. |
| **A2-R3** | Every previewed row MUST carry exactly one verdict: new, duplicate, enriched, or error. |
| **A2-R4** | A row that fails processing MUST become an error row; it MUST NOT abort the import. |
| **A2-R5** | A file-level parse failure MUST produce a single error covering the file, and the wizard MUST still render. |
| **A2-R6** | Error messages shown to the user MUST be plain language; full diagnostics MUST go to the local log only. |
| **A2-R7** | Rows belonging to an unrecognised account MUST produce a de-duplicated naming prompt, not a failure. |
| **A2-R8** | Naming an account MUST re-run the preview against the completed account set. |
| **A2-R9** | Preview results MUST expire after a bounded window, and an expired preview MUST be re-run rather than partially committed. |
| **A2-R10** | The preview cache MUST round-trip through a plain data encoding; a schema mismatch MUST fail loudly rather than dropping rows. |
| **A2-R11** | Confirm MUST NOT wrap the whole recording phase in one transaction; recording MUST commit in bounded, individually idempotent chunks. |
| **A2-R12** | Enrichment application and the run's status change MUST commit together, so a confirmed status always implies enrichments landed. |
| **A2-R13** | Re-confirming an already-confirmed run MUST be a no-op reporting the original counts. |
| **A2-R14** | Downstream dispatch MUST occur strictly after the commit, never inside the transaction. |
| **A2-R15** | Card-statement promotion MUST run before chain-resolution dispatch. |
| **A2-R16** | Re-importing a file whose content hash matches a confirmed run MUST short-circuit to an empty preview. |
| **A2-R17** | The consolidated first-import view MUST exclude runs older than the staleness window and runs already confirmed. |
| **A2-R18** | A caller batching several confirms inside its own transaction MUST be able to suppress per-confirm dispatch and fire it once afterwards. |
| **A2-R19** | Each source format MUST enforce its own upload size cap, and exceeding it MUST be reported with the cap named. |
| **A2-R20** | An import run's state MUST be one of previewed, confirmed, or discarded; confirmed MUST be terminal. |

## Related

- [A1 Source formats and parsers](a1-source-formats.md)
- [A3 Idempotency and fingerprinting](a3-idempotency.md) — the verdict rules
- [A9 Starting balances](a9-starting-balances.md)
- [B4 Counterparties](../b-ledger/b4-counterparties.md) · [B5 Chain resolution](../b-ledger/b5-chain-resolution.md)
- [F2 First-run setup wizard](../f-platform/f2-setup-wizard.md) — the consolidated view
- [J1 First run](../../journeys/j1-first-run.md) · [J2 Daily use](../../journeys/j2-daily-use.md)
