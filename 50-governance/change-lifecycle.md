# Change lifecycle

**Status:** Accepted

How a change moves from an idea to something a user has.

## The two shapes

### A behavioural change

```text
idea
  │
  ▼
discussion  ── agree the shape before anyone writes code
  │
  ▼
SPEC PR  ── new or amended requirement, reviewed as prose
  │           merges FIRST
  ▼
implementation PR  ── cites the identifier the spec PR created
  │                    tests, changelog entry, browser walkthrough
  ▼
merge  ── squash or rebase; linear history
  │
  ▼
version manifest  ── the requirement is locked into a release's goals
  │
  ▼
release
```

The specification change **merges first**
([GOV-R4](README.md#the-gov-r-namespace)). That is the whole point: the
requirement is written by someone thinking about the problem, not reconstructed
afterwards from a diff.

### Everything else

```text
change  ──▶  cites GOV-R12  ──▶  review  ──▶  merge
```

Dependency bumps, formatting, pipeline mechanics, documentation corrections.
Straight through.

## Discussion first, for anything large

Open a discussion, or ask in [the Discord](https://discord.gg/FYuV9CbTHR), before
building something substantial. Agreeing on shape early is cheaper than reworking
a finished pull request — for the contributor most of all.

## Contested decisions become records

Where a competent engineer could reasonably have chosen otherwise, the decision
gets a record **before** the change that depends on it merges
([GOV-R7](README.md#the-gov-r-namespace)).

A record captures the alternatives and why they lost, so revisiting later starts
from evidence rather than from scratch. Records are immutable once accepted;
changing a decision means writing a new one that supersedes it and links both
ways ([GOV-R9](README.md#the-gov-r-namespace)).

"We use this library for CSV" is not a decision. It is a default.

## Review

| Kind | Reviewed by |
|------|-------------|
| A specification change | Reading prose. Is the requirement testable, permanent, and correctly scoped? |
| An implementation change | Reading code, plus the pipeline. Does it satisfy the cited requirement? |
| A workflow or ownership change | **Owner approval, always** ([GOV-R19](README.md#the-gov-r-namespace)) — these execute with a token |
| A goals change | As a goals change ([GOV-R21](README.md#the-gov-r-namespace), [70-operations/staging.md](../70-operations/staging.md)) |

Every required check passes **before review starts**
([GOV-R18](README.md#the-gov-r-namespace)). Reviewing a red pull request wastes
the reviewer's attention on things the pipeline would have told the author.

A pull request receives a sticky comment linking each cited identifier to its
defining file, updated on every push, so a reviewer can see what is claimed
without leaving the page ([GOV-R22](README.md#the-gov-r-namespace)).

## Merging

Squash or rebase; the default branch keeps a linear history
([GOV-R17](README.md#the-gov-r-namespace)). No merge commits. The head branch is
deleted afterwards.

Every commit on the default branch is signed, and force-push and deletion are
blocked ([40-quality/ci-cd.md](../40-quality/ci-cd.md)).

## The solo posture, and when it ends

The project is currently maintained by one person, and the branch protection is
**light**: an administrator may push directly without a pull-request-of-one
ceremony. That is an honest accommodation of the actual situation rather than
theatre.

**It ends the moment external contributors arrive.** At that point the bypass
becomes pull-request-only, and the ceremony starts being worth its cost.

The one carve-out that is already non-optional: workflow and ownership changes
require owner approval regardless.

## From merge to release

A merged change is not released. It sits on the default branch until a version
manifest locks its requirements into a release's goals and that version is
staged, made releasable, and cut
([70-operations/staging.md](../70-operations/staging.md),
[70-operations/releasing.md](../70-operations/releasing.md)).

**Landed is not shipped**, and the [roadmap](../00-overview/roadmap.md) keeps the
two apart deliberately — most of v2.0 is currently landed and unreleased.

## Reverting

A revert is a normal change with a normal citation. Where a revert undoes
something a version manifest locked, the manifest is updated too — a released
version's goals are a statement about what shipped, and it must stay true.

## Related

- [canonical-spec.md](canonical-spec.md) · [contributing.md](contributing.md) · [overrides.md](overrides.md)
- [40-quality/definition-of-done.md](../40-quality/definition-of-done.md)
- [70-operations/staging.md](../70-operations/staging.md)
