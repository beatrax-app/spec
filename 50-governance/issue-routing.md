# Issue routing

**Status:** Accepted

Where things go, and what happens to them.

## Where

| Kind | Where |
|------|-------|
| Behaviour contradicts the specification | An issue on the repository it affects |
| A behaviour the specification does not cover | A discussion, then a specification pull request |
| A question | [The Discord](https://discord.nightworks.io), or a discussion |
| A proposal | A discussion first |
| A security vulnerability | **Private vulnerability reporting only** — never a public issue |
| A corpus suggestion | The in-product flow ([C9](../10-functional/features/c-insight/c9-community-corpus.md)) |
| Anything about the specification itself | An issue or a pull request here |

## The distinction that matters

**A bug is behaviour that contradicts the specification.** Everything else —
however reasonable — is a change request, and a change request becomes a
specification change before it becomes code
([GOV-R23](README.md#the-gov-r-namespace)).

That is not pedantry. It is what keeps the specification an accurate description
of the product rather than a description of some of it.

## What happens to a new issue

Automatically: it is labelled as needing triage and assigned to the covering
maintainer from the generated ownership file, and a notification is posted to the
maintainer channel.

Then, by hand:

1. **Is it a bug or a change request?** Which requirement does it contradict? If
   none, it is a change request.
2. **Label it** from the canonical set: an area label, plus a kind, plus a
   status.
3. **Route it.** A change request gets the specification-change label and a
   pointer to the discussion or pull request that will carry it.
4. **Scope it.** Work outside the currently staged version's goals is labelled
   for the next one rather than silently expanding the current release
   ([70-operations/staging.md](../70-operations/staging.md)).

## Labels

One canonical set, synced to every repository from one file
([70-operations/labels.yml](../70-operations/labels.yml),
[OPS-R6](../70-operations/README.md#the-ops-r-namespace)).

**Never create a label by hand.** Add it to the file and let the sync apply it
everywhere — a hand-made label exists in one repository and nowhere else, which
is how label sets fragment.

The set covers kinds, areas, statuses, and release-train concerns. Area labels
map one-to-one onto the feature areas in the
[catalogue](../10-functional/features/).

## Awaiting a maintainer

A pull request from a non-maintainer that passes CI with no review is flagged and
posted to the maintainer channel. The flag clears when a review lands or the
pull request closes.

That exists because the failure mode of a solo-maintained project is not
rejecting contributions — it is **not noticing them**.

## Stale handling

Generous, and easy to reverse. An issue quiet for a long stretch is marked stale
and closed after a further grace period, with a message saying a comment keeps it
open and reopening is one click.

Exempt: anything blocked, security-relevant, or explicitly marked as wanting
help. Those are not stale; they are waiting.

## Response expectations

A small team working in spare hours. Targets, honestly labelled as targets:

| Kind | Target |
|------|--------|
| A security report acknowledged | Within a week |
| A new issue triaged | Within a fortnight |
| A pull request first-reviewed | Within a fortnight |
| A security patch or a detailed status update | Within two months |

If something slips, the honest response is to say so
([G5](../10-functional/features/g-ux/g5-plain-language.md) applies to
maintainers too).

## Related

- [contributing.md](contributing.md) · [change-lifecycle.md](change-lifecycle.md)
- [70-operations/labels.yml](../70-operations/labels.yml) · [70-operations/project-workflow.md](../70-operations/project-workflow.md) · [70-operations/notifications.md](../70-operations/notifications.md)
- [30-repos/dot-github.md](../30-repos/dot-github.md)
