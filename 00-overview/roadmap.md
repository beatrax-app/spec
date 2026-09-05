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

The phases and rulings still open are below. They are not the whole of what is
unsatisfied: an audit of every identifier in
[the v2.0 manifest](../70-operations/versions/2.0.0.toml) on 2026-09-05 found
thirty-six of its three hundred and thirty-nine goals unmet, two asserted but
unproven, and four outside what the repositories can decide. Most of those are
single requirements inside features that otherwise landed, so they are recorded
where they can be read against the goal they belong to rather than restated
here. **This page is not a second copy of that list**, and the sentence that
once stood here — "this is the whole outstanding list, everything else is
done" — was true of the phases and false of the requirements.

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

**Scope is decided: all four stores, and direct download is retained wherever it
remains possible.** The Mac App Store, the Microsoft Store, the App Store and
Google Play — and where a sandboxed store build and a direct-download build can
both ship for a platform, both ship. Store distribution is **additive**, not a
replacement ([ADR-0032](decisions/0032-all-four-stores-additive-to-direct-download.md)).

One of the four is not a submission. The desktop bundle embeds a static
interpreter and relies on two hardened-runtime relaxations to map it, and the
sandbox a Mac App Store build must run under ignores one of them, so that
listing needs a different runtime strategy before it needs a submission. It is
the largest unknown in this release. What the other three cost is not yet
measured, and the specification does not claim it is small
([F8](../10-functional/features/f-platform/f8-app-store-distribution.md)).

Feature: [F8](../10-functional/features/f-platform/f8-app-store-distribution.md),
with [F1](../10-functional/features/f-platform/f1-desktop-shell.md) covering the
direct-download channel this is additive to.

> **This page was the stale one, and by more than a ruling.**
> [F8](../10-functional/features/f-platform/f8-app-store-distribution.md) was
> accepted on 2026-09-04 with twenty-six requirements, a scope, and a finding
> that the paid-identity trade had already been made — while this section still
> read "not started; no plans written" and the open question below still asked
> which stores. A roadmap that lags an Accepted feature page by that much is a
> governance defect of its own: the feature page is authoritative about its own
> feature, and a reader who starts here is told the opposite of what is true.
> The same rot may sit elsewhere on this page.

### 3 — The three latent risks, no longer deferred

Three requirements were carried in the product repo's deferred register as
**accepted deferrals** — documented, unscheduled, and judged safe because v2.0
ships single-user with one bank connection. That judgement is reversed. All
three are in v2.0 scope and are being built now.

| Requirement | The risk it closes |
|-------------|--------------------|
| [A6-R20](../10-functional/features/a-ingestion/a6-open-banking.md#acceptance-criteria) | Per-connection credential storage. One live aggregator session exists system-wide, so linking a second bank rebinds the session to it. |
| [A6-R21](../10-functional/features/a-ingestion/a6-open-banking.md#acceptance-criteria) | Per-user credential keying. The connector's secrets file is global to the installation and warns rather than failing closed when a second user exists. |
| [F3-R33](../10-functional/features/f-platform/f3-auth-and-app-lock.md#acceptance-criteria) | Operating-system key custody on desktop and mobile. The adapters are registered and unwired, so the unlocked key follows session custody everywhere. |

What the deferral actually rested on was the product staying single-user and
single-bank — which is a **current limitation, not a design choice**
([ADR-0008](decisions/0008-multi-user-belongstouser.md)). Closing the three
removes the condition rather than the symptom, and it unblocks the
shared-household surface that was sitting behind `A6-R21` in the backlog below.

The requirements stay marked *(Open)* in their feature documents and the
"Known limitation" sections stay as written: the code is not merged, and the
work that merges it will propose its own wording. What changed here is the
schedule, not the state.

### 4 — Relayed device identity

[E2-R18, E2-R19, E2-R20 and E2-R21](../10-functional/features/e-sync/e2-device-pairing.md#acceptance-criteria)
— a confirmed device introducing another, the weaker grant that introduction
carries, and the two catch-up rules that stop an unverifiable author's
operations being dropped on the floor
([ADR-0027](decisions/0027-a-confirmed-device-may-introduce-another.md)) — are
in v2.0 scope and are being built now.

> **They were previously in neither bucket, and that was a defect in this
> page.** They appeared in neither the outstanding list above nor the
> [post-v2.0 backlog](#post-v20-backlog), and neither in
> [the v2.0 manifest's goals](../70-operations/versions/2.0.0.toml). A
> requirement in neither list is not "unclassified" — it is invisible: nothing
> schedules it, and nothing has declined it either. The buckets on this page
> only mean anything if every requirement is in exactly one of them, and four
> were in none. Recorded rather than quietly corrected, because the next
> requirement to fall through will fall through the same gap.

They stay marked *(Open)* in [E2](../10-functional/features/e-sync/e2-device-pairing.md)
for the same reason as the three above: the classification changed, the state
did not.

### 5 — Release-readiness carry-over

Not phases, but they gate a tag. Tracked in
[70-operations/versions/2.0.0.toml](../70-operations/versions/2.0.0.toml) and in
the [definition of done](../40-quality/definition-of-done.md). **This bucket now
has no outstanding items.**

The v2.0 upgrade note for the category-linked-pot retirement is **done**
([D3-R16](../10-functional/features/d-money/d3-pots.md#acceptance-criteria),
[OPS-R12](../70-operations/README.md)), as of 2026-09-05. The note is carried in
a commit's `BREAKING CHANGE:` footer — the only place prose can live in a body
generated from the commit history ([OPS-R11](../70-operations/README.md)) — and
the changelog configuration renders that footer in full at the top of the
release body rather than as one subject line among thousands. The app says it as
well: the cutover raises a one-time banner naming the amount released and the
pots it came out of, because the desktop updater renders no release notes of its
own and a phone takes its update from an app store, so neither reader would
otherwise be told that money they had set aside is now unallocated.

It had been outstanding since the retirement landed, and for that whole period
[the v2.0 manifest](../70-operations/versions/2.0.0.toml) listed that
requirement under a heading reading "(landed)" — one file away from this section
saying it was not. Nothing read either. That is what opened the manifest audit,
and `scripts/manifest_check.py` is what now refuses the two pages disagreeing.

The cross-user isolation route probes that stood here are **done**. The pass
enumerated all seventy-six authenticated `GET` routes against the live router
rather than against a list, probed or reasoned every one, and found and fixed a
real cross-user leak in the developer console's "Last command" tile on the way.
It is recorded as a defence in
[40-quality/security.md](../40-quality/security.md#the-threat-model) rather than
as an outstanding item, which is where a closed gap belongs.

---

## Post-v2.0 backlog

**Not v2.0 scope.** Listed so it is visible, not so it is scheduled.

| Item | Notes |
|------|-------|
| **Public API and scripting interface** | A local read plus scoped-write API for scripting and third-party integration, mirroring what Actual Budget offers. Must stay loopback-bound and token-gated — never off-machine — or it contradicts [P1](vision.md#p1--nothing-leaves-the-machine). Requirements undefined. |
| **SMTP-based password reset** | Deliberately deferred. Three SMTP-free reset paths already ship; adding outbound mail means an OAuth-scope upgrade, a deliverability surface, and an online-to-reset requirement. Reopens only on evidence the existing paths fail real users. See [ADR-0010](decisions/0010-recovery-codes-no-smtp.md). |
| **A real shared-household surface** | The schema has been multi-user-ready since the first phase, and the second-user activation is an authentication-and-UI change rather than a migration. Its blocker — the per-user secret isolation of `A6-R21` — is [now in v2.0 scope](#3--the-three-latent-risks-no-longer-deferred), so what keeps this out of v2.0 is its own size rather than a dependency. It remains a milestone of its own. See [ADR-0008](decisions/0008-multi-user-belongstouser.md). |
| **PostgreSQL** | Possible, not planned. No SQLite-specific schema features are used, so the migration stays a config change plus a dump and load. Shipping it pre-emptively would import every operational cost SQLite exists to avoid. See [ADR-0005](decisions/0005-sqlite-wal.md). |

---

## Open questions

Genuinely unresolved. Recorded here rather than guessed at.

### Does a sandboxed build keep its data, and can it still find a peer?

The two sub-questions the store-scope ruling did **not** settle, kept here
because they are the ones that could still change what a store build is allowed
to claim:

- Does a sandboxed build keep a user-data path that survives upgrades?
- Does local-network discovery survive the sandbox?

Neither is a call anybody can make. They are engineering unknowns, answerable
only by building a sandboxed bundle and measuring it, and the decision to ship
all four store listings is what makes them urgent rather than academic. A
capability that is dead under a sandbox may not be described in that platform's
listing ([F8-R26](../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria)),
so an unmeasured answer is a listing that cannot honestly be written.

*Which stores, and whether store distribution forces paid signing identities,
were the other two sub-questions here. Both are answered — see
[ADR-0032](decisions/0032-all-four-stores-additive-to-direct-download.md) and
section 2 above.*

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
