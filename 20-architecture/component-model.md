# Component model

**Status:** Accepted

Thirty-four modules. Each owns a slice of the domain, exposes a narrow public
surface, and is forbidden from reaching into another's interior
([ADR-0001](../00-overview/decisions/0001-modular-architecture.md),
[ARCH-R1](README.md#the-arch-r-namespace)).

## The modules

Grouped by the feature area they serve.

### Ingestion

| Module | Owns | Features |
|--------|------|----------|
| **Ingestion** | The canonical source-row shape, the per-format adapters, and the adapter registry. Writes nothing. | [A1](../10-functional/features/a-ingestion/a1-source-formats.md) |
| **Import** | The preview-and-confirm pipeline, the payment-type and starting-balance registries, merchant aliases, and the post-commit dispatch boundary. | [A2](../10-functional/features/a-ingestion/a2-import-wizard.md) · [A3](../10-functional/features/a-ingestion/a3-idempotency.md) |
| **EmailScan** | Mail-provider grants, per-inbox scan state and cursors, message storage, discovery. | [A4](../10-functional/features/a-ingestion/a4-email-scanning.md) |
| **Receipts** | Receipt matching, the matcher registry, chain-hint emission, file-import records. | [A5](../10-functional/features/a-ingestion/a5-receipt-matching.md) |
| **OpenBanking** | The optional aggregator connector: credentials, consent, fetch, and the remote adapter. | [A6](../10-functional/features/a-ingestion/a6-open-banking.md) |
| **CashBook** | Manual entry into the canonical ledger. | [A7](../10-functional/features/a-ingestion/a7-cash-book.md) |
| **Migration** | The one-time importer for competing budget tools, its staging tables, and the three-way merge. | [A8](../10-functional/features/a-ingestion/a8-migration-importers.md) |

### The ledger

| Module | Owns | Features |
|--------|------|----------|
| **Ledger** | Transactions, accounts, categories, merchants, import runs, currencies, statement summaries, splits. **The canonical store.** | [B1](../10-functional/features/b-ledger/b1-transactions.md) · [B7](../10-functional/features/b-ledger/b7-splits.md) · [B8](../10-functional/features/b-ledger/b8-reconciliation.md) |
| **Categorization** | The rule-based classifier, merchant memory, the triage queue, the rules surface, and receipt-conflict resolution. | [B2](../10-functional/features/b-ledger/b2-categorisation.md) · [B3](../10-functional/features/b-ledger/b3-rules-engine.md) |
| **Counterparties** | Counterparty resolution, the index, profiles, and triage. | [B4](../10-functional/features/b-ledger/b4-counterparties.md) |
| **Chains** | Funding-chain and settlement resolution, the chain ledger, the alias bridge, and the per-user resolver pass. | [B5](../10-functional/features/b-ledger/b5-chain-resolution.md) |
| **Transfers** | Self-transfer pairing. A matcher and a listener; no tables, no routes. | [B6](../10-functional/features/b-ledger/b6-transfers.md) |
| **Search** | The full-text index and the palette's backing service. | [B9](../10-functional/features/b-ledger/b9-search.md) |
| **FX** | Rate providers, the provider registry, and base-currency conversion. | [B10](../10-functional/features/b-ledger/b10-multi-currency.md) |

### Insight

| Module | Owns | Features |
|--------|------|----------|
| **Recurring** | Series detection, the series state machine, and the acknowledgement surface. | [C2](../10-functional/features/c-insight/c2-recurring.md) |
| **DriftAlerts** | Drift detection over series, the alert state machine, and the savings-insight surface. | [C3](../10-functional/features/c-insight/c3-drift-alerts.md) |
| **Anomaly** | Per-transaction unusual-charge detection, its own state machine, and suppression rules. | [C4](../10-functional/features/c-insight/c4-anomaly.md) |
| **Forecasting** | Projections, scenarios, percentile bands, and shortfall windows. | [C5](../10-functional/features/c-insight/c5-forecasting.md) |
| **Calendar** | The month-grid composition. Read-only. | [C6](../10-functional/features/c-insight/c6-calendar.md) |
| **Reports** | The report builder and saved reports. | [C7](../10-functional/features/c-insight/c7-reports.md) |
| **Notifications** | The deduplicated inbox, per-device preferences, and the trigger listeners. | [C8](../10-functional/features/c-insight/c8-notifications.md) |
| **Position** | The single public definition of "your current position", composed from other modules' public surfaces. Register-only: no routes, no views. | [C1](../10-functional/features/c-insight/c1-dashboard.md) |
| **Community** | The bundled merchant corpus, the support-resource corpus, and the opt-in contribution surface. | [C9](../10-functional/features/c-insight/c9-community-corpus.md) |

### Money management

| Module | Owns | Features |
|--------|------|----------|
| **Budgets** | Envelope assignments, moves, settings, and the carryover fold. | [D1](../10-functional/features/d-money/d1-envelope-budgeting.md) |
| **Goals** | Savings goals, progress, and projections. | [D2](../10-functional/features/d-money/d2-goals.md) |
| **Pots** | Virtual sub-balances and their movements. | [D3](../10-functional/features/d-money/d3-pots.md) |
| **Tax** | Tagging, the year view, the country corpus, and the exports. | [D4](../10-functional/features/d-money/d4-tax.md) |

### Sync

| Module | Owns | Features |
|--------|------|----------|
| **Sync** | The operation log, the clock, the merge registry and strategies, the replayer and rebuilder, device identity and pairing, the transport and relay, the encryption keyring and the sensitive-column registry. | [E1](../10-functional/features/e-sync/e1-change-capture.md)–[E4](../10-functional/features/e-sync/e4-at-rest-encryption.md) · [E6](../10-functional/features/e-sync/e6-sync-status.md) |
| **Mobile** | The mobile shell: first-launch bootstrap, biometric lock, camera pairing, initial-sync gate, and the outbound-only transport. | [E5](../10-functional/features/e-sync/e5-mobile-peer.md) |

### Platform

| Module | Owns | Features |
|--------|------|----------|
| **Core** | The user model, the user-scoping trait, the current-user and clock abstractions, alerts, preferences, the path authority, the health endpoint, and the install, diagnose, backup, restore, and prune commands. **The floor of the dependency graph — it imports from no other module.** | [F4](../10-functional/features/f-platform/f4-backup-restore.md) · [F6](../10-functional/features/f-platform/f6-updates.md) · [F7](../10-functional/features/f-platform/f7-data-locations.md) |
| **Auth** | Credentials, recovery codes, the owner/partner model, the app-lock, and biometrics. | [F3](../10-functional/features/f-platform/f3-auth-and-app-lock.md) |
| **Desktop** | The platform-shell quarantine: **every** shell import lives here and nowhere else. | [F1](../10-functional/features/f-platform/f1-desktop-shell.md) |
| **Onboarding** | The first-run wizard and its progress tracking. | [F2](../10-functional/features/f-platform/f2-setup-wizard.md) |
| **DevMode** | The developer gate and the dev console. | [F5](../10-functional/features/f-platform/f5-dev-console.md) |

## The shape of a module

```text
Modules/<Name>/
├── Public/       ← contracts, DTOs, events, services other modules MAY import
├── Internal/     ← actions, jobs, listeners, parsers, resolvers — NEVER imported elsewhere
├── Models/       ← other modules MAY use these directly, deliberately
├── Database/     ← per-module migrations, seeders, factories
├── Routes/       ← the module's own URL surface
├── Resources/    ← views and assets it owns
├── Providers/    ← its bindings, schedules, and component registrations
└── tests/        ← module-owned
```

A module may import another's **public** surface and its **models**. It may not
import another's **interior**. Models are a deliberate shared read seam
([ADR-0002](../00-overview/decisions/0002-di-only-rule.md)); only the global
accessor indirection is forbidden.

## The two boundary paths

**Contracts**, where one module needs a behaviour another owns. The consumer
declares the interface in its own public surface; the owner implements it; the
binding is wired in the owner's provider. The consumer never learns which class
implements it.

**Events**, where one module reacts to something another does. The owner raises
an event from its public surface; any consumer's listeners may subscribe. Once
another module listens, removing the event is a breaking change — which is why
events live in the public surface.

## Enforcement

| Mechanism | Catches |
|-----------|---------|
| **A custom static-analysis rule** | An import into another module's interior, at analysis time. It checks the declared namespace first, falling back to the filesystem path, and rejects **everything** outside the public and model namespaces — including directories that currently hold no classes, so a future module cannot silently gain a public surface. |
| **Architecture tests** | Cross-module imports, state-column mutators, forbidden global accessors, shell imports, path helpers, raw queries missing a user filter, per-registry contracts, and theme companions. |
| **Strict static-analysis rules** | The global-accessor ban. |

A violation fails the test run, which fails the pull-request gate.

## Related

- [ADR-0001](../00-overview/decisions/0001-modular-architecture.md) · [ADR-0002](../00-overview/decisions/0002-di-only-rule.md)
- [contracts/module-boundary.md](contracts/module-boundary.md)
- [data-flow.md](data-flow.md) · [data-model.md](data-model.md)
- [30-repos/beatrax.md](../30-repos/beatrax.md)
