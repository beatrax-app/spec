# Architecture

**Status:** Accepted

The structural shape of the system, written **against** the
[feature catalogue](../10-functional/features/) rather than alongside it. A
technical decision here that cites no requirement is unjustified and should be
challenged in review.

## Contents

| Page | Covers |
|------|--------|
| [system-context.md](system-context.md) | What Beatrax is, what it talks to, and what it deliberately does not |
| [component-model.md](component-model.md) | The thirty-four modules and what each owns |
| [data-flow.md](data-flow.md) | The end-to-end path from a source file to a rendered figure |
| [data-model.md](data-model.md) | The tables, their trust boundaries, and their state columns |
| [platform-matrix.md](platform-matrix.md) | What runs where, and what differs |
| [contracts/](contracts/) | The inter-repo and inter-module contracts |

## The `ARCH-R` namespace

Architectural requirements are structural rather than behavioural. They are
things the *shape* of the system must satisfy, which no single feature owns.

| ID | Requirement |
|----|-------------|
| **ARCH-R1** | Every domain MUST live in its own module with a public surface and a private interior; a module MUST NOT import another module's interior. |
| **ARCH-R2** | The module boundary MUST be enforced by both static analysis and an architecture test, not by convention. |
| **ARCH-R3** | Cross-module behaviour MUST flow through the consuming module's declared contract or through an event, never through a direct call into an interior. |
| **ARCH-R4** | Every collaborator MUST be constructor-injected; global accessors are forbidden outside the documented bootstrap carve-out. |
| **ARCH-R5** | Every state column MUST have exactly one sanctioned mutator, enforced by architecture test and, where the store supports it, by trigger. |
| **ARCH-R6** | Every user-scoped table MUST carry a user reference, and every query that can run outside an authenticated request MUST filter on it explicitly. |
| **ARCH-R7** | Every monetary value MUST be stored as a minor-unit integer plus a currency code and handled as exact money. |
| **ARCH-R8** | Every storage path MUST resolve through a single path authority, enforced by architecture test. |
| **ARCH-R9** | Platform-shell imports MUST be confined to a single module, enforced by architecture test. |
| **ARCH-R10** | Migrations MUST be append-only; a shipped migration MUST NOT be edited. |
| **ARCH-R11** | The database MUST be reproducible by replaying the merged operation log. |
| **ARCH-R12** | Every write that must reach other devices MUST be captured to the operation log, and the merge registry MUST be verified against the live schema by test. |
| **ARCH-R13** | The set of columns encrypted at rest MUST be defined in a single registry, and a regression guard MUST fail the build on a raw read or write of a registered column. |
| **ARCH-R14** | Work requiring the at-rest key MUST run in a context where the key is available, or skip with a warning; it MUST NOT silently produce a wrong result. |
| **ARCH-R15** | The outbound network surface MUST be enumerable and MUST be enumerated in [G1](../10-functional/features/g-ux/g1-privacy.md). |
| **ARCH-R16** | The product MUST run as a single process against a single-file store, with no additional service required at install time. |
| **ARCH-R17** | Long-running work MUST commit in bounded transactions; no operation may hold a transaction proportional to total history. |
| **ARCH-R18** | Every background dispatch MUST occur after the transaction that caused it commits, never inside it. |
| **ARCH-R19** | A parser MUST NOT write to the database. |
| **ARCH-R20** | Every ingestion path MUST be idempotent on the transaction fingerprint. |

## Related

- [00-overview/decisions/](../00-overview/decisions/) — why the shape is what it is
- [30-repos/](../30-repos/) — how the shape is distributed across repositories
- [40-quality/](../40-quality/) — how it is enforced
