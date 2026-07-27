# The canonical-spec rule

**Status:** Accepted

## The rule

> **This repository is canonical.** No change lands in any implementation
> repository unless it cites an identifier that already exists here.

Enforced mechanically, on every pull request, in every repository
([GOV-R1](README.md#the-gov-r-namespace)–[GOV-R3](README.md#the-gov-r-namespace)).

## Why

Documentation that trails implementation is documentation nobody trusts, and
documentation nobody trusts stops being written. The only way out is to make the
specification a **prerequisite** rather than an output.

The gate is what makes it a prerequisite instead of an aspiration. Without it,
this is a policy, and policies decay.

There is a second effect, and it is the more valuable one: **every architectural
decision has to be justified against a requirement**. A technical choice citing
no requirement is unjustified and should be challenged in review. That is what
keeps the technical specification written *against* the functional one rather
than alongside it.

## How to cite

A trailer in a commit **and** in the pull-request body:

```text
Spec: B5-R13
```

Several identifiers are fine:

```text
Spec: E1-R9, E1-R13, ADR-0014
```

## What is citable

| Kind | Example | Defined in |
|------|---------|------------|
| A product requirement | `A2-R11` | Its feature doc |
| A governance rule | `GOV-R4` | [50-governance](README.md) |
| An architectural requirement | `ARCH-R12` | [20-architecture](../20-architecture/README.md) |
| A quality rule | `Q-R6` | [40-quality](../40-quality/README.md) |
| A brand requirement | `DES-R3` | [60-brand](../60-brand/README.md) |
| An operations requirement | `OPS-R11` | [70-operations](../70-operations/README.md) |
| A per-repository requirement | `REPO-R23` | [30-repos](../30-repos/README.md) |
| A decision record | `ADR-0014` | [00-overview/decisions](../00-overview/decisions/) |

## Routine maintenance

Dependency bumps, formatting, and pipeline mechanics cite
**[GOV-R12](README.md#the-gov-r-namespace)**.

That identifier exists so routine work has an honest answer instead of forcing
contributors to invent a requirement — which would be the worse outcome, because
an invented requirement pollutes the specification permanently.

## What happens when you cannot cite

You are changing behaviour the specification does not describe. That is not a
gate problem; it is a specification gap.

**Open a pull request here first.** Add the requirement, get it reviewed, merge
it. Then cite it
([GOV-R13](README.md#the-gov-r-namespace),
[change-lifecycle.md](change-lifecycle.md)).

This is the intended friction and it is where the value is: the requirement gets
written by someone who has thought about the problem, at the moment they are
thinking about it, rather than reconstructed afterwards by someone reading a
diff.

## Ordering

A behavioural change's specification change **merges first**
([GOV-R4](README.md#the-gov-r-namespace)).

**Ordering is not machine-checked** — the gate verifies existence, not sequence.
It is verified in review, and hardening it is tracked work. Recorded plainly so
nobody assumes a guarantee that is not there.

## Identifiers are permanent

Never reused, never renumbered
([GOV-R8](README.md#the-gov-r-namespace),
[GOV-R10](README.md#the-gov-r-namespace)). A withdrawn requirement is marked
withdrawn in place.

Commits reference them, version manifests lock them, and tests cite them.
Renumbering would silently invalidate history.

## Never in code comments

Identifiers belong in commit trailers and pull-request bodies. **Never in a code
comment** ([GOV-R6](README.md#the-gov-r-namespace),
[ADR-0011](../00-overview/decisions/0011-code-comment-policy.md)).

A comment carrying a requirement identifier is workflow provenance in a place
that outlives the workflow, and it is a mechanical violation of the comment
policy.

## This repository is subject to its own rules

Integrity checks run here on every change: identifiers resolve, none is
duplicated, no internal link is broken
([GOV-R11](README.md#the-gov-r-namespace)).

**The governance gate does not run here, and cannot.** A change introducing a
requirement cannot cite an identifier that already exists on the default branch,
because it is the change that creates it. Citations here are checked against the
tree under review instead.

## What the gate does not do

- It does not check that the citation is **apt**. Citing an unrelated identifier
  passes the gate and fails review.
- It does not check **ordering**, as above.
- It does not check that the implementation actually **satisfies** the
  requirement. That is the reviewer's job, and the test's.

The gate makes the specification impossible to ignore. It does not make review
unnecessary.

## Related

- [change-lifecycle.md](change-lifecycle.md) · [contributing.md](contributing.md) · [cross-repo-ci.md](cross-repo-ci.md)
- [30-repos/spec.md](../30-repos/spec.md)
- [ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md)
