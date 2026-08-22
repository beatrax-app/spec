# Governance

**Status:** Accepted

How change enters the organisation. **Read [canonical-spec.md](canonical-spec.md)
before your first pull request** — it is the one rule everything else follows
from.

## Contents

| Page | Covers |
|------|--------|
| [canonical-spec.md](canonical-spec.md) | The rule: this repository is canonical, and the gate that enforces it |
| [change-lifecycle.md](change-lifecycle.md) | How a change moves from idea to release |
| [contributing.md](contributing.md) | What a contributor does, concretely |
| [cross-repo-ci.md](cross-repo-ci.md) | The shared workflows and how repositories call them |
| [dco.md](dco.md) | Sign-off: what it attests and why it is required |
| [issue-routing.md](issue-routing.md) | Where things go, and what happens to them |
| [overrides.md](overrides.md) | When a rule may be broken, and by whom |
| [ai-contributors.md](ai-contributors.md) | Rules for AI-assisted contributions |

## The `GOV-R` namespace

| ID | Requirement |
|----|-------------|
| **GOV-R1** | This repository is canonical. Where it and any other document disagree, this repository wins. |
| **GOV-R2** | Every change to an implementation repository MUST carry a specification citation in a commit trailer and in the pull-request body. |
| **GOV-R3** | Every cited identifier MUST already exist on the canonical specification's default branch. |
| **GOV-R4** | A behavioural change's specification change MUST merge **before** its implementation. |
| **GOV-R5** | Routine maintenance MUST cite the maintenance identifier rather than inventing a requirement. |
| **GOV-R6** | Requirement identifiers MUST NOT appear in code comments. |
| **GOV-R7** | A contested decision MUST be recorded as a decision record before the change that depends on it merges. |
| **GOV-R8** | Identifiers MUST be permanent and never reused; a withdrawn one MUST be marked in place. |
| **GOV-R9** | A decision record MUST NOT be edited once accepted; it MUST be superseded by a new one that links both ways. |
| **GOV-R10** | Requirements MUST NOT be renumbered. |
| **GOV-R11** | This repository MUST be subject to its own integrity checks. |
| **GOV-R12** | Routine maintenance — dependencies, formatting, pipeline mechanics — MUST cite this identifier. |
| **GOV-R13** | A change that cannot cite an existing identifier MUST become a specification change first, not an exception. |
| **GOV-R14** | Every repository MUST call the shared governance gate. |
| **GOV-R15** | Every commit MUST carry a sign-off matching its author, except merge commits and automation-authored commits, which have no human to attest. |
| **GOV-R16** | Commit subjects MUST follow the conventional format. |
| **GOV-R17** | Pull requests MUST be squashed or rebased; the default branch MUST keep a linear history. |
| **GOV-R18** | A pull request MUST pass every required check before review starts. |
| **GOV-R19** | A change to a workflow file or to the ownership file MUST require owner approval. |
| **GOV-R20** | Maintainership MUST be declared in one registry, and every ownership file MUST be generated from it. |
| **GOV-R21** | A specification change that alters a released version's locked goals MUST be reviewed as a goals change. |
| **GOV-R22** | A pull request MUST receive a sticky comment linking each cited identifier to its defining file. |
| **GOV-R23** | An issue that describes a behaviour the specification does not cover MUST become a specification change before implementation. |
| **GOV-R24** | The project lead holds override authority; every override MUST be recorded ([overrides.md](overrides.md)). |
| **GOV-R25** | Where a decision is genuinely unmade, the document MUST say so under an explicit open-question heading rather than inventing an answer. |

## Where to ask

| Kind | Where |
|------|-------|
| A bug, or a behaviour that contradicts the specification | An issue on the repository it affects |
| A question about how something works | [The Discord](https://discord.nightworks.io), or a discussion |
| A proposal that changes behaviour | A discussion first, then a specification pull request |
| A security report | Private vulnerability reporting, never a public issue ([40-quality/security.md](../40-quality/security.md)) |

**Ask before building something large.** Agreeing on shape early is cheaper than
reworking a finished pull request, for everyone.

## Related

- [30-repos/](../30-repos/) · [40-quality/](../40-quality/) · [70-operations/](../70-operations/)
