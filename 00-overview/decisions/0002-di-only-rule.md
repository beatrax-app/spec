# ADR-0002: Dependency injection only; no facades or global helpers

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

Laravel's facade layer and global helper functions (`auth()`, `request()`,
`config()`, `app()`, `now()`, `Auth::user()`, `DB::table()`, `Cache::get()`,
`Log::info()`) are convenient and ubiquitous in the ecosystem. They are also,
for code that has to remain testable under Larastan level 10 strict and provable
at the module boundary, a slow trap.

Three concrete pains made the case during the early phases:

- **Unit tests acquired hidden setup.** A service that called `auth()`
  internally needed a full container to test. A service that declared
  `User $user` in its constructor needed nothing — instantiate with a stub, call
  the method, assert. The first style accreted a database-refresh requirement
  and slowed the suite; the second ran in microseconds.
- **Static analysis could not see across facade calls.** `Auth::user()` returns
  `User|null` regardless of whether the calling context guarantees an
  authenticated user. A constructor-injected `User $user` is non-nullable by
  construction. Level 10 strict caught the entire class of bugs the facade form
  silently allowed.
- **Module boundaries leaked through helpers.** A `request()` call inside a
  forecasting service does not *look* like a cross-module dependency — but it
  pulls the current HTTP request into a domain service that has no business
  knowing about HTTP. Constructor injection makes the leak visible because the
  request object has to be passed in explicitly.

The rule was tried tentatively in the first phase, formalised into an
architecture invariant in the second, and held without exception through the
eleven phases that shipped v1.0.

## Decision

All collaborators are constructor-injected.

- **Forbidden:** facade static calls (`Auth::user()`, `DB::table()`,
  `Cache::get()`, `Log::info()`, `Storage::disk()`, `Bus::dispatch()`, …) and
  global helper functions (`auth()`, `request()`, `config()`, `app()`, `now()`,
  `today()`, `view()`, …).
- **Allowed:** Eloquent models used directly — instantiation, static lookups,
  relationship traversal, and query-builder via `$model->newQuery()`. The model
  is treated as a value type the consumer is allowed to know about; only the
  global facade indirection is forbidden.
- **Logging** uses a constructor-injected PSR-3 `LoggerInterface`.
- **Time** uses `CarbonImmutable` instances passed in, never `now()` at the call
  site.
- **Configuration** is read via constructor-injected typed config objects or a
  config-repository collaborator. Free-form `config('foo.bar')` is forbidden in
  module code.

One allow-listed exception: Laravel service providers and the Core module's
console-bootstrap layer may use the facade form during framework bootstrap,
because they run before the container has resolved enough to inject. That
carve-out is itself enforced by its own architecture invariants, so it cannot
quietly widen.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Half-DI: facades allowed for cross-cutting concerns (logging, events)** | The carve-out always grew. "Just logging" became "logging plus events" became "logging plus events plus cache". The invariant was easier to defend at the boundary than in the middle. |
| **A custom facade wrapper exposing the typed interface but still globally accessible** | Same testability problem as the facade itself, plus a layer of indirection to debug. |

## Consequences

### Positive

- **Tests stay fast and honest.** Most unit tests instantiate a class with stub
  collaborators and run in microseconds. Feature tests that need a database
  still use one — but by choice, not because a buried helper forced it.
- **Level 10 strict is sustainable.** Every dependency has a declared type.
  Nullability is decided at the constructor, not at every call site.
- **Module boundaries stay visible.** A service that needs the authenticated
  user declares it in its signature, so the dependency shows up in the import
  graph. There is no way to smuggle a cross-module dependency through a global
  helper without someone noticing.

### Negative

- **Onboarding cost.** A developer joining the project has to un-learn the
  facade form for a week or two. The reward — fast tests, visible boundaries —
  is paid back immediately, but the friction is real.
- Constructors are longer. Accepted.

### Neutral

- Third-party packages that use facades internally are unaffected; the rule
  governs first-party module code only.

## Revisit if

- A framework upgrade makes facades statically analysable to the same standard
  as constructor injection, removing the second of the three original
  justifications.

## Related

- [ADR-0001](0001-modular-architecture.md) — the directory split this rule
  operates inside
- [40-quality/code-standards.md](../../40-quality/code-standards.md) — the full
  standard
- [20-architecture/contracts/module-boundary.md](../../20-architecture/contracts/module-boundary.md)
