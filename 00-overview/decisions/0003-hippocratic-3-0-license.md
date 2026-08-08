# ADR-0003: Hippocratic License 3.0

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-33

## Context

Beatrax is a local-only personal-finance dashboard. It reads bank statements,
credit-card PDFs, PayPal exports, and email receipts. It resolves funding chains
across accounts. That class of code earns trust by being readable — by shipping
its full source so the people who run it can audit what it does on their own
machine.

Closing the source would have been the simpler legal choice. It would also have
been the wrong product choice for a privacy-first tool whose core promise —
"nothing leaves your machine" — is only credible when the user can verify it
themselves.

Three requirements had to hold at once:

1. **The source must be visible.** The privacy story collapses if the user has
   to take the maintainer's word for it.
2. **The source must be redistributable in some form.** Users need to fork their
   own copy, pin a specific version, ship a patched build to a partner. A fully
   closed licence blocks the community contribution that small open-development
   projects depend on.
3. **The licence should express that the code is not a tool for harm.** Finance
   products show up in surveillance and rights-abuse contexts. Naming that risk
   explicitly is a low-cost way to set the tone.

## Decision

Beatrax ships under the Hippocratic License 3.0, specifically the unmodified
`HL3-FULL` variant covering the full ethical-use clause set. The licence text
lives at the product repo root in `LICENSE`; the human-readable rationale is
[90-appendix/license-rationale.md](../../90-appendix/license-rationale.md).

Documentation in this spec repository is licensed separately under
CC BY-SA 4.0 — see [LICENSE.md](../../LICENSE.md).

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **MIT / Apache-2.0** | Satisfies visibility and redistribution but cannot carry the ethical-use clause — the Open Source Definition forbids restrictions on fields of endeavour. |
| **AGPL-3.0** | Satisfies visibility and a stronger redistribution requirement, but viral copyleft is the wrong trade for a single-user dashboard nobody else will bundle as a dependency. |
| **Closed source, binary distribution only** | Fails the visibility requirement outright, which is the requirement the whole privacy story rests on. |
| **A custom ethical-source licence drafted from scratch** | Too much legal risk for a one-person project. Hippocratic 3.0 is the off-the-shelf answer to exactly this design space. |

## Consequences

### Positive

- The privacy claim is auditable rather than asserted, which is the entire point.
- The licence names the obligation explicitly rather than leaving it implied.

### Negative

- **Source-available, not open source.** The licence is not OSI-approved.
  Procurement processes, downstream relicensing workflows, and "is this open
  source?" compliance checks will return *no, it is source-available*. This is
  the explicit trade.
- **Not bundleable as a permissively-licensed dependency.** Other projects
  cannot pull Beatrax in under MIT or Apache umbrella terms. Beatrax is a
  finished product, not a building block; the constraint matches the intent.
- **A packaging-metadata wrinkle.** The SPDX list does not yet carry an
  identifier for Hippocratic-3.0 (v2.1 is registered; v3.0 sits behind an open
  registration request), so the dependency manifest declares the identifier with
  SPDX validation disabled and points at the notice file for canonical
  attribution.

### Neutral

- Modifications and redistributions inherit the same terms, which is what a
  licensee would expect from any copyleft-adjacent licence.

## Revisit if

- SPDX registers a Hippocratic-3.0 identifier, at which point the packaging
  workaround can be removed (a documentation change, not a decision change).
- The Organization for Ethical Source publishes a v4 with materially different
  clauses.

## Related

- [ADR-0004](0004-local-only-hosting.md) — the privacy posture this licence
  codifies
- [90-appendix/license-rationale.md](../../90-appendix/license-rationale.md) —
  the long-form public explanation
- [60-brand/trademark.md](../../60-brand/trademark.md) — the marks are handled
  separately from the code licence
