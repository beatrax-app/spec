# ADR-0018: Amount columns stay plaintext under at-rest encryption

**Status:** Accepted
**Date:** 2026-07-09

## Context

At-rest encryption protects the local database with a per-user Group Data Key
released by the app-lock. The question this ADR settles is *what* it encrypts.

Encrypting everything is the intuitive answer and it breaks the product. Amounts
are aggregated in SQL constantly: the dashboard's period totals, category
roll-ups, budget progress, forecast projections, net worth, the reconciliation
running balance, report aggregation. Every one of those is a `SUM` or a
`GROUP BY` over an amount column. Encrypted amounts mean loading the whole
result set into PHP and summing there, on a ledger that is never pruned.

Full-text search has the same shape. The index needs plaintext to match on;
searching ciphertext is not a thing.

So the decision is not "encrypt or not" but "which columns, and what does the
resulting leak actually reveal to an attacker who has the database file but not
the key".

## Decision

A **registry of sensitive columns** defines exactly what is encrypted. It is a
single list, and it is the input to a regression guard that fails the build if a
registered column is read or written raw.

**Encrypted:** the identifying and descriptive columns — transaction
description, counterparty name, counterparty IBAN, the raw parser payload,
transaction notes; counterparty display name, merchant name, and IBAN; tax-tag
notes; split-leg notes; notification title, body, parameters, and trigger type.

**Deliberately plaintext:**

- **Amount columns** — the native amount, the settled amount, and the FX rate —
  because SQL aggregation over them is load-bearing across the whole product.
- **Dates, account references, and type enums**, for the same reason.
- **The full-text search index body**, which is a disclosed plaintext shadow of
  the encrypted description and counterparty columns. It is written by decrypting
  first, precisely so search works at all.

Three further plaintext exceptions are knowingly accepted and named rather than
hidden: the recurring detector's cluster key, the migration importer's baseline
values, and the stored/incoming values on enrichment-conflict rows.

**Everything that reads an encrypted column decrypts before matching.** A
predicate, a JSON parse, a comparison, or a display that reads ciphertext raw is
a defect — under an encrypted user it either never matches or renders ciphertext
at the user. This is the failure mode the design is most prone to, and it was
common enough during activation that closing it took a dedicated sixteen-plan
correctness pass.

**Work that needs the key runs where the key is.** Background jobs dispatched
from a request run synchronously so they inherit the unlocked key; jobs that can
only run from a daemon, where no key is available, skip with a warning rather
than silently producing wrong results.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Encrypt everything, including amounts** | Every aggregate becomes a full table load plus PHP-side summation over a history that is never pruned. The product stops being usable well before the dataset stops being small. |
| **Encrypt amounts, drop full-text search** | Trades a shipped, load-bearing feature for a leak reduction that is modest — see below. |
| **Whole-file encryption via an encrypted SQLite build** | Would encrypt everything uniformly, but requires a database extension outside the bundled runtime's supported set ([ADR-0006](0006-nativephp-desktop-shell.md)) and would not survive the desktop packaging constraint. |
| **Encrypt amounts with an order-preserving or homomorphic scheme** | Order-preserving encryption leaks ordering, which for a spend distribution is most of the signal, and the complexity is disproportionate. |

## Consequences

### Positive

- Aggregation, budgeting, forecasting, and search all keep working with the
  database encrypted.
- The encrypted set covers what actually identifies a person: who they paid,
  what for, and their account identifiers.

### Negative

- **The leak is real and must be stated plainly.** An attacker with the database
  file but not the key sees a complete, dated, per-account distribution of
  amounts, plus the search index's plaintext shadow of descriptions and
  counterparty names. That is a great deal. The honest framing is that at-rest
  encryption raises the cost of casual access to a copied file and to a
  cloud-backed device backup; it is not a defence against an attacker who has the
  file and cares.
- The in-app copy must say this rather than implying end-to-end opacity.
- Every new column that holds identifying text has to be added to the registry,
  and forgetting is silent until someone reads ciphertext at a user.

### Neutral

- The registry is also what the sync layer's field encryption keys off, so the
  encrypted set is the same on disk and on the wire.

## Revisit if

- A supported encrypted-storage option becomes available inside the bundled
  runtime, making uniform whole-file encryption viable without losing SQL
  aggregation.
- The search index's plaintext shadow is judged too large a leak, which would
  mean an encrypted-search design — a new ADR.

## Related

- [ADR-0014](0014-op-log-crdt-merge-engine.md) · [ADR-0016](0016-noise-transport-zero-knowledge-relay.md)
- [ADR-0009](0009-brick-money-multi-currency.md) — why amounts are integer columns
- [E4 At-rest encryption, revocation and rekey](../../10-functional/features/e-sync/e4-at-rest-encryption.md)
- [40-quality/security.md](../../40-quality/security.md)
