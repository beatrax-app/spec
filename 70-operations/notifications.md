# Notifications

**Status:** Accepted

What gets announced, where, and the rules the announcer obeys.

> This page is about **project** notifications — what the organisation announces
> to people. The product's own notifications, to its user, are
> [C8](../10-functional/features/c-insight/c8-notifications.md).

## Where

The project's chat is **[Discord](https://discord.nightworks.io)**.

| Announcement | Audience |
|--------------|----------|
| A release published | Everyone |
| A new issue needing triage | Maintainers |
| A pull request awaiting review | Maintainers |
| A build failure on the default branch | Maintainers |

Nothing else is announced automatically. An announcement stream that carries
everything is a stream nobody reads, which means the two announcements that
matter get missed.

## The rules the announcer obeys

| Rule | Why |
|------|-----|
| **A missing webhook is a no-op, not a failure** | A repository without the secret configured must not fail its pipeline over a notification. |
| **Every dynamic value reaches the payload through the environment** and is serialised as data — never interpolated into a shell ([OPS-R24](README.md#the-ops-r-namespace)) | Issue titles and branch names are attacker-controllable. |
| **Role mentions only, never everyone** ([OPS-R23](README.md#the-ops-r-namespace)) | A tool that can wake a whole server will be muted, and then it announces nothing. |
| **A mention rides only the opening message** of a threaded announcement | Continuations do not re-notify. |
| **Long bodies split at line boundaries** and continue beneath the opening message | A truncated announcement is worse than a long one. |
| **A threading failure falls back to a plain post** | A misconfigured channel must never lose the announcement. |
| **No secret, token, or key material may appear** in any announcement | Announcements are public or semi-public by nature. |

## Release announcements

A release announcement carries the version, a link, and the headline of what
changed — drawn from the generated notes, which are the single record of a release
([OPS-R11](README.md#the-ops-r-namespace)).

**A breaking change is stated in the announcement, not left to the reader to
find** ([OPS-R12](README.md#the-ops-r-namespace)). For v2.0 that means the
category-linked-pot retirement and the manual re-assignment it requires
([ADR-0017](../00-overview/decisions/0017-envelope-budgeting-replaces-category-pots.md)).

A draft release is **not** announced. Announcement follows publication, so
nobody is told about something they cannot download
([releasing.md](releasing.md)).

## What is deliberately not announced

| Not announced | Why |
|---------------|-----|
| Every merge | Noise. The release is the record. |
| Every dependency bump | Noise, and grouped anyway. |
| Product telemetry | There is none ([ADR-0004](../00-overview/decisions/0004-local-only-hosting.md)). |
| Anything derived from a user's data | There is nothing to derive it from, and there never will be. |

That last row is not a policy so much as a structural fact, and it is worth
stating: the project has no channel through which a user's data could reach an
announcement, because it never leaves their machine.

## Related

- [releasing.md](releasing.md) · [project-workflow.md](project-workflow.md)
- [50-governance/issue-routing.md](../50-governance/issue-routing.md)
- [C8 Notifications](../10-functional/features/c-insight/c8-notifications.md) — the product's own, which is a different thing
