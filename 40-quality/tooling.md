# Tooling

**Status:** Accepted

What the organisation uses, and how it is pinned.

## The product

| Purpose | Tool |
|---------|------|
| Formatting | The framework's standard preset |
| Static analysis | The framework-aware analyser at maximum level in strict mode, plus a strict rule set and a custom boundary rule |
| Tests | The framework-adjacent test runner, with architecture, snapshot, and data-driven support |
| Local environment | A containerised toolchain — the host needs only the container runtime |
| Desktop packaging | The shell's own build command, on three platform runners |
| Local inspection | The framework's console tools; a database client of the developer's choice |

**The containerised toolchain is the standard.** A host language install drifts
from the version and extension set the pipeline uses, and "works on my machine"
bugs follow.

## This repository

| Purpose | Tool |
|---------|------|
| Integrity, governance gate, generation | Small standalone scripts, no dependencies beyond the standard library |
| Spelling | A fast spell-checker with a project dictionary |
| Links | A link checker with a shared configuration |
| Markdown | A linter with a shared configuration |
| Workflow lint | A workflow linter |
| Documentation site | A static book builder, with navigation generated from the section tree |
| Task running | A task runner exposing the same commands the pipeline runs |
| Local hooks | A hook manager mirroring the cheap checks |

The automation scripts deliberately have **no third-party dependencies**. They
run anywhere the standard runtime does, which is what makes them cheap to call
from every repository.

## Pinning

| Kind | Policy |
|------|--------|
| Third-party actions | **Full commit hash**, with an inline version comment ([ADR-0012](../00-overview/decisions/0012-action-pinning.md)) |
| First-party reusable workflows | Their major-version tag (`@v1`) |
| Language dependencies | A lock file, committed |
| Runtime version | The bundled version, with the next one in the matrix |

Scheduled updates run across every ecosystem, grouped so the noise is bounded.
Automation **proposes**; review **verifies** that a bumped hash corresponds to the
version its comment claims.

## Configuration lives at the root

Every tool's configuration is a committed file at the repository root, so the
behaviour a contributor gets locally is the behaviour the pipeline gets. A tool
configured only in a workflow is a tool nobody can run locally.

The shared editor configuration covers indentation and line endings across
languages.

## Adding a tool

Three questions:

1. **Does it enforce something this specification requires?** A tool that
   enforces nothing is a preference, and preferences do not become gates.
2. **Can a contributor run it locally?** If it only exists in the pipeline, it
   produces failures nobody can reproduce.
3. **What is its failure mode?** A tool that fails open is worse than none,
   because it produces a green tick that means nothing.

## Deliberately absent

| Absent | Why |
|--------|-----|
| A coverage threshold gate | The required-test classes are the bar ([testing-strategy.md](testing-strategy.md)) |
| A frontend test runner | Frontend tests are not required |
| A third-party error tracker | [ADR-0004](../00-overview/decisions/0004-local-only-hosting.md) |
| A hosted code-quality service that ingests source | Would send the source somewhere; the local analyser does the job |
| A monorepo build orchestrator | Four repositories with independent lifecycles ([ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md)) |

## Related

- [ci-cd.md](ci-cd.md) · [testing-strategy.md](testing-strategy.md) · [code-standards.md](code-standards.md)
- [ADR-0012](../00-overview/decisions/0012-action-pinning.md)
