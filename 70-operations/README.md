# Operations

**Status:** Accepted

Running the project: releasing, staging, maintainership, labels, notifications,
and the runbooks.

## Contents

| Page | Covers |
|------|--------|
| [releasing.md](releasing.md) | Branching, tagging, and cutting a release |
| [staging.md](staging.md) | How a version's goals are locked and made releasable |
| [versions/](versions/) | The machine-readable version manifests |
| [maintainers.md](maintainers.md) | Who maintains what, and how ownership is generated |
| [project-workflow.md](project-workflow.md) | Labels, boards, and how work is tracked |
| [notifications.md](notifications.md) | What gets announced, where |
| [runbooks.md](runbooks.md) | Operational procedures |
| [labels.yml](labels.yml) · [maintainers.toml](maintainers.toml) | The registries themselves |

## The `OPS-R` namespace

| ID | Requirement |
|----|-------------|
| **OPS-R1** | The pushed tag MUST be the single source of truth for a build's version string. |
| **OPS-R2** | A build produced outside the release pipeline MUST self-identify as a development build. |
| **OPS-R3** | The release workflow MUST trigger only on a tag push. |
| **OPS-R4** | A stable tag MUST publish as a draft for human review; a tag carrying any semver prerelease identifier MUST publish immediately as a prerelease. |
| **OPS-R5** | Every platform build MUST pass its smoke test before the publish step runs. |
| **OPS-R6** | Labels MUST be synced to every repository from one canonical file; a label MUST NOT be created by hand. |
| **OPS-R7** | Maintainership MUST be declared in one registry, and every ownership file MUST be generated from it. |
| **OPS-R8** | A generated file MUST NOT be edited by hand. |
| **OPS-R9** | Dependency updates MUST run on a schedule and MUST be grouped so the noise is bounded. |
| **OPS-R10** | Every release MUST publish checksums and a signed manifest. |
| **OPS-R11** | A release body MUST be generated from the commit history the tag spans; no hand-maintained file may be the release-note source. |
| **OPS-R12** | A breaking change MUST be given release-note prominence, not one line among the rest. |
| **OPS-R13** | A version's goals MUST be locked in a manifest before it is staged. |
| **OPS-R14** | Every goal MUST be a requirement identifier that the specification defines. |
| **OPS-R15** | Only one version may be staged or releasable at a time. |
| **OPS-R16** | A manifest MUST record its status, and status MUST move planned → staged → releasable → released. |
| **OPS-R17** | A change to a staged version's goals MUST be reviewed as a goals change. |
| **OPS-R18** | The branch ruleset's required status checks MUST be updated whenever a job name or a matrix axis changes. |
| **OPS-R19** | The default branch MUST be protected with linear history, signed commits, required checks, and blocked force-push and deletion. |
| **OPS-R20** | A new issue MUST be labelled as needing triage and assigned from the generated ownership file. |
| **OPS-R21** | Work outside the currently staged version's goals MUST be labelled for a later version rather than expanding the current one. |
| **OPS-R22** | A pull request from a non-maintainer that passes checks with no review MUST be flagged and announced. |
| **OPS-R23** | Announcements MUST NOT mention everyone; role mentions only, and only on an opening message. |
| **OPS-R24** | Untrusted event data MUST reach an announcement through the environment, never by interpolation into a shell. |
| **OPS-R25** | A stale policy MUST be generous and MUST exempt anything blocked, security-relevant, or marked as wanting help. |
| **OPS-R26** | Backups MUST be verified, retained on a bounded policy, and exempt a pre-restore snapshot from pruning. |

## Where announcements go

The project's chat is **[Discord](https://discord.gg/FYuV9CbTHR)**. Build and
release notifications, triage notices, and awaiting-review flags post there;
what goes where is [notifications.md](notifications.md).

## Related

- [40-quality/ci-cd.md](../40-quality/ci-cd.md) · [50-governance/](../50-governance/)
- [20-architecture/contracts/versioning.md](../20-architecture/contracts/versioning.md)
