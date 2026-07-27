# AGENTS.md — spec

Orientation for a focused session in this repository.

> **Common rules for every beatrax repository** live in
> [50-governance/ai-contributors.md](50-governance/ai-contributors.md). This file
> is the spec-repository-specific header; the shared rules are canonical there.

## What this repository is

The **canonical specification** for beatrax. No code. It spans every
implementation repository and owns the cross-cutting decisions between them.
Everything else in the organisation is built *against* this repository, and every
change elsewhere cites an identifier that exists here.

Start at [README.md](README.md), then the section you need.

## The load-bearing rule

**This repository is canonical.** When you change it:

- New requirements get a **new, permanent identifier** — never renumber, never
  reuse a withdrawn one. Mark withdrawn ones withdrawn in place.
- A behavioural change is a new or edited requirement; a contested decision is a
  new **decision record** — immutable, superseded rather than edited.
- Identifiers live in seven namespaces: feature (`B5-R13`), `GOV-R`, `ARCH-R`,
  `REPO-R`, `Q-R`, `DES-R`, `OPS-R`. They belong in commit messages and
  pull-request bodies — **never in code comments** (`GOV-R6`).

## The rule specific to this specification

This specification describes a product that **already exists**. That has one
failure mode above all others: **inventing a requirement that reads well and was
never true.**

- Every requirement traces to something real in the product repository — its
  code, its documentation, its planning corpus, or its history.
- Where a source is silent or two sources disagree, say so under an explicit
  **open question** heading (`GOV-R25`) and add it to
  [90-appendix/open-questions.md](90-appendix/open-questions.md).
- Where something is not yet satisfied, mark the requirement *(Open)* and say so
  plainly. Several already are.
- [90-appendix/provenance.md](90-appendix/provenance.md) records where the
  content came from. Keep it honest.

## Before you commit

Run `just ci`, or at minimum `python3 scripts/integrity.py`: every cited
identifier must resolve, none may be duplicated, every internal link must
resolve. CI enforces the same.

Specification pull requests do **not** run the governance gate — this repository
is the source of citations, not a consumer. They run integrity, hygiene, and the
documentation build.

## Layout

```text
00-overview/     vision, glossary, roadmap, 20 decision records
10-functional/   51 features across 7 areas, 7 journeys — WHAT and WHY
20-architecture/ system context, components, data flow, data model,
                 platform matrix, 4 contracts
30-repos/        per-repository specifications
40-quality/      standards, comments, testing, CI/CD, security, done, tooling
50-governance/   the canonical-spec rule and its enforcement
60-brand/        brand rules, surface mapping, accessibility, trademark
70-operations/   releasing, staging, versions, maintainers, workflow, runbooks
90-appendix/     licence rationale, retention, provenance, open questions, refs
scripts/         integrity.py, spec_check.py (the reusable gate), and friends
```

## House style

Dense, opinionated, tables over prose. Every document: a status, a one-line
intent, the substance, a requirements table, then Related links.

British-leaning English, calm and precise — the same voice as the product
([60-brand/brand-rules.md](60-brand/brand-rules.md)). No exclamation marks. No
claiming a protection the implementation does not provide.

Every technical claim traces to a requirement. A decision citing nothing should
be challenged.

## Conventions and preferences

- Commits carry **no** AI or co-author attribution trailers.
- Propose before writing; wait for approval before committing.
- Maintained by NightWorks.io · community on
  [Discord](https://discord.gg/FYuV9CbTHR).
