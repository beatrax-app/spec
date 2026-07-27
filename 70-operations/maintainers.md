# Maintainers

**Status:** Accepted

## The registry

One file: [maintainers.toml](maintainers.toml). Every repository's ownership
file is **generated** from it
([OPS-R7](README.md#the-ops-r-namespace),
[GOV-R20](../50-governance/README.md#the-gov-r-namespace)).

Editing an ownership file by hand is a defect: the next regeneration overwrites
it, and the divergence in between is invisible.

## What an entry declares

| Field | Meaning |
|-------|---------|
| `handle` | The platform account. |
| `name` | The person. |
| `lead` | Whether they hold override authority ([50-governance/overrides.md](../50-governance/overrides.md)). |
| `scope` | Which repositories they maintain. `*` means all. |
| `domains` | Which specification sections or path globs they own. `*` means everything in their repositories. |

Scope and domains are separate so maintainership can be split — by repository,
by area, or both — without splitting the registry.

## Current maintainership

**One maintainer**, holding lead authority, covering every repository and every
domain.

That is the honest state of the project. Stating it plainly matters more than
looking larger: a contributor deciding whether to invest an afternoon deserves to
know how many people will review it.

## What a maintainer does

- Triages issues within the target window
  ([50-governance/issue-routing.md](../50-governance/issue-routing.md)).
- Reviews pull requests in their domains.
- Approves changes to workflow files and ownership files, always
  ([GOV-R19](../50-governance/README.md#the-gov-r-namespace)).
- Cuts releases in their repositories
  ([releasing.md](releasing.md)).
- Keeps the registries current.

## What the lead does additionally

Holds override authority, and owes a record, a follow-up, and a deadline for
every override used ([50-governance/overrides.md](../50-governance/overrides.md)).

**With one maintainer, the lead approving an override is one person agreeing with
themselves.** That weakness is stated rather than dressed up; the mitigation is
the never-overridable list.

## Adding a maintainer

1. Add an entry with the narrowest scope and domains that fit the work.
2. Regenerate every affected ownership file.
3. Grant the platform permissions matching the declared scope — no more.
4. Tighten the branch-protection bypass from administrator to pull-request-only.
   The solo accommodation ends when a second person arrives
   ([50-governance/change-lifecycle.md](../50-governance/change-lifecycle.md#the-solo-posture-and-when-it-ends)).

## Removing one

1. Remove the entry, regenerate.
2. Revoke platform permissions.
3. **Rotate any secret they had access to.** Release-signing material in
   particular — it is the only binary-integrity signal the product has
   ([40-quality/security.md](../40-quality/security.md)).

## Secrets

Only the product repository holds release-signing secrets
([REPO-R12](../30-repos/README.md#the-repo-r-namespace)). Access follows lead
authority.

Everything else the pipelines need is a platform-issued token scoped to the run.

## Related

- [maintainers.toml](maintainers.toml) · [project-workflow.md](project-workflow.md)
- [50-governance/overrides.md](../50-governance/overrides.md) · [50-governance/cross-repo-ci.md](../50-governance/cross-repo-ci.md)
