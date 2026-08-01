<h1 align="center">beatrax — Specification</h1>

<p align="center">
  <em>A local-first personal finance dashboard for the unified picture of your cross-account money.</em>
</p>

The single source of truth for the beatrax project: what it is, why it is built
this way, and the standards every repository in the organisation is held to.

This repository contains **no code**. It spans the implementation repositories
and owns every cross-cutting decision between them.

<p align="center">
  <a href="https://github.com/beatrax-app/spec/actions/workflows/integrity.yml"><img alt="integrity" src="https://github.com/beatrax-app/spec/actions/workflows/integrity.yml/badge.svg"></a>
  <a href="https://github.com/beatrax-app/spec/actions/workflows/docs.yml"><img alt="docs" src="https://github.com/beatrax-app/spec/actions/workflows/docs.yml/badge.svg"></a>
</p>

---

## The organisation at a glance

| Repo | What it is | Language | Licence |
|------|-----------|----------|---------|
| **[spec](https://github.com/beatrax-app/spec)** | This repository. Functional and technical specification. | Markdown | CC BY-SA 4.0 |
| **[beatrax](https://github.com/beatrax-app/beatrax)** | The product — Laravel application, thirty-four modules, desktop and mobile bundles. | PHP | Hippocratic 3.0 |
| **[website](https://github.com/beatrax-app/website)** | The public site. | Static | Content CC BY-SA 4.0 |
| **[.github](https://github.com/beatrax-app/.github)** | Organisation-wide community health files, inherited by every repository. | Markdown | CC BY-SA 4.0 |

**In one sentence:** a local-first personal finance dashboard that reads the
statement formats European banks already export, resolves the funding chains
between accounts so you can see what actually paid for what, and syncs
peer-to-peer between your own devices without a server that can read anything.

---

## How to navigate

Sections are numbered so they sort in reading order. Start at `00`, skip ahead
freely.

| Section | Contents | Read this if… |
|---------|----------|---------------|
| **[00-overview](00-overview/)** | Vision, glossary, roadmap, and twenty Architecture Decision Records | …you want the *why* behind any choice |
| **[10-functional](10-functional/)** | Fifty-two features across seven areas, and seven user journeys | …you are deciding what to build, or verifying it got built |
| **[20-architecture](20-architecture/)** | System context, component model, data flow, data model, platform matrix, contracts | …you are implementing across a seam |
| **[30-repos](30-repos/)** | Per-repository specifications | …you are working inside one repository |
| **[40-quality](40-quality/)** | Code standards, comment policy, testing, CI/CD, security, definition of done | …you are writing or reviewing a pull request |
| **[50-governance](50-governance/)** | How change enters the organisation. The spec is canonical — **read this before your first PR** | …you are contributing anywhere |
| **[60-brand](60-brand/)** | Brand rules, surface mapping, the accessibility contract, trademark | …you are touching anything visible |
| **[70-operations](70-operations/)** | Releasing, staging, versions, labels, maintainers, runbooks | …you are running the project or cutting a release |
| **[90-appendix](90-appendix/)** | Licence rationale, data retention, provenance, open questions, references | …you are chasing a citation, or want to know what is unresolved |

### Fast paths

- **"I want to understand the product"** → [vision](00-overview/vision.md) → [journeys](10-functional/journeys/) → [J1 First run](10-functional/journeys/j1-first-run.md)
- **"What does it actually do?"** → [the feature catalogue](10-functional/features/) — 52 features
- **"What is shipped, and what is not?"** → [roadmap](00-overview/roadmap.md) — three buckets, kept strictly apart
- **"How does sync work?"** → [E1](10-functional/features/e-sync/e1-change-capture.md) → [E3](10-functional/features/e-sync/e3-transport.md) → [ADR-0014](00-overview/decisions/0014-op-log-crdt-merge-engine.md) → [ADR-0015](00-overview/decisions/0015-multi-master-p2p-sync.md)
- **"What does it send anywhere?"** → [G1 Privacy stance](10-functional/features/g-ux/g1-privacy.md) — the complete outbound surface
- **"Why is it built this way?"** → [decisions/](00-overview/decisions/)
- **"I want to contribute"** → [contributing](50-governance/contributing.md) — every change cites an identifier that already exists here
- **"What is still unresolved?"** → [open questions](90-appendix/open-questions.md)

---

## Conventions used throughout

| Convention | Meaning |
|------------|---------|
| **MUST / SHOULD / MAY** | [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) keywords. `MUST` is a hard requirement; violating it is a defect. |
| `<feature>-R<n>` | A product requirement, e.g. `B5-R13`. Requirements live **inside** their feature — there is no separate requirements tree. |
| `GOV-R<n>` | A [governance](50-governance/) rule — how change enters the organisation. |
| `ARCH-R<n>` | An [architectural](20-architecture/) requirement — structural rather than behavioural. |
| `Q-R<n>` | A [quality](40-quality/) rule — how code is written. |
| `DES-R<n>` | A [brand](60-brand/) requirement — the checkable visual and verbal constraints. |
| `OPS-R<n>` | An [operations](70-operations/) requirement — running the project. |
| `REPO-R<n>` | A [per-repository](30-repos/) requirement. |
| `J<n>` | A [user journey](10-functional/journeys/). Journeys are the acceptance tests. |
| `ADR-####` | An Architecture Decision Record. Immutable once accepted; superseded rather than edited. |
| **Status: Draft / Accepted / Superseded** | Every document carries one at the top. |

All identifiers are **permanent and never reused**. A withdrawn one is marked
withdrawn in place, because commits and version manifests reference them. They
belong in commit trailers and pull-request bodies — **never in code comments**
([GOV-R6](50-governance/canonical-spec.md#never-in-code-comments)).

---

## Where the product actually is

**The latest released tag is `v1.3.0`, cut 2026-06-14.** Everything since then is
merged, tested, and **not yet in anyone's hands** — the sync stack, envelope
budgeting, splits, reconciliation, the rules engine, migration importers,
notifications, open banking, and the report builder.

That work is being promoted from the former `v1.4` line to **v2.0**, because it
retires category-linked pots (a breaking data change) and because a
single-machine dashboard became a multi-device encrypted system.

The [roadmap](00-overview/roadmap.md) keeps three buckets strictly apart —
**shipped**, **landed but unreleased**, and **remaining for v2.0** — and the
[version manifest](70-operations/versions/2.0.0.toml) locks what v2.0 is
committed to.

## Spec status

| Section | Status | Contents |
|---------|--------|----------|
| 00-overview | Accepted | Vision, glossary, roadmap, 20 decision records |
| 10-functional | Accepted | 52 features across 7 areas, 7 journeys |
| 20-architecture | Accepted | System context, components, data flow, data model, platform matrix, 4 contracts |
| 30-repos | Accepted | spec, beatrax, website, .github |
| 40-quality | Accepted | Standards, comments, testing, CI/CD, security, done, tooling |
| 50-governance | Accepted | Canonical-spec rule, lifecycle, contributing, cross-repo CI, sign-off, routing, overrides, AI contributors |
| 60-brand | Accepted | Brand rules, surface mapping, accessibility, trademark |
| 70-operations | Accepted | Releasing, staging, versions, maintainers, workflow, notifications, runbooks |
| 90-appendix | Accepted | Licence rationale, data retention, provenance, open questions, references |

Unlike a spec-first project, this specification was written **against a product
that already exists**. That has an obvious failure mode — inventing requirements
that read well and were never true — and the defence is
[provenance.md](90-appendix/provenance.md), which says where every part came
from, and [open-questions.md](90-appendix/open-questions.md), which says what is
genuinely unresolved rather than smoothing it over.

---

## Changing this spec

**This repository is canonical.** No change lands in `beatrax` or `website`
unless it cites an identifier that already exists here — enforced mechanically.
See [50-governance](50-governance/).

1. Contested decisions need a new record in `00-overview/decisions/`.
2. Requirements get a **new number**; they are never renumbered, because commits
   and version manifests reference them. A withdrawn one is marked withdrawn in
   place.
3. Superseding a decision means writing a new record that links back — never
   editing the old one. The record of *why you changed your mind* is the valuable
   part.
4. Requirement identifiers belong in commit messages and pull-request bodies.
   **Never in code comments** ([the comment policy](40-quality/code-comments.md)).

## Where to ask

| Kind | Where |
|------|-------|
| A bug, or behaviour that contradicts this spec | An issue on the repository it affects |
| A question | [Discord](https://discord.gg/FYuV9CbTHR), or a discussion |
| A proposal | A discussion first, then a spec pull request |
| A security report | Private vulnerability reporting — never a public issue |

## Licence

Documentation is [CC BY-SA 4.0](LICENSE.md). Code in the product repository is
the **Hippocratic License 3.0** — an ethical-source licence that is deliberately
**not** OSI-approved. That has real practical consequences; read
[the licence rationale](90-appendix/license-rationale.md) before depending on it.

The marks are neither ([60-brand/trademark.md](60-brand/trademark.md)).

---

<p align="center">
  <a href="https://nightworks.io">NightWorks.io</a>
  &nbsp;&middot;&nbsp;
  <a href="https://discord.gg/FYuV9CbTHR">Discord</a>
</p>
