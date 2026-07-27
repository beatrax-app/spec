# ADR-0012: Third-party actions SHA-pinned; first-party reusable workflows on `@main`

**Status:** Accepted
**Date:** 2026-07-27

## Context

Every workflow in the org executes with a token that can write to the
repository. A workflow that resolves a third-party action by tag resolves it at
run time, and tags on GitHub are mutable: the owner of the action can move the
tag to a different commit at any point, and the consuming repository will
silently run the new code with its own token. This is not theoretical — a
widely-used action was compromised by exactly this mechanism in 2025, and the
compromise propagated to every repository that referenced it by tag.

The product repository already adopted full-SHA pinning for this reason. The
question this ADR settles is what the *org-wide* rule is, and whether it applies
equally to first-party reusable workflows defined in this repository.

## Decision

Two rules, deliberately different:

1. **Every third-party action is pinned to a full 40-character commit SHA**, with
   an inline comment naming the released version so dependency automation can
   recognise and propose updates. A tag reference in a workflow is a review
   blocker.

   ```yaml
   - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
   ```

2. **First-party reusable workflows — the ones defined in this repository and
   called from sibling repos — are referenced as `@main`.** They are org-owned
   code that this org's own review process gates, so pinning them buys no
   security and costs real coordination: a fix to the shared DCO check would
   otherwise need a pin bump in every consuming repository before it took
   effect.

Dependency automation watches the actions ecosystem weekly so the inline version
comments do not rot.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Tag references everywhere** | The exact attack this rule exists to prevent. |
| **SHA-pin everything, including first-party reusables** | A one-line fix to a shared workflow would need a pin bump in every consumer before it took effect, which is how shared workflows drift back into per-repo copies. The threat model does not justify it: the code is ours, gated by our own review. |
| **A vendored copy of each third-party action** | Maximum control, but a maintenance burden out of proportion to a four-repo org. |

## Consequences

### Positive

- A compromised upstream action cannot reach org repositories without a
  reviewed pin bump.
- Shared workflow fixes propagate in one merge.

### Negative

- **Pin bumps are noisy.** Dependency automation groups them into a single
  weekly pull request to keep the noise bounded.
- A reviewer has to actually check that a bumped SHA corresponds to the version
  the comment claims. Automation proposes; review verifies.

### Neutral

- Repository-level secret scanning and push protection cover the credential half
  of the same problem, and are configured at the platform level rather than as a
  workflow.

## Revisit if

- GitHub introduces immutable tags or a signed-action mechanism strong enough to
  replace SHA pinning.

## Related

- [40-quality/ci-cd.md](../../40-quality/ci-cd.md) — the full pipeline
- [40-quality/security.md](../../40-quality/security.md)
- [50-governance/cross-repo-ci.md](../../50-governance/cross-repo-ci.md) — which
  workflows are shared and how they are called
