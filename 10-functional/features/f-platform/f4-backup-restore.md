# F4 — Backup, restore and recovery

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

There is no cloud copy. There is no support team with a snapshot. If the file is
gone, the history is gone — and the history is what the product is for.

Backup therefore has to be genuinely reliable, restore has to be genuinely safe,
and the diagnostics have to tell the user something is wrong before it matters.

## Behaviour

### Backups are consistent, not just copies

A backup produces a consistent snapshot alongside live writes and verifies its
integrity afterwards. It is not a naive file copy, which under the store's
journal mode can be stale relative to the log.

A metadata sidecar records a data-version marker so an unchanged database can be
skipped rather than backed up identically every night. Files are written with
owner-only permissions, applied explicitly rather than left to the process
default.

Retention keeps a small number of recent daily backups plus a small number of
recent weekly ones. The policy is pure logic with no file access, so it is
testable on its own.

### Encrypted backups

A backup can be encrypted with a passphrase, using a memory-hard derivation and
authenticated chunked encryption, with a self-describing header carrying the
salt and the derivation parameters.

The construction is symmetric throughout with no asymmetric step, which means the
known quantum attacks against public-key cryptography have nothing to attack; a
256-bit symmetric key leaves a 128-bit post-quantum margin, and the memory-hard
derivation bounds brute force by memory rather than by cycles. A post-quantum key
exchange is deliberately **not** used — there is no recipient public key, and the
passphrase's entropy is the real floor.

### Restore ordering is the safety contract

1. Decrypt and integrity-check to a temporary location. A wrong passphrase or a
   corrupt backup fails **before** the live database is touched.
2. Take a pre-restore snapshot of what is about to be replaced. That snapshot is
   exempt from retention pruning.
3. Swap the file in atomically.
4. Verify integrity afterwards through the application's own connection, so the
   store's configuration is re-applied.

Restore additionally requires maintenance mode, or an explicit override, and an
explicit confirmation in a non-interactive context.

### A backup the running build cannot read

A backup carries a database, and a database has a shape the code around it
expects. Restoring one whose shape does not match the build reading it produces
no error and no refusal: the swap succeeds, the verification passes, and the
application then runs against a schema its own code does not match.

The two directions are not symmetric, and only one of them is recoverable.

**A backup from a newer build** names schema changes this one has never heard
of. Migrations only move forward, so there is no path from that database to a
shape this build can read. Nothing detects it either: a pending-migration check
asks whether each migration the build *has* was recorded as run, which a newer
database answers yes to for every one of them. The mismatch is invisible and
permanent.

**A backup from an older build** is missing schema changes this one has. Where
migrations run before the first request that database is brought forward, and
where they do not it is served against code that does not match it — a
difference between shells rather than a property of the restore.

So the restore compares before it swaps, and refuses both. The set of migrations
already recorded in the backup is what it compares: that set is inside every
backup ever taken, where a marker introduced now would be absent from all of
them and could only judge the ones written afterwards.

A refusal has to say which direction it is, because the two ask different things
of the reader — one is answered by installing a newer build, the other is not
answerable at all.

**What this costs.** A backup taken before an update cannot be restored after
one. That is the majority of backups a reader holds more than a few weeks, and
on a mobile install it is the common case rather than a corner: the restore
screen is reached from a fresh install, a fresh install is whatever version the
store is serving, and the reader cannot choose an older one. The cost is
accepted because the alternative on that path is a restore that reports success
and leaves the reader's ledger being read by code that does not match it. It is
recorded here rather than left to be discovered.

### A refusal the reader never sees

A restore that refuses has to refuse *to somebody*. A reason written to a
surface the flow does not arrive at is not a refusal the reader received, and
the same holds for the paths a successful restore reports — the location of the
pre-restore snapshot is the only record the reader has of their undo, and it is
worth nothing on a screen that never renders.

### Diagnostics

A doctor command walks a set of probes and reports. Probes cover the runtime
version against the declared minimum, the presence of expected tooling, the
store's journal and durability settings, backup freshness, and the search
index's health.

A probe **must never throw** — a diagnostic that crashes is worse than no
diagnostic. Exit codes distinguish clean, warning, and critical.

Backup staleness beyond a threshold raises a warning and a system alert, rate-
limited so it does not repeat every run.

### Alerts

Operator-facing alerts surface in a banner. They are ordered by severity with a
chronological tie-break, cover both user-scoped and installation-wide alerts, and
are **never deleted** — acknowledgement is a one-way stamp through a single
sanctioned writer.

A boot-time probe detects configuration drift on the store, de-duplicated so a
restart storm does not produce an alert storm.

### Installation

An install command runs pending migrations, creates the first account if absent,
and always raises the installed event so idempotent seeders re-run. Re-running it
does not overwrite an existing account's password.

It **refuses to run where the database path is inside a cloud-sync folder** — two
machines syncing one database file through a file-sync product is a corruption
guarantee, and the refusal is a real protection rather than a warning.

### Failed jobs

A prune command accepts a duration grammar. A zero duration is **rejected**,
because it would delete every record, and that is the kind of footgun a
maintenance command should refuse rather than confirm.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A missing backup file at restore | Aborts before touching the live database. |
| A wrong passphrase | Fails during decryption, before the live database is touched. |
| An unchanged database at backup time | Skipped via the data-version marker. |
| Tooling missing at diagnosis time | Warning, not failure. |
| A backup older than the threshold | Warning plus a rate-limited alert. |
| An install where the database path is under cloud sync | Refused. |
| A zero-duration prune | Rejected. |
| A restore in a non-interactive context without confirmation | Refused. |
| The application key sentinel present but the key absent | Short-circuits by sentinel; documented as an operator-recovery path. |
| A backup naming a schema change the build does not have | Refused before the live database is touched, naming the direction. |
| A backup missing a schema change the build has run | Refused the same way, naming the other direction. |
| A backup whose recorded schema changes match the build exactly | Restored. |
| A backup recording no schema changes at all | Restored — it carries no claim to check, and refusing would strand a fixture. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F4-R1** | A backup MUST produce a consistent snapshot alongside live writes and MUST verify integrity afterwards. |
| **F4-R2** | Backup files MUST be written with owner-only permissions applied explicitly. |
| **F4-R3** | A metadata sidecar MUST record a data-version marker enabling an unchanged database to be skipped. |
| **F4-R4** | Retention MUST keep a bounded set of recent daily and weekly backups, expressed as pure logic with no file access. |
| **F4-R5** | Encrypted backups MUST use a memory-hard derivation and authenticated chunked encryption with a self-describing header. |
| **F4-R6** | The encrypted-backup construction MUST be symmetric throughout; no asymmetric key exchange may be introduced. |
| **F4-R7** | Restore MUST decrypt and integrity-check to a temporary location before the live database is touched. |
| **F4-R8** | Restore MUST take a pre-restore snapshot, exempt from retention pruning, before swapping. |
| **F4-R9** | The swap MUST be atomic. |
| **F4-R10** | Post-restore verification MUST run through the application's own connection so store configuration is re-applied. |
| **F4-R11** | Restore MUST require maintenance mode or an explicit override, and an explicit confirmation in a non-interactive context. |
| **F4-R12** | A diagnostic probe MUST NOT throw. |
| **F4-R13** | Diagnostic exit codes MUST distinguish clean, warning, and critical. |
| **F4-R14** | Backup staleness beyond a threshold MUST raise a warning and a rate-limited alert. |
| **F4-R15** | Alerts MUST be ordered by severity with a chronological tie-break and MUST cover both user-scoped and installation-wide alerts. |
| **F4-R16** | Alerts MUST never be deleted by any retention, acknowledgement or maintenance path, and acknowledgement MUST be a one-way stamp through a single sanctioned writer. Deleting an account removes that account's own alerts with its other rows ([F8-R25](f8-app-store-distribution.md)); that is the only sanctioned removal. |
| **F4-R17** | Boot-time configuration-drift detection MUST be de-duplicated against restarts. |
| **F4-R18** | The install command MUST run migrations, create the first account if absent, and always raise the installed event. |
| **F4-R19** | Re-running install MUST NOT overwrite an existing account's password. |
| **F4-R20** | Install MUST refuse to run where the database path lies inside a cloud-sync folder. |
| **F4-R21** | The failed-job prune command MUST reject a zero duration. |
| **F4-R22** | The prune duration grammar MUST reject ambiguous units. |
| **F4-R23** | A restore MUST compare the schema changes recorded in the backup against those the running build carries, before the live database is touched, and MUST refuse a backup that names one the build does not have OR is missing one the build has run. The comparison MUST read the set already recorded in the backup rather than a marker added to new backups, which every backup a reader already holds would lack. A backup recording none MUST be restored rather than refused. |
| **F4-R24** | A refusal MUST name which direction the mismatch is, because installing a newer build answers one and nothing answers the other. |
| **F4-R25** | Every refusal a restore raises, and every path a successful restore reports, MUST reach a surface that renders it. A reason flashed to a screen the flow does not arrive at is not a refusal the reader received. |

## Related

- [ADR-0005](../../../00-overview/decisions/0005-sqlite-wal.md) · [ADR-0007](../../../00-overview/decisions/0007-database-queue-driver.md)
- [F7 Data locations, export and deletion](f7-data-locations.md)
- [F5 Developer mode](f5-dev-console.md) — where diagnostics surface in-app
- [E4 At-rest encryption](../e-sync/e4-at-rest-encryption.md) — backup precedes the conversion
- [J6 Recovery](../../journeys/j6-recovery.md)
- [70-operations/runbooks.md](../../../70-operations/runbooks.md)
