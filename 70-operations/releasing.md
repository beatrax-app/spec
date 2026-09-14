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
| `vX.Y.Z-<prerelease>` | preview | Published immediately as a prerelease. Any semver prerelease identifier — `-rc.1`, `-beta`, `-develop`. |

**The hyphen is what decides the channel.** A tag with a prerelease identifier
is a preview; one without is stable. The identifier itself carries no meaning to
the pipeline — it is there for the humans reading the release list, so name it
for what the build is (`-rc.1` before a release, `-develop` for a snapshot off
the integration branch).

The asymmetry is [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md):
a mistaken stable tag push costs a deleted draft, not a bad release in the
field. That record's examples predate this generalisation and name `-rc.N`
specifically; the decision it records — stable drafts, previews publish — is
unchanged.

There is **one** preview channel, not a tier ladder. Anything needing a tester
before stable rides it, whatever the identifier says.

A preview tag rides a **staged** version; a stable tag needs a **releasable**
one ([staging.md](staging.md)). That is the point of a preview: to exercise
goals that are not all satisfied yet.

**The pushed tag is the single source of truth for the version string**
([OPS-R1](README.md#the-ops-r-namespace)). The workflow strips the leading
marker and exports it; the build reads it there. A build produced outside the
pipeline sets nothing and self-identifies as a development build
([OPS-R2](README.md#the-ops-r-namespace)).

## Cutting a release

### Before the tag

- [ ] Every goal in the version manifest is satisfied
      ([versions/](versions/)).
- [ ] The commit subjects since the last tag read as **release notes**, in the
      user's language. They are the release body.
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

Sign and push the tag. The notes are assembled from the commits it spans, so
there is nothing to move by hand.

### What the pipeline does

1. **Quality gate**, fail-fast across the runtime matrix.
2. **Four platform builds in parallel** — macOS, Windows, Linux and Android —
   each interrogating the artifact it produced rather than trusting the build's
   exit code: that it is signed by the identity expected, that it carries
   nothing it must not, and that the update manifest written beside it names it.
3. **Smoke tests, on the shapes a runner can start.** The Linux and Windows
   bundles are launched and asked for their health endpoint before they are
   uploaded, and the shipped self-host recipe is launched and probed beside them.
   The answer is compared against the tag, so a bundle that runs but reports
   another version fails too.

   This page previously said a hosted runner could not launch any of the four.
   That was written from the probes removed in May 2026, and it was right about
   the outcome and wrong about the reason, which mattered because each recorded
   cause had an escape nobody had tried. The Linux runner has no display, so
   `xvfb-run` supplies one. `open -a` on macOS goes through Gatekeeper, so the
   bundle's own binary is executed instead, named by `CFBundleExecutable`. The
   Windows installer-to-launch race is avoided by launching the unpacked tree
   rather than installing it. Two of the three then worked.

   **macOS and Android are not launched, and the reasons are different.** An
   `.apk` is installed onto a device or an emulator and has no process a runner
   can ask — that was always true. macOS was tried and measured: on
   `v2.0.0-rc.3` the bundle's binary executed and cleared every signing gate,
   and Electron died with `Fatal process out of memory: Failed to reserve
   virtual memory for CodeRange`. V8 cannot reserve its code range on a
   `macos-14` runner. That is a property of the runner, not the bundle, and the
   signing friction this page used to blame was never reached.

   **What covers those two is a person.** Installing a release on a real machine
   and using it is manual, local, and owed before a stable tag. A runner proves
   a bundle starts and answers; it does not prove the application works, and it
   never did.
4. **Publish**, only if all five succeeded: generate the release notes from
   the commits since the previous tag, generate the update manifests with
   binary hashes, sign each manifest, and create the release with every binary
   and manifest attached — as a draft for stable, published for a preview.
5. **Verify what was published**, re-reading the manifests and the checksum file
   back off the release page and re-checking every signature against the
   publisher key, so that what the page serves is what the pipeline signed.

### After the tag

- [ ] Verify the signed manifest **by hand**, using the recipe published for
      users. That reproducibility is what makes the chain trustworthy.
- [ ] Publish the draft, for a stable release.
- [ ] Announce ([notifications.md](notifications.md)).
- [ ] Mark the version manifest released, and plan the next
      ([staging.md](staging.md)).

## If something goes wrong

**A build fails.** Nothing is published — the publish step requires all five,
the smoke test among them, so four green platform builds are not on their own a
reason for it to have run. Fix and re-tag with a new patch version; do not move
a tag.

**A bad release is already published.** Publish a fixed version. A yanked
manifest stops the updater offering it, but users who already installed it have
it — which is exactly why the draft step exists for stable.

**A tag was pushed by mistake.** Delete the draft. For a preview tag, which
publishes immediately, publish a corrected one — it is already in the field.

## What is never overridable here

- Publishing without every platform build passing.
- Publishing without a signed manifest.
- Any update path that skips verification.

See [50-governance/overrides.md](../50-governance/overrides.md).

## Related

- [staging.md](staging.md) · [versions/](versions/) · [notifications.md](notifications.md)
- [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md)
- [40-quality/ci-cd.md](../40-quality/ci-cd.md) · [F6 Updates](../10-functional/features/f-platform/f6-updates.md)
