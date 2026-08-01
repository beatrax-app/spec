# Feature catalogue

**Status:** Accepted

Fifty-two features across seven areas. This catalogue is the **contract the
technical spec is written against** — every architecture and implementation
decision must trace to a feature requirement here, not the other way round.

## How to read a feature doc

Each follows the same shape:

| Section | Contains |
|---------|----------|
| **Purpose** | What problem it solves, for whom. One or two paragraphs. |
| **Behaviour** | What the user sees and does, and what the system guarantees. Functional — no class names, no packages, no table names. |
| **States** | The states it can be in and what moves between them, where a lifecycle exists. |
| **Edge cases** | What happens when it goes wrong. Often the longest section, deliberately. |
| **Acceptance criteria** | Numbered, testable, RFC 2119. `A1-R1`, `A1-R2`, … |
| **Related** | Cross-links to neighbouring features, journeys, and decisions. |

### Requirement IDs

Requirements live **inside** their feature — there is no separate requirements
tree. An ID is `<feature>-R<n>`: `A1-R3` is the third acceptance criterion of
feature A1.

IDs are **permanent**. A requirement that is removed is marked *Withdrawn* in
place; its number is never reused. Tests, commits, and version manifests cite
these IDs.

### Where the behaviour came from

Every requirement in this catalogue is derived from the product repository —
its shipped code, its module documentation, its architecture decision records,
or its planning corpus. **Nothing here was invented.** Where a source is silent
or two sources disagree, the feature doc says so under an explicit *Open
question* heading rather than guessing.

The vast majority of this catalogue describes behaviour that **already
exists**. See the [roadmap](../../00-overview/roadmap.md) for what is shipped,
what has landed but is unreleased, and what is still outstanding.

## Audience

There is one: **the household**. A single person, or two people sharing an
install. There is no operator/end-user split, no administrator persona, and no
support team — the person who installs beatrax is the person who uses it.

The only meaningful distinction inside a household is **owner** versus
**partner**: the first account created is the owner, holds the developer flag,
and can create and reset the second account. That distinction appears only in
[F3](f-platform/f3-auth-and-app-lock.md).

---

## A — Ingestion

How money gets into beatrax. The most-used surface and the one that has to be
boringly reliable, because a bad import corrupts everything downstream.

| ID | Feature |
|----|---------|
| [A1](a-ingestion/a1-source-formats.md) | Source formats and parsers |
| [A2](a-ingestion/a2-import-wizard.md) | Import preview and confirm |
| [A3](a-ingestion/a3-idempotency.md) | Idempotency, fingerprinting and enrichment |
| [A4](a-ingestion/a4-email-scanning.md) | Email-receipt scanning |
| [A5](a-ingestion/a5-receipt-matching.md) | Receipt matching and chain hints |
| [A6](a-ingestion/a6-open-banking.md) | Open-banking import connector |
| [A7](a-ingestion/a7-cash-book.md) | Cash book — manual entry |
| [A8](a-ingestion/a8-migration-importers.md) | Migration from YNAB, nYNAB and Actual |
| [A9](a-ingestion/a9-starting-balances.md) | Starting balances and statement metadata |

## B — The ledger

The canonical record and everything that makes sense of it.

| ID | Feature |
|----|---------|
| [B1](b-ledger/b1-transactions.md) | Transactions, accounts and the ledger |
| [B2](b-ledger/b2-categorisation.md) | Categorisation and merchant memory |
| [B3](b-ledger/b3-rules-engine.md) | The rules engine |
| [B4](b-ledger/b4-counterparties.md) | Counterparties and triage |
| [B5](b-ledger/b5-chain-resolution.md) | Funding-chain resolution |
| [B6](b-ledger/b6-transfers.md) | Self-transfer pairing |
| [B7](b-ledger/b7-splits.md) | Split transactions |
| [B8](b-ledger/b8-reconciliation.md) | Reconciliation and cleared status |
| [B9](b-ledger/b9-search.md) | Full-text search |
| [B10](b-ledger/b10-multi-currency.md) | Multi-currency and FX conversion |

## C — Insight and alerts

What beatrax notices on the user's behalf.

| ID | Feature |
|----|---------|
| [C1](c-insight/c1-dashboard.md) | Dashboard and current position |
| [C2](c-insight/c2-recurring.md) | Recurring detection |
| [C3](c-insight/c3-drift-alerts.md) | Subscription drift alerts |
| [C4](c-insight/c4-anomaly.md) | Unusual-charge alerts |
| [C5](c-insight/c5-forecasting.md) | Cash-flow forecasting and scenarios |
| [C6](c-insight/c6-calendar.md) | Bills and cash-flow calendar |
| [C7](c-insight/c7-reports.md) | Report builder and saved reports |
| [C8](c-insight/c8-notifications.md) | Notifications and reminders |
| [C9](c-insight/c9-community-corpus.md) | Community merchant corpus |

## D — Money management

The features that move beatrax from *observe* to *operate*.

| ID | Feature |
|----|---------|
| [D1](d-money/d1-envelope-budgeting.md) | Envelope (zero-based) budgeting |
| [D2](d-money/d2-goals.md) | Savings goals |
| [D3](d-money/d3-pots.md) | Savings pots |
| [D4](d-money/d4-tax.md) | Tax tagging and per-year export |

## E — Sync and devices

The v2.0 headline. Local-first, end-to-end encrypted, peer-to-peer.

| ID | Feature |
|----|---------|
| [E1](e-sync/e1-change-capture.md) | Change capture and CRDT merge |
| [E2](e-sync/e2-device-pairing.md) | Device identity and pairing |
| [E3](e-sync/e3-transport.md) | Encrypted transport, LAN-direct and relay |
| [E4](e-sync/e4-at-rest-encryption.md) | At-rest encryption, revocation and rekey |
| [E5](e-sync/e5-mobile-peer.md) | The mobile client as a synced peer |
| [E6](e-sync/e6-sync-status.md) | Sync status and health |

## F — Platform

How beatrax runs, installs, protects itself, and recovers.

| ID | Feature |
|----|---------|
| [F1](f-platform/f1-desktop-shell.md) | Desktop shell and packaging |
| [F2](f-platform/f2-setup-wizard.md) | First-run setup wizard |
| [F3](f-platform/f3-auth-and-app-lock.md) | Authentication, app-lock and recovery |
| [F4](f-platform/f4-backup-restore.md) | Backup, restore and recovery |
| [F5](f-platform/f5-dev-console.md) | Developer mode and the dev console |
| [F6](f-platform/f6-updates.md) | Updates and release verification |
| [F7](f-platform/f7-data-locations.md) | Data locations, export and deletion |

## G — Cross-cutting UX

These are not screens. They are **properties every other feature must
exhibit**. G1 in particular is the one the whole product is judged on.

| ID | Feature |
|----|---------|
| [G1](g-ux/g1-privacy.md) | Privacy stance and the outbound-call surface |
| [G2](g-ux/g2-error-model.md) | Error and remedy model |
| [G3](g-ux/g3-accessibility.md) | Accessibility |
| [G4](g-ux/g4-pwa.md) | Responsive and installable PWA |
| [G5](g-ux/g5-plain-language.md) | Plain language and in-product help |
| [G6](g-ux/g6-keyboard.md) | Keyboard and command palette |
| [G7](g-ux/g7-localisation.md) | Interface localisation and language selection |

---

## The navigation this produces

The application's actual navigation, mapped to the features that own it:

| Surface | Feature |
|---------|---------|
| Dashboard | [C1](c-insight/c1-dashboard.md) |
| Transactions · Uncategorized · Rules | [B1](b-ledger/b1-transactions.md) · [B2](b-ledger/b2-categorisation.md) · [B3](b-ledger/b3-rules-engine.md) |
| Counterparties · Triage | [B4](b-ledger/b4-counterparties.md) |
| Chains · Chain review · Chain hints | [B5](b-ledger/b5-chain-resolution.md) |
| Reconcile | [B8](b-ledger/b8-reconciliation.md) |
| Recurring · Subscriptions | [C2](c-insight/c2-recurring.md) |
| Drift alerts · Unusual charges | [C3](c-insight/c3-drift-alerts.md) · [C4](c-insight/c4-anomaly.md) |
| Forecast | [C5](c-insight/c5-forecasting.md) |
| Calendar | [C6](c-insight/c6-calendar.md) |
| Reports | [C7](c-insight/c7-reports.md) |
| Notifications | [C8](c-insight/c8-notifications.md) |
| Budgets | [D1](d-money/d1-envelope-budgeting.md) |
| Goals · Pots | [D2](d-money/d2-goals.md) · [D3](d-money/d3-pots.md) |
| Tax | [D4](d-money/d4-tax.md) |
| Import · Migrations | [A2](a-ingestion/a2-import-wizard.md) · [A8](a-ingestion/a8-migration-importers.md) |
| Cash book | [A7](a-ingestion/a7-cash-book.md) |
| Inboxes | [A4](a-ingestion/a4-email-scanning.md) |
| Sync | [E6](e-sync/e6-sync-status.md) |
| Settings | across features; the platform ones in [F](f-platform/) |
| Dev Console | [F5](f-platform/f5-dev-console.md) |
| Command palette (⌘K) | [G6](g-ux/g6-keyboard.md) |

---

## Traceability

Three links, all of which CI checks:

```text
Journey  ──exercises──▶  Feature  ──contains──▶  Requirement  ◀──implements──  Code
                                                      ▲
                                                      └──cites──  Architecture doc
```

1. Every [journey](../journeys/) names the features it exercises.
2. Every feature owns numbered requirements.
3. Every architecture and per-repo doc cites the requirement IDs it satisfies.

**A technical decision that cites no requirement is unjustified**, and should be
challenged in review. That is the rule that keeps the technical spec written
*against* the features rather than alongside them.
