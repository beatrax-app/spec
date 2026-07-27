# ADR-0005: SQLite with WAL journal mode as the canonical store

**Status:** Accepted; the portability claim below is superseded by [ADR-0022](0022-sqlite-only-schema.md)
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

beatrax runs on one machine at a time. Concurrent write load is bounded by one
household's import cadence — a handful of statements per month, plus background
email scans every fifteen minutes, plus sync ops arriving from peers.

A real database server (PostgreSQL, MySQL) would have brought a separate process
to manage, run, back up, and upgrade across versions; a network port to
firewall; a connection-pool layer for an app that opens at most three
connections at once; and an operational story for users who install a desktop
app and would otherwise see "click to install". Adding a Postgres dependency
turns installation into a multi-component setup wizard.

The minimum value such a server would have added — concurrent writers,
distributed replicas, advanced query optimisation — is invisible to a
single-household dashboard.

SQLite ships with PHP, lives in a single file, requires no service manager, and
has been the Laravel default driver since Laravel 11. The remaining concern was
concurrency: a background queue worker plus a scheduler plus a web request all
want to read while one of them might be writing. SQLite's default
rollback-journal mode serialises readers and writers; WAL mode lets readers
proceed while a writer is active.

## Decision

- **Storage engine:** SQLite 3.45 or newer — whatever the development image
  ships, whatever the bundled runtime carries in the desktop installer.
- **Journal mode:** `WAL`, set once at database creation and re-asserted by the
  diagnostics command on every run. `PRAGMA synchronous=NORMAL` is paired with
  it — a full fsync per write is unnecessary for a single-household store with
  filesystem-level backup.
- **Database location:** the project directory in local development; the per-OS
  user-data directory in the shipped bundle, resolved through a single
  path-authority service so the file survives app upgrades.
- **Co-resident subsystems:** the application schema, the database queue tables,
  the database cache and lock tables, and the sessions table. One file, multiple
  table sets, one WAL.
- **Backups** use SQLite's `VACUUM INTO` to produce a consistent copy alongside
  live writes.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **PostgreSQL 16** | Every operational cost above, for capability the product does not need. *(This row claimed the migration path was preserved. It is not — thirty-two migrations use SQLite-only triggers and search is built on FTS5. See [ADR-0022](0022-sqlite-only-schema.md).)* |
| **MySQL / MariaDB** | Same rejection, plus a less clean framework-default story. |
| **SQLite with the default rollback journal** | The scheduler-plus-worker-plus-request concurrency produced "database is locked" errors during background jobs. WAL is the fix. |
| **A separate database file per subsystem** | The cross-file consistency story was more complex than the value it added, and the framework's database queue driver is happy sharing the application database. |

## Consequences

### Positive

- Installation is "double-click the installer". There is no second component.
- Backup is genuinely "copy one file", and the supported path handles the WAL
  correctly so the copy is consistent.
- The whole dataset, including the queue and cache, is captured atomically by
  one backup.

### Negative

- **Single-writer remains.** WAL allows readers during a write, but only one
  write transaction may be active. Long-running jobs commit in small
  transactions, and the chain resolver serialises itself per user with an
  overlap guard.
- **The queue driver choice is bounded by this.** Redis-based queues need a
  separate server, which violates the single-file posture. See
  [ADR-0007](0007-database-queue-driver.md).
- A direct file copy taken while the app is running can be stale relative to the
  WAL unless a checkpoint runs first. The supported backup path handles this;
  the naive copy does not, and the documentation has to say so.

### Neutral

- Migration to Postgres remains possible but is not planned. Laravel abstracts
  the driver and the schema uses no SQLite-specific features, so it stays a
  config change plus a dump and load.

## Revisit if

- A genuine multi-machine deployment with concurrent writers ever becomes a
  goal, which would contradict [ADR-0004](0004-local-only-hosting.md) and needs
  its own ADR first.

## Related

- [ADR-0007](0007-database-queue-driver.md) — uses this file as the queue store
- [ADR-0014](0014-op-log-crdt-merge-engine.md) — treats this file as a
  materialised view of the op-log
- [20-architecture/data-model.md](../../20-architecture/data-model.md)
- [F4 Backup, restore and recovery](../../10-functional/features/f-platform/f4-backup-restore.md)
