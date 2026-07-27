# Releasing

**Status:** Accepted

## Branching

**The default branch is the integration branch.** Work merges into it; releases
are cut from it.

There is no long-lived development branch. The former `release/v1.4` branch is
merged into the default branch and **retired** — it is not a living branch and
must not be documented as one
([REPO-R37](../30-repos/README.md#the-repo-r-namespace),
[00-overview/roadmap.md](../00-overview/roadmap.md#the-v14--v20-promotion)).

Historical release branches from earlier versions remain as history and receive
no new work.

The default branch is protected: linear history, signed commits, required
status checks, blocked force-push and deletion
([OPS-R19](README.md#the-ops-r-namespace)).

## Versioning

Semantic versioning, read as
[20-architecture/contracts/versioning.md](../20-architecture/contracts/versioning.md)
describes it. For a local-first application holding the user's only copy, a
**major** means something the user must be told about: data whose meaning
changed, a capability retired, or a wire contract that no longer interoperates.

**The next release is v2.0**, cut from the default branch inside the
`beatrax-app` organisation. Two things force the major: the retirement of
category-linked pots
([ADR-0017](../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)),
which changes what a user's data means and requires manual re-assignment; and
the arrival of a multi-device encrypted sync stack, which changes the product's
shape.

## Tags

| Shape | Channel | Publish behaviour |
|-------|---------|-------------------|
| `vX.Y.Z` | stable | Builds, smoke-tests, uploads, and creates a **draft**. A human reviews and publishes. |
| `vX.Y.Z-rc.N` | preview | Published immediately as a prerelease. |

The asymmetry is [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md):
a mistaken stable tag push costs a deleted draft, not a bad release in the
field.

There is no alpha tier. Anything needing a tester before stable rides the
preview channel.

**The pushed tag is the single source of truth for the version string**
([OPS-R1](README.md#the-ops-r-namespace)). The workflow strips the leading
marker and exports it; the build reads it there. A build produced outside the
pipeline sets nothing and self-identifies as a development build
([OPS-R2](README.md#the-ops-r-namespace)).

## Cutting a release

### Before the tag

- [ ] Every goal in the version manifest is satisfied
      ([versions/](versions/)).
- [ ] The changelog's unreleased section is complete and reads as **release
      notes**, in the user's language.
- [ ] Any breaking change has release-note prominence
      ([OPS-R12](README.md#the-ops-r-namespace)).
- [ ] The branch ruleset's required checks still name the jobs that actually run
      ([OPS-R18](README.md#the-ops-r-namespace)). A renamed job silently stops
      being required.
- [ ] Public screenshots reflect a version that exists
      ([60-brand/brand-rules.md](../60-brand/brand-rules.md#screenshots)).
- [ ] The definition of done's release section is clear
      ([40-quality/definition-of-done.md](../40-quality/definition-of-done.md#before-a-release)).

### The tag

Move the changelog's unreleased section under the version heading, commit,
sign, and push the tag.

### What the pipeline does

1. **Quality gate**, fail-fast across the runtime matrix.
2. **Three platform builds in parallel**, each installing or extracting its
   bundle, launching it, asking its health endpoint, and comparing the reported
   versions before upload.
3. **Publish**, only if all three succeeded: generate the update manifests with
   binary hashes, sign each manifest, and create the release with every binary
   and manifest attached — as a draft for stable, published for a release
   candidate.

### After the tag

- [ ] Verify the signed manifest **by hand**, using the recipe published for
      users. That reproducibility is what makes the chain trustworthy.
- [ ] Publish the draft, for a stable release.
- [ ] Announce ([notifications.md](notifications.md)).
- [ ] Mark the version manifest released, and plan the next
      ([staging.md](staging.md)).

## If something goes wrong

**A build fails.** Nothing is published — the publish step requires all three.
Fix and re-tag with a new patch version; do not move a tag.

**A bad release is already published.** Publish a fixed version. A yanked
manifest stops the updater offering it, but users who already installed it have
it — which is exactly why the draft step exists for stable.

**A tag was pushed by mistake.** Delete the draft. For a release candidate,
which publishes immediately, publish a corrected one.

## What is never overridable here

- Publishing without every platform build passing.
- Publishing without a signed manifest.
- Any update path that skips verification.

See [50-governance/overrides.md](../50-governance/overrides.md).

## Related

- [staging.md](staging.md) · [versions/](versions/) · [notifications.md](notifications.md)
- [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md)
- [40-quality/ci-cd.md](../40-quality/ci-cd.md) · [F6 Updates](../10-functional/features/f-platform/f6-updates.md)
