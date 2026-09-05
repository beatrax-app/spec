# Licence rationale

**Status:** Accepted

The two long-form decisions the readme and the notice link out to.

## Why the Hippocratic License 3.0

Beatrax handles a person's full banking history, their email receipts, and the
funding chains between their accounts. That class of code earns trust by being
**readable** — by shipping its full source so the people who run it can audit
what it does on their own machine.

Closing the source would have been the simpler legal choice. It would have been
the wrong product choice.

Three things had to be true at once:

1. **The source has to be visible.** The whole privacy story of a local-only
   finance application collapses if the user has to take the maintainer's word
   for "nothing leaves your machine". Shipping the source makes the claim
   auditable.

2. **The source has to be redistributable in some form.** Without redistribution
   rights, users cannot fork their own copy, pin a version, or ship a patched
   build to a partner. A fully closed licence blocks the community contribution
   small open-development projects depend on.

3. **The licence has to express that the code is not a tool for harm.** Finance
   products show up in surveillance and rights-abuse contexts. Adopting a licence
   that names that risk explicitly is a low-cost way to say: this was made for
   personal use; do not repurpose it to hurt people.

OSI-approved permissive licences satisfy the first two and **cannot** satisfy the
third — the Open Source Definition forbids restrictions on fields of endeavour,
and an ethical-use clause is a restriction. OSI-approved copyleft licences
satisfy the first two but turn distribution into a viral copyleft event for
anyone building on the code, which is the wrong trade for a single-household
dashboard nobody will bundle as a dependency. Closed-source fails the first.

The Hippocratic License 3.0 satisfies all three.

### What that costs, stated plainly

It is **source-available, not open source**. It is not OSI-approved.

- Procurement processes, downstream relicensing workflows, and "is this open
  source?" compliance checks will correctly return *no*.
- Other projects cannot pull Beatrax in under permissive umbrella terms.

If you need an OSI-approved licence for any of those reasons, **Beatrax is not
the right project for your use case**. That is a genuine trade, not a
technicality, and the product's own copy says so
([DES-R8](../60-brand/README.md#the-des-r-namespace)).

### The packaging wrinkle

The public licence-identifier list does not yet carry an entry for this licence
version — the previous version is registered and this one sits behind an open
registration request. The dependency manifest therefore declares the identifier
with validation disabled and points at the notice file for canonical
attribution.

The intent is to use the identifier the wider ecosystem will recognise once the
registration lands. Until then the notice is authoritative.

### This specification is licensed differently

The **documentation** in this repository is CC BY-SA 4.0
([LICENSE.md](../LICENSE.md)). The **code** in the product repository is the
Hippocratic License 3.0. The **marks** are neither
([60-brand/trademark.md](../60-brand/trademark.md)).

## Why no paid signing certificates

> **This stance has been narrowed, and the heading is kept because the reasoning
> below is still the reason it was taken.** Paid signing identities **are** now
> held — on macOS, on Windows through a hosted signing service, and on both
> mobile platforms — and the release build refuses to publish without them.
> Store distribution is what changed it
> ([ADR-0032](../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md)).
> What follows is the argument that produced the original position, kept intact,
> and then the exception that overrides it and what that exception costs.

### The position, and why it was taken

Beatrax ships installers for three desktop platforms. On two of them, the
first-launch experience for an unsigned application is a security dialogue asking
the user to confirm they want to run software the operating system cannot tie to
a paid developer identity.

Two subscriptions would make that dialogue go away: one platform vendor's
developer identity, and another's hosted signing service. Beatrax subscribed to
neither.

The reasoning was small and specific:

1. **Both gate shipping on a recurring subscription.** If it lapses for any
   reason — an expired payment method, a billing email in a spam folder, a
   missed identity-verification renewal — builds stop being signable and the
   project cannot cut a release until it is restored. For a project that aspires
   to be shippable in any month a maintainer has an hour spare, that is a fragile
   gate.

2. **Neither provides binary integrity the update path does not already
   provide.** Every release publishes hashes inside a signed update manifest. The
   application verifies the manifest signature against a key embedded in the
   bundle, then verifies each binary against the manifest. That chain catches a
   tampered payload regardless of whether the installer was vendor-signed
   ([F6](../10-functional/features/f-platform/f6-updates.md)).

3. **The dialogue is a one-time cost the user can pass themselves.** The install
   documentation walks the exact sequence per platform **and explains why the
   warning appears** — a user told to click past a security warning without a
   reason has learned a bad habit; one told why has learned something true
   ([J1](../10-functional/journeys/j1-first-run.md)).

The trade is real but bounded: one dialogue on first launch, then normal
behaviour thereafter. Updates ride a path carrying signature and hash
verification on every binary — arguably a **more** thoroughly verified mechanism
than a vendor-signed application whose update payload often relies only on the
vendor signature.

Users who want to verify a release by hand can: every release publishes
checksums and the signed manifest, and the recipe reproduces the same chain the
updater runs.

### The exception: store distribution, and what it costs

**A store listing requires a paid identity, and all four store listings are now
in scope** — the Mac App Store, the Microsoft Store, the App Store and Google
Play, with direct download retained wherever it remains possible
([ADR-0032](../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md),
[F8](../10-functional/features/f-platform/f8-app-store-distribution.md)). There
is no version of a store listing that does not carry one. The stance above
therefore holds for the direct-download channel's *reasoning* and no longer holds
as a description of what the project pays for.

**Nothing in the reasoning was found to be wrong.** That is the part worth
stating plainly, because it is tempting to narrow a stance by quietly deciding
its argument was weak. It was not.

| The original objection | What happened to it |
|------------------------|---------------------|
| Both gate shipping on a recurring subscription | **Still true, and now carried rather than avoided.** A lapsed payment method or a missed identity-verification renewal stops a release, and with a listing it stops an update reaching users who have no other channel. The mitigation is bookkeeping: every identity the pipeline requires is recorded with its expiry ([F8-R3](../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria)). |
| Neither provides binary integrity the update path does not already provide | **Still true.** The signed manifest and per-binary hashes are unchanged, and they remain what a direct-download install verifies against. A vendor signature is now an additional signal rather than a replacement for one. |
| The dialogue is a one-time cost the user can pass themselves | **True, and no longer the whole picture.** It is a cost only the users who arrive by direct download can pass. It is not passable by a phone user, and it is not passable on a machine configured to refuse software the operating system cannot attribute. |

What was traded, stated plainly: **a release process that could not be stopped by
a billing failure, for reaching users who cannot or will not sideload.** The
first was a real property and it is gone. It was given up deliberately, and the
condition that would prove the objection right — a lapse actually blocking a
release — is written into ADR-0032's revisit list rather than left to be
rediscovered.

Two sub-questions of the original store-distribution question are **not** settled
by any of this: whether a sandboxed build keeps a user-data path that survives
upgrades, and whether local-network discovery survives the sandbox. Both are
engineering unknowns rather than decisions, and they stay recorded as open in
[open-questions.md](open-questions.md).

## Related

- [ADR-0003](../00-overview/decisions/0003-hippocratic-3-0-license.md) · [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md)
- [ADR-0032](../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md) — the store-distribution decision that narrowed the signing stance above
- [60-brand/trademark.md](../60-brand/trademark.md) · [30-repos/website.md](../30-repos/website.md)
- [F6 Updates and release verification](../10-functional/features/f-platform/f6-updates.md)
