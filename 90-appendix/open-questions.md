# Open questions

**Status:** Accepted

Every genuinely unresolved question in this specification, in one place.

They are recorded here **and** in the document each belongs to. A question
smoothed over reads better and is worse: nobody knows to check it
([GOV-R25](../50-governance/README.md#the-gov-r-namespace)).

## Product and release

### What is in scope for app-store distribution?

The last unscoped piece of v2.0. Sub-questions, none answered by any source:

- **Which stores?** Four review processes with four sandboxing models.
- **Does it force paid signing identities**, which
  [the licence rationale](license-rationale.md#why-no-paid-signing-certificates)
  currently declines? A store listing may make that trade different.
- **Does a sandboxed build keep a user-data path that survives upgrades**, and
  does local-network discovery survive the sandbox?

*In: [00-overview/roadmap.md](../00-overview/roadmap.md#open-questions) ·
[20-architecture/platform-matrix.md](../20-architecture/platform-matrix.md) ·
[license-rationale.md](license-rationale.md#the-open-question)*

### Is the mobile local-notification hardware check a v2.0 blocker?

The plugin is installed and the adapter wired; the on-device proof that a banner
fires is outstanding. Whether v2.0 advertises mobile notifications, or ships them
present-but-unadvertised, is a product call nobody has made.

*In: [E5-R24](../10-functional/features/e-sync/e5-mobile-peer.md#acceptance-criteria) ·
[00-overview/roadmap.md](../00-overview/roadmap.md#open-questions)*

## Correctness and security

### When do the connector's per-connection and per-user secret gaps become blockers?

One live aggregator session exists system-wide, and the secrets file has no
per-user keying. Under v2.0's single-user, single-bank shape both are documented
limitations. **A second bank makes the first a defect; a second user makes the
second one a security issue.**

Neither has a scheduled fix.

*In: [A6-R20, A6-R21](../10-functional/features/a-ingestion/a6-open-banking.md#acceptance-criteria) ·
[40-quality/security.md](../40-quality/security.md#known-outstanding-items)*

### Does lock-on-window-close act on the focused window's session?

The listener fires on the shell's internal channel, and it has not been verified
that this carries the focused window's session. If it does not, the lock-on-close
guarantee silently does not hold. **It cannot be verified outside a real bundle
build.**

*In: [F1-R18](../10-functional/features/f-platform/f1-desktop-shell.md#acceptance-criteria) ·
[40-quality/security.md](../40-quality/security.md#known-outstanding-items)*

### When is operating-system key custody wired?

Adapters are registered and unwired; the unlocked key follows session custody on
every platform. Combined with the absent mobile backup-exclusion bridge,
key-at-rest protection is weaker than the design intends.

*In: [F3-R33](../10-functional/features/f-platform/f3-auth-and-app-lock.md#acceptance-criteria) ·
[E4-R23, E4-R24](../10-functional/features/e-sync/e4-at-rest-encryption.md#acceptance-criteria)*

### Is the search index's plaintext shadow an acceptable leak indefinitely?

Full-text search needs plaintext. The index is therefore a readable shadow of
encrypted descriptions and counterparty names. Accepted today; whether an
encrypted-search design is ever worth its cost is unasked.

*In: [ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md#revisit-if)*

### Should the hand-built transport handshake be replaced?

It is vector-validated, and it is the highest-risk component in the product. If
a well-maintained, audited implementation for the platform appears, replacing it
is a clear win. None currently exists.

*In: [ADR-0016](../00-overview/decisions/0016-noise-transport-zero-knowledge-relay.md#revisit-if)*

## Quality and process

### What accessibility conformance target applies?

The theme-companion test, the non-colour-carrier rule, the keyboard
requirements, and locale formatting are all in force. **No conformance level is
named, and no automated audit runs.** Choosing one, and deciding whether it gates
a release, is undecided.

*In: [G3-R12](../10-functional/features/g-ux/g3-accessibility.md#open-question) ·
[60-brand/accessibility.md](../60-brand/accessibility.md#open-question)*

### Should ordering be machine-checked?

The governance gate verifies that a cited identifier **exists**, not that the
specification change **merged first**. Ordering is verified in review. Hardening
it is tracked and unscheduled.

*In: [50-governance/canonical-spec.md](../50-governance/canonical-spec.md#ordering)*

### Should design tokens become a versioned package?

Shared today by convention and by contract, not by a dependency the build
resolves. Adequate at four repositories and one maintainer; not at a larger
scale.

*In: [20-architecture/contracts/design-tokens.md](../20-architecture/contracts/design-tokens.md#open-question)*

### Should screenshot freshness be a gate?

A release-checklist item today. The seam between the site and the product fails
here first, because both look fine in isolation.

*In: [60-brand/brand-rules.md](../60-brand/brand-rules.md#screenshots) ·
[20-architecture/contracts/design-tokens.md](../20-architecture/contracts/design-tokens.md#screenshots-are-shared-assets)*

### Should the shared gate scripts be pinned to the tag that called them?

`spec-check`, `dco`, `commitlint` and `spec-references` are called at `@v1` but
check this repository out at `main` and run the scripts they find there. The
specification corpus has to come from `main` — a requirement merged an hour ago
must be citable. The scripts are the gate's *logic*, and a change to one reaches
every consumer's merge gate on merge, which is what the moving tag is supposed to
prevent. `commit_lint.py` has already travelled that way once, as a widening.

Pinning them to `github.job_workflow_sha` would fix it, at the cost of a script
fix reaching nobody until the tag moves. Nobody has weighed that trade.

*In: [50-governance/cross-repo-ci.md](../50-governance/cross-repo-ci.md#what-the-tag-does-not-cover) ·
[ADR-0030](../00-overview/decisions/0030-the-tag-governs-the-workflow-not-what-it-reads.md)*

## Organisation

### What is the website's hosting and deployment arrangement?

A repository-local decision. [30-repos/website.md](../30-repos/website.md) states
what the site must and must not do rather than how it is served — but if the
arrangement introduces an outbound dependency on a visitor's browser, that is a
requirement change, not a deployment detail.

*In: [30-repos/website.md](../30-repos/website.md#open-question)*

### Should the marks be registered?

Nothing is registered. [60-brand/trademark.md](../60-brand/trademark.md) states a
position rather than asserting a registration, and enforcement beyond stating it
is not something this project is set up to do.

*In: [60-brand/trademark.md](../60-brand/trademark.md#open-question)*

### Does the solo override model survive a second maintainer?

The lead approving their own override is one person agreeing with themselves.
Stated rather than dressed up; mitigated by the record, the follow-up, and the
never-overridable list. Whether it needs replacing when a second maintainer
arrives is unasked.

*In: [50-governance/overrides.md](../50-governance/overrides.md#the-solo-caveat) ·
[70-operations/maintainers.md](../70-operations/maintainers.md)*

## Related

- [provenance.md](provenance.md) — where the rest of this specification came from
- [00-overview/roadmap.md](../00-overview/roadmap.md)
