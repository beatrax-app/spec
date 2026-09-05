# Open questions

**Status:** Accepted

Every genuinely unresolved question in this specification, in one place.

They are recorded here **and** in the document each belongs to. A question
smoothed over reads better and is worse: nobody knows to check it
([GOV-R25](../50-governance/README.md#the-gov-r-namespace)).

**Two kinds of entry live here, and they are kept apart.** Everything under the
headings that follow is *unresolved*: nobody has made the call, and the entry
says what would settle it. The final section, [Accepted
tensions](#accepted-tensions), is the opposite — decisions that **have** been
made, where two requirements still pull against each other and the cost of
living with that was judged lower than the cost of resolving it. Filing a settled
call as an open question is the same defect as smoothing over an unsettled one,
so an entry that has been decided is moved down rather than left above.

**And an answered question can also simply go.** Moving down is right only when
the pull *survives* the answer. Where the answer removes it — where the decision
leaves nothing pulling in the other direction — the answer belongs in the
requirement it changed, and the entry belongs nowhere. Keeping a resolved
question in a section headed "accepted tensions" states a tension that does not
exist, which is the same overclaim in the other direction. Three tests, applied
per entry: is it still unanswered, does something still pull against the answer,
or is it finished. Git is the record of the ones that finished.

## Product and release

### Does a sandboxed build keep its data, and can it still find a peer?

What remains of the store-distribution question after
[ADR-0032](../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md)
answered the rest of it:

- **Does a sandboxed build keep a user-data path that survives upgrades?**
- **Does local-network discovery survive the sandbox?**

Neither is a decision anybody can take. They are engineering unknowns,
answerable only by building a sandboxed bundle and measuring it — and the scope
decision is what makes them urgent rather than academic. `F8-R26` forbids a
listing describing a capability that does not work on that platform, so an
unmeasured answer is a listing whose copy cannot honestly be written. If the
answer to either is no, a desktop store listing becomes a diminished product
rather than a second channel.

The Mac App Store carries a third constraint that is **not** an open question but
a known cost: the sandbox ignores one of the two hardened-runtime relaxations the
desktop bundle needs to map its static interpreter, so that listing is preceded
by a runtime strategy rather than by a submission. It is stated in
[F8](../10-functional/features/f-platform/f8-app-store-distribution.md#the-mac-app-store-is-a-runtime-problem-not-a-submission),
not here.

*Which stores, and whether a listing forces paid signing identities, were the
other two sub-questions of this entry. Both are answered — the second is now an
[accepted tension](#paid-signing-identities-were-declined-on-reasoning-that-still-holds).*

*In: [00-overview/roadmap.md](../00-overview/roadmap.md#does-a-sandboxed-build-keep-its-data-and-can-it-still-find-a-peer) ·
[F8-R26](../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria) ·
[20-architecture/platform-matrix.md](../20-architecture/platform-matrix.md#distribution)*

## Correctness and security

### Does lock-on-window-close act on the focused window's session?

The listener fires on the shell's internal channel, and it has not been verified
that this carries the focused window's session. If it does not, the lock-on-close
guarantee silently does not hold. **It cannot be verified outside a real bundle
build.**

*In: [F1-R18](../10-functional/features/f-platform/f1-desktop-shell.md#acceptance-criteria) ·
[40-quality/security.md](../40-quality/security.md#known-outstanding-items)*

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

## Accepted tensions

**Nothing in this section is waiting on a decision.** Each is a pair of
requirements that pull against each other, where the pull was examined and
accepted rather than removed. They are recorded so that a later reader finds the
reasoning instead of re-opening the argument, and so that the conditions that
would reverse the judgement are written down rather than remembered.

### A digest cadence of "off" does not stop the digest arriving

The cadence is a preference of the **device** that holds it, but the notification
row is a **user** artefact: it always persists and it always syncs. A phone set
to "off" beside a desktop set to weekly still receives the digest in its inbox
and on its navigation badge. Only the operating-system notification is
suppressed.

**Accepted.** A per-device preference must not decide whether a user-scoped row
exists, because the row is the same row on every device and the alternative is a
device silently withholding history from its peers. What the setting surface owes
the reader is a sentence saying the inbox entry still arrives — a copy change,
not a behaviour change.

*Would reverse it:* a genuine per-device notification store, which the sync model
does not currently have.

*In: [C1-R12](../10-functional/features/c-insight/c1-dashboard.md#acceptance-criteria) ·
[C8](../10-functional/features/c-insight/c8-notifications.md)*

### The owner can reset a partner, and that is not a privilege boundary

`F3-R4` lets the owner reset a partner's password and forbids the reverse.
[40-quality/security.md](../40-quality/security.md) says every account is a
co-equal, fully-trusted operator and that partner accounts are a convenience
rather than a privilege boundary. Both are accepted, and neither defers to the
other.

**Accepted, and the threat model is the one that governs.** The path around the
asymmetry is short — any account may enable developer mode and reach the command
registry — so the owner-only reset is an affordance, not a control. Household
co-tenancy is a trust boundary the product deliberately does not police.

*Would reverse it:* multi-tenancy beyond one household, which v2.0 does not ship
and the licence discourages.

*In: [F3-R4, F3-R5](../10-functional/features/f-platform/f3-auth-and-app-lock.md#acceptance-criteria) ·
[40-quality/security.md](../40-quality/security.md)*

### A fallback English string is announced in the surrounding locale

`G7-R13` requires the document language attribute to name the active locale.
`G7-R12` fills a missing key with its English value. So in a partially translated
locale, English text sits inside a document stamped `lang="nl"` and a screen
reader pronounces it with Dutch phonetics — which is the defect `G7` itself
names, and `G5-R14`'s "MUST read as English" is not true for a listener.

**Accepted.** Marking it per string would mean threading fallback provenance
through every translation call site, and the framework's fallback returns a bare
string carrying no provenance, so nothing downstream *could* mark it. Coverage is
therefore governed at the locale level rather than per string.

*Would reverse it:* a translation layer that reports which locale answered a
lookup, at which point the tagging becomes mechanical.

*In: [G7-R12, G7-R13](../10-functional/features/g-ux/g7-localisation.md#acceptance-criteria) ·
[G5-R14](../10-functional/features/g-ux/g5-plain-language.md#acceptance-criteria)*

### Paid signing identities were declined on reasoning that still holds

[The licence rationale](license-rationale.md#why-no-paid-signing-certificates)
declined two signing subscriptions because both gate shipping on a recurring
payment: a lapsed card or a missed identity-verification renewal stops a release
until somebody restores it. `F8-R2` requires every store artefact to be signed by
a recorded identity and a build to fail rather than emit an unsigned one, and
there is no store listing without a paid identity behind it. The two pull in
opposite directions and both stand.

**Accepted, and the objection was not found to be wrong.** Paid identities are
held on macOS, Windows and both mobile platforms, and the release build refuses
to publish without them
([ADR-0032](../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md)).
What was traded is a release process that could not be stopped by a billing
failure, in exchange for reaching users who cannot or will not sideload — a
phone user, and anyone on a machine configured to refuse software the operating
system cannot attribute. The first was a real property and it is gone. The
mitigation is bookkeeping rather than architecture: `F8-R3` requires every
identity the pipeline needs to be recorded with its expiry, because an expiry
nobody is watching is the failure mode, not the subscription itself.

The reasoning is kept in place rather than rewritten, so that a reader meeting
the exception finds why the stance existed instead of a paragraph that reads as
though it never did.

*Would reverse it:* a lapse actually blocking a release, or a platform offering
attributable distribution without a recurring identity.

*In: [F8-R2, F8-R3](../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria) ·
[license-rationale.md](license-rationale.md#the-exception-store-distribution-and-what-it-costs)
· [ADR-0032](../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md)*

### A conformance level is named that nothing measures

`G3-R12` requires a conformance target to be chosen and stated, and it is: **WCAG
2.2 Level AA**. `DES-R8` forbids copy claiming a protection the implementation
does not provide, and no automated accessibility audit runs in the pipeline, so
nothing measures conformance on any build. Naming a standard nobody measures is
the shape of claim `DES-R8` exists to prevent.

**Accepted, and the wording is what carries it.** AA is stated as a target the
product is **built to**, never as a level a build has been **certified against**,
and `G3-R12` requires that distinction to be kept for as long as no audit runs.
The half of AA most likely to be quietly false was measured rather than asserted:
every foreground/background pair in the palette was sampled through a canvas
rather than pattern-matched out of the stylesheet — a regex over colour utilities
cannot read `oklch()`, and a light-only fix breaks dark mode — and 664 failures
against the AA ratio were taken to zero in both themes. `G3-R1` through `G3-R11`
are individually enforced, several by architecture test.

The pull does not go away: a reader can still take "WCAG 2.2 AA" as a claim about
a build rather than about an intention. Living with that was judged better than
the alternatives, which are to name nothing — the position this replaced, and one
that told a user with an accessibility need less than it could — or to gate a
release on an audit that does not exist.

*Would reverse it:* an accessibility audit in the pipeline, at which point AA
becomes a gate rather than a target and the tension disappears rather than being
managed.

*In: [G3-R12](../10-functional/features/g-ux/g3-accessibility.md#conformance-target) ·
[60-brand/accessibility.md](../60-brand/accessibility.md#conformance-target) ·
[DES-R8](../60-brand/README.md#the-des-r-namespace)*

## Related

- [provenance.md](provenance.md) — where the rest of this specification came from
- [00-overview/roadmap.md](../00-overview/roadmap.md)
