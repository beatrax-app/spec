# Repositories

**Status:** Accepted

Four repositories under `beatrax-app`. The split, and why it is not a monorepo,
is [ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md).

| Repo | What it is | Language | Licence |
|------|-----------|----------|---------|
| **[spec](spec.md)** | This repository. Functional and technical specification. | Markdown | CC BY-SA 4.0 |
| **[beatrax](beatrax.md)** | The product: application, modules, desktop and mobile bundles. | PHP | Hippocratic 3.0 |
| **[website](website.md)** | The public site. | Static | Content CC BY-SA 4.0; code Hippocratic 3.0 |
| **[.github](dot-github.md)** | Org-wide community health files. | Markdown | CC BY-SA 4.0 |

## The `REPO-R` namespace

Requirements that govern a repository's own structure and tooling, as opposed to
the product's behaviour.

| ID | Requirement |
|----|-------------|
| **REPO-R1** | Every repository MUST call the shared governance gate, and no behavioural change may merge without a citation that resolves on the canonical spec. |
| **REPO-R2** | Every repository MUST call the shared sign-off check. |
| **REPO-R3** | Every repository MUST call the shared commit-subject check. |
| **REPO-R4** | Every repository MUST call the shared hygiene checks. |
| **REPO-R5** | Every repository's `CODEOWNERS` MUST be generated from the single maintainer registry and MUST NOT be edited by hand. |
| **REPO-R6** | Every repository MUST sync its labels from the canonical label set. |
| **REPO-R7** | Every third-party action MUST be pinned to a full commit hash with an inline version comment; first-party reusable workflows MUST be referenced on the default branch. |
| **REPO-R8** | Every repository MUST protect its default branch with linear history, signed commits, required status checks, and blocked force-push and deletion. |
| **REPO-R9** | Every repository MUST enable platform secret scanning and push protection. |
| **REPO-R10** | Every repository MUST enable dependency alerts and scheduled dependency updates. |
| **REPO-R11** | Every repository MUST carry a licence file naming its terms unambiguously. |
| **REPO-R12** | Only the product repository may hold release-signing secrets. |
| **REPO-R13** | A change to a workflow file or to `CODEOWNERS` MUST require owner approval, even where the branch ruleset otherwise permits a direct push. |

## The org's shape

```text
                    ┌──────────────────┐
                    │       spec       │  canonical · defines the shared CI
                    └────────┬─────────┘
                             │ cited by, and calls into
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌───────────┐  ┌────────────┐
        │ beatrax  │  │  website  │  │  .github   │
        └──────────┘  └───────────┘  └────────────┘
```

The spec is canonical and also the **host** of the shared workflows, so the rule
and its enforcement live in the same place
([50-governance/cross-repo-ci.md](../50-governance/cross-repo-ci.md)).

## The move from `nightworksio`

The product repository is moving from a shared personal-scope organisation to
`beatrax-app`. Practical consequences:

- Existing clone URLs and issue references redirect, but the product
  repository's own documentation references the old path and needs a sweep.
- Organisation-level settings — labels, rulesets, secret scanning, the maintainer
  registry — can be tuned for beatrax without affecting unrelated projects.
- The development branch is merged into the default branch and retired; the next
  release is cut from the default branch inside the new organisation
  ([00-overview/roadmap.md](../00-overview/roadmap.md#the-v14--v20-promotion)).

## Related

- [ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md) · [ADR-0012](../00-overview/decisions/0012-action-pinning.md)
- [50-governance/](../50-governance/) · [70-operations/](../70-operations/)
