# Testing strategy

**Status:** Accepted

## What is tested, and where

| Level | Covers | Shape |
|-------|--------|-------|
| **Unit** | Pure logic: parsers, cadence inference, statistics, percentiles, fingerprint normalisation, retention policy, pattern generalisation, amount parsing. | Instantiate with stubs, call, assert. Microseconds. |
| **Feature** | A behaviour end to end through the application, with a database. | The bulk of the suite. |
| **Contract** | Cross-module invariants: idempotency, sanctioned writers, boundary compliance, comment policy, cross-user isolation, registry consistency. | The load-bearing safety net. |
| **Architecture** | Structural rules asserted over the source tree itself. | Fails on a violation, not on a regression. |

Data-driven tests carry their fixtures with them — "given this row, expect this
transaction" is exactly the shape ingestion needs.

## The architecture tests are the point

The module boundary, the dependency rule, the sanctioned writers, the
state-machine mutators, the shell quarantine, the path authority, the encrypted
registry, and the theme companions are all asserted structurally.

This is what makes [ADR-0001](../00-overview/decisions/0001-modular-architecture.md)
and [ADR-0002](../00-overview/decisions/0002-di-only-rule.md) real rather than
aspirational. A convention that lives only in a document decays; one that fails
the build does not.

Twenty-nine boundary invariants shipped at the first stable release and the set
has grown since. **A new module ships its own invariants alongside the contracts
it defines** ([Q-R8](README.md#the-q-r-namespace)).

## The tests that must exist

Some tests are required by class, not by coverage:

| Class | Requirement |
|-------|-------------|
| **Cross-user isolation** | Every user-scoped surface has a test asserting a cross-user request returns not-found ([Q-R9](README.md#the-q-r-namespace)). A route added without one is a gap. |
| **Idempotency** | Every ingestion path has a test proving a re-run produces no new rows ([Q-R10](README.md#the-q-r-namespace)). |
| **Sanctioned writer** | Every shared column has an architecture test naming its one writer. |
| **State machine** | Every lifecycle has tests for its legal transitions and for an illegal one raising. |
| **Registry consistency** | The merge registry is verified against the live schema; the encrypted-column registry backs a regression guard on raw reads and writes. |
| **Query budget** | Where a bounded query count matters, a test asserts it. |
| **Convergence** | Sync merge strategies have tests proving two devices converge. |

## What is not tested

**Frontend tests are not required.** The interface is server-rendered with a thin
client layer, and test investment goes into backend correctness. This is a
deliberate trade, stated so it is not mistaken for an oversight.

**Browser acceptance is human.** Driven browser walkthroughs happen per feature
before it is considered done, but they are a human gate rather than an automated
one.

**Real-device acceptance is human**, and it is currently the outstanding gate on
the mobile peer ([E5](../10-functional/features/e-sync/e5-mobile-peer.md)).

## Determinism

Tests must not depend on wall-clock time, on random values, or on execution
order.

- Time is injected and frozen where it matters.
- Seed data is deterministic — no random generation in seeders.
- Projections derive their jitter from a stable seed, so "noise" is reproducible
  ([C5](../10-functional/features/c-insight/c5-forecasting.md)).

A test that passes alone and fails in a batch is a **defect in the test**, and
the honest response is to bisect it rather than to run that suite serially
forever.

## Known environment limitations

A small number of tests spawn real child processes, and those behave
inconsistently under a bind-mounted container filesystem while passing on native
runners.

This is a documented environment limitation, not a regression — and it is
documented **specifically** so a contributor whose only failures are those tests
does not spend an afternoon on them.

## Coverage

There is **no coverage threshold gate**. The required-test classes above are the
actual bar: a suite with high coverage and no cross-user test is worse than one
with lower coverage and a complete set of isolation probes.

Coverage is measured and looked at. It does not fail a build on a number.

## Skipping

A test marked skipped or pending to make a gate green **must carry a recorded
reason** ([Q-R25](README.md#the-q-r-namespace)). An unexplained skip is a silent
loss of a guarantee somebody deliberately added.

## Running

The full suite runs serially, as the pipeline runs it. A parallel run is
available for faster local iteration, with the known-flaky suites called out.

## Related

- [code-standards.md](code-standards.md) · [ci-cd.md](ci-cd.md) · [definition-of-done.md](definition-of-done.md)
- [20-architecture/contracts/module-boundary.md](../20-architecture/contracts/module-boundary.md)
