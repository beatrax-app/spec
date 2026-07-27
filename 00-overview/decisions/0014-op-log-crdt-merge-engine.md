# ADR-0014: A signed append-only op-log with HLC ordering; SQLite as a materialised view

**Status:** Accepted
**Date:** 2026-06-14

## Context

Multi-device sync ([ADR-0015](0015-multi-master-p2p-sync.md)) needs a merge
model. The store is SQLite ([ADR-0005](0005-sqlite-wal.md)) holding a
long-lived, append-mostly financial ledger where correctness is auditable
against the user's bank statement to the cent. The obvious approaches all have
known failure modes:

- **Row-level last-writer-wins over table snapshots** loses concurrent edits to
  different fields of the same row. Two devices, one renaming a counterparty and
  one setting a category, must both keep their edit.
- **Bidirectional diffing** requires a reference point both sides agree on,
  which is exactly what a partitioned, occasionally-connected peer set does not
  have.
- **A vector clock per row** grows without bound in device count and needs
  garbage collection nobody wants to design for a ledger that never prunes.
- **Wall-clock timestamps** are not a total order across devices with clock
  skew, and skew on a laptop that has been closed for a week is not small.

Because the merge model is the foundation every downstream sync phase builds on,
a dedicated spike ran **first**, against the live schema rather than a toy one,
and had to produce a go/no-go finding before anything committed to it. It did.

## Decision

The op-log is the source of truth; SQLite is a deterministic materialised view of
it.

- **Every local mutation is captured** to an append-only log of operations. Each
  entry is signed by the device that produced it with that device's Ed25519 key
  ([ADR-0015](0015-multi-master-p2p-sync.md)).
- **Ordering is by Hybrid Logical Clock** — a `(physical-millis, counter)` pair
  that gives a total order across devices without a coordinating server and
  stays close to wall-clock time, so an op-log is still human-readable when
  debugging.
- **The database is reproducible** by replaying the merged log from scratch. A
  full rebuild is a supported operation, not a theoretical property, and it is
  what a device does after receiving a batch of older ops it had not seen.
- **Merge strategy is per-table and per-field**, declared in a central registry:
  - *Last-writer-wins per field* is the default. Highest HLC wins, resolved
    independently per column, so the two-devices-two-fields case above works.
    A null value is the tombstone sentinel.
  - *Grow-only counter* for monotonic counters, summed as the maximum observed
    per device.
  - *Observed-remove set* for set-valued columns.
  - Deletes win over concurrent edits by default, per table.
- **Imported rows deduplicate on the existing fingerprint**
  ([A3](../../10-functional/features/a-ingestion/a3-idempotency.md)) rather than
  through the merge layer. Two devices importing the same statement converge
  because the fingerprint already made that idempotent — the sync layer inherits
  the property rather than reinventing it.
- **The replayer never throws.** An op it refuses to apply goes to a quarantine
  table with a reason: wrong user, unknown device key, forged signature, unknown
  table, incomplete row creation, undecryptable payload. A poisoned or
  malformed op degrades one row, never the sync session.

Every op is written as JSON on the wire, unconditionally, so a schema skew
produces a loud decode failure rather than a silent type coercion.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Row-level LWW over snapshots** | Loses concurrent edits to different fields. The failure is silent, which for a ledger is disqualifying. |
| **An off-the-shelf CRDT database** | Would replace SQLite, which means replacing the entire query surface, the money casts, the FTS index, and the migration history. The value is in the merge semantics, not the storage engine. |
| **Vector clocks per row** | Unbounded growth in device count over a history that is never pruned. |
| **Server-mediated ordering** | There is no server ([ADR-0004](0004-local-only-hosting.md)). |
| **Wall-clock timestamps** | Not a total order under clock skew, and skew is large in practice on laptops. |

## Consequences

### Positive

- Concurrent edits to different fields of the same row both survive, which is
  the case users actually hit.
- The database can be rebuilt from the log, which makes "did the merge do the
  right thing?" answerable rather than a matter of trust.
- The quarantine table is an observable, debuggable failure surface rather than
  an exception that kills a session.

### Negative

- **Every write site must emit an op.** A write that bypasses the capture
  listener is invisible to peers, and the failure is silent on the writing
  device. Architecture tests and a per-table merge registry constrain this, but
  it is the standing hazard of the design.
- **The registry can drift from the schema.** A column added without a
  corresponding registry entry simply does not sync, again silently. A
  schema-guard test exists precisely because this happened.
- **Storage grows with the op-log**, on top of a ledger that is already never
  pruned.
- Rebuild is not free on a large history, and it has to be trigger-safe because
  the schema carries enforcement triggers.

### Neutral

- The log is per-user-scoped like everything else
  ([ADR-0008](0008-multi-user-belongstouser.md)), and the replayer enforces that
  scope as its first guard rather than trusting the ambient session.

## Revisit if

- A merge strategy beyond the three implemented ones is needed often enough that
  the registry stops being expressive.
- Op-log growth becomes a real storage problem on multi-year histories, which
  would mean designing compaction — a new ADR, because compaction and
  "reproducible from the log" are in tension.

## Related

- [ADR-0015](0015-multi-master-p2p-sync.md) · [ADR-0016](0016-noise-transport-zero-knowledge-relay.md)
- [ADR-0018](0018-amounts-plaintext-at-rest.md)
- [E1 Change capture and CRDT merge](../../10-functional/features/e-sync/e1-change-capture.md)
- [20-architecture/contracts/op-log.md](../../20-architecture/contracts/op-log.md)
