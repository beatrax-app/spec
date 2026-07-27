# CI and CD

**Status:** Accepted

## The gates, per repository

| Gate | Where it is defined | Applies to |
|------|---------------------|------------|
| **Governance** — cites an identifier that exists on the canonical spec | This repository, reusable | Every implementation repository |
| **Sign-off** — every commit attests its origin | This repository, reusable | Every repository |
| **Commit subjects** — conventional | This repository, reusable | Every repository |
| **Hygiene** — workflow lint, spelling, links, markdown | This repository, reusable | Every repository |
| **Security** — secret scanning, dependency vulnerabilities | This repository, reusable | Every repository |
| **Quality** — formatting, static analysis, tests | The product repository | The product |
| **Integrity** — identifiers resolve, none duplicated, links unbroken | This repository | This repository |
| **Documentation** — assemble, link-check, build, publish | This repository | This repository |

Shared gates are defined **once** and called, so a fix propagates in one merge
([Q-R20](README.md#the-q-r-namespace),
[50-governance/cross-repo-ci.md](../50-governance/cross-repo-ci.md)).

## The product's quality gate

Three checks, across a runtime matrix covering the version the bundle ships and
the next supported one. All three must pass before review starts.

1. **Formatting** — the standard preset.
2. **Static analysis** — maximum level, strict mode, with the custom boundary
   rule and the strict rule set.
3. **Tests** — the full suite including architecture tests, run serially as the
   pipeline runs it.

Running both runtime versions catches code drifting toward a construct only the
newer one supports **before** it breaks a release build
([20-architecture/platform-matrix.md](../20-architecture/platform-matrix.md)).

## The release pipeline

Triggered by a tag push, and by nothing else.

```text
tag push
   │
   ▼
1  quality gate, fail-fast
   │      (a broken build must not spend forty minutes producing
   │       installers it cannot publish)
   ▼
2  three platform builds, in parallel
   │      each: install → build → smoke-test → upload
   │      smoke test = install or extract, launch, ask the health
   │      endpoint, compare the reported versions
   ▼
3  publish — only when all three succeeded
          generate the update manifests with binary hashes
          sign each manifest
          create the release with every binary and manifest attached
          stable → DRAFT · release candidate → published prerelease
```

The asymmetric publish is
[ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md).

The smoke test exists to catch the most common silent regression for this class
of build: **a bundle that boots but reports the wrong version**.

## Rules the pipeline obeys

| Rule | Why |
|------|-----|
| **Third-party actions pinned to a full commit hash**, with an inline version comment | Tags are mutable, and this attack has happened in the wild ([ADR-0012](../00-overview/decisions/0012-action-pinning.md)) |
| **First-party reusable workflows referenced by major-version tag** | The tag mover and the consumer are the same protected repository, so fixes still propagate in one merge — but a breaking change can cut `v2` instead of breaking every sibling at once |
| **No trigger that exposes secrets to a fork's code** | The canonical secret-exfiltration pattern, made impossible by construction |
| **No build-time telemetry or third-party upload** | The local-only contract extends to the pipeline |
| **No update path that skips verification** | The signed manifest is the only binary-integrity signal ([F6](../10-functional/features/f-platform/f6-updates.md)) |
| **Only the product repository holds signing secrets** | Least privilege across the organisation |
| **Untrusted event data passes through the environment**, never string interpolation into a shell | Workflow injection |

## Secret scanning

Handled at the **platform level** — repository secret scanning plus push
protection — rather than as a workflow. That covers every push and pull request
against the canonical provider patterns.

The repositories hold no project-specific high-entropy tokens needing a custom
rule.

## Branch protection

The default branch of every repository:

| Rule | Effect |
|------|--------|
| Blocked deletion | The branch cannot be removed |
| Blocked force-push | Published history cannot be rewritten |
| Linear history | Squash or rebase only |
| Signed commits | Every commit on the default branch is verified |
| Required status checks | The listed gates must pass |
| Up-to-date before merge | A rebase against the default branch is forced |

The posture is **light and solo-friendly**: an administrator may push directly
without a pull-request-of-one ceremony. That bypass switches off the moment
external contributors arrive
([50-governance/change-lifecycle.md](../50-governance/change-lifecycle.md)).

**One carve-out is not optional:** a change to a workflow file or to the
ownership file requires owner approval regardless, because workflow files execute
with a token and need the second pair of eyes the bypass would otherwise skip
([REPO-R13](../30-repos/README.md#the-repo-r-namespace)).

### Keeping the ruleset honest

The ruleset names status checks by exact string. **If a job name or a matrix axis
changes, the ruleset needs the same edit** — otherwise a renamed check silently
stops being required, and the protection quietly evaporates. That is a
release-checklist item, not something to notice later.

## Local hooks

The cheap checks — spelling, markdown, integrity — run locally before commit and
push, so a contributor finds a failure in seconds rather than in a pipeline
([Q-R21](README.md#the-q-r-namespace)).

They mirror CI; they do not replace it.

## Dependencies

Scheduled updates across every ecosystem, grouped so the noise is bounded.
Alerts enabled. A digest bump is **proposed** by automation and **verified** by
review — a reviewer checks that the new hash corresponds to the version the
comment claims.

## Related

- [ADR-0012](../00-overview/decisions/0012-action-pinning.md) · [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md)
- [security.md](security.md) · [tooling.md](tooling.md) · [testing-strategy.md](testing-strategy.md)
- [50-governance/cross-repo-ci.md](../50-governance/cross-repo-ci.md)
- [70-operations/releasing.md](../70-operations/releasing.md)
