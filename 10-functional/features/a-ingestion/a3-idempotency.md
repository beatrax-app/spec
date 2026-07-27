# A3 — Idempotency, fingerprinting and enrichment

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

A user will re-import the same statement. They will import an overlapping
period. They will import the same month twice in two different formats because
one was easier to download. They will connect open banking after a year of file
imports and pull the same transactions again.

None of that may produce a duplicate, and none of it may lose the extra detail
the second source carried. This feature is the mechanism that makes both true —
and it is what device sync inherits rather than reinventing
([ADR-0014](../../../00-overview/decisions/0014-op-log-crdt-merge-engine.md)).

## Behaviour

### The fingerprint

Every transaction carries a fingerprint derived from the properties that
identify it as *the same real-world event*: the owning user, the account, the
booking and posting dates, the amount and currency, and the normalised
counterparty name.

Normalisation lower-cases, strips diacritics, collapses punctuation to spaces,
trims, and truncates to a bounded length — so two exports of the same
transaction whose descriptions differ only in casing or accents produce the same
fingerprint.

**The source reference is deliberately excluded.** Including it would make the
same transaction from two formats look like two transactions, which is precisely
the case enrichment exists to handle.

A uniqueness constraint on user, account, and fingerprint is what makes the
guarantee structural rather than procedural.

### Where a counterparty name is missing

A literal sentinel substitutes for an absent, empty, or punctuation-only
counterparty name, because the uniqueness constraint needs a non-null value to
catch duplicates that lack a usable name.

### Three verdicts

| Verdict | Condition | Effect |
|---------|-----------|--------|
| **New** | No row with this fingerprint | Insert |
| **Duplicate** | A row exists, and this source is not stronger | Skip |
| **Enriched** | A row exists, and this source is stronger | Update in place, append provenance |

"Stronger" is decided by a single ranking of source references, shared between
the preview-time classifier and the write-time applier. Sharing it is what
closes the window between preview and confirm: the applier re-reads the stored
reference under a row lock and re-ranks, so a change between the two phases
turns the enrichment into a no-op rather than an incorrect overwrite.

### Statement-versus-statement collisions never enrich

If both sides are bank-statement formats — re-importing a period as CAMT.053
after CSV, for instance — the second is a plain duplicate. Without this rule
every row of a re-imported month would falsely register as enriched.
Receipt-driven enrichment, where at least one side is a receipt, is unaffected.

### Provenance is append-only

Each enrichment appends an entry to the row's provenance trail; nothing is ever
overwritten. A row can therefore say "first observed as bank CSV on one date,
enriched by a PayPal receipt later", and that history survives every subsequent
import.

### Conflicts are surfaced, not silently resolved

When an enrichment carries a value that disagrees with what is stored — a
different counterparty name, description, currency, or amount — the disagreement
is recorded rather than applied blindly. A per-user preference decides what
happens:

- **Ask** (default): the conflict is recorded and surfaced for the user to
  resolve, and the field is left alone.
- **Prefer the receipt**: the incoming value lands.
- **Prefer the first write**: the stored value stays; only the source reference
  strengthens.

Comparison is case-insensitive for text, case-normalised for currency, and exact
for amounts. Under at-rest encryption the **stored value is decrypted before
comparison**; comparing ciphertext to plaintext would register a false conflict
on every single re-import.

### Only known fields can be updated

The set of fields an enrichment may touch is a fixed allow-list, so a corrupted
or crafted preview cache cannot turn an arbitrary key into a database column
update.

### The version is explicit

The fingerprint algorithm carries a version. Changing it is a forward migration
that re-derives every existing row's fingerprint — never an in-place edit of the
original migration — and the re-derivation is itself idempotent.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Two imports racing on the same file | Both produce identical fingerprints; the uniqueness constraint keeps exactly one row. |
| The same transaction in two formats, same period | First is new; second is enriched or duplicate depending on relative source strength. |
| Two genuinely distinct identical same-day transactions | Both record. Manual cash-book entries in particular must not collapse — see [A7](a7-cash-book.md). |
| An enrichment whose target row was deleted between preview and confirm | Dropped and logged; the import continues. |
| An enrichment that no longer outranks the stored reference at write time | Dropped as a no-op. |
| A row with no usable counterparty name | The sentinel keeps the uniqueness constraint effective. |
| Fingerprint version bump | A forward migration re-derives every row; re-running it changes nothing. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A3-R1** | Every transaction MUST carry a fingerprint derived from user, account, booking and posting dates, amount, currency, and normalised counterparty name. |
| **A3-R2** | The source reference MUST NOT contribute to the fingerprint. |
| **A3-R3** | Counterparty normalisation MUST lower-case, strip diacritics, collapse punctuation, trim, and truncate to a bounded length. |
| **A3-R4** | A missing, empty, or punctuation-only counterparty name MUST be replaced by a literal sentinel so the uniqueness constraint remains effective. |
| **A3-R5** | A uniqueness constraint on user, account, and fingerprint MUST exist; idempotency MUST NOT rely on application-level checks alone. |
| **A3-R6** | Re-importing an identical file MUST produce zero new rows. |
| **A3-R7** | Every previewed row MUST classify as new, duplicate, or enriched. |
| **A3-R8** | Source-reference ranking MUST be shared between the preview classifier and the write-time applier. |
| **A3-R9** | The applier MUST re-read and re-rank the stored reference under a row lock, and MUST drop the enrichment if the stored reference now ranks at least as high. |
| **A3-R10** | A collision where both sources are bank-statement formats MUST classify as duplicate, never enriched. |
| **A3-R11** | Enrichment provenance MUST be append-only; an existing entry MUST NOT be overwritten. |
| **A3-R12** | A disagreement between an incoming enrichment and the stored value MUST be recorded rather than silently applied. |
| **A3-R13** | The user MUST be able to choose between asking, preferring the receipt, and preferring the first write; asking MUST be the default. |
| **A3-R14** | Under at-rest encryption, the stored value MUST be decrypted before comparison with an incoming value. |
| **A3-R15** | The fields an enrichment may update MUST be a fixed allow-list. |
| **A3-R16** | Text comparison MUST be case-insensitive, currency comparison case-normalised, and amount comparison exact. |
| **A3-R17** | The fingerprint algorithm MUST carry an explicit version, and a version change MUST ship as a forward migration that re-derives every row. |
| **A3-R18** | The re-derivation MUST be idempotent. |
| **A3-R19** | Fingerprint lookup MUST filter explicitly by user rather than relying on an ambient scope, so a fingerprint owned by another user can never affect this user's verdict. |

## Related

- [A2 Import preview and confirm](a2-import-wizard.md) — where the verdicts are shown
- [A5 Receipt matching](a5-receipt-matching.md) — the main source of enrichments
- [A6 Open-banking connector](a6-open-banking.md) — inherits this for free
- [E1 Change capture and CRDT merge](../e-sync/e1-change-capture.md) — sync inherits it too
- [ADR-0014](../../../00-overview/decisions/0014-op-log-crdt-merge-engine.md)
- [20-architecture/data-flow.md](../../../20-architecture/data-flow.md)
