# `beatrax-app/.github`

**Status:** Accepted · **Licence:** CC BY-SA 4.0

Organisation-wide community health files, inherited by every repository that
does not define its own.

## What it is

The repository whose *name* is the mechanism. Files placed here are inherited
across the organisation, which is the only reason it exists as a separate
repository at all
([ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md)).

## What it holds

| File | Purpose |
|------|---------|
| **Organisation profile** | What `beatrax-app` is, for someone who arrives at the organisation page first. |
| **Code of conduct** | The Contributor Covenant. |
| **Contributing** | A short page pointing at [50-governance/contributing.md](../50-governance/contributing.md), which is canonical. |
| **Security policy** | How to report a vulnerability, the scope, the safe-harbour terms, and the response timeline. |
| **Issue and pull-request templates** | Shared across repositories. The pull-request template MUST prompt for the specification citation the gate requires. |
| **Funding, if any** | Currently none. |

## The security policy

Reports go through **private vulnerability reporting**, not the public issue
tracker.

**In scope:** the application code; the bundled dependencies where the
vulnerability is reachable through Beatrax's own usage; the shell layer in the
released installers; the update verification chain; and local data-at-rest
assumptions.

**Out of scope:** third-party services Beatrax integrates with, unless triggered
exclusively by a flaw in Beatrax's handling; operating-system security on the
user's machine; social engineering; issues requiring the user to grant
destructive permissions on their own machine; and theoretical risks with no
demonstrable reproduction.

**Safe harbour** applies to good-faith research: report privately, do not exploit
beyond demonstrating the issue, do not access data that is not yours, and do not
disclose before the coordinated date.

**Timeline targets** — acknowledgement within a week, a triage decision within a
fortnight, a patch or a detailed status update within two months, and
coordinated disclosure at ninety days from acknowledgement unless extended by
agreement. These are targets, not guarantees, from a small team working in spare
hours — and the policy says so rather than promising more than it can deliver.

## Duplication is deliberate

Some content here restates what [50-governance](../50-governance/) owns. That is
intentional: a contributor who arrives at a repository should find a short,
correct answer without a hop, **and** a pointer to the canonical statement.

The rule for keeping them honest: the short page **points at** the canonical one
and never contradicts it. Where a detail would diverge, the short page omits it
rather than paraphrasing it.

## Requirements

| ID | Requirement |
|----|-------------|
| **REPO-R48** | Organisation-wide health files MUST live here and MUST be inherited by every repository that does not define its own. |
| **REPO-R49** | The pull-request template MUST prompt for the specification citation the governance gate requires. |
| **REPO-R50** | The security policy MUST route reports through private vulnerability reporting, never the public issue tracker. |
| **REPO-R51** | The security policy MUST state its scope, its safe-harbour terms, and its response targets, and MUST present targets as targets. |
| **REPO-R52** | A community health file MUST NOT contradict [50-governance](../50-governance/); where a detail would diverge it MUST omit rather than paraphrase. |
| **REPO-R53** | A code of conduct MUST be present and MUST name its source. |

## Related

- [50-governance/contributing.md](../50-governance/contributing.md) · [50-governance/issue-routing.md](../50-governance/issue-routing.md)
- [40-quality/security.md](../40-quality/security.md)
- [ADR-0013](../00-overview/decisions/0013-four-repo-org-split.md)
