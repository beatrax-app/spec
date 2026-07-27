# Contract — the module boundary

**Status:** Accepted

The contract every module in the product repository obeys, and the mechanisms
that enforce it. Recorded here rather than only in the product repository
because it is the structural rule the whole architecture rests on
([ADR-0001](../../00-overview/decisions/0001-modular-architecture.md)).

## The contract

A module MAY import from another module's:

- **public surface** — contracts, data objects, events, and services the owning
  module has committed to keeping stable, and
- **models** — a deliberate shared read seam.

A module MUST NOT import from another module's:

- **interior** — actions, jobs, listeners, parsers, pipeline stages, resolvers,
  state machines, controllers, and anything else, or
- **any other namespace it owns** — its database directory, its providers, its
  resources, its routes.

That last clause is deliberately absolute: **everything outside the public and
model namespaces is closed**, including directories that hold no classes today,
so a future module cannot silently acquire a public surface by accident.

## The two paths across a boundary

### A contract, for a behaviour

The **consuming** module declares the interface in its own public surface. The
owning module implements it in its interior. The binding is wired in the owning
module's provider.

The consumer never learns which class implements it, which is what makes the
implementation free to change.

### An event, for a reaction

The **owning** module raises an event from its public surface. Any other
module's listeners may subscribe.

Events live in the public surface because once another module listens for one,
removing it is a breaking change — the same status as a contract.

## Enforcement

Three independent mechanisms, deliberately.

| Mechanism | When | Catches |
|-----------|------|---------|
| **A custom static-analysis rule** | Analysis | Any import outside the public and model namespaces. Detects the importing module by declared namespace first, falling back to filesystem path, so deliberate violation fixtures can live outside the module tree. |
| **Architecture tests** | Test run | Cross-module imports, state-column mutators, forbidden global accessors, shell imports, path helpers, raw queries missing a user filter, registry contracts, and theme companions. |
| **Strict analysis rules** | Analysis | The global-accessor ban. |

A violation fails the test run, which fails the pull-request gate. Files outside
the module tree are not governed by the boundary rule.

## Sanctioned-writer invariants

The boundary is not only about imports. A set of architecture invariants
establishes, for each shared column or table, **exactly one** sanctioned writer:

| Concern | Rule |
|---------|------|
| Transactions | One sanctioned writer; every other module goes through it. |
| The category column | One sanctioned updater. |
| The pair pointer | The chain resolver and the transfer matcher only. |
| Statement summaries | One sanctioned writer. |
| Every state column | One sanctioned state machine ([data-model.md](../data-model.md)). |
| Split legs | One sanctioned writer. |
| The developer audit trail | One sanctioned writer. |
| Alert acknowledgement | One sanctioned writer. |
| Provider secrets | One sanctioned repository. |
| The learnt identifier bridge | One sanctioned reader. |
| External link opening | One sanctioned action, behind a scheme and host gate. |

Additionally, read-only relationships are enforced where they matter: the chain
resolvers may not write transactions (bar the documented retyping exception and
the pair pointer); the mail scanner, the recurring detector, the forecaster, and
the receipt matcher may not write transactions at all; parsers may not write
anything.

## Adding a module

1. Create the seven standard directories and the module manifest.
2. Declare its public surface.
3. Register its bindings, schedules, and components in its own provider.
4. Add its own architecture invariants alongside the contracts it defines.
5. Register any table it introduces in the merge registry
   ([op-log.md](op-log.md)) and, where the table holds identifying text, in the
   sensitive-column registry.

Step 5 is the one most often missed, and the failure is silent: an unregistered
column simply never syncs. A schema-guard test exists because that has happened.

## Related

- [ADR-0001](../../00-overview/decisions/0001-modular-architecture.md) · [ADR-0002](../../00-overview/decisions/0002-di-only-rule.md)
- [component-model.md](../component-model.md) · [data-model.md](../data-model.md)
- [40-quality/code-standards.md](../../40-quality/code-standards.md)
