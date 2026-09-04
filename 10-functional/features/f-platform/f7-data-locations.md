# F7 — Data locations, export and deletion

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

"Nothing leaves your machine" is only a meaningful promise if the user can point
at where their data is, take a copy of it, and delete it — without asking
anybody.

## Behaviour

### What is stored

| Kind | Contents |
|------|----------|
| **The database** | Transactions, accounts, categories, counterparties, rules, budgets, goals, pots, tags, alerts, notifications, the operation log, and derived state. |
| **Source artefacts** | The original files the user uploaded, and the raw messages the mail scanner pulled in. |
| **Secrets** | Open-banking connector credentials, in a filesystem-permission-protected directory. OAuth client secrets and token blobs are database columns, encrypted at rest. |
| **Backups** | Snapshots, on the same machine. |
| **Logs** | On disk, local only. |

Nothing else, anywhere.

### Where it is

A per-operating-system user-data directory in the shipped bundle, the project
directory in local development. Paths resolve through a **single path
authority** — enforced by architecture test — which is what makes the per-platform
redirection work at all.

The exact resolved paths are visible **inside the application**, with a copy
action for each. A documentation page that says where data *should* be is not
the same as the application telling you where it *is*.

### Secrets have two custody models, deliberately

Not every secret is kept the same way, and one rule generalised across both was
wrong for one of them.

**Open-banking connector credentials** live in a file outside the database, in a
filesystem-permission-protected directory. That is the stronger form and it is
what the rule was written for: those credentials are long-lived, and a database
that a user can copy, back up and hand to a support channel is the wrong place
for them.

**OAuth client secrets and token blobs** are database columns, encrypted at rest.
A mail connector's token is bound to the account row it belongs to, travels with
it, and is revoked by the provider rather than by deleting a file — so a column
is the right shape, and the protection is the encryption rather than the
location.

The second model is only as strong as the key, and the key is per-install only
because it is minted on first launch behind a sentinel
([REPO-R34](../../../30-repos/beatrax.md)) — every installation ships with the
same one baked in. So `REPO-R34`'s "minted" has to mean **verified**, not
attempted: a mint whose failure goes unnoticed, behind a sentinel stamped anyway,
retires the attempt for good and leaves the shipped key in place on that
install — encrypting its columns with a key every other installation also holds.
The requirement below states the storage rule; that one carries the weight.

### The bundle never writes into itself

Reinstalling or updating never touches user data, because user data is never
inside the installation directory.

### Nor does it carry the build machine's data

Writing is one direction. The other is what the artefact arrives with, and it is
a separate promise: a bundle can leave the build machine already holding data it
never had to write.

Both packagers produce a shipped artefact by **copying the working tree**, and
the only thing standing between a working directory and a shipped binary is an
exclusion list. `.gitignore` has no part in that copy, which is what makes the
failure quiet — a directory absent from `git status` reads as a directory that
is not there.

Two kinds of thing must never make the trip:

- **Build-time secrets.** A release pipeline materialises signing material into
  the tree and *then* runs the packager, so the key is present at the exact
  moment the copy is taken. Handling the signing passwords is not the same as
  handling the signing key; a bundle can be built by a correctly configured
  pipeline and still ship the credential that signs it.
- **Working-directory artefacts.** A developer's machine accumulates captured
  screens, dropped statements and generated output. None of it is the product,
  and all of it is a picture of a real ledger.

So the bound is an **explicit exclusion list**, named entry by entry, rather than
anything inferred from the repository. Inference is what failed: a directory can
be tracked while every file that ever appears in it is ignored, and a pattern
anchored to the project root never matches the same name one directory down.
Excluding a directory once names a directory; stating the rule is what catches
the next one.

### Retention

**Indefinite, by default.** Multi-year drift analysis, chain reconstruction, and
category trends all depend on the full history, and there is no job that prunes
ledger rows.

Two bounded exceptions apply to operational artefacts rather than user data:
backups are pruned on a documented schedule ([F4](f4-backup-restore.md)), and
notifications are pruned after a long window ([C8](../c-insight/c8-notifications.md)).
Failed-job records are pruned only on explicit command. Logs rotate daily and
are discarded after a bounded number of days. Alerts and audit rows are kept.

An operational artefact is something the product generated for its own running —
a backup, a notification, a log file, a failed-job record. A ledger table is
never one, and neither is anything a ledger row points at: a job that deletes
rows the ledger references is deleting user data, whatever it is called.

### Export

Two supported paths:

- **A backup file** — self-contained and openable by any compatible tool. Source
  artefacts live outside it, so a full archive means copying that directory too,
  and the documentation says so rather than implying the backup is everything.
- **A direct file copy**, with the application stopped, taking the database and
  its journal files as a unit. The backup path is preferred because it produces
  a consistent snapshot without stopping anything.

A single export action bundles the latest backup and the artefact directory into
one archive for users who want one click.

### Deletion

Two mechanisms, for two different asks.

**Deleting an account** is an in-application control, confirmed by password and
available to every account rather than only the first. It removes that account's
rows, files, recovery codes, sync identity and keyring, so a paired peer cannot
push the account back. It is specified in full by
[F8-R25](f8-app-store-distribution.md), because both mobile stores require an
application that offers account creation to offer account deletion.

**Deleting the data** is deleting the files, and that is deliberate: the user
owns the filesystem and the filesystem is authoritative. An in-application
control that removed rows while leaving the file behind would be worse than
nothing, which is why account deletion removes files too rather than only rows.

The documented procedure names every path: the database and its journal files,
the artefacts, the backups, the secrets.

**Uninstalling does not delete user data.** That is intentional: an accidental
uninstall must not destroy a multi-year history. Users who want full removal
delete the user-data directory explicitly, and the documentation states this
plainly rather than letting them discover it.

### Third parties

Nothing, by the application itself. The exceptions are exactly the optional
outbound calls the user enabled, enumerated in [G1](../g-ux/g1-privacy.md). With
every one of them off the only outbound call left is the update check, and with
that disabled too the application makes no network call at all — the same
carve-out [G1-R4](../g-ux/g1-privacy.md) states, rather than a stricter claim
this document cannot keep.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A user asking where their data is | The in-application page shows the resolved paths with copy actions. |
| An application update | User data is untouched. |
| A log file older than the rotation window | Discarded; logs are operational artefacts, not ledger history. |
| An uninstall | User data survives, by design and stated. |
| A backup copied to another machine | Opens, given a compatible store version. |
| A direct copy taken while running | May be stale relative to the journal; the backup path is the supported one. |
| Source artefacts | Not inside the backup; copying them is a separate documented step. |
| A signing key or a capture directory present in the tree at build time | Excluded by name from the packager's copy; `.gitignore` does not bound a build. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F7-R1** | Every storage path MUST resolve through a single path authority, enforced by architecture test. |
| **F7-R2** | The resolved paths MUST be visible inside the application with a copy action for each. |
| **F7-R3** | The bundle MUST NOT hold user data inside its own installation directory, neither written there at runtime nor carried there from the machine that built it. |
| **F7-R4** | Reinstalling or updating MUST NOT touch user data. |
| **F7-R5** | Ledger history MUST be retained indefinitely; no automatic pruning of ledger rows may exist. |
| **F7-R6** | Retention exceptions MUST be limited to operational artefacts — records the product generated for its own running, never a ledger table and never a row a ledger row references — and MUST be documented. |
| **F7-R7** | Open-banking connector credentials MUST live in a filesystem-permission-protected directory, never in the database. |
| **F7-R8** | A backup export MUST be self-contained for the database and openable by any compatible tool. |
| **F7-R9** | The documentation MUST state that source artefacts are outside the backup and MUST name the directory. |
| **F7-R10** | A single export action MUST bundle the latest backup and the artefact directory. |
| **F7-R11** | Deletion MUST be by removing files, and the procedure MUST name every path. |
| **F7-R12** | Uninstalling MUST NOT delete user data, and this MUST be stated plainly to the user. |
| **F7-R13** | The set of third parties any data reaches MUST be exactly the optional outbound calls the user enabled. |
| **F7-R14** | With every optional feature and the update check disabled, the application MUST make no outbound call. |
| **F7-R15** | A shipped bundle MUST NOT contain build-time secrets or working-directory artefacts from the machine that built it, and the copy that produces it MUST be bounded by an explicit exclusion list rather than by `.gitignore`. |
| **F7-R16** | An OAuth client secret or token blob held in the database MUST be encrypted at rest, never stored as a plaintext column. |

## Related

- [G1 Privacy stance](../g-ux/g1-privacy.md) — the enumerated outbound surface
- [F4 Backup, restore and recovery](f4-backup-restore.md)
- [ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md) · [ADR-0005](../../../00-overview/decisions/0005-sqlite-wal.md)
- [90-appendix/data-retention.md](../../../90-appendix/data-retention.md)
