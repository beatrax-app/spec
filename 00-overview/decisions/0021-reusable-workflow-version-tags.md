# ADR-0021: First-party reusable workflows are referenced by major version tag

**Status:** Accepted
**Date:** 2026-07-27
**Supersedes:** the second rule of
[ADR-0012](0012-action-pinning.md) — first-party reusable workflows on `@main`.
Its first rule, full-SHA pinning for third-party actions, stands unchanged.

## Context

ADR-0012 settled two rules. The first — third-party actions pinned to a full
commit SHA — is not in question and is not touched here.

The second said first-party reusable workflows, the ones this repository defines
and its siblings call, are referenced as `@main`. The reasoning was that they are
org-owned code gated by the org's own review, so pinning buys no security and
costs real coordination.

In practice the organisation did not do this. The website repository and this
repository's own internal call both pinned to commits, deliberately, in a change
whose message was "a tag or branch reference can be repointed without the calling
workflow changing, which is the whole reason the third-party actions are pinned".
The product repository's new callers used `@main`, per the ADR as written.

So the org had three repositories doing two different things, and a rule nobody
had followed since it was written. That is worse than either option: a rule that
is contradicted in the tree teaches contributors the specification describes
intentions rather than facts.

Both positions have a real point, and the disagreement is genuine:

- `@main` is right that a shared fix should propagate in one merge. Requiring a
  bump in every consumer before a DCO-check fix takes effect is exactly how
  shared workflows decay back into per-repo copies.
- The pinning change is right that `@main` means an unreviewed-by-the-consumer
  change to this repository's default branch reaches every sibling's pipeline
  immediately, including the pipelines that gate merges.

## Decision

**First-party reusable workflows are referenced by a moving major-version tag.**

```yaml
uses: beatrax-app/spec/.github/workflows/dco.yml@v1
```

Three rules make that work:

1. **`v1` moves.** A fix or an additive change to a shared workflow moves the
   `v1` tag forward when it merges. Consumers pick it up on their next run, with
   no change on their side — the propagation property `@main` was protecting.

2. **A breaking change cuts `v2`.** Consumers move deliberately, one repository
   at a time, and a half-migrated org is a valid state rather than a broken one.
   Breaking means, precisely: removing or renaming an input or a secret; making
   an optional input required; renaming a job, because consumers name jobs in
   their branch rulesets as required checks ([OPS-R18](../../70-operations/README.md#the-ops-r-namespace));
   or changing behaviour such that a pull request which passed before now fails.

3. **Every move is also an immutable tag.** `v1` is repointed onto a
   `v1.<minor>.<patch>` tag that is never moved, so what `v1` pointed at on any
   given day is recoverable, and a consumer that needs to hold still can pin to
   the immutable one.

## Why this is not the mutable-tag risk ADR-0012 warned about

ADR-0012's threat is real and unchanged: a third-party action's owner can move a
tag onto malicious code, and the consumer runs it with a write-capable token. The
2025 compromise it cites worked exactly that way.

That threat does not transfer here, for a reason worth stating rather than
assuming. **The tag mover and the tag consumer are the same party.** Moving `v1`
requires a push to this repository, whose default branch is protected — linear
history, signed commits, required checks, owner approval on workflow files
([REPO-R8](../../30-repos/README.md#the-repo-r-namespace),
[REPO-R13](../../30-repos/README.md#the-repo-r-namespace)). An attacker who can
move `v1` can already push to `main`, which `@main` would have executed anyway.

Against `@main`, this decision is strictly stronger: a breaking change no longer
reaches consumers the moment it merges. Against full SHA pinning, it is weaker by
exactly the amount of trust the org already places in its own protected branch.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Keep `@main`** | Correct on propagation, but leaves no mechanism for a breaking change: every consumer breaks simultaneously, at merge time, in the pipeline that gates merges. |
| **SHA-pin first-party too** | A one-line fix to a shared check needs a bump pull request in every consumer before it takes effect. It also makes this repository pin itself to its own commits for its internal call, which is self-referential churn with no reader. |
| **Immutable tags only, no moving major** | Every shared fix becomes a bump in three repositories — SHA pinning with extra steps. |

## Consequences

### Positive

- One reference form across every repository, matching what the specification says.
- Shared fixes still propagate in one merge.
- Breaking changes to a workflow contract become explicit and migratable.
- What `v1` pointed at on any date stays recoverable.

### Negative

- **This repository now has a release step it did not have.** Merging a change to
  a shared workflow is no longer sufficient; the tag has to move, and a forgotten
  move means the fix silently does not reach anyone.
- Judging whether a change is breaking is a human call, and getting it wrong
  breaks consumers rather than a build here.

### Neutral

- Dependency automation does not propose major-tag moves, so `v1 → v2` is
  deliberate work, which is the intent.

## Revisit if

- The tag move is forgotten often enough to be a real failure mode, at which
  point it should be automated on merge rather than left to discipline.
- GitHub introduces immutable tags, which would let the moving major and the
  audit trail be the same object.

## Related

- [ADR-0030](0030-the-tag-governs-the-workflow-not-what-it-reads.md) — what the
  tag turned out not to cover, and the check that reports a forgotten move
- [ADR-0012](0012-action-pinning.md) — superseded in part; its third-party rule stands
- [50-governance/cross-repo-ci.md](../../50-governance/cross-repo-ci.md) — the shared workflows and how they are called
- [40-quality/ci-cd.md](../../40-quality/ci-cd.md) · [30-repos/README.md](../../30-repos/README.md)
