# Architecture Decision Records

**Status:** Accepted

An ADR captures a decision that was *contested* — where a competent engineer
could reasonably have chosen otherwise. It records the alternatives and why they
lost, so that revisiting the decision later starts from evidence rather than
from scratch.

## Rules

1. **ADRs are immutable once Accepted.** To change a decision, write a new ADR
   that supersedes the old one and link both ways. The record of changing your
   mind is the valuable part.
2. **Only genuinely contested decisions get an ADR.** "We use `league/csv` for
   CSV parsing" is not a decision, it is a default.
3. **Numbers are permanent and never reused.** A withdrawn ADR is marked
   withdrawn in place.
4. **Cite them as `ADR-NNNN`.** CI resolves every citation against the files in
   this directory ([GOV-R11](../../50-governance/canonical-spec.md#the-gov-r-namespace)).

## Provenance

ADRs 0001–0011 were written inside the product repository (`.docs/adr/`) between
May and July 2026 and are **ported here without changing their decisions**. Their
original "graduated from" provenance lines are preserved because they are real
history. ADRs 0012 onward were written for this spec, each from evidence in the
product repo's shipped code, its planning corpus, or its CI configuration — none
of them invent a decision that was not already made.

## Index

| # | Decision | Status | Origin |
|---|----------|--------|--------|
| [0001](0001-modular-architecture.md) | Modular architecture via `nwidart/laravel-modules` | Accepted | Ported |
| [0002](0002-di-only-rule.md) | Dependency injection only; no facades or global helpers | Accepted | Ported |
| [0003](0003-hippocratic-3-0-license.md) | Hippocratic License 3.0 | Accepted | Ported |
| [0004](0004-local-only-hosting.md) | Local-only hosting; no cloud, telemetry, or remote logging | Accepted | Ported |
| [0005](0005-sqlite-wal.md) | SQLite with WAL journal mode as the canonical store | Accepted | Ported |
| [0006](0006-nativephp-desktop-shell.md) | NativePHP as the desktop shell | Accepted | Ported |
| [0007](0007-database-queue-driver.md) | Database queue driver in the shipped bundle; Horizon is dev-only | Accepted | Ported |
| [0008](0008-multi-user-belongstouser.md) | Multi-user readiness via `BelongsToUser` and explicit `user_id` filters | Accepted | Ported |
| [0009](0009-brick-money-multi-currency.md) | `brick/money` for multi-currency arithmetic | Accepted | Ported |
| [0010](0010-recovery-codes-no-smtp.md) | Password reset via recovery codes; no SMTP-based reset | Accepted | Ported |
| [0011](0011-code-comment-policy.md) | Code comment policy: readable code, architecture in documentation | Accepted | Ported |
| [0012](0012-action-pinning.md) | Third-party actions SHA-pinned; first-party reusable workflows on `@main` | Accepted | New |
| [0013](0013-four-repo-org-split.md) | Four repositories in the `beatrax-app` org, not a monorepo | Accepted | New |
| [0014](0014-op-log-crdt-merge-engine.md) | A signed append-only op-log with HLC ordering; SQLite as a materialised view | Accepted | New |
| [0015](0015-multi-master-p2p-sync.md) | Full peer-to-peer multi-master sync, not hub-and-spoke | Accepted | New |
| [0016](0016-noise-transport-zero-knowledge-relay.md) | Noise XX/IK transport with a zero-knowledge relay fallback | Accepted | New |
| [0017](0017-envelope-budgeting-replaces-category-pots.md) | Envelope budgeting replaces category-linked pots | Accepted | New |
| [0018](0018-amounts-plaintext-at-rest.md) | Amount columns stay plaintext under at-rest encryption | Accepted | New |
| [0019](0019-asymmetric-release-publish.md) | Stable tags publish as drafts; release candidates publish immediately | Accepted | New |
| [0020](0020-open-banking-byo-key-ais-only.md) | Open banking is bring-your-own-key, AIS-only, and off by default | Accepted | New |

> **Not here:** the spec's own governance rules. Those are not architectural —
> no component's design depends on them. They live in
> [50-governance](../../50-governance/).

## Template

```markdown
# ADR-NNNN: <title>

**Status:** Proposed | Accepted | Superseded by ADR-NNNN
**Date:** YYYY-MM-DD

## Context
What forces are at play? What makes this non-obvious?

## Decision
What we are doing, stated plainly.

## Alternatives considered
| Option | Why it lost |

## Consequences
### Positive
### Negative
### Neutral

## Revisit if
Concrete conditions that would justify a new ADR.
```

## Reading order

For a first pass, the two structural decisions that shape every source file:

1. [ADR-0001 — Modular architecture](0001-modular-architecture.md)
2. [ADR-0002 — Dependency injection only](0002-di-only-rule.md)

Then the privacy posture and how it is expressed:

3. [ADR-0004 — Local-only hosting](0004-local-only-hosting.md)
4. [ADR-0003 — Hippocratic License 3.0](0003-hippocratic-3-0-license.md)

Then the operational layer:

5. [ADR-0005 — SQLite with WAL](0005-sqlite-wal.md)
6. [ADR-0007 — Database queue driver](0007-database-queue-driver.md)
7. [ADR-0006 — NativePHP desktop shell](0006-nativephp-desktop-shell.md)

Then the sync stack, which is the largest single body of design in the project:

8. [ADR-0015 — Multi-master peer-to-peer sync](0015-multi-master-p2p-sync.md)
9. [ADR-0014 — Op-log and CRDT merge engine](0014-op-log-crdt-merge-engine.md)
10. [ADR-0016 — Noise transport and zero-knowledge relay](0016-noise-transport-zero-knowledge-relay.md)
11. [ADR-0018 — Amounts plaintext at rest](0018-amounts-plaintext-at-rest.md)

Then the domain-specific calls and the org-level ones as you need them.
