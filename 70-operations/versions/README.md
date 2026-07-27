# Version manifests

**Status:** Accepted

One file per version. The machine-readable record of what a release is committed
to delivering.

The procedure is [staging.md](../staging.md).

## The contract

| Field | Meaning |
|-------|---------|
| `version` | The release. Matches the eventual tag. |
| `status` | `planned` → `staged` → `releasable` → `released`, or `yanked`. |
| `repos` | Which repositories this version cuts. |
| `goals` | The requirement identifiers this version is committed to delivering. |

Every goal must be an identifier the specification defines
([OPS-R14](../README.md#the-ops-r-namespace)). Validation refuses otherwise.

Only one version may be `staged` or `releasable` at a time
([OPS-R15](../README.md#the-ops-r-namespace)).

## The manifests

| Version | Status | Notes |
|---------|--------|-------|
| [2.0.0](2.0.0.toml) | staged | The current train. Most goals already satisfied by landed, unreleased work. |
| [TEMPLATE](TEMPLATE.toml) | — | Copy this to start a new one. |

## Why earlier versions have no manifest

Releases up to and including v1.3.0 were cut **before** this specification
existed, under the product repository's own planning process. Reconstructing
manifests for them would mean back-filling identifiers against work already
shipped, which produces a document that looks authoritative and was written
afterwards — exactly the failure mode this specification exists to avoid.

What those releases delivered is recorded honestly in the
[roadmap](../../00-overview/roadmap.md#shipped--v130-and-earlier), traced to the
features it maps onto, and labelled as history rather than as a locked
commitment.

**v2.0 is the first version whose goals were locked in advance.**

## Adding one

1. Copy the template.
2. Fill in the version, the repositories, and the goals.
3. Leave the status as `planned` while the goals are still being drafted.
4. Stage it when the goals are settled and no other version is in flight.

## Related

- [staging.md](../staging.md) · [releasing.md](../releasing.md)
- [00-overview/roadmap.md](../../00-overview/roadmap.md)
- [20-architecture/contracts/versioning.md](../../20-architecture/contracts/versioning.md)
