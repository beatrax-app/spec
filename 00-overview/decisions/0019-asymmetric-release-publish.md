# ADR-0019: Stable tags publish as drafts; release candidates publish immediately

**Status:** Accepted
**Date:** 2026-07-27

## Context

The release pipeline is triggered by pushing a tag, and only by pushing a tag.
That is a deliberately small trigger surface, but it makes the tag push itself
the point of no return: a mistaken `git push --tags` with a stale local tag would
otherwise ship to every user on the stable auto-update channel.

Two audiences exist and they want different things. Stable-channel users want
releases that a human looked at. Preview-channel users have explicitly opted into
early builds and want them as soon as they exist; a draft holding pattern is
friction for no benefit.

There is no paid OS-level code signing
([the licence rationale](../../90-appendix/license-rationale.md#why-no-paid-signing-certificates)),
so the Ed25519-signed update manifest is the sole binary-integrity signal. That
raises the cost of a bad publish: there is no vendor revocation to fall back on.

## Decision

The release workflow's publish behaviour is asymmetric by tag shape.

| Tag shape | Channel | Publish behaviour |
|-----------|---------|-------------------|
| `vX.Y.Z` | stable | Artefacts build, smoke-test, and upload; the release is created as a **draft**. A human reviews and clicks Publish. |
| `vX.Y.Z-rc.N` | preview | Published immediately and flagged as a prerelease. |

There is no alpha tier. Anything that needs to reach a tester before going
stable rides the preview channel as a release candidate.

Supporting rules:

- **The pushed tag is the single source of truth for the version string.** The
  workflow strips the leading `v` and exports it; the build reads it from there.
  A build produced outside the pipeline sets nothing and therefore
  self-identifies as a development build, so there is never ambiguity about
  which path produced a binary.
- **The workflow never triggers on a pull-request event that would give a fork
  access to secrets.** Tag push only.
- **Every platform build must succeed before publish runs.** A partial release
  cannot reach the publish step.
- **Each platform bundle is smoke-tested before upload** — installed or
  extracted, launched, and asked for its health endpoint, which returns the app,
  runtime, and database versions. That catches the most common silent
  regression: a bundle that boots but reports the wrong version.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Publish everything immediately** | One mistaken tag push ships to every stable user, with no vendor revocation available. |
| **Draft everything, including release candidates** | Adds a manual step to the channel whose whole purpose is speed, for users who opted into the risk. |
| **A manual dispatch trigger for releases** | Considered and kept, but only as a build-only verification path: it produces artefacts for inspection without smoke-testing, signing, or publishing. Making it the release trigger would widen the trigger surface for no gain. |
| **A protected environment approval instead of a draft** | Equivalent in effect, but the draft is visible to anyone with write access and shows the actual artefacts, which is a better review surface than an approval button. |

## Consequences

### Positive

- A mistaken stable tag push costs a deleted draft, not a bad release in the
  field.
- The draft is a genuine review surface: the reviewer sees the real artefacts and
  the real generated notes.
- Both channels are live from the first release, so a stable and a preview
  release can coexist without channel-ordering surprises.

### Negative

- **A release needs a human at the keyboard** at publish time. For a project
  maintained in spare hours, that can add days between a tag and a download.
- Two channels to keep coherent in the updater and in the release notes.

### Neutral

- Release notes are generated from the commit history rather than written on
  the release, so the commit subject is what a contributor is asked for — and a
  subject written for the implementer reads that way to the user.

## Revisit if

- Paid signing identities are adopted (see the
  [roadmap's open questions](../roadmap.md#open-questions) on app-store
  distribution), which changes the revocation story and may justify a different
  publish posture.

## Related

- [70-operations/releasing.md](../../70-operations/releasing.md) — the operator
  procedure
- [70-operations/staging.md](../../70-operations/staging.md) — how a version
  becomes releasable in the first place
- [F6 Updates and release verification](../../10-functional/features/f-platform/f6-updates.md)
- [40-quality/ci-cd.md](../../40-quality/ci-cd.md)
