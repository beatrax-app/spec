# Provenance

**Status:** Accepted

Where the content of this specification came from, and what was deliberately
left behind.

This page exists because a specification written **after** the product it
describes has an obvious failure mode: inventing requirements that read well and
were never true. The defence is to say where every part came from.

## The sources

| Source | What it gave |
|--------|--------------|
| The product repository's decision records | [ADR-0001](../00-overview/decisions/0001-modular-architecture.md)–[ADR-0011](../00-overview/decisions/0011-code-comment-policy.md), ported without changing their decisions |
| Its architecture documentation | [20-architecture](../20-architecture/) — module boundaries, the data model, the ingestion pipeline, chain resolution, categorisation |
| Its per-module documentation | The behaviour, states, edge cases, and behavioural contracts throughout [10-functional](../10-functional/features/) |
| Its conventions documentation | [40-quality/code-comments.md](../40-quality/code-comments.md), including the mechanical and judgment rule tables |
| Its pipeline documentation | [40-quality/ci-cd.md](../40-quality/ci-cd.md), branch protection, the release sequence |
| Its legal documentation | [90-appendix/license-rationale.md](license-rationale.md), [90-appendix/data-retention.md](data-retention.md) |
| Its research and history documentation | Constraints and hazards that became requirements |
| Its planning corpus | The [roadmap](../00-overview/roadmap.md)'s three buckets, the requirement inventory, the deferred register |
| Its git history, tags, and releases | The release baseline — verified rather than assumed |
| Its readme, notice, security policy, and contributing guide | The voice, the licence posture, [30-repos](../30-repos/) |
| The module tree | The functional map, [20-architecture/component-model.md](../20-architecture/component-model.md) |
| The route surface | The navigation map in [10-functional/features/README.md](../10-functional/features/README.md) |

## What was verified rather than assumed

The release baseline. The latest tag was checked against the repository's actual
tags and branches rather than taken from a planning document:

- Seven tags exist; **`v1.3.0`**, dated 2026-06-14, is the newest and sits on the
  default branch.
- The former development line carried substantial merged work with no tag.
- That line is being promoted to **v2.0** and retired as a branch.

The [roadmap](../00-overview/roadmap.md) is built on that verification, and it
keeps shipped, landed-but-unreleased, and outstanding strictly apart.

## What was deliberately left in the product repository

Not everything belongs here. The split is **what and why** versus **where in the
code**.

| Left behind | Why |
|-------------|-----|
| Per-module implementation maps — which class, which file, which table | They change with every refactor. This specification names behaviour and contracts; the code is where the code is. |
| Local development setup and troubleshooting | Changes with the toolchain and must be tested against it. |
| Executable runbooks with real commands and flags | Same. [70-operations/runbooks.md](../70-operations/runbooks.md) states what each must guarantee; the product states how. |
| The release notes | They are generated from the commit history and belong with the releases. |
| Per-module test-running instructions | Toolchain detail. |
| Design explorations and interface sketches | Distilled into the shipped surfaces and into [60-brand](../60-brand/). |
| The internal codename | Not the product's name. Recorded in the [glossary](../00-overview/glossary.md#deliberately-not-used) so nobody reintroduces it. |
| Workflow scaffolding — plan files, discussion logs, pattern maps, review transcripts | Artefacts of a process, not reference documentation. The decisions they produced are in the decision records; the acceptance criteria they produced are in the feature docs. |
| Phase numbers | Identifiers here are requirements and decision records. Phase numbers have no relationship to them and reconciling the two would be noise ([roadmap](../00-overview/roadmap.md#open-questions)). |

## What was added rather than ported

Nine decision records —
[ADR-0012](../00-overview/decisions/0012-action-pinning.md) onward — were written
for this specification. **None invents a decision.** Each records one already
made and evidenced in the product's code, its pipeline configuration, or its
planning corpus: action pinning, the organisation split, the merge model, the
sync topology, the transport, the envelope cutover, the plaintext set, the
publish asymmetry, and the connector's constraints.

The `GOV-R`, `ARCH-R`, `Q-R`, `DES-R`, `OPS-R`, and `REPO-R` namespaces are new,
because the organisation is new. They codify practices already in force.

## Where sources disagreed

Recorded rather than silently resolved:

| Disagreement | Resolution |
|--------------|------------|
| The product's release-cadence document still describes a pre-public version series and names a graduation tag that shipped four releases ago | It is **stale**. [70-operations/releasing.md](../70-operations/releasing.md) is current; the product page needs updating or deleting ([roadmap](../00-overview/roadmap.md#conflicting-release-cadence-documentation)). |
| A planning document's headline requirement count disagreed with the count of identifiers it listed | Noted in the source itself. Neither number is used here; this specification counts its own. |
| Two phase entries covered the same comment-policy work, one recorded complete and one not started | The work is done; the duplicate entry is a planning artefact. Not carried over. |
| A dependency-version table in the product's stack documentation predates several upgrades | Superseded by the lock file. This specification names versions only where a decision depends on them. |

## Open questions carried forward

Every unresolved question found in the sources, or created by this
specification's own scope, is recorded under an explicit heading in the document
it belongs to — never smoothed over
([GOV-R26](../50-governance/README.md#the-gov-r-namespace)).

They are indexed in [open-questions.md](open-questions.md).

## Related

- [00-overview/roadmap.md](../00-overview/roadmap.md) · [open-questions.md](open-questions.md)
- [30-repos/beatrax.md](../30-repos/beatrax.md#what-lives-here-versus-in-the-spec)
- [50-governance/canonical-spec.md](../50-governance/canonical-spec.md)
