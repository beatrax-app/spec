# ADR-0007: Database queue driver in the shipped bundle; Horizon is dev-only

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

beatrax runs background work: chain resolution per user, email-scan backfill,
drift and anomaly re-evaluation, forecast recomputation, notification triggers,
sync catch-up. Laravel gives a clean abstraction over queue drivers and the
application code is driver-agnostic. The choice of driver is an operational
decision, and it changes per deployment surface.

In local development the developer already has Docker available, and the queue
dashboard is a useful debugging surface. In the shipped desktop bundle
([ADR-0006](0006-nativephp-desktop-shell.md)) Redis cannot ship — it would
require either bundling a Redis binary inside the distribution (large,
platform-specific, operationally painful) or asking end users to install Redis
themselves, which is a non-starter for a double-click install.

The SQLite database ([ADR-0005](0005-sqlite-wal.md)) is already on disk, already
in WAL mode, and the framework's database queue driver stores jobs in the same
file alongside the application schema. For one household at the projected job
rate, SQLite handles the queue tables cleanly.

## Decision

- **Shipped desktop bundle:** the `database` queue connection. Jobs land in the
  standard queue tables in the same SQLite file as the application schema. The
  `database` cache driver uses the same file, which matters because overlap
  locks on scheduled jobs live in the cache-lock table.
- **Local development:** the same default. A developer-only runtime override may
  switch to Redis and start the queue dashboard; the dashboard's embedded view
  is gated on that flag.
- **The queue dashboard is development-only.** Its service provider early-exits
  unless both the runtime flag and the Redis connection are set, and an
  architecture invariant forbids any production code path from importing a
  dashboard symbol.
- **Workers in the bundle:** the shell launches a long-running queue worker in
  its child-process slot. Equivalent launch-agent templates ship for local
  development and self-hosted deployment.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Bundle Redis inside the distribution** | Large, platform-specific, operationally hostile to non-technical users. |
| **Ask users to install Redis themselves** | The double-click-to-install target dies the moment a setup wizard appears. |
| **Ship the queue dashboard in Docker as an optional add-on** | Same UX problem one layer up, plus a documentation burden for a feature most users will never enable. |
| **Ship the dashboard's UI without its Redis dependency** | Not technically possible without rewriting its storage layer. |

## Consequences

### Positive

- **One operational surface, not two.** Users never install or configure Redis.
  Data, queue, and cache all live in one file, and one backup captures all three
  atomically.
- Failed-job visibility without a dashboard: a developer-mode page reads the
  failed-jobs table directly and covers the inspect-and-retry path real users
  need. Sparser than the dashboard, sufficient.

### Negative

- **A job-rate ceiling.** The driver tops out well above the projected rate but
  far below what Redis would give. If a future feature pushes past it, the
  abstraction allows swapping drivers per deployment — but the dashboard would
  return only as a developer surface, never in the shipped bundle.
- Queue polling costs a periodic SQLite read even when idle.

### Neutral

- Overlap locks and unique-until-processing locks work identically on both
  backends, so the developer override does not change job semantics.

## Revisit if

- Sync catch-up or a future import path pushes sustained job rates into the
  hundreds per minute on a real user's machine.

## Related

- [ADR-0005](0005-sqlite-wal.md) — the storage backing the queue tables
- [ADR-0006](0006-nativephp-desktop-shell.md) — the bundle that cannot carry Redis
- [F5 Developer mode and dev console](../../10-functional/features/f-platform/f5-dev-console.md)
- [F4 Backup, restore and recovery](../../10-functional/features/f-platform/f4-backup-restore.md)
