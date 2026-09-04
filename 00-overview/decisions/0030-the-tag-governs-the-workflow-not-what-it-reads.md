# ADR-0030: The major tag governs the workflow definition, not what the workflow reads

**Status:** Accepted
**Date:** 2026-09-04

## Context

[ADR-0021](0021-reusable-workflow-version-tags.md) put the shared workflows on a
moving `v1`, moved by hand when a shared workflow merges. It named its own
failure mode plainly — *"a forgotten move means the fix silently does not reach
anyone"* — and made one further claim, in defending the moving tag against
[ADR-0012](0012-action-pinning.md)'s mutable-tag threat:

> Against `@main`, this decision is strictly stronger: a breaking change no
> longer reaches consumers the moment it merges.

Both halves were checked against the repository rather than assumed.

**The forgotten move has not happened yet.** `v1` has pointed at `d838668` since
2026-07-28 and `main` is 17 commits ahead of it. None of those 17 commits changed
a shared workflow, so no move has been owed since the tag was last set. The
discipline is not failing; it has not yet been tested. Nothing anywhere would
have said so either way, which is the part worth fixing.

**The second claim is false as implemented.** Five of the eleven shared workflows
read this repository at its *default branch* while they run, not at the tag they
were called from:

| Workflow | Reads from `main` at run time |
|----------|-------------------------------|
| `spec-check.yml` | the whole specification corpus, and `scripts/spec_check.py` |
| `dco.yml` | `scripts/dco_check.py` |
| `commitlint.yml` | `scripts/commit_lint.py` |
| `spec-references.yml` | `scripts/spec_refs.py` |
| `label-sync.yml` | `70-operations/labels.yml` |

Commit `1b3e2ff` is the proof rather than the illustration. It widened
`commit_lint.py`'s subject pattern to accept a comma-separated scope. Every
consumer's `commitlint` job — a required check on their merges — ran the new
pattern on its next pull request. No tag moved, no consumer reviewed it, and
nothing recorded that a merge gate had changed under them. It happened to be a
widening. A tightening travels by the identical path.

## Decision

**The major tag is a promise about the workflow definition. What the workflow
reads at run time is governed separately, and the two are stated apart.**

1. **The workflow definition rides the tag.** Unchanged from ADR-0021.

2. **The specification corpus is read from the default branch, deliberately.**
   A consumer citing a requirement that merged here an hour ago must pass the
   governance gate. Pinning the corpus to `v1` would make a correct citation fail
   until an unrelated tag move happened, which is a worse gate than no gate.
   [cross-repo-ci.md](../../50-governance/cross-repo-ci.md#how-the-governance-gate-works)
   already says the gate checks out the default branch; this makes the *reason*
   part of the record.

3. **The gate scripts are read from the default branch, and that is not
   deliberate.** They are the gate's logic, not its subject matter. They rode in
   on the same checkout as the corpus. Whether to pin them is
   [an open question](../../90-appendix/open-questions.md), not a thing this
   decision settles — the fix has a real cost and no one has paid it yet.

4. **A shared workflow that changed without the tag moving MUST fail a check**
   that names the tag, both commits, how far behind, and which files differ
   ([OPS-R27](../../70-operations/README.md#the-ops-r-namespace)).

### What the check does not do

It does not go red because `v1` is behind `main`. It is behind by 17 commits
today and every one of them is specification prose that no consumer's pipeline
loads through the tag. A check that is red every day is a check its readers learn
to skip, which is how the security gate's own download failure was argued
([Q-R27](../../40-quality/README.md#the-q-r-namespace)). It goes red on the
condition that actually costs a consumer something: a **shared** workflow —
`workflow_call`, so callable from another repository — differing between the tag
and the default branch. Files read at run time are reported as a notice, because
they have already arrived and moving the tag does not change them.

## Alternatives

| Alternative | Why it lost |
|-------------|-------------|
| **Move `v1` automatically on merge to `main`** | It reintroduces `@main` under another name. ADR-0021 keeps a human in the loop precisely because *"judging whether a change is breaking is a human call"*; an unconditional auto-move makes that call by default, every time, in the direction of shipping. Its own "Revisit if" gates automation on the move being *forgotten often enough to be a real failure mode* — and it has not yet been forgotten once, because it has not yet been owed. Reconsider on evidence, not on the fright of finding the tag 17 commits behind. |
| **Automate the move, but only behind an explicit maintainer declaration** | The form automation should take *if* forgetting proves real: a label or a trailer in which the maintainer states the change is not breaking, and the pipeline does the tagging. Not built now, for want of the evidence that would justify it. |
| **Pin the gate scripts to `github.job_workflow_sha`** | The right shape for point 3 — it is the commit the reusable workflow itself resolved from, so the scripts would travel with the tag while the corpus stayed on `main`. It means a second checkout in four workflows and a script fix reaching nobody until a tag move, which is the trade ADR-0021 made for workflows and has not been asked about for scripts. Left open rather than taken silently. |
| **Report the drift and never fail** | The failure mode is nobody noticing. A notice among green ticks is the state we are already in. |
| **Fail whenever `v1` is behind `main`** | Red every day for a specification commit that reaches consumers by a path the tag does not control. It trains the reader to ignore the one run that matters. |

## Consequences

### Positive

- A forgotten move is caught at the merge that creates it, and again every day it
  survives.
- The pull request that will owe a move says so while its author is still there.
- ADR-0021's third rule is enforced rather than remembered: a `v1` sitting on a
  commit with no immutable `v1.x.y` beside it fails the same check.
- What the tag does and does not cover is written down, so the next reader does
  not have to infer it from four `ref: main` lines in four different files.

### Negative

- The check is one more thing that can be red on `main`, where nothing is blocked
  by it. That is the cost of reporting a condition no pull request can gate.
- Point 3 leaves a known gap open rather than closing it. Recording it is
  strictly better than the previous state, in which it was neither closed nor
  known, but it is not a fix.

### Neutral

- No consumer repository changes. The call sites stay `@v1`.

## Revisit if

- A move is forgotten in practice, which is now observable — at which point the
  labelled or trailered automation above is the shape to build.
- The open question on pinning the gate scripts is answered either way.

## Related

- [ADR-0021](0021-reusable-workflow-version-tags.md) — the moving tag, and the
  claim this decision corrects
- [ADR-0012](0012-action-pinning.md) — the pinning rules, and the threat model
  ADR-0021 argued against
- [50-governance/cross-repo-ci.md](../../50-governance/cross-repo-ci.md) ·
  [70-operations/releasing.md](../../70-operations/releasing.md)
