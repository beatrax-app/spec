# `beatrax-app/beatrax`

**Status:** Accepted · **Licence:** Hippocratic License 3.0

The product. Moving from `nightworksio/beatrax`.

## What it is

A Laravel application organised into thirty-four modules
([20-architecture/component-model.md](../20-architecture/component-model.md)),
shipped as a desktop bundle for three platforms plus a mobile client, and
runnable self-hosted.

## Stack

| Layer | Choice | Recorded in |
|-------|--------|-------------|
| Language | PHP 8.5 | [ADR-0006](../00-overview/decisions/0006-nativephp-desktop-shell.md) |
| Framework | Laravel 13 | — |
| Interface | Livewire with single-file components, a component library, and Alpine for local interactivity | — |
| Styling | Tailwind v4 | — |
| Store | SQLite in write-ahead journal mode | [ADR-0005](../00-overview/decisions/0005-sqlite-wal.md) |
| Modules | Per-module structure with a public and internal split | [ADR-0001](../00-overview/decisions/0001-modular-architecture.md) |
| Money | Exact minor-unit money with a dedicated library | [ADR-0009](../00-overview/decisions/0009-brick-money-multi-currency.md) |
| Queue | The database driver in the bundle | [ADR-0007](../00-overview/decisions/0007-database-queue-driver.md) |
| Desktop | A bundled runtime plus an embedded browser shell | [ADR-0006](../00-overview/decisions/0006-nativephp-desktop-shell.md) |
| Charts | A client charting library, resizing with its container | [G4](../10-functional/features/g-ux/g4-pwa.md) |

Parser libraries for the ISO 20022 statement format, the legacy SWIFT format,
CSV, and PDF; typed data objects; and the platform's own cryptographic
primitives for signing, key agreement, sealing, and key derivation.

**No runtime extension outside the bundled set may be used**
([20-architecture/platform-matrix.md](../20-architecture/platform-matrix.md)).
In particular the removed mail extension is not used anywhere, which is the
contractual reason mail access is provider-API-only
([A4](../10-functional/features/a-ingestion/a4-email-scanning.md)).

## The quality gate

Three gates on every pull request, across a runtime matrix covering the bundled
version and the next one:

1. **Formatting** — the standard preset.
2. **Static analysis** — the maximum level, in strict mode, with the custom
   boundary rule and the strict rule set.
3. **Tests** — unit, feature, contract, and architecture, in one run.

All three must pass before review starts.
[40-quality/](../40-quality/) is the full statement.

## What lives here versus in the spec

| Here | In the spec |
|------|-------------|
| Implementation detail: which class, which file, which table | Behaviour and requirements |
| Local development setup and troubleshooting | The quality standards it satisfies |
| Operational runbooks with real commands | The operations requirements they satisfy |
| Per-module implementation maps | The component model |
| The changelog | The roadmap |

The product repository keeps its own internal documentation tree for the left
column. This specification owns **what** and **why**; that tree owns **where in
the code**.

**Where the two disagree, this specification wins**, and the product-repository
page is the one that needs updating
([50-governance/canonical-spec.md](../50-governance/canonical-spec.md)).

## Branching, going forward

The default branch is the integration branch. The former development branch is
merged into it and **retired** — it is not a living branch and must not be
documented as one.

The next release is cut from the default branch inside the new organisation
([00-overview/roadmap.md](../00-overview/roadmap.md#the-v14--v20-promotion),
[70-operations/releasing.md](../70-operations/releasing.md)).

## Requirements

| ID | Requirement |
|----|-------------|
| **REPO-R22** | The module boundary MUST be enforced by both a custom static-analysis rule and architecture tests. |
| **REPO-R23** | The quality gate MUST run formatting, maximum-level strict static analysis, and the full test suite, and all three MUST pass before review. |
| **REPO-R24** | The gate MUST run across a runtime matrix covering both the bundled version and the next supported one. |
| **REPO-R25** | No runtime extension outside the bundled set may be used. |
| **REPO-R26** | The release workflow MUST trigger only on a tag push. |
| **REPO-R27** | The release workflow MUST NOT use any trigger that would expose repository secrets to a fork's code. |
| **REPO-R28** | Every platform build MUST succeed before the publish step runs. |
| **REPO-R29** | Each platform bundle MUST be smoke-tested — launched and asked for its health endpoint — before upload. |
| **REPO-R30** | Release manifests MUST be signed, and every binary hash MUST be recorded in the signed manifest. |
| **REPO-R31** | A stable tag MUST publish as a draft; a release-candidate tag MUST publish immediately as a prerelease. |
| **REPO-R32** | The changelog MUST be the single source of release notes, and the release body MUST be generated from it. |
| **REPO-R33** | A user-visible change MUST add a changelog entry; an omitted entry MUST simply not appear in the release. |
| **REPO-R34** | The bundled environment template MUST contain only placeholders, and the application key MUST be minted on first launch behind a sentinel. |
| **REPO-R35** | No build-time telemetry, error-reporting initialisation, or third-party source-map upload may exist in the pipeline. |
| **REPO-R36** | The product's own documentation MUST NOT contradict this specification; where it does, this specification wins and the product page is corrected. |
| **REPO-R37** | The former development branch MUST be retired after merge and MUST NOT be documented as a living branch. |

## Related

- [20-architecture/](../20-architecture/) · [40-quality/](../40-quality/)
- [10-functional/features/](../10-functional/features/) — the behaviour this implements
- [70-operations/releasing.md](../70-operations/releasing.md)
- [ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md)
