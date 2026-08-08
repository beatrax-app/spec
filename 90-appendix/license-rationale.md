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

Beatrax ships installers for three desktop platforms. On two of them, the
first-launch experience for an unsigned application is a security dialogue asking
the user to confirm they want to run software the operating system cannot tie to
a paid developer identity.

Two subscriptions would make that dialogue go away: one platform vendor's
developer identity, and another's hosted signing service. Beatrax subscribes to
neither.

The reasoning is small and specific:

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

### The open question

**Store distribution may change this trade.** A store listing may require a paid
identity, and the balance of a recurring-subscription risk against reaching users
who will never sideload is genuinely different.

That is unresolved, along with the rest of store distribution
([00-overview/roadmap.md](../00-overview/roadmap.md#open-questions)).

## Related

- [ADR-0003](../00-overview/decisions/0003-hippocratic-3-0-license.md) · [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md)
- [60-brand/trademark.md](../60-brand/trademark.md) · [30-repos/website.md](../30-repos/website.md)
- [F6 Updates and release verification](../10-functional/features/f-platform/f6-updates.md)
