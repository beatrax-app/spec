# E1 — Change capture and CRDT merge

**Status:** Accepted · **Area:** E — Sync and devices

---

## Purpose

The foundation every other sync feature stands on. Local changes are captured to
a signed, append-only log ordered by a clock that works without a coordinating
server; the database becomes a deterministic view of that log; and two devices
that have both moved on converge without either losing an edit.

The full reasoning is
[ADR-0014](../../../00-overview/decisions/0014-op-log-crdt-merge-engine.md), and
it was validated by a spike against the real schema before any downstream work
committed to it.

## Behaviour

### Every local change becomes a signed operation

A mutation is captured as an entry in an append-only log: what table, what row,
what field, what value, when. Each entry is signed by the device that produced
it with that device's own key ([E2](e2-device-pairing.md)).

Entries are written as plain data on the wire, unconditionally, so a schema skew
produces a loud decode failure rather than a silent type coercion. A stored null
is the tombstone sentinel and is never confused with a literal null value.

### Ordering without a server

Entries are ordered by a hybrid logical clock — a physical-time component plus a
counter — giving a total order across devices without anybody arbitrating, while
staying close to wall-clock time so a log remains readable when something goes
wrong.

### The database is a view of the log

The store can be rebuilt from scratch by replaying the merged log. This is a
**supported operation**, not a theoretical property: it is what a device does
after receiving a batch of older entries it had not seen, and it is trigger-safe
because the schema carries enforcement triggers.

### Merge is per table and per field

A central registry declares, per table, how each field merges:

| Strategy | Used for |
|----------|----------|
| **Last-writer-wins per field** | The default. Highest clock wins, resolved independently per column. |
| **Grow-only counter** | Monotonic counters, summed as the maximum observed per device. |
| **Observed-remove set** | Set-valued columns. |

Per-field resolution is the whole point: two devices, one renaming a
counterparty and one setting a category on the same row, both keep their edit.

Deletes win over concurrent edits by default, per table.

### Imported rows deduplicate by fingerprint

Two devices importing the same statement converge because the fingerprint
already made that idempotent ([A3](../a-ingestion/a3-idempotency.md)). The sync
layer inherits the property rather than reinventing it.

### The replayer never throws

An operation the replayer refuses goes to a **quarantine** with a reason, and
the session continues:

| Reason | Meaning |
|--------|---------|
| Wrong user | The entry is not for this user. |
| Unknown device | No key for the signing device. |
| Bad signature | The signature does not verify. |
| Unknown table | Not in the allow-list. |
| Incomplete creation | A row-create entry missing required fields. |
| Strategy error | The merge strategy failed. |
| Undecryptable | The payload could not be decrypted under any known key epoch. |

Every write the replayer performs carries an explicit user filter, and the
user-scope check is its **first** guard rather than a trust in the ambient
session.

Quarantined entries are visible on a read-only health surface so a problem is
observable rather than merely absent.

### Every write site must emit

A write that bypasses capture is invisible to peers, and the failure is silent on
the writing device. This is the standing hazard of the design and it is managed
three ways: the capture listener never throws (a capture failure must not break
the user's action), the merge registry is checked against the real schema by
test, and architecture tests constrain where writes may happen.

The registry drifting from the schema — a column added with no registry entry,
so it silently never syncs — is a real failure mode that has occurred, which is
why the schema-guard test exists.

### Compensating operations

Some changes cascade. A change that reclassifies linked rows emits a
compensating operation rather than relying on every peer re-deriving the
cascade, so peers converge on the same result rather than on their own
recomputation.

### The search index follows

The full-text index is refreshed as part of merge, so a row that arrives from a
peer is findable ([B9](../b-ledger/b9-search.md)).

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Two devices editing different fields of one row | Both edits survive. |
| Two devices editing the same field | Highest clock wins. |
| A delete concurrent with an edit | The delete wins, per the table's rule. |
| An entry signed by an unknown device | Quarantined. |
| An entry for another user | Quarantined on the first guard. |
| An entry for a table not in the allow-list | Quarantined. |
| An entry that cannot be decrypted | Quarantined; the session continues. |
| A capture listener failure | Swallowed; the user's action completes. |
| Two devices importing the same statement | Converge via the fingerprint. |
| A large backlog of older entries | A full rebuild replays them deterministically. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E1-R1** | Every local mutation MUST be captured as an entry in an append-only log. |
| **E1-R2** | Every entry MUST be signed by the originating device's own key. |
| **E1-R3** | Entries MUST be ordered by a hybrid logical clock giving a total order across devices without a coordinator. |
| **E1-R4** | Entry payloads MUST be encoded as plain data unconditionally; a schema skew MUST fail loudly. |
| **E1-R5** | A stored null MUST be the tombstone sentinel and MUST NOT be confusable with a literal null value. |
| **E1-R6** | The database MUST be reproducible by replaying the merged log from scratch, and rebuild MUST be a supported operation. |
| **E1-R7** | Rebuild MUST be safe in the presence of schema enforcement triggers. |
| **E1-R8** | Merge strategy MUST be declared per table and per field in a central registry. |
| **E1-R9** | Last-writer-wins MUST resolve independently per field, so concurrent edits to different fields of one row both survive. |
| **E1-R10** | Grow-only counter and observed-remove set strategies MUST be available. |
| **E1-R11** | Delete-wins behaviour MUST be configurable per table, defaulting to deletes winning. |
| **E1-R12** | Imported rows MUST deduplicate via the existing import fingerprint rather than a sync-specific mechanism. |
| **E1-R13** | The replayer MUST NOT throw; a refused entry MUST be quarantined with a reason. |
| **E1-R14** | Quarantine reasons MUST distinguish wrong user, unknown device, bad signature, unknown table, incomplete creation, strategy error, and undecryptable payload. |
| **E1-R15** | The user-scope check MUST be the replayer's first guard. |
| **E1-R16** | Every write the replayer performs MUST carry an explicit user filter. |
| **E1-R17** | Quarantined entries MUST be visible on a read-only health surface. |
| **E1-R18** | The capture listener MUST never throw; a capture failure MUST NOT break the user's action. |
| **E1-R19** | The merge registry MUST be verified against the real schema by test. |
| **E1-R20** | A cascading change MUST emit a compensating operation rather than relying on peers to re-derive the cascade. |
| **E1-R21** | The full-text index MUST be refreshed as part of merge. |
| **E1-R22** | A table not present in the allow-list MUST NOT be writable by the replayer. |

## Related

- [ADR-0014](../../../00-overview/decisions/0014-op-log-crdt-merge-engine.md) · [ADR-0015](../../../00-overview/decisions/0015-multi-master-p2p-sync.md)
- [E2 Device identity and pairing](e2-device-pairing.md) — the signing keys
- [E3 Transport](e3-transport.md) — how entries travel
- [E4 At-rest encryption](e4-at-rest-encryption.md) — how payloads are protected
- [E6 Sync status and health](e6-sync-status.md) — the quarantine surface
- [A3 Idempotency](../a-ingestion/a3-idempotency.md)
- [20-architecture/contracts/op-log.md](../../../20-architecture/contracts/op-log.md)
