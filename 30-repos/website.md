# `beatrax-app/website`

**Status:** Accepted · **Licence:** content CC BY-SA 4.0; code Hippocratic 3.0

The public site.

## What it is

The place someone lands before they have downloaded anything. It explains what
beatrax is, who it is for, what it costs them in trust, and where to get it.

It is **not** the documentation site — that is built from this specification and
published from it
([30-repos/spec.md](spec.md)).

## What it must say

The site is the first place the product's honesty is tested, because it is the
only surface where overstating things is tempting.

| Must say | Because |
|----------|---------|
| Source-available, **not** open source | The licence is not OSI-approved, and the distinction has real consequences ([90-appendix/license-rationale.md](../90-appendix/license-rationale.md)) |
| Local-first, with the outbound surface named | The claim is checkable and should be presented as checkable ([G1](../10-functional/features/g-ux/g1-privacy.md)) |
| That sync is peer-to-peer and end-to-end encrypted, and what the relay can see | Overstating it would be the worst kind of dishonesty for this product |
| That the installers are unsigned, and why | The user meets the warning anyway; better they meet the reason first |
| Which platforms are supported, including the Intel exception | [20-architecture/platform-matrix.md](../20-architecture/platform-matrix.md) |

It must **not** claim protections the product does not provide
([G5](../10-functional/features/g-ux/g5-plain-language.md)).

## Voice and visuals

One voice with the product and this specification: British-leaning, calm,
precise. No exclamation marks, no growth-marketing register, no urgency
manufactured out of nothing.

Brand primitives are shared, not re-invented
([20-architecture/contracts/design-tokens.md](../20-architecture/contracts/design-tokens.md)).
Screenshots come from the product repository.

## What it does not do

- **No analytics.** A privacy-first product's marketing site tracking its
  visitors would be an unforced contradiction, and anyone who noticed would be
  right to draw conclusions about the rest of it.
- **No newsletter capture, no chat widget, no third-party embeds** that would
  load code from elsewhere onto a visitor's browser.
- **No download telemetry.**

## Requirements

| ID | Requirement |
|----|-------------|
| **REPO-R38** | The site MUST NOT include analytics, tracking, or third-party embeds that load code onto a visitor's browser. |
| **REPO-R39** | The site MUST describe beatrax as source-available and MUST NOT describe it as open source. |
| **REPO-R40** | The site MUST name the outbound-call surface rather than only claiming local-first. |
| **REPO-R41** | The site MUST state what a sync relay can and cannot observe. |
| **REPO-R42** | The site MUST state that installers are unsigned and MUST explain why. |
| **REPO-R43** | The site MUST NOT claim a protection the product does not provide. |
| **REPO-R44** | The site MUST consume shared brand primitives and MUST NOT introduce its own. |
| **REPO-R45** | Screenshots MUST come from the product repository and SHOULD be refreshed when a release materially changes a surface. |
| **REPO-R46** | The site MUST state which platforms are supported, including documented exceptions. |
| **REPO-R47** | Deployment MUST be from the default branch, and the deployed commit MUST be identifiable. |

## Open question

**The hosting and deployment target is not settled here.** The site's build and
deploy arrangement is a repository-local decision; this page states what the
site must and must not do rather than how it is served.

If the arrangement ever introduces an outbound dependency on a visitor's browser
— a hosted font, an embedded map, an analytics endpoint — that is a change to
`REPO-R38` and needs review, not a deployment detail.

## Related

- [G1 Privacy stance](../10-functional/features/g-ux/g1-privacy.md) · [G5 Plain language](../10-functional/features/g-ux/g5-plain-language.md)
- [60-brand/](../60-brand/) · [20-architecture/contracts/design-tokens.md](../20-architecture/contracts/design-tokens.md)
- [90-appendix/license-rationale.md](../90-appendix/license-rationale.md)
