# Cross-repository CI

**Status:** Accepted

Shared checks are defined **once**, in this repository, and called by the others.
One definition, no drift ([Q-R20](../40-quality/README.md#the-q-r-namespace)).

## The reusable workflows

| Workflow | Enforces |
|----------|----------|
| **Governance gate** | A citation is present, and every cited identifier exists on the canonical specification ([GOV-R2](README.md#the-gov-r-namespace), [GOV-R3](README.md#the-gov-r-namespace)) |
| **Sign-off** | Every commit carries a sign-off matching its author ([GOV-R15](README.md#the-gov-r-namespace)) |
| **Commit lint** | Conventional subjects ([GOV-R16](README.md#the-gov-r-namespace)) |
| **Hygiene** | Workflow lint, spelling, links, markdown |
| **Security** | Secret scanning and dependency vulnerabilities |
| **Label sync** | Upserts the canonical label set ([OPS-R6](../70-operations/README.md#the-ops-r-namespace)) |
| **Stale** | A gentle, generous stale policy |
| **Notify** | Posts to the maintainer channel |
| **Spec references** | The sticky comment linking cited identifiers to their defining files ([GOV-R22](README.md#the-gov-r-namespace)) |

## How a repository calls one

A short caller workflow that names the shared definition, referenced by its
**major-version tag**
([ADR-0021](../00-overview/decisions/0021-reusable-workflow-version-tags.md)):

```yaml
jobs:
  dco:
    uses: beatrax-app/spec/.github/workflows/dco.yml@v1
```

`v1` moves forward as fixes merge here, so a fix still propagates in one merge
rather than needing a bump in every consumer. A **breaking** change cuts `v2`
instead, so consumers migrate deliberately rather than all failing at once.

Every repository calls the governance gate, sign-off, commit lint, and hygiene
([REPO-R1](../30-repos/README.md#the-repo-r-namespace)–[REPO-R4](../30-repos/README.md#the-repo-r-namespace)).

## The workflow contract, and what breaks it

The tag is a promise about the **calling interface**, not about the internals.
These are breaking, and cut a new major:

| Change | Why it breaks a consumer |
|--------|--------------------------|
| Removing or renaming an input or secret | The caller's `with:`/`secrets:` block stops matching |
| Making an optional input required | Callers that omit it start failing |
| Renaming a job | Consumers name jobs as required status checks in their rulesets; a rename silently stops the check being required ([OPS-R18](../70-operations/README.md#the-ops-r-namespace)) |
| Tightening a check so a pull request that passed now fails | The gate moves under merges already in flight |

Everything else — a bug fix, a new optional input, a faster implementation — moves
`v1` forward.

**Every move is also an immutable `v1.<minor>.<patch>` tag**, so what `v1` pointed
at on a given day stays recoverable and a consumer that must hold still can pin
to the immutable one.

### Moving the tag

After a change to a shared workflow merges here:

```sh
git tag -s v1.2.0 -m "shared workflows v1.2.0"
git tag -f -s v1   -m "shared workflows v1 → v1.2.0"
git push origin v1.2.0
git push --force origin v1
```

Forgetting this means the fix reaches nobody, which is the one real cost of this
scheme ([ADR-0021](../00-overview/decisions/0021-reusable-workflow-version-tags.md#negative)).

## How the governance gate works

1. Check out the calling repository's pull request.
2. Check out the canonical specification's default branch alongside it.
3. Gather the pull-request body and the commit messages **through the
   environment** — untrusted event data is never interpolated into a shell.
4. Extract every identifier from the citation trailers.
5. Resolve each against the specification checkout: requirement definitions are
   found by their table-row shape; decision records by their filenames.
6. Fail with guidance if there is no citation, or if any identifier does not
   resolve.

The failure message explains what to do — cite a requirement, open a
specification pull request, or cite the maintenance identifier — rather than only
saying no ([G2](../10-functional/features/g-ux/g2-error-model.md) applies to the
pipeline too).

## Generated rather than maintained

| Artefact | Generated from |
|----------|----------------|
| Each repository's ownership file | The single maintainer registry ([GOV-R20](README.md#the-gov-r-namespace)) |
| Each repository's labels | The canonical label set |
| The documentation site's navigation | The section tree |

Editing a generated file by hand is a defect: the next regeneration overwrites
it, and the divergence in between is invisible.

## Why the shared workflows live in the specification repository

Because the rule and its enforcement belong together. A governance rule stated
here and enforced in a repository somewhere else is two things that can drift.

It also means the specification repository is a **dependency of the others'
pipelines**, which is worth stating plainly: an outage or a broken default branch
here blocks merges elsewhere. The mitigation is that the scripts have no
third-party dependencies and the workflows are small.

## Adding a shared check

1. Does every repository need it? If not, it belongs in the one that does.
2. Can it fail closed? A check that fails open produces a green tick that means
   nothing.
3. Does it enforce something this specification requires? If it enforces nothing
   written down, write that down first.

## Related

- [canonical-spec.md](canonical-spec.md) · [dco.md](dco.md)
- [40-quality/ci-cd.md](../40-quality/ci-cd.md) · [ADR-0012](../00-overview/decisions/0012-action-pinning.md)
- [30-repos/spec.md](../30-repos/spec.md) · [70-operations/maintainers.md](../70-operations/maintainers.md)
