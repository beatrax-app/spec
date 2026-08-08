# Vision

**Status:** Accepted

---

## The problem

Money does not move in straight lines. A single monthly Netflix charge can
touch four accounts: it is billed to PayPal, PayPal pulls from an ICS credit
card, ICS settles the whole month's card spend to the bank in one bulk SEPA
transfer, and the bank statement shows one anonymous debit for a figure that
matches nothing the user recognises.

Every account app shows one leg of that chain and calls it the whole picture.
The result is a monthly reconciliation puzzle that nobody has time to solve, so
nobody solves it — and the household's actual fixed cost, its actual funding
sources, and its actual runway all stay invisible.

## The core value

> **Show me, in one place, what I actually owe and where the money truly came
> from — across every account chain — so my monthly finances stop being a
> manual reconciliation puzzle.**

That sentence is the product. If everything else fails, Beatrax must still
surface the complete picture of monthly fixed payments and the funding chain
that connects them. It is carried verbatim from the product repo's own
`.planning/PROJECT.md`, and it is the tiebreaker for every scoping argument in
this spec.

## Who it is for

A single person, or a two-person household, managing their own finances across
several banks, cards, and payment processors. They are technically literate
enough to install a desktop application, grant read-only OAuth access to their
own mailbox if they want receipt scanning, and open a CSV when they need to.

Someone who banks exclusively with one institution that already has a good app
does not need Beatrax. Someone whose spending is split across several banks,
cards, PayPal, and app-store subscriptions — and who has given up reconciling
it by hand — is exactly who it is for.

## Principles

These are load-bearing. A feature that violates one is wrong even if users ask
for it.

### P1 — Nothing leaves the machine

Beatrax is local-first and local-only. No telemetry, no analytics, no crash
reporter, no cloud database, no remote account. The SQLite file, the OAuth
tokens, and the cached receipts live on the user's disk and never leave it
unless the user exports them.

The privacy story has to be *provable*, not promised. That is why the source is
published ([ADR-0003](decisions/0003-hippocratic-3-0-license.md)) and why the
outbound-call surface is small enough to enumerate — see
[G1 Privacy stance](../10-functional/features/g-ux/g1-privacy.md).

Full rationale: [ADR-0004](decisions/0004-local-only-hosting.md).

### P2 — Sync without a server that can read anything

Multi-device sync is the one place where the local-only promise is under
genuine pressure, and it is where most products quietly give up. Beatrax does
not. Devices sync peer-to-peer over the LAN; when a peer is offline the fallback
is a store-and-forward relay that only ever holds ciphertext it cannot decrypt.

"Encrypted at rest on our servers" is not the bar. The bar is that the relay
operator — including the maintainer — learns nothing but message sizes and
timing. See [ADR-0016](decisions/0016-noise-transport-zero-knowledge-relay.md)
and [E3](../10-functional/features/e-sync/e3-transport.md).

### P3 — Imports are idempotent, history is permanent

The same statement, re-imported, produces zero new rows. A stronger source
arriving later enriches the existing row rather than duplicating it, and the
provenance of every enrichment is appended, never overwritten.

History is retained forever. Multi-year subscription-drift analysis and
cross-account chain reconstruction are the product's differentiators, and both
depend on nothing ever being pruned. There is no retention job over ledger
rows.

See [A3 Idempotency and fingerprinting](../10-functional/features/a-ingestion/a3-idempotency.md).

### P4 — Precision over recall, and never a silent guess

The categoriser leaves a transaction uncategorised rather than assigning the
wrong category, because a wrong category silently mistrains the memory layer
and corrupts every downstream number. The chain resolver writes a *candidate*
for the user to confirm rather than auto-linking a weak match. The anomaly
detector suppresses a projection it cannot support with enough observations.

Wherever the system is unsure, it says so and offers the user a place to
decide. That place is a queue — triage, review, candidates — not a modal that
blocks the morning glance.

### P5 — Money arithmetic is exact

Every monetary value is an exact minor-unit integer plus a currency code,
handled through `brick/money`. Adding two currencies throws rather than
producing a plausible-looking nonsense total. Original and settled amounts are
both preserved so FX information can never be silently lost.

See [ADR-0009](decisions/0009-brick-money-multi-currency.md).

### P6 — Boundaries are enforced by tests, not by discipline

The module boundary, the dependency-injection rule, the state-machine sole-mutator
rule, the encrypted-column registry, and the comment policy are all enforced by
architecture tests that fail the build. Conventions that depend on reviewer
vigilance decay; conventions that fail CI do not.

See [ADR-0001](decisions/0001-modular-architecture.md),
[ADR-0002](decisions/0002-di-only-rule.md),
[ADR-0011](decisions/0011-code-comment-policy.md), and
[40-quality](../40-quality/).

### P7 — It informs; it never transacts

Beatrax tells the user that a subscription rose 40%, models what cancelling it
would do to their forecast, and links to the provider's own cancellation page.
It does not cancel anything, move money, or act on the user's behalf. The
optional open-banking connector is account-information-only by construction —
there is no payment-initiation scope in the code to enable.

## What success looks like

| Signal | Target |
|--------|--------|
| A new user reaches a populated dashboard | In one guided session, from statement files they already have |
| Re-importing last month's statement | Zero new rows, every time |
| The user can answer "what actually paid for this?" | From any leg of the chain, in one click |
| Outbound network calls in the shipped bundle, with all optional features off | Zero |
| A second device joins | Without any account, server, or maintainer involvement |
| A device is lost | Revoking it rotates the group key without the user re-pairing everything else |

## Non-goals

These are decided, not undecided. Re-proposing one needs an ADR that supersedes
the reasoning, not an issue.

| Non-goal | Why |
|----------|-----|
| **Cloud sync that can read the data** | Contradicts P1 and P2 outright. Sync is end-to-end encrypted and zero-knowledge or it does not ship. |
| **Telemetry, even opt-in** | The presence of the SDK is the leak. See [ADR-0004](decisions/0004-local-only-hosting.md). |
| **A remote error reporter** | Stack traces carry local variable contents — balances, merchant names, IBAN fragments. Scrubbing leaves too much residual risk. |
| **Acting on the user's behalf** | Auto-cancel, auto-switch, payment initiation. Violates P7. |
| **iCloud Mail ingestion** | Provider APIs only. There is no supported API; IMAP-era approaches are ruled out with `ext-imap`. |
| **A hosted multi-tenant service** | The product is a desktop application for one household. Every operational assumption in the architecture depends on that. |
| **LLM-based categorisation** | The explainability the deterministic matchers give up nothing worth having. Recorded in [B2](../10-functional/features/b-ledger/b2-categorisation.md). |

## What Beatrax is not

It is not a budgeting-first app that happens to import statements — the ledger
and the chain resolution came first, and envelope budgeting arrived on top of
them. It is not a bank aggregator: the recommended path is the statement files
the user's bank already exports, and the open-banking connector is an optional,
off-by-default convenience.

And it is not open source in the OSI sense. It is source-available under the
Hippocratic License 3.0, deliberately. See
[the licence rationale](../90-appendix/license-rationale.md).

## Related

- [Roadmap](roadmap.md) — where the product is now and what v2.0 still needs
- [Glossary](glossary.md) — the vocabulary this spec uses precisely
- [Feature catalogue](../10-functional/features/) — the behaviour this vision produces
- [Decisions](decisions/) — the record of every contested call
