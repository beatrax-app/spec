# Staging a version

**Status:** Accepted

A release is not "whatever happened to merge". It is a **locked set of
requirement identifiers** the release is committed to delivering, recorded in a
manifest before work is judged against it.

## Why lock goals

Two failure modes this prevents:

**Scope creep by accretion.** Without a locked set, a release contains whatever
merged, and "is this ready" has no answer because there is no definition of
ready.

**Silent omission.** A requirement everybody assumed was in a release, and was
not, is discovered by a user.

A manifest turns both into checkable questions.

## The manifests

One file per version under [versions/](versions/), naming:

- The version.
- Its status.
- Which repositories it cuts.
- **Its goals** — the requirement identifiers it is committed to delivering.

Every goal must be an identifier the specification actually defines
([OPS-R14](README.md#the-ops-r-namespace)). A manifest citing something that
does not exist fails validation, which is the same guarantee the governance gate
gives commits.

## The lifecycle

```text
planned  ──▶  staged  ──▶  releasable  ──▶  released
                                              │
                                              └──▶ yanked
```

| Status | Meaning |
|--------|---------|
| **planned** | Goals drafted. Editable. |
| **staged** | Goals locked. Work is judged against them. |
| **releasable** | Every goal satisfied. Ready to tag. |
| **released** | Tagged and published. |
| **yanked** | Withdrawn after release. |

**Only one version may be staged or releasable at a time**
([OPS-R15](README.md#the-ops-r-namespace)). The train is serial. Two versions in
flight means two answers to "what are we working on", and neither is true.

## Staging

Validation refuses unless:

1. The manifest exists and is `planned`.
2. No other version is already `staged` or `releasable`.
3. Every goal resolves to a requirement the specification defines.

On success it names the repositories the version cuts.

## While a version is staged

**Goals are locked.** Changing them is a reviewed change, labelled as a goals
change ([OPS-R17](README.md#the-ops-r-namespace),
[GOV-R21](../50-governance/README.md#the-gov-r-namespace)) — not a quiet edit.

Work outside the goals is **not blocked**; bugs get fixed, dependencies get
bumped. But a *feature* outside the goals is labelled for a later version rather
than silently expanding this one
([OPS-R21](README.md#the-ops-r-namespace)).

## Making a version releasable

Every goal satisfied, in the sense the
[definition of done](../40-quality/definition-of-done.md) means: implemented,
tested, cited, documented, and walked.

A goal that will not make it is either **descoped** — moved to a later manifest,
as a reviewed goals change — or the version waits. It is not quietly dropped.

## After release

The manifest is marked released and stays as a permanent record of what that
version committed to. It is not deleted and not edited afterwards, except to
mark it yanked.

A revert that undoes something a released manifest locked updates the manifest
too — a released version's goals are a statement about what shipped, and it must
stay true.

## The current state

**v2.0 is staged.** Its manifest is [versions/2.0.0.toml](versions/2.0.0.toml),
and the bulk of its goals are already satisfied by work that has landed and not
yet been released — see the
[roadmap](../00-overview/roadmap.md#landed-but-unreleased--the-body-of-v20).

The outstanding goals are the mobile peer's remaining acceptance work and
app-store distribution, the latter of which is
[not yet scoped](../00-overview/roadmap.md#open-questions).

## Related

- [releasing.md](releasing.md) · [versions/](versions/)
- [50-governance/change-lifecycle.md](../50-governance/change-lifecycle.md)
- [40-quality/definition-of-done.md](../40-quality/definition-of-done.md)
- [00-overview/roadmap.md](../00-overview/roadmap.md)
