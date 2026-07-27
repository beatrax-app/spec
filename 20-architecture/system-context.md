# System context

**Status:** Accepted

What beatrax is, what it talks to, and what it deliberately does not.

## The system boundary

```text
                        ┌─────────────────────────────────────┐
                        │           THE USER'S MACHINE        │
                        │                                     │
  Statement files ─────▶│  ┌───────────────────────────────┐  │
  (CAMT.053, MT940,     │  │          beatrax              │  │
   CSV, card PDF,       │  │                               │  │
   processor CSV)       │  │   Laravel + Livewire, in a    │  │
                        │  │   desktop shell or a local    │  │
  Budget exports ──────▶│  │   environment                 │  │
  (YNAB, Actual)        │  │                               │  │
                        │  │   SQLite (WAL)  ── the whole  │  │
  Dropped receipts ────▶│  │   dataset, one file           │  │
  (.eml, .mbox)         │  │                               │  │
                        │  │   Secrets ── permission-      │  │
                        │  │   protected files             │  │
                        │  │                               │  │
                        │  │   Backups ── same machine     │  │
                        │  └───────────────────────────────┘  │
                        │                 │                   │
                        └─────────────────┼───────────────────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     │      THE ENUMERATED OUTBOUND SURFACE    │
                     │                                         │
                     │  Release manifest  (on, disableable)    │
                     │  Mail provider API (off by default)     │
                     │  Exchange rates    (off by default)     │
                     │  Open banking      (off by default)     │
                     │  Sync peers        (off until paired)   │
                     │  Sync relay        (off until set)      │
                     │  External links    (on user click)      │
                     └─────────────────────────────────────────┘
```

**With every optional feature off and update checking disabled, the box has no
outbound arrows at all.** That is the claim, and
[G1](../10-functional/features/g-ux/g1-privacy.md) is where it is stated as
requirements ([ARCH-R15](README.md#the-arch-r-namespace)).

## Actors

| Actor | Role |
|-------|------|
| **The household** | One or two people. There is no operator/user split — the person who installs it is the person who uses it. The only distinction is owner versus partner, and it exists only for account administration ([F3](../10-functional/features/f-platform/f3-auth-and-app-lock.md)). |
| **A paired device** | Another copy, equal in the merge, trusted because the user paired it ([E2](../10-functional/features/e-sync/e2-device-pairing.md)). |
| **A relay** | Optional, user-configured, ciphertext-only. It is not part of the system in any meaningful sense — it moves opaque bytes ([E3](../10-functional/features/e-sync/e3-transport.md)). |

There is no maintainer actor at runtime. Nothing the maintainer operates is in
any data path.

## External systems

| System | Relationship | Default |
|--------|--------------|---------|
| **The user's bank** | Produces files the user downloads. No integration. | Always |
| **A PSD2 aggregator** | The user's own account, machine-to-aggregator ([A6](../10-functional/features/a-ingestion/a6-open-banking.md)). | Off |
| **A mail provider** | The user's own grant, read-only ([A4](../10-functional/features/a-ingestion/a4-email-scanning.md)). | Off |
| **An exchange-rate source** | Optional; a bundled snapshot works offline ([B10](../10-functional/features/b-ledger/b10-multi-currency.md)). | Off |
| **The release host** | Signed manifests and binaries ([F6](../10-functional/features/f-platform/f6-updates.md)). | On |

## Deployment shapes

| Shape | Description |
|-------|-------------|
| **Desktop bundle** | The primary shape. A per-platform installer carrying its own runtime ([F1](../10-functional/features/f-platform/f1-desktop-shell.md)). |
| **Mobile client** | A native shell rendering the same interface, holding its own encrypted copy, syncing as a peer ([E5](../10-functional/features/e-sync/e5-mobile-peer.md)). |
| **Self-hosted** | The application on a machine the household controls, reached over their own network. Same code, different host. |
| **Local development** | The containerised toolchain. |

Every shape is loopback-bound by default and refuses non-loopback requests
([F6](../10-functional/features/f-platform/f6-updates.md)).

## Quality attributes, in priority order

1. **Privacy.** Structural, not policy. Trades against everything else and wins.
2. **Correctness of money.** Exact arithmetic, idempotent ingestion, no silent
   defaults. A wrong number is worse than no number.
3. **Durability.** History is never pruned; backup and restore are first-class;
   a second device is a second copy.
4. **Calm.** The daily loop is seconds. Attention is spent where something is
   wrong.
5. **Performance.** Bounded queries, bounded transactions, bounded scans — but
   never at the cost of the four above.

## What is deliberately absent

| Absent | Why |
|--------|-----|
| A server component | [ADR-0004](../00-overview/decisions/0004-local-only-hosting.md) |
| An account system | Nothing to authenticate against; identity is per device. |
| A message broker, a cache server, a search server | [ADR-0005](../00-overview/decisions/0005-sqlite-wal.md), [ADR-0007](../00-overview/decisions/0007-database-queue-driver.md) |
| A separate frontend application | Server-rendered; [ADR-0006](../00-overview/decisions/0006-nativephp-desktop-shell.md) |
| A model-inference component | [B2](../10-functional/features/b-ledger/b2-categorisation.md) |
| Payment initiation | Structurally absent; [ADR-0020](../00-overview/decisions/0020-open-banking-byo-key-ais-only.md) |

## Related

- [component-model.md](component-model.md) · [data-flow.md](data-flow.md) · [platform-matrix.md](platform-matrix.md)
- [G1 Privacy stance](../10-functional/features/g-ux/g1-privacy.md)
