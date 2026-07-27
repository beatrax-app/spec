# ADR-0022: The schema is SQLite-only, including for self-hosting

**Status:** Accepted
**Date:** 2026-07-27
**Supersedes:** the portability claim in
[ADR-0005](0005-sqlite-wal.md#alternatives-considered) — "the migration path is
preserved: no SQLite-only schema feature is used". Its decision, SQLite in
write-ahead journal mode, stands and is reinforced.

## Context

ADR-0005 chose SQLite and, in rejecting PostgreSQL, recorded that the door was
left open: no SQLite-only schema feature was in use, so a move to a server
database would remain a Laravel-level concern.

That stopped being true, and nobody noticed because nothing tested it. Walking
the self-hosting instructions on a clean machine surfaced it: the shipped
`deploy/server/` stack runs `postgres:16-alpine`, and `artisan migrate` against
it fails on the first substantive table.

```text
SQLSTATE[42601]: syntax error at or near "NEW"
SQL: CREATE TRIGGER transactions_type_check_insert BEFORE INSERT ON transactions
     FOR EACH ROW WHEN NEW.type NOT IN (...) BEGIN SELECT RAISE(ABORT, '...'); END
```

A survey of the migrations found the coupling is not incidental:

| Feature | Migrations |
|---------|-----------|
| `RAISE(ABORT, …)` enum-guard triggers | **32** |
| An FTS5 virtual table for full-text search | 1 |

The triggers are a mechanical port — PostgreSQL wants a trigger function rather
than an inline body. **FTS5 is not.** Full-text search would have to be rebuilt
on `tsvector`, with its own indexing strategy, ranking behaviour and migration
of the existing index. That is a project, not a compatibility shim.

## Decision

**SQLite is the only supported database, in every deployment shape — desktop
bundle, mobile shell, and self-hosted server.** The schema may use SQLite
features freely, and does.

The self-hosting recipe ships SQLite. The PostgreSQL and MySQL options in the
deployment guide are withdrawn: they described something that could not work.

## Why this rather than making the schema portable

Portability was never a requirement of this product; it was a door left open in
case one appeared, and the door had already closed without anyone checking.
Re-opening it would mean rewriting search on a second engine to serve a use case
nobody has asked for — a single-person or two-person household running their own
copy is not a workload SQLite struggles with.

The honest position is the one the code already takes.

## Consequences

### Positive

- The deployment guide describes something that works. Anyone following it now
  reaches a running instance rather than a syntax error on the first migration.
- One database engine across every shape, so a bug reproduces everywhere and the
  test suite covers what ships.
- The schema can keep using the features it already relies on without a portability
  claim hanging over them.

### Negative

- **A server database is no longer a documented escape hatch.** An installation
  that outgrows SQLite has no supported migration path, and creating one would be
  the project described above.
- SQLite concurrency limits now apply to the self-hosted shape too. Write-ahead
  journal mode plus a busy timeout is the mitigation, and the workload — one
  household — is well inside it.

### Neutral

- Nothing changes for the desktop or mobile bundles, which were already SQLite.

## Revisit if

- A self-hosted deployment appears with genuine multi-writer concurrency, which
  would make the search rewrite worth costing rather than assuming.

## Related

- [ADR-0005](0005-sqlite-wal.md) — the store decision this reinforces
- [ADR-0004](0004-local-only-hosting.md) · [ADR-0007](0007-database-queue-driver.md)
- [20-architecture/data-model.md](../../20-architecture/data-model.md)
