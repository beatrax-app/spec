# Overview

**Status:** Accepted

Why Beatrax exists, what it is committed to, and the record of every contested
decision.

| Page | Read this if… |
|------|---------------|
| [vision.md](vision.md) | …you want the problem, the principles, and the non-goals |
| [glossary.md](glossary.md) | …a word in this specification is being used precisely |
| [roadmap.md](roadmap.md) | …you need to know what is shipped, what has landed but is unreleased, and what remains |
| [decisions/](decisions/) | …you want to know why something is the way it is |

## Start here

> **Show me, in one place, what I actually owe and where the money truly came
> from — across every account chain — so my monthly finances stop being a manual
> reconciliation puzzle.**

That sentence is the product. Everything in this specification is downstream of
it, and it is the tiebreaker for every scoping argument
([vision.md](vision.md)).

## The seven principles

| | |
|---|---|
| **P1** | Nothing leaves the machine |
| **P2** | Sync without a server that can read anything |
| **P3** | Imports are idempotent, history is permanent |
| **P4** | Precision over recall, and never a silent guess |
| **P5** | Money arithmetic is exact |
| **P6** | Boundaries are enforced by tests, not by discipline |
| **P7** | It informs; it never transacts |

Each is stated in full, with what it rules out, in [vision.md](vision.md).

## Where the product is

The latest released tag is **`v1.3.0`** (2026-06-14). The bulk of v2.0 —
the sync stack, envelope budgeting, splits, reconciliation, the rules engine,
migration importers, notifications, open banking, reports — is **landed and
unreleased**. What remains is the mobile peer's real-device acceptance and
app-store distribution.

[roadmap.md](roadmap.md) keeps the three buckets strictly apart, and explains
why the former v1.4 line is being promoted to v2.0 rather than shipped as a
minor.

## Related

- [10-functional/features/](../10-functional/features/) — the behaviour
- [20-architecture/](../20-architecture/) — the shape
- [90-appendix/provenance.md](../90-appendix/provenance.md) — where this came from
