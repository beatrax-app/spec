# Data retention

**Status:** Accepted

The data-handling contract the local-only posture implies: what is stored, where,
for how long, and how a user takes it away or destroys it.

The behavioural requirements are
[F7](../10-functional/features/f-platform/f7-data-locations.md); this page is the
long-form statement it points at.

## What is stored

| Kind | Contents |
|------|----------|
| **The database** | Every parsed transaction from every ingested statement, card statement, processor export, and matched receipt; accounts, categories, counterparties, rules, budgets, goals, pots, tax tags; and derived state — chain links, recurring detections, alerts, forecasts, notifications, the operation log. |
| **Source artefacts** | The original files the user uploaded and the raw messages the mail scanner fetched. |
| **Secrets** | Provider tokens and connector credentials, in a filesystem-permission-protected directory. **Never in the database.** |
| **Backups** | Snapshots, on the same machine. |
| **Logs and audit rows** | On disk, local only. |

**Nothing is stored elsewhere.** There is no cloud database, no analytics
endpoint, no error reporter, no telemetry pipeline
([ADR-0004](../00-overview/decisions/0004-local-only-hosting.md)).

## Where it lives

A per-operating-system user-data directory in the shipped bundle; the project
directory in local development; on-device application storage on mobile.

Paths resolve through a single authority
([ARCH-R8](../20-architecture/README.md#the-arch-r-namespace)), and **the exact
resolved paths are visible inside the application** with a copy action for each.
A document saying where data *should* be is not the same as the application
telling you where it *is*.

**The bundle never writes inside its own installation directory.** Reinstalling
or auto-updating never touches user data.

## How long it is kept

**Indefinitely, by default.**

The product's value — multi-year subscription-drift analysis, cross-account chain
reconstruction, historical category trends — depends on the full history being
available. **No job prunes ledger rows**
([P3](../00-overview/vision.md#p3--imports-are-idempotent-history-is-permanent)).

Three bounded exceptions apply to **operational artefacts**, not user data:

| Artefact | Policy |
|----------|--------|
| Backups | Pruned to a bounded set of recent daily and weekly snapshots. A pre-restore snapshot is exempt. The owner can keep more by copying them elsewhere. |
| Notifications | Pruned after a long window ([C8](../10-functional/features/c-insight/c8-notifications.md)). |
| Failed-job records | Pruned only on explicit command, which refuses a zero duration. |

Alerts, logs, and audit rows are kept.

## How a user exports

**A backup file.** Self-contained for the database, openable by any compatible
tool, portable across machines. **Source artefacts are not inside it** — copying
that directory is a separate, documented step, and the documentation says so
rather than implying the backup is everything.

**A direct file copy**, with the application stopped, taking the database and its
journal files as a unit. The backup path is preferred: it produces a consistent
snapshot without stopping anything.

A single export action bundles the latest backup and the artefact directory for
users who want one click.

## How a user deletes

**The only mechanism is deleting the files**, and that is deliberate. There is no
in-application wipe button, because the user owns the filesystem and the
filesystem is authoritative — a button that deleted rows while leaving the file
would be worse than nothing.

The documented procedure names every path: the database and its journal files,
the artefacts, the backups, the secrets.

**Uninstalling does not delete user data.** That is intentional — an accidental
uninstall must not destroy a multi-year history — and it is stated plainly rather
than left to be discovered.

## What reaches a third party

**Nothing, by the application itself.** The exceptions are exactly the optional
outbound calls the user enabled, enumerated in
[G1](../10-functional/features/g-ux/g1-privacy.md):

| Call | Reaches |
|------|---------|
| Mail scanning | The user's own mail provider, with the user's own grant. Tokens and message bodies reach nobody else. |
| Open banking | The user's own aggregator account, machine-to-aggregator. |
| Exchange rates | A rate source. No user data is sent — only a request for rates. |
| Update check | The release host. No user-identifying data beyond what any request carries. |
| Sync | The user's own devices, end-to-end encrypted. A relay, if configured, holds ciphertext it cannot read. |

With all of them off, **the application makes no outbound call**.

## What at-rest encryption does and does not do

It encrypts the identifying and descriptive columns. It does **not** encrypt
amounts, dates, account references, or the search index — aggregation and search
depend on them
([ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)).

An attacker with the database file but not the key sees a complete dated
per-account distribution of amounts and a plaintext shadow of descriptions.

**What it buys** is raising the cost of casual access to a copied file or a
cloud-backed device backup. It is not a defence against a determined attacker
with the file. The product's own copy says this
([40-quality/security.md](../40-quality/security.md)).

## Related

- [F7 Data locations, export and deletion](../10-functional/features/f-platform/f7-data-locations.md) · [G1 Privacy stance](../10-functional/features/g-ux/g1-privacy.md)
- [ADR-0004](../00-overview/decisions/0004-local-only-hosting.md) · [ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)
- [F4 Backup, restore and recovery](../10-functional/features/f-platform/f4-backup-restore.md)
