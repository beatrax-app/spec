# Roadmap

**Status:** Accepted · **Baseline verified:** 2026-07-27 against `nightworksio/beatrax`

---

## How to read this page

The product repository is a working codebase with seven years of nothing and
then fourteen months of a great deal. To keep "done" honest, this roadmap
anchors on one fact that is checkable rather than claimed:

> **The latest tagged release is the definition of done.**

At the time of writing that tag is **`v1.3.0`**, cut **2026-06-14**, and it sits
on `main`. Everything since then lives on the development line and is *landed
but unreleased* — real, tested, merged code that no user has yet been handed.

The roadmap therefore keeps three buckets strictly apart, and the
[version manifests](../70-operations/versions/) mirror the same split:

| Bucket | Meaning |
|--------|---------|
| **[Shipped](#shipped--v130-and-earlier)** | In `v1.3.0` or an earlier tag. A user running the latest release has it. |
| **[Landed, unreleased](#landed-but-unreleased--the-body-of-v20)** | Merged on the development line, not in any tag. This is the bulk of v2.0. |
| **[Remaining for v2.0](#remaining-before-v20-can-ship)** | Still outstanding. v2.0 cannot be cut until these close. |

Anything past that is [post-v2.0 backlog](#post-v20-backlog) and is explicitly
**not** v2.0 scope.

### The v1.4 → v2.0 promotion

The development line was originally numbered `release/v1.4`. It is being
**promoted to v2.0** and the branch retired. Two things force a major bump
rather than a minor one:

1. **A breaking data change already landed.** Category-linked pots are retired;
   envelope budgeting replaces them. On upgrade every category-linked pot is
   archived and its balance released to the account's unallocated pool, and the
   user must re-assign that money into envelopes by hand. Goal-linked pots are
   unaffected. See [ADR-0017](decisions/0017-envelope-budgeting-replaces-category-pots.md).
2. **The product's shape changed.** A single-machine dashboard became a
   multi-device, end-to-end-encrypted, peer-to-peer system with its own identity,
   transport, and at-rest-encryption stack. Calling that a minor release would
   understate it to the point of dishonesty.

The go-forward branching model is documented in
[70-operations/releasing.md](../70-operations/releasing.md): `main` is the
integration branch, `release/v1.4` is merged into it and deleted, and **v2.0 is
cut from `main`** inside the `beatrax-app` org. `release/v1.4` is not a living
branch and must not be documented as one.

---

## Shipped — `v1.3.0` and earlier

Seven tags exist: `v1.0.1-beta`, `v1.0.2-beta`, `v1.0.3-beta`, `v1.1.0`,
`v1.1.1`, `v1.2.0`, `v1.3.0`.

### The v1.0 line — the ledger and the chains

The founding capability set: idempotent multi-format ingestion, multi-currency
with original and settled amounts both preserved, cross-account chain
resolution, email-receipt ingestion, recurring detection with drift alerts,
30/60/90-day forecasting with what-if scenarios, and the operational layer
(backup/restore, doctor, system alerts, scheduler daemons).

Features: [A1](../10-functional/features/a-ingestion/a1-source-formats.md),
[A2](../10-functional/features/a-ingestion/a2-import-wizard.md),
[A3](../10-functional/features/a-ingestion/a3-idempotency.md),
[A4](../10-functional/features/a-ingestion/a4-email-scanning.md),
[A5](../10-functional/features/a-ingestion/a5-receipt-matching.md),
[B1](../10-functional/features/b-ledger/b1-transactions.md),
[B2](../10-functional/features/b-ledger/b2-categorisation.md),
[B4](../10-functional/features/b-ledger/b4-counterparties.md),
[B5](../10-functional/features/b-ledger/b5-chain-resolution.md),
[B6](../10-functional/features/b-ledger/b6-transfers.md),
[C2](../10-functional/features/c-insight/c2-recurring.md),
[C3](../10-functional/features/c-insight/c3-drift-alerts.md),
[C5](../10-functional/features/c-insight/c5-forecasting.md),
[F1](../10-functional/features/f-platform/f1-desktop-shell.md),
[F2](../10-functional/features/f-platform/f2-setup-wizard.md),
[F4](../10-functional/features/f-platform/f4-backup-restore.md),
[F5](../10-functional/features/f-platform/f5-dev-console.md),
[F6](../10-functional/features/f-platform/f6-updates.md).

### `v1.1` — runtime and packaging

PHP 8.5 runtime floor, desktop packaging across macOS / Windows / Linux, and
bounded persistence for large imports.

### `v1.2` — the first insight layer

Category budgets (the flat monthly ceiling that envelope budgeting later
replaced), the cash book, the net-worth roll-up, month-over-month spending
comparison, counterparty profiles with support-resource links, encrypted backup
and restore (Argon2id + XChaCha20-Poly1305), and the self-hosted server
deployment path — which is what later unblocked both the mobile peer and device
sync.

Features: [A7](../10-functional/features/a-ingestion/a7-cash-book.md),
[C1](../10-functional/features/c-insight/c1-dashboard.md),
[C9](../10-functional/features/c-insight/c9-community-corpus.md).

### `v1.3.0` "Local & in sync" — shipped 2026-06-14

The largest release to date; nine phases, forty-one plans.

| Delivered | Feature |
|-----------|---------|
| Base-currency FX conversion — pluggable, offline-capable rate sources | [B10](../10-functional/features/b-ledger/b10-multi-currency.md) |
| Savings goals with forecast-driven projected finish dates | [D2](../10-functional/features/d-money/d2-goals.md) |
| Savings pots / envelopes over a real account balance | [D3](../10-functional/features/d-money/d3-pots.md) |
| Responsive, installable PWA with an offline app shell | [G4](../10-functional/features/g-ux/g4-pwa.md) |
| PIN / biometric app-lock, and the at-rest key-unlock gate sync later consumes | [F3](../10-functional/features/f-platform/f3-auth-and-app-lock.md) |
| Bills / cash-flow calendar with a running projected balance | [C6](../10-functional/features/c-insight/c6-calendar.md) |
| Tax-deductible tagging and per-year CSV/PDF export | [D4](../10-functional/features/d-money/d4-tax.md) |
| Full-text search over all retained history (FTS5 trigram) + ⌘K palette | [B9](../10-functional/features/b-ledger/b9-search.md) · [G6](../10-functional/features/g-ux/g6-keyboard.md) |
| Unusual-charge / anomaly alerts | [C4](../10-functional/features/c-insight/c4-anomaly.md) |

At ship: 3 662 tests green, Larastan level 10 strict and Pint clean.

---

## Landed but unreleased — the body of v2.0

Every item below is merged and covered by tests on the development line. None
of it is in a tag. This is what a v2.0 release note will mostly consist of.

### The sync stack

The headline. Five phases, de-risked by a dedicated spike before anything
downstream committed.

| Landed | Feature | Decision |
|--------|---------|----------|
| Op-log / CRDT merge-layer spike validated against the live schema | — | [ADR-0014](decisions/0014-op-log-crdt-merge-engine.md) |
| Change capture + CRDT merge engine: signed append-only op-log, HLC ordering, SQLite as a deterministic materialised view | [E1](../10-functional/features/e-sync/e1-change-capture.md) | [ADR-0014](decisions/0014-op-log-crdt-merge-engine.md), [ADR-0015](decisions/0015-multi-master-p2p-sync.md) |
| Device identity + pairing: Ed25519 / X25519, QR and word-code, safety numbers | [E2](../10-functional/features/e-sync/e2-device-pairing.md) | [ADR-0015](decisions/0015-multi-master-p2p-sync.md) |
| Encrypted transport: Noise XX/IK, mDNS LAN-direct, zero-knowledge relay fallback | [E3](../10-functional/features/e-sync/e3-transport.md) | [ADR-0016](decisions/0016-noise-transport-zero-knowledge-relay.md) |
| At-rest encryption per device, device revocation, group-key rotation and re-wrap | [E4](../10-functional/features/e-sync/e4-at-rest-encryption.md) | [ADR-0018](decisions/0018-amounts-plaintext-at-rest.md) |
| Sync status and health surfaces | [E6](../10-functional/features/e-sync/e6-sync-status.md) | — |

A follow-on correctness pass (sixteen plans) closed the encryption
activation-surface gaps: every write site encrypts, every read, predicate, and
JSON parse decrypts before matching, and queued work that needs the key runs
where the key is.

### Budgeting parity — the "observe → operate" cluster

Five phases promoted from the backlog after a feature-gap comparison against
Actual Budget, and sequenced ahead of the rest of the milestone at the project
lead's request.

| Landed | Feature |
|--------|---------|
| Split transactions across multiple categories (the hard prerequisite for honest envelopes) | [B7](../10-functional/features/b-ledger/b7-splits.md) |
| Envelope (zero-based) budgeting: ready-to-assign pool, monthly grid, move-money, rollover, templates | [D1](../10-functional/features/d-money/d1-envelope-budgeting.md) |
| Account reconciliation with cleared status | [B8](../10-functional/features/b-ledger/b8-reconciliation.md) |
| General-purpose rules engine (multi-condition, multi-action, re-applicable) | [B3](../10-functional/features/b-ledger/b3-rules-engine.md) |
| Migration importers for YNAB4, nYNAB, and Actual Budget | [A8](../10-functional/features/a-ingestion/a8-migration-importers.md) |

### Notifications, open banking, reports, and the comment policy

| Landed | Feature |
|--------|---------|
| Notifications and reminders: four proactive triggers plus a persistent, deduplicated inbox with cross-device-synced read state | [C8](../10-functional/features/c-insight/c8-notifications.md) |
| Optional open-banking import connector: Enable Banking aggregator, bring-your-own-key, AIS-only, off by default | [A6](../10-functional/features/a-ingestion/a6-open-banking.md) |
| Custom report builder and saved reports (`/reports`), up to three pinned to the dashboard | [C7](../10-functional/features/c-insight/c7-reports.md) |
| Code-comment policy enforced by an architecture test, after a manual sweep of roughly 1 435 backend PHP files | [ADR-0011](decisions/0011-code-comment-policy.md) · [40-quality/code-comments.md](../40-quality/code-comments.md) |
| The single Public definition of "your current position", composed from other modules' Public seams | [C1](../10-functional/features/c-insight/c1-dashboard.md) |

---

## Remaining before v2.0 can ship

This is the whole outstanding list. Everything else is done.

### 1 — Mobile client as a fully synced peer

Ten of eleven plans are complete. The mobile client already holds its own
encrypted on-device copy, dials out over LAN with relay fallback, unlocks
biometrically, pairs camera-first with a word-code fallback, runs a blocking
resumable initial sync, and shows sync status.

**Outstanding:** the final plan — full surface-parity smoke test, the as-is
invariant, and real-device UAT on iPhone and Android.

That gate is taken. Real two-device pairing UAT ran on hardware on 2026-09-05
and passed twice from a clean install, so the "import from another device" flow
may be advertised as device-verified.

The other two hardware checks were taken on 2026-09-04, on an iPhone 12 mini
running iOS 26.5.2: the local-notification plugin fires a real OS banner, and
the on-device database is excluded from iCloud backup.

Feature: [E5](../10-functional/features/e-sync/e5-mobile-peer.md).

### 2 — App-store publishing and distribution

Not started; no plans written. The scope is genuinely undecided — see the
[open questions](#open-questions) below.

Feature: [F1](../10-functional/features/f-platform/f1-desktop-shell.md) covers
today's direct-download distribution; store distribution is additive to it.

### 3 — Release-readiness carry-over

Not phases, but they gate a tag. Tracked in
[70-operations/versions/2.0.0.toml](../70-operations/versions/2.0.0.toml) and in
the [definition of done](../40-quality/definition-of-done.md):

- A small set of known-latent risks recorded in the product repo's deferred
  register — chiefly the single global open-banking secrets file with no
  per-user keying, the single live Enable Banking session versus a
  per-connection schema, and desktop/mobile OS-keychain key custody being
  registered but unwired. Each is documented in the feature it belongs to.
- Cross-user isolation route probes for a handful of authenticated GET routes
  that were registered before their probes were written.
- The v2.0 upgrade note for the category-linked-pot retirement, which is a
  user-visible breaking change and needs release-note prominence.

---

## Post-v2.0 backlog

**Not v2.0 scope.** Listed so it is visible, not so it is scheduled.

| Item | Notes |
|------|-------|
| **Public API and scripting interface** | A local read plus scoped-write API for scripting and third-party integration, mirroring what Actual Budget offers. Must stay loopback-bound and token-gated — never off-machine — or it contradicts [P1](vision.md#p1--nothing-leaves-the-machine). Requirements undefined. |
| **SMTP-based password reset** | Deliberately deferred. Three SMTP-free reset paths already ship; adding outbound mail means an OAuth-scope upgrade, a deliverability surface, and an online-to-reset requirement. Reopens only on evidence the existing paths fail real users. See [ADR-0010](decisions/0010-recovery-codes-no-smtp.md). |
| **A real shared-household surface** | The schema has been multi-user-ready since the first phase, and the second-user activation is an authentication-and-UI change rather than a migration. But it is a milestone of its own, and it is blocked behind the per-user secret-isolation work listed above. See [ADR-0008](decisions/0008-multi-user-belongstouser.md). |
| **PostgreSQL** | Possible, not planned. No SQLite-specific schema features are used, so the migration stays a config change plus a dump and load. Shipping it pre-emptively would import every operational cost SQLite exists to avoid. See [ADR-0005](decisions/0005-sqlite-wal.md). |

---

## Open questions

Genuinely unresolved. Recorded here rather than guessed at.

### What is in scope for app-store publishing?

Phase 20 has a title and no plan. The open sub-questions:

- Which stores? The Mac App Store, the Microsoft Store, and the mobile stores
  are four different review processes with four different sandboxing
  constraints, and the mobile client's LAN-direct sync and background-pull
  behaviour interact with all of them.
- Does store distribution force paid signing identities, which
  [the licence rationale](../90-appendix/license-rationale.md#why-no-paid-signing-certificates)
  currently declines? A store listing may make that trade different.
- Does a sandboxed build still get an `~/Library/Application Support` path that
  survives upgrades, and does mDNS discovery survive the sandbox?

Nothing in the sources answers these. They must be answered before Phase 20 can
be planned.

### Does the codebase's own phase numbering carry into the spec?

It does not, and this spec deliberately does not use phase numbers as
identifiers. The product repo's planning corpus retires phase numbers 16 and 17
because they collide with a pre-existing numbering scheme in 310 commits from
May 2026. That constraint is real inside the product repo and irrelevant here —
the spec's identifiers are requirement IDs and ADR numbers, and they have no
relationship to phase numbers. Recorded so nobody tries to reconcile the two.

### Conflicting release-cadence documentation

The product repo's `.docs/cicd/release-cadence.md` still describes the `v0.x`
pre-public series and names `v1.0.0` as a future graduation tag. That document
predates four shipped releases and is stale. The
[releasing](../70-operations/releasing.md) page in this spec is the current
statement; the product-repo page needs updating or deleting when the repo moves
into the org.

---

## Related

- [70-operations/versions/](../70-operations/versions/) — the machine-readable
  manifests that lock each version's goals
- [70-operations/releasing.md](../70-operations/releasing.md) — branching, tagging,
  and the asymmetric publish rule
- [Vision](vision.md) — the principles that decide what does *not* get scheduled
- [Decisions](decisions/) — why each of the above is shaped the way it is
