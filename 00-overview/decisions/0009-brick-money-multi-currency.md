# ADR-0009: brick/money for multi-currency arithmetic

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

Beatrax handles money in multiple currencies. App-store receipts arrive in USD.
Card issuers settle foreign-currency charges from many countries — some
merchants quote USD, hotel chains quote GBP, European retailers stay in EUR. The
system has to preserve both the original-currency amount and the settled amount,
present them side by side, sum cash-flow projections per currency, and never
silently lose FX information.

PHP's two default tools both fail this job:

- **`float`** corrupts arithmetic silently at the second decimal place. Two
  charges of 19.99 added back together do not always come back as 39.98. For
  arithmetic the user audits against their bank statement to the cent, floats
  are unacceptable.
- **Integer cents** works for a single-currency app. The moment a second
  currency lands, "amount in cents" stops being a complete representation — the
  currency code has to travel with the value, and every addition has to refuse
  to mix two currencies. Enforcing that by hand across every model becomes a
  sprawl of defensive checks.

Two libraries were in scope. `moneyphp/money` is long-established and arrives
transitively via the CAMT parser. `brick/money` is newer: immutable Money
objects, exact arithmetic without BCMath, explicit rounding, pluggable
conversion, a multi-currency bag type, and modern type signatures.

## Decision

Every monetary value is a `brick/money` `Money` instance once it crosses the
parser boundary.

- **Domain code** constructs from minor units, uses the library's arithmetic
  methods, and formats for display with the user's locale.
- **DTOs** carry `Money` instances directly, not separate amount and currency
  fields.
- **Models** cast persisted columns through a money cast reading an
  `*_minor INTEGER` column plus a `VARCHAR(3)` currency column. The columns
  themselves stay primitive — SQLite knows nothing about Money; the cast is the
  boundary.
- **Multi-currency totals** use the library's money-bag type rather than summing
  into a single currency. A monthly total shows each currency on its own line,
  not a rate-converted aggregate. Conversion happens only when the user asks for
  it, through the base-currency conversion feature.
- **The CAMT boundary** converts the parser's value objects into `brick/money`
  instances inside the parser directory. The rest of the codebase only ever sees
  `brick/money` types.
- **Rate values** read from the database are cast to string before being handed
  to the library. A rate that becomes a PHP float has already lost precision.

Two architecture invariants hold the line: every model with a `*_minor` column
must cast through the money cast, and no service touching money may declare a
`float` parameter or return type.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Use `moneyphp/money` throughout** | Would avoid a second money library in the lock file, but gives up immutable semantics, exact arithmetic without BCMath, and the multi-currency bag. The transitive dependency does not force the rest of the codebase to share the choice. |
| **Integer cents plus a manual currency column** | The multi-currency arithmetic-safety story would be hand-rolled for every addition and comparison. Defensive checks would have out-grown the library cost within a month. |
| **Floats with rounding at display time** | Rounding at display does not undo the corruption that accumulates during arithmetic. |

## Consequences

### Positive

- **Arithmetic is exact.** No rounding surprises anywhere on the money path.
- **Currency mixing throws** rather than silently producing a nonsense total.
  The exception surfaces at the service layer.
- **FX information is preserved.** A foreign-currency charge settled into the
  base currency keeps both representations, plus the derived rate at
  eight-decimal scale, so the chain layer can show "you paid USD 19.99, which
  cost you EUR 18.42" without recomputing anything.
- Display is locale-aware for free.

### Negative

- **Two money libraries in the lock file.** The coexistence is bounded — no
  application code imports the transitive one, and conversion happens at a
  single boundary — but it is a wrinkle a reader will notice.
- Every money read from the database goes through a cast, which is a small,
  constant cost on large result sets.

### Neutral

- Amount columns stay plaintext even under at-rest encryption, precisely because
  aggregation happens in SQL. See [ADR-0018](0018-amounts-plaintext-at-rest.md).

## Revisit if

- `brick/money` stops tracking PHP releases the bundled runtime depends on.

## Related

- [ADR-0005](0005-sqlite-wal.md) — the columns Money is cast to
- [ADR-0018](0018-amounts-plaintext-at-rest.md)
- [B10 Multi-currency and FX conversion](../../10-functional/features/b-ledger/b10-multi-currency.md)
- [20-architecture/data-model.md](../../20-architecture/data-model.md)
