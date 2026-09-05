# `beatrax-app/spec`

**Status:** Accepted · **Licence:** CC BY-SA 4.0

This repository. The canonical specification, and the host of the shared CI the
other repositories call.

## What it is

**No code ships from here.** It spans the implementation repositories and owns
every cross-cutting decision between them. It is also, deliberately, where the
governance gate is *implemented* as well as *stated* — the rule and its
enforcement in one place.

## Structure

```text
00-overview/     vision, glossary, roadmap, decisions/
10-functional/   features/ (7 areas, 52 features), journeys/ (7)
20-architecture/ system context, components, data flow, data model,
                 platform matrix, contracts/
30-repos/        one page per repository
40-quality/      standards, comments, testing, CI/CD, security, done
50-governance/   canonical-spec rule, lifecycle, contributing, cross-repo CI,
                 sign-off, routing, overrides, AI contributors
60-brand/        brand rules, accessibility, surface mapping, trademark
70-operations/   releasing, staging, versions/, labels, maintainers,
                 notifications, project workflow, runbooks
90-appendix/     licence rationale, data retention, references
scripts/         the CI automation
.github/         workflows, CODEOWNERS, labeler
```

## The automation it hosts

| Script | Does |
|--------|------|
| `spec_check.py` | The governance gate. Verifies a change cites an identifier that exists on the canonical spec. |
| `spec_refs.py` | Builds the sticky pull-request comment linking each cited identifier to its defining file. |
| `integrity.py` | This repository's own gate: identifiers resolve, none are duplicated, no internal link is broken. |
| `dco_check.py` | Verifies every commit carries a sign-off matching its author. |
| `commit_lint.py` | Verifies conventional commit subjects. |
| `gen_codeowners.py` | Generates a repository's `CODEOWNERS` from the maintainer registry. |
| `gen_summary.py` | Generates the documentation-site navigation from the section tree. |
| `check_stageable.py` | Validates that a version manifest may be staged. |
| `manifest_check.py` | Reads every version manifest whatever its status: goals resolve, none is listed twice, and no goal is claimed landed while its own feature page or the roadmap still calls it open. |

## The workflows it defines

**Reusable**, called by the others: the governance gate, sign-off, commit
linting, hygiene, security, label sync, stale handling, and the notification
hop.

**Self-triggering**, on this repository: integrity, documentation build and
publish, labelling, triage, and awaiting-maintainer.

## This repository is subject to its own rules

Integrity checks run on every change here. Identifiers must resolve; duplicates
fail; broken links fail. The specification is not exempt from the discipline it
imposes ([GOV-R11](../50-governance/README.md#the-gov-r-namespace)).

**The governance gate does not run on this repository**, and cannot: a change
introducing a requirement cannot cite an identifier that already exists on the
canonical spec, because it *is* the change that creates it. Citations here are
checked by the integrity script against the tree under review instead.

## Conventions

| Convention | Meaning |
|------------|---------|
| `MUST` / `SHOULD` / `MAY` | RFC 2119. `MUST` is a hard requirement; violating it is a defect. |
| `<feature>-R<n>` | A product requirement, inside its feature doc. |
| `GOV-R<n>` · `ARCH-R<n>` · `Q-R<n>` · `DES-R<n>` · `OPS-R<n>` · `REPO-R<n>` | Governance, architecture, quality, brand, operations, per-repository. |
| `ADR-NNNN` | A decision record. Immutable once accepted. |
| **Status** | Every document carries one. |

**All identifiers are permanent and never reused.** A withdrawn one is marked
withdrawn in place, because commits and version manifests reference it. They
belong in commit trailers and pull-request bodies — **never in an implementation
repository's code comments**
([ADR-0011](../00-overview/decisions/0011-code-comment-policy.md)). The gate
scripts here are the exception, because a gate that enforces a rule should name
it; their citations are read by the integrity check like any other.

## Requirements

| ID | Requirement |
|----|-------------|
| **REPO-R14** | This repository MUST contain no shipped code. |
| **REPO-R15** | Integrity checks MUST run on every change: every identifier resolves, none is duplicated, no internal link is broken. The citation scan MUST read every file that can carry a citation — the Markdown tree, the shared workflow definitions, and the gate scripts — because an identifier invented in a file nothing reads is indistinguishable from one that exists. |
| **REPO-R16** | Requirement identifiers MUST be permanent; a withdrawn one MUST be marked in place and never reused. |
| **REPO-R17** | Every reusable workflow the organisation shares MUST be defined here and nowhere else. |
| **REPO-R18** | The maintainer registry and the label set MUST live here and be the only source for every repository. |
| **REPO-R19** | Every document MUST carry a status. |
| **REPO-R20** | The documentation site MUST be link-checked before it is built, so a published page never contains a broken internal link. |
| **REPO-R21** | Where a decision is genuinely unmade, the document MUST record it under an explicit open-question heading rather than inventing an answer. |

## Related

- [50-governance/canonical-spec.md](../50-governance/canonical-spec.md) · [50-governance/cross-repo-ci.md](../50-governance/cross-repo-ci.md)
- [ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md)
- [README.md](../README.md)
