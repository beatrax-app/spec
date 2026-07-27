# ADR-0001: Modular architecture via nwidart/laravel-modules

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

beatrax grew across eleven shipped phases into a system with eighteen bounded
domains — Auth, Categorization, Chains, Community, Core, Counterparties,
Desktop, DevMode, DriftAlerts, EmailScan, Forecasting, Import, Ingestion,
Ledger, Onboarding, Receipts, Recurring, Transfers. It has since grown to
thirty-four. The original Laravel single-namespace layout was tried briefly in
the earliest spikes and discarded after the first three modules. With more than
a handful of domains, two failure modes appeared every week:

- **Implicit coupling.** Code in one feature reached into another's Eloquent
  models, query builders, or job classes. A change in the receiver silently
  broke the caller, and the test suite caught it only because every domain
  shared the same database.
- **Diluted ownership.** When the directory layout was `app/Models`,
  `app/Services`, `app/Jobs`, nothing in the filesystem said which module owned
  which class. Discussions about "where should this go" recurred every week.

## Decision

Every domain lives under `Modules/<Name>/` with a strict `Public/` versus
`Internal/` split:

- `Modules/<Name>/Public/` — service-class contracts, DTOs, events, and
  services that other modules MAY import. The public surface is the module's
  API.
- `Modules/<Name>/Internal/` — actions, jobs, listeners, parsers, pipeline
  stages, resolvers, and HTTP controllers. Only the owning module may import
  anything from here.
- `Modules/<Name>/Models/` — Eloquent models. Other modules MAY use them
  directly (instantiation, `Model::find()`, relationships, query-builder via
  `$model->newQuery()`); see [ADR-0002](0002-di-only-rule.md) for the
  facade-versus-Eloquent boundary.
- `Modules/<Name>/Database/` — per-module migrations, seeders, and factories.
- `Modules/<Name>/Routes/`, `Modules/<Name>/Resources/views/`,
  `Modules/<Name>/tests/` — standard Laravel locations, scoped per module.

Cross-module access goes through the importing module's `Public/` surface or
through Laravel events. A module that needs a behaviour another module owns
declares a contract in its own `Public/Contracts/`; the owning module implements
it; the binding is wired in a service provider. The receiver never imports the
implementer's `Internal/` namespace.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Plain Laravel namespaces with import-linter rules** | The rule set would have grown unbounded, and no off-the-shelf linter understood Laravel's facade indirection. |
| **Hand-rolled "Contexts" directory with custom auto-loading** | Too much custom infrastructure to maintain alongside a single-developer project. |
| **Hexagonal / onion architecture with port and adapter layers** | The ceremony of declaring ports for every collaborator swamped the velocity benefit of module-level isolation for a project where one person owns every boundary anyway. |

## Consequences

### Positive

- **Enforced by tests, not convention.** The boundary architecture test carries
  dedicated invariants for cross-module imports, state-column mutators, facade
  usage, and NativePHP shell access. Twenty-nine shipped at v1.0.0 and the set
  has grown since; new modules add their own invariants alongside the contract
  they define. A boundary violation fails the test run, which fails the PR gate.
- **A second, earlier line of defence.** A custom static-analysis rule catches
  the same class of violation at analysis time rather than test time. From a
  file resolving to `Modules\X\…`, any import targeting another module `Y` must
  begin with `Modules\Y\Public\…` or `Modules\Y\Models\…`; anything else fails,
  including directories that currently hold no classes, so a future module
  cannot silently gain a public surface.
- **New modules follow a fixed template.** Adding a module means creating the
  seven standard directories plus the manifest files that wire the
  service-provider auto-loader. The cost of creating one is low, which means the
  right answer to "where does this go" is often "a new module".
- **Refactoring discipline.** Pulling logic out of a fat controller asks "which
  module owns this", not "where does this fit in `app/Services/`".

### Negative

- **Migration ordering is global even though migrations are per-module.**
  Laravel sorts by timestamp across all modules, so cross-module foreign keys
  work — but a developer adding a column on another module's table is doing
  something wrong by definition, and only review catches that.
- Thirty-four service providers to boot. Measurable, accepted.

### Neutral

- The convention is the one the Laravel community already recognises, so the
  onboarding cost for the directory layout itself is near zero.

## Revisit if

- The module count grows past the point where the boundary test's runtime is
  material to the PR gate.
- A module boundary is repeatedly violated for the same legitimate reason,
  indicating the split is in the wrong place rather than that the rule is wrong.

## Related

- [ADR-0002](0002-di-only-rule.md) — why collaborators are constructor-injected
  even within a module
- [ADR-0011](0011-code-comment-policy.md) — the same enforce-by-test posture
  applied to comments
- [20-architecture/contracts/module-boundary.md](../../20-architecture/contracts/module-boundary.md)
  — the boundary contract as it applies across the org
- [20-architecture/component-model.md](../../20-architecture/component-model.md)
  — every module and what it owns
