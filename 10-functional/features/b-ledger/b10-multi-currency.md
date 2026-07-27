# B10 — Multi-currency and FX conversion

**Status:** Accepted · **Area:** B — The ledger

---

## Purpose

A household with an app-store subscription billed in dollars, a hotel booked in
pounds, and a bank account in euros has three currencies whether it wants them
or not. beatrax preserves every one of them exactly, shows what a charge really
cost, and — when the user asks — rolls everything into one reporting currency
without ever pretending the conversion was free.

## Behaviour

### Both amounts, always

A transaction preserves its native amount and currency **and** its settled
amount and currency, plus the derived rate at high precision where they differ.
Neither is derived from the other at display time; both are stored, because FX
information that is lost cannot be recovered.

The user can flip the transaction list between settled-currency-only and
original-currency views to see what a charge actually cost.

### Currencies never silently mix

Adding two different currencies throws rather than producing a total. A
multi-currency total is presented as several lines, one per currency — not as a
rate-converted aggregate the user did not ask for.

### The base currency is a choice

The user picks one reporting currency. Every roll-up renders in it. Accounts
keep their own currency; only the roll-up converts.

Conversion is explicit and disclosed: for any converted figure the user can see
the rate used, its source, and its as-of date.

### Rates come from a chain, and offline still works

Rate providers are consulted in priority order. Online providers are consulted
only if the user has enabled online rate fetching, which is **off by default**
([G1](../g-ux/g1-privacy.md)). A bundled offline snapshot is the final provider
and always succeeds, so conversion works with no network at all.

A provider that fails repeatedly is skipped for a period rather than retried on
every request. If every provider is unavailable, the caller falls back to
showing original currencies rather than inventing a rate.

Rates are keyed by the date the feed reports, never by the current date, so a
weekend or a holiday does not create a phantom rate for a day the market was
closed. A value outside a plausible range is logged and skipped rather than
stored.

### Cross-rates are derived, and staleness is honest

A rate between two non-base currencies is derived exactly from two base-anchored
pairs rather than requiring a direct pair. The as-of date, the source, and the
staleness of such a conversion reflect the **oldest** leg involved — otherwise a
stale leg could be reported as fresh.

The staleness threshold accommodates a normal market weekend, so a Monday
morning does not falsely flag Friday's rates.

### Where a rate is missing

An account whose currency has no available rate is **excluded** from the
converted roll-up and the exclusion is flagged, with the affected accounts
named. A silent zero or a one-to-one fallback would be a lie.

### Conversion is never a float

Rates read from storage are handled as exact decimal values from the moment they
leave the database. A rate that becomes a floating-point number has already lost
precision.

### Two conversion modes

**Current-snapshot** conversion uses the latest available rate — right for
"what is my net worth today". **Historical** conversion prefers the rate the
transaction itself recorded, falling back to a dated snapshot — right for "what
did this cost me at the time".

Where a figure is already in the target currency, conversion short-circuits with
no query and no rate disclosure.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Every provider fails | The caller falls back to original currencies; no rate is invented. |
| A provider returns an empty rate set | Treated as a failure, not a success. |
| A rate outside the plausible range | Logged and skipped. |
| A weekend or holiday feed | Keyed by the feed's own date. |
| A cross-rate with one stale leg | Reported as stale, dated by the oldest leg. |
| An account with no rate for its currency | Excluded from the roll-up and named in the exclusion. |
| A figure already in the target currency | Zero-cost passthrough, no disclosure rendered. |
| Online fetching disabled | The bundled snapshot is used; everything still works. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **B10-R1** | Every transaction MUST preserve both its native and settled amount and currency, and the derived rate where they differ. |
| **B10-R2** | The user MUST be able to switch the transaction list between settled-only and original-currency views. |
| **B10-R3** | Adding two different currencies MUST raise rather than producing a total. |
| **B10-R4** | A multi-currency total MUST be presented per currency unless the user explicitly asked for conversion. |
| **B10-R5** | The user MUST be able to choose a base reporting currency, and every roll-up MUST render in it. |
| **B10-R6** | For any converted figure the user MUST be able to see the rate, its source, and its as-of date. |
| **B10-R7** | Rate providers MUST be consulted in priority order with a bundled offline provider as the final fallback. |
| **B10-R8** | Online rate fetching MUST be off by default. |
| **B10-R9** | Conversion MUST work with no network connection. |
| **B10-R10** | A repeatedly failing provider MUST be skipped for a period rather than retried on every request. |
| **B10-R11** | If every provider is unavailable, the caller MUST fall back to original currencies; a rate MUST NOT be invented. |
| **B10-R12** | Rates MUST be keyed by the date the feed reports, never by the current date. |
| **B10-R13** | A rate value outside a plausible range MUST be logged and skipped, not stored. |
| **B10-R14** | Cross-rates MUST be derived exactly from base-anchored pairs. |
| **B10-R15** | A multi-leg conversion's as-of date, source, and staleness MUST reflect the oldest leg. |
| **B10-R16** | The staleness threshold MUST accommodate a normal market weekend. |
| **B10-R17** | An account with no available rate MUST be excluded from the converted roll-up and MUST be named in the exclusion. |
| **B10-R18** | Rate values MUST be handled as exact decimals from the point they leave storage; a rate MUST NOT be represented as a floating-point number. |
| **B10-R19** | Current-snapshot and historical conversion MUST be distinct operations, and historical conversion MUST prefer the rate the transaction recorded. |
| **B10-R20** | Conversion to the same currency MUST short-circuit with no query and no rate disclosure. |

## Related

- [ADR-0009](../../../00-overview/decisions/0009-brick-money-multi-currency.md)
- [B1 Transactions](b1-transactions.md) · [C1 Dashboard](../c-insight/c1-dashboard.md)
- [C7 Report builder](../c-insight/c7-reports.md) — currency modes
- [G1 Privacy stance](../g-ux/g1-privacy.md) — online fetching is one of the optional outbound calls
