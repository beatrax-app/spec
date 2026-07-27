# Contract — the operation log

**Status:** Accepted

The wire and storage contract for change capture and merge. Two devices running
different builds must still converge, so this contract is what a version bump
has to stay compatible with.

The reasoning is
[ADR-0014](../../00-overview/decisions/0014-op-log-crdt-merge-engine.md).

## The entry

An entry identifies **what changed, on which row, to what value, when, and by
whom**:

| Element | Contract |
|---------|----------|
| **Table and row** | The table must be in the replayer's allow-list; an entry naming anything else is quarantined. |
| **Operation kind** | Row creation, field set, or delete. |
| **Field and value** | For a field set. |
| **Clock** | A physical-time component plus a counter. |
| **Device** | The originating device identifier. |
| **Signature** | Over the entry, by the originating device's signing key. |
| **Key epoch** | Which encryption generation the payload belongs to, where the field is encrypted. |
| **User** | The owning user. Checked **first** by the replayer. |

### Encoding rules

- **Values are always encoded as plain data on the wire, unconditionally.** A
  schema skew produces a loud decode failure rather than a silent coercion.
- **A stored null is the tombstone sentinel.** It is never confusable with a
  literal null: an encoded literal null decodes to a value, not to an absent
  one. This distinction has its own test.
- **Deleting a field means setting it to the sentinel**, not omitting it.

## Ordering

Entries order by clock: physical component first, then counter, then a stable
tie-break. That gives a total order across devices with no coordinator, while
staying close to wall-clock time so a log remains readable during debugging.

Clock state is persisted, so a restart does not reset the counter and produce
entries that sort behind ones already sent.

## The merge registry

Per table, and per field within it:

| Strategy | Semantics |
|----------|-----------|
| **Last-writer-wins per field** | Highest clock wins, resolved independently per column. The default. |
| **Grow-only counter** | The sum of the maximum observed value per device. |
| **Observed-remove set** | Set semantics with observed-remove tombstones. |

An unregistered field defaults to last-writer-wins.

Per table:

- **Delete wins.** Whether a delete beats a concurrent edit. Defaults to yes.
- **Creation required.** Whether a field set against a non-existent row is
  applied or quarantined as an incomplete creation.

**The registry must be verified against the live schema by test.** A column added
without a registry entry silently never syncs — a real failure mode that has
occurred, and the reason the schema guard exists
([ARCH-R12](../README.md#the-arch-r-namespace)).

## The replayer contract

The replayer **never throws**. An entry it refuses is quarantined with a reason.

Guards, in order:

1. **User scope.** First, always. Not a trust in the ambient session.
2. **Table allow-list.**
3. **Signature**, against a **confirmed** device's key.
4. **Decryption**, under a known key epoch.
5. **The strategy** for the field.

| Quarantine reason | Meaning |
|-------------------|---------|
| Cross-user | Not this user's entry. |
| Missing device key | No confirmed device matches. |
| Forged signature | Verification failed. |
| Unknown table | Not in the allow-list. |
| Incomplete creation | Field set against a non-existent row where creation is required. |
| Strategy error | The merge strategy failed. |
| Decrypt failed | No known epoch decrypts the payload. |

Every write the replayer performs carries an explicit user filter.

Quarantined entries surface on a read-only health view
([E6](../../10-functional/features/e-sync/e6-sync-status.md)). The view is
read-only by design: a quarantined entry is evidence of a defect, and the right
response is to fix the defect.

## Rebuild

The database must be reproducible by replaying the merged log from scratch. It
is a supported operation, not a theoretical property, and it must be safe in the
presence of schema enforcement triggers — which means re-installing them around
the rebuild rather than fighting them.

## Framing

The transport frames entries with a length prefix and hard caps on both frame
size and entries per frame ([E3](../../10-functional/features/e-sync/e3-transport.md)).
Catch-up exchanges from a watermark rather than re-sending the whole log, with a
bound on frames per session.

## Compatibility

| Change | Compatible? |
|--------|-------------|
| Adding a table to the allow-list and the registry | Yes. Older peers quarantine its entries as unknown-table; newer peers apply them. |
| Adding a field with a registered strategy | Yes. |
| Changing a field's strategy | **No.** Two devices would resolve the same conflict differently. Needs a coordinated version change. |
| Changing the encoding | **No.** |
| Changing the clock shape | **No.** |
| Removing a table from the allow-list | **No.** Entries in flight would quarantine. |

The compatible cases are additive; the incompatible ones all change how a value
is *interpreted*, which is exactly what two peers must agree on.

## Related

- [ADR-0014](../../00-overview/decisions/0014-op-log-crdt-merge-engine.md) · [ADR-0015](../../00-overview/decisions/0015-multi-master-p2p-sync.md) · [ADR-0018](../../00-overview/decisions/0018-amounts-plaintext-at-rest.md)
- [E1 Change capture](../../10-functional/features/e-sync/e1-change-capture.md)
- [versioning.md](versioning.md)
- [data-model.md](../data-model.md)
