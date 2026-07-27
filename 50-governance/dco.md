# Sign-off

**Status:** Accepted

Every commit carries a Developer Certificate of Origin sign-off matching its
author ([GOV-R15](README.md#the-gov-r-namespace)).

## What it attests

By signing off you certify that you wrote the contribution, or that you have the
right to submit it under the project's licence, and that you understand the
contribution and the sign-off are public and retained indefinitely.

The canonical text is the Developer Certificate of Origin, version 1.1.

## Why this rather than a contributor agreement

A licence agreement asks a contributor to grant rights to a legal entity. There
is no legal entity here, and creating one to accept contributions would be
disproportionate for a project this size.

Sign-off achieves what actually matters — a per-commit, auditable attestation of
provenance — with no paperwork, no account, and no relationship to establish.

It also matters more than usual **because the licence is unusual**. beatrax is
source-available under an ethical-use licence rather than a permissive one
([ADR-0003](../00-overview/decisions/0003-hippocratic-3-0-license.md)), so a
contributor genuinely needs to have read what they are contributing under.

## How

Commit with the sign-off flag, which appends the trailer using your configured
identity. Configure that identity once, and set it to something you are willing
to have in public history permanently.

For a commit already made, amend it with the same flag. For several, rebase with
sign-off applied.

## What is checked

The shared check verifies that **every** commit in a pull request carries a
sign-off whose address matches the commit's author address.

Two exemptions, both because there is no human to attest:

- **Merge commits**, which the platform authors.
- **Automation-authored commits** — dependency bumps, branch updates.

Nothing else is exempt. A missing sign-off fails the check with instructions.

## Common failures

| Failure | Fix |
|---------|-----|
| Sign-off address differs from author address | They must match. Amend, or fix your configured identity and amend. |
| One commit in a series lacks it | Rebase with sign-off applied. |
| A web-interface commit | Add the trailer manually, or make the change locally. |

## Related

- [contributing.md](contributing.md) · [cross-repo-ci.md](cross-repo-ci.md)
- [ADR-0003](../00-overview/decisions/0003-hippocratic-3-0-license.md)
- [90-appendix/license-rationale.md](../90-appendix/license-rationale.md)
