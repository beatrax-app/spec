# Contract — versioning and compatibility

**Status:** Accepted

What a version number promises, and what a user upgrading is entitled to
assume.

## The scheme

Semantic versioning on the shipped product, with Beatrax's own reading of what
each component means for a **local-first application that holds the user's only
copy of their data**.

| Bump | Means |
|------|-------|
| **Patch** | Fixes only. No schema change that alters meaning, no behaviour change a user would notice, no contract change. |
| **Minor** | New capability. Additive schema changes. Existing data keeps its meaning. Older peers may not understand new features, but nothing breaks. |
| **Major** | Something a user must be told about: data whose meaning changed, a capability retired, or a wire contract that no longer interoperates. |

## What forces a major

**A user-visible data change.** The retirement of category-linked pots
([ADR-0017](../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md))
archives pots and releases balances, and the user must re-assign that money by
hand. Data changed meaning; that is a major.

**An operation-log contract break.** Changing a field's merge strategy, the
encoding, or the clock shape means two peers resolve the same conflict
differently ([op-log.md](op-log.md)). That is a major, and it needs a
coordinated upgrade path — not a silent divergence.

**Retiring a capability**, even where the data survives.

## What does not force a major

- Adding a table or a field, both registered.
- Adding a source format, a matcher, a rate provider, or a detector.
- Anything the user does not have to know about.

## Data compatibility

**Forward migrations only.** Migrations are append-only
([ARCH-R10](../README.md#the-arch-r-namespace)); a shipped migration is never
edited. A user upgrading runs new migrations on top of their populated database,
and the only way to guarantee they apply cleanly is for every change to be its
own forward step.

**There is no downgrade path.** A database migrated to a newer version is not
readable by an older one, and the honest response is a restore from a backup
taken before the upgrade ([F4](../../10-functional/features/f-platform/f4-backup-restore.md)).
Pretending otherwise would be worse.

**Data-shape changes ship as re-derivations.** The fingerprint version change is
the canonical example: a forward migration that re-derived every row, itself
idempotent, rather than an edit to the original.

## Peer compatibility

Two devices on different versions:

| Situation | Behaviour |
|-----------|-----------|
| Same major and minor | Full interoperation. |
| Newer peer sends an entry for a table the older does not know | The older quarantines it as unknown-table. It is not lost — it is quarantined, visible, and applied after the older device upgrades. |
| Newer peer sends a field the older does not know | Quarantined or ignored per the table's rule. |
| Either side has a different merge strategy for a field | **Incompatible.** A major bump and a coordinated upgrade. |
| Either side has a different encoding or clock shape | **Incompatible.** |

The quarantine is what makes version skew survivable rather than corrupting: an
older peer refuses what it cannot understand and says so, instead of guessing.

## The version string

The pushed tag is the **single source of truth**. The release workflow strips the
leading marker and exports it; the build reads it from there.

A build produced outside the pipeline sets nothing and self-identifies as a
development build, so there is never ambiguity about which path produced a
binary ([ADR-0019](../../00-overview/decisions/0019-asymmetric-release-publish.md)).

The health endpoint reports the application, runtime, and store versions, with
no timestamp, so an external probe can equality-check the whole body
([F6](../../10-functional/features/f-platform/f6-updates.md)).

## Specification versioning

This repository is **not** versioned by tag. It is continuously current, and its
requirement identifiers are permanent and never reused — which is what lets a
commit from any point in history cite one and have it still resolve.

Which requirements a release is committed to is expressed by the version
manifests in [70-operations/versions/](../../70-operations/versions/), not by a
tag on this repository.

## Related

- [op-log.md](op-log.md) — the wire contract a major protects
- [ADR-0017](../../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md) · [ADR-0019](../../00-overview/decisions/0019-asymmetric-release-publish.md)
- [70-operations/releasing.md](../../70-operations/releasing.md) · [70-operations/versions/](../../70-operations/versions/)
- [00-overview/roadmap.md](../../00-overview/roadmap.md)
