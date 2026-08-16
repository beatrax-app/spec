# ADR-0013: Four repositories in the `beatrax-app` org, not a monorepo

**Status:** Accepted
**Date:** 2026-07-27

## Context

Beatrax was developed in a single repository, `nightworksio/beatrax`, under a
personal-scope organisation shared with unrelated projects. It is moving to its
own organisation, `beatrax-app`. That move is the moment to decide what the
repository boundary is, because it is expensive to change afterwards — commit
history, issue references, and clone URLs all depend on it.

The org produces four artefacts with genuinely different change rates and review
styles:

- A **specification** that changes when a decision is made, and is reviewed by
  reading prose.
- A **product** — the Laravel application and its desktop and mobile bundles —
  that changes constantly and is reviewed by reading PHP against a
  three-gate CI matrix.
- A **website** that changes on announcements and copy edits, reviewed by looking
  at it.
- **Org-wide community health files** that change rarely and apply everywhere.

The product repository is genuinely monolithic and should stay that way: the
module boundary ([ADR-0001](0001-modular-architecture.md)) already provides
internal separation, it is enforced by tests, and splitting thirty-four modules
into thirty-four repositories would trade one enforced boundary for thirty-four
unenforced ones plus a version-skew problem.

## Decision

Four repositories under `beatrax-app`:

| Repo | Contents | Changes when | Reviewed by |
|------|----------|--------------|-------------|
| [`spec`](../../30-repos/spec.md) | This specification | A decision is made | Reading prose |
| [`beatrax`](../../30-repos/beatrax.md) | The product: Laravel application, modules, desktop and mobile bundles | Feature work | Reading PHP, plus the CI gate |
| [`website`](../../30-repos/website.md) | The public site | Announcements, copy | Looking at it |
| [`.github`](../../30-repos/dot-github.md) | Org-wide community health files, inherited by every repo | Rarely | Reading prose |

**The spec is canonical.** No behavioural change lands in `beatrax` or `website`
without citing an identifier that already exists in `spec`, enforced mechanically
by a reusable workflow this repository defines
([50-governance/canonical-spec.md](../../50-governance/canonical-spec.md)).

Shared CI — the governance gate, DCO, commit linting, hygiene, label sync,
triage — is defined **once, here**, and called by the others
([ADR-0012](0012-action-pinning.md),
[50-governance/cross-repo-ci.md](../../50-governance/cross-repo-ci.md)).

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **One repository for everything** | The spec would be versioned with the code it governs, which makes "cite something that already exists on the canonical spec" circular — a PR could add the requirement and the implementation in the same commit, and the gate would pass. The separation is what gives the gate teeth. |
| **Two repositories (`beatrax` + `spec`)** | Workable, but the website's deploy pipeline and the product's release pipeline have nothing in common, and org-wide health files genuinely need the `.github` repository name to be inherited at all. |
| **Splitting the product by module** | Thirty-four repositories, thirty-four version skews, and a boundary that stops being test-enforceable the moment it crosses a repository line. The module boundary already works. |
| **Keeping it under `nightworksio`** | The org is shared with unrelated projects, so org-level settings, labels, and reusable workflows cannot be tuned for Beatrax without affecting them. |

## Consequences

### Positive

- The spec is citable and versioned independently of any implementation, which
  is what makes the governance gate meaningful rather than ceremonial.
- Each repository gets CI proportionate to its risk. The website does not pay
  for a PHP matrix; the spec does not pay for a desktop build.
- Issues land in the right place without triage.
- Org-level settings — labels, rulesets, secret scanning, the maintainer
  registry — have one home.

### Negative

- **Cross-repo changes need coordination.** A behavioural change is two pull
  requests: the spec change first, then the implementation citing it. This is
  the intended friction, but it is friction.
- **Four sets of repository settings to keep aligned.** Mitigated by generating
  `CODEOWNERS` from a single maintainer registry and syncing labels from a single
  file, both defined here.
- The move itself breaks existing clone URLs and issue references. GitHub
  redirects handle most of it; the product repo's own documentation needs a
  sweep.

### Neutral

- The product repository keeps its internal `.docs/` tree for implementation-level
  detail. This spec owns *what* and *why*; `.docs/` owns *where in the code*. The
  split is documented in [30-repos/beatrax.md](../../30-repos/beatrax.md).

## Revisit if

- Cross-repo coordination overhead visibly slows development.
- The website and the product start needing to ship in lockstep.

## Related

- [30-repos/](../../30-repos/) — the per-repository specifications
- [50-governance/canonical-spec.md](../../50-governance/canonical-spec.md)
- [50-governance/cross-repo-ci.md](../../50-governance/cross-repo-ci.md)
