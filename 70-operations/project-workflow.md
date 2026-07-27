# Project workflow

**Status:** Accepted

How work is tracked, and by what.

## The tools, and the deliberate absences

| Tool | Used |
|------|------|
| Issues | Yes — the record of work |
| Milestones | Yes — grouped by version |
| Discussions | Yes — questions, proposals, show-and-tell |
| Labels | Yes — one canonical set, synced |
| Wiki | **No** — documentation lives in this repository and the product's own tree |
| Project boards | **No** — issues and milestones cover it at this scale |

The absences are deliberate. A wiki is a second documentation home with no
review gate, which is how documentation forks from reality. A board at
one-maintainer scale is a second place to keep in sync with the first.

## Labels

One canonical set in [labels.yml](labels.yml), synced to every repository
([OPS-R6](README.md#the-ops-r-namespace)).

**Never create a label by hand.** Add it to the file; the sync applies it
everywhere. A hand-made label exists in one repository and nowhere else, which is
how label sets fragment.

The set covers:

| Group | Examples |
|-------|----------|
| **Kind** | bug, enhancement, documentation, question |
| **Governance** | spec-change, needs-spec, governance |
| **Status** | needs-triage, awaiting-maintainer, blocked |
| **Release train** | release-blocker, goals-change, scope:next |
| **Concern** | security, privacy, breaking-change, dependencies, ci |
| **Welcome** | good first issue, help wanted |
| **Area** | one per feature area in the [catalogue](../10-functional/features/) |

Area labels map one-to-one onto the catalogue's areas, so "where does this
belong" has the same answer in the tracker and in the specification.

## Automation

| Automation | Does |
|------------|------|
| **Triage** | Labels a new issue as needing triage, assigns from the generated ownership file, and announces ([OPS-R20](README.md#the-ops-r-namespace)) |
| **Labeller** | Applies area and kind labels from the changed paths |
| **Awaiting maintainer** | Flags a non-maintainer pull request that passed checks with no review, and clears the flag when a review lands or it closes ([OPS-R22](README.md#the-ops-r-namespace)) |
| **Label sync** | Upserts the canonical set on a schedule. Additive — it never deletes a label it does not know about |
| **Stale** | Marks quiet items stale after a generous window and closes after a further grace period, exempting anything blocked, security-relevant, or marked as wanting help ([OPS-R25](README.md#the-ops-r-namespace)) |
| **Dependencies** | Scheduled updates across every ecosystem, grouped ([OPS-R9](README.md#the-ops-r-namespace)) |

The awaiting-maintainer flag exists because the failure mode of a
solo-maintained project is not rejecting contributions — it is **not noticing
them**.

## Milestones and the release train

A milestone per version, matching a manifest under [versions/](versions/).

The manifest is the **authority** on what a version is committed to; the
milestone is a convenience view. Where they disagree, the manifest wins and the
milestone is corrected.

Work outside the staged version's goals is labelled for a later version rather
than silently expanding the current release
([OPS-R21](README.md#the-ops-r-namespace),
[staging.md](staging.md)).

## Anything generated is not edited

Ownership files, labels, and the documentation navigation are all generated
([OPS-R8](README.md#the-ops-r-namespace)). Editing one by hand is a defect that
survives only until the next regeneration.

## Related

- [labels.yml](labels.yml) · [maintainers.md](maintainers.md) · [staging.md](staging.md) · [notifications.md](notifications.md)
- [50-governance/issue-routing.md](../50-governance/issue-routing.md)
