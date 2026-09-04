# Quality

**Status:** Accepted

How code is written, tested, reviewed, and shipped. Every rule here is either
enforced by a gate or explicitly marked as a judgment call — a rule that depends
on reviewer vigilance and nothing else decays, and this section says so about
itself.

## Contents

| Page | Covers |
|------|--------|
| [code-standards.md](code-standards.md) | How code is written |
| [code-comments.md](code-comments.md) | The comment policy, mechanical and judgment rules |
| [testing-strategy.md](testing-strategy.md) | What is tested, at which level, and what is not |
| [ci-cd.md](ci-cd.md) | The pipeline, its gates, and its rules |
| [security.md](security.md) | The threat model and the security practices |
| [definition-of-done.md](definition-of-done.md) | When a change is finished |
| [tooling.md](tooling.md) | The tools and how they are pinned |

## The `Q-R` namespace

| ID | Requirement |
|----|-------------|
| **Q-R1** | Every collaborator MUST be constructor-injected; global accessors are forbidden outside the documented bootstrap carve-out. |
| **Q-R2** | Static analysis MUST run at the maximum level in strict mode, and MUST pass. |
| **Q-R3** | Formatting MUST be applied by the standard preset, and MUST pass. |
| **Q-R4** | The full test suite MUST pass, including architecture tests. |
| **Q-R5** | All three gates MUST pass before review starts. |
| **Q-R6** | Money MUST NOT be represented as a floating-point number anywhere on the money path. |
| **Q-R7** | Every architectural invariant MUST have a test that fails when it is violated. |
| **Q-R8** | A new module MUST ship its own invariants alongside the contracts it defines. |
| **Q-R9** | Every user-scoped surface MUST have a cross-user test asserting not-found. |
| **Q-R10** | Every ingestion path MUST have an idempotency test proving a re-run produces no new rows. |
| **Q-R11** | Comments MUST obey the mechanical rules, enforced by test. |
| **Q-R12** | Every documentation link in code MUST resolve to a real file, enforced by test. |
| **Q-R13** | Commit subjects MUST be conventional. |
| **Q-R14** | Every commit MUST carry a sign-off matching its author. |
| **Q-R15** | Every third-party action MUST be pinned to a full commit hash with an inline version comment. |
| **Q-R16** | No pipeline may use a trigger that exposes repository secrets to a fork's code. |
| **Q-R17** | No build-time telemetry or third-party upload may exist in the pipeline. |
| **Q-R18** | Secret scanning and push protection MUST be enabled at the platform level. |
| **Q-R19** | Dependency alerts and scheduled updates MUST be enabled. |
| **Q-R20** | Hygiene checks — workflow lint, spelling, links, markdown — MUST be defined once and shared. |
| **Q-R21** | Local hooks MUST mirror the cheap CI checks so a contributor finds a failure before pushing. |
| **Q-R22** | The documentation site MUST be link-checked before it is built. |
| **Q-R23** | A change that alters behaviour MUST cite a requirement identifier that already exists on the canonical spec. |
| **Q-R24** | A user-visible change MUST carry a conventional commit subject written as release-note copy, in the user's language. |
| **Q-R25** | A test MUST NOT be marked skipped or pending to make a gate green without a recorded reason. |
| **Q-R26** | A component property rendered as raw markup MUST be locked against client mutation. |
| **Q-R27** | A gate MUST NOT fail on a transient network condition: a download it performs MUST be retried with bounded backoff, and an executable it fetches MUST be verified against a pinned digest before it runs. |

## The principle underneath

> **A rule that is not enforced is not a rule.**

Every convention in this section that *can* be mechanised **is** mechanised. The
ones that cannot — whether a comment earns its place, whether an abstraction is
the right one — are labelled as judgment rules and are binding anyway, on humans
and on AI contributors alike
([50-governance/ai-contributors.md](../50-governance/ai-contributors.md)).

That split is deliberate. Conflating them makes the mechanical layer either
toothless or tyrannical.

## Related

- [ADR-0001](../00-overview/decisions/0001-modular-architecture.md) · [ADR-0002](../00-overview/decisions/0002-di-only-rule.md) · [ADR-0011](../00-overview/decisions/0011-code-comment-policy.md) · [ADR-0012](../00-overview/decisions/0012-action-pinning.md)
- [20-architecture/contracts/module-boundary.md](../20-architecture/contracts/module-boundary.md)
- [50-governance/](../50-governance/)
