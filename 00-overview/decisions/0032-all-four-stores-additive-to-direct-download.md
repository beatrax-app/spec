# ADR-0032: All four stores, and direct download is not retired

**Status:** Accepted
**Date:** 2026-09-05
**Supersedes:** the "no paid signing identity is held" claim in
[ADR-0006](0006-nativephp-desktop-shell.md) and
[ADR-0019](0019-asymmetric-release-publish.md), and the app-store scope recorded
in [F8](../../10-functional/features/f-platform/f8-app-store-distribution.md) on
2026-09-04. Everything else in both records stands: the NativePHP shell and its
trade-offs, and the asymmetric draft-versus-immediate publish behaviour.

## Context

Direct download reaches people who will fetch an installer and click past a
security dialogue. It does not reach a phone, and it does not reach anyone whose
operating system is configured to refuse software that arrived any other way.

Two things had already moved before this decision was taken, and neither had
been carried through the specification.

**The scope had been narrowed on technical grounds.**
[F8](../../10-functional/features/f-platform/f8-app-store-distribution.md) was
accepted on 2026-09-04 with two stores — the App Store and Google Play, mobile
only — and put the Mac App Store and the Microsoft Store out of scope. Its
reason for the Mac App Store is not a cost or a review-process objection and is
not disputed here: the desktop bundle embeds a static interpreter and relies on
two hardened-runtime relaxations to map it, and the sandbox a Mac App Store
build must run under ignores one of them. That listing needs a different runtime
strategy before it needs a submission.

**The paid-identity question had already been answered in the pipeline.** The
release build refuses to publish a macOS bundle without a developer identity and
notarisation credentials, and refuses a Windows installer without a hosted
signing service's credentials; the mobile builds sign from a distribution
certificate against a registered team. Every one of those is a paid, renewable
identity, and they are held.
[The licence rationale](../../90-appendix/license-rationale.md#why-no-paid-signing-certificates)
still read as though none were, and so did
[the platform matrix](../../20-architecture/platform-matrix.md). F8 said so; the
ripple was never done.

So the open question this record closes was, by the time it was closed, partly a
question nobody had noticed was already answered.

## Decision

**All four stores are in scope, and direct download is retained wherever it
remains possible.**

| Channel | Position |
|---------|----------|
| Mac App Store | In scope. Blocked behind a runtime strategy, not behind a submission. |
| Microsoft Store | In scope. |
| App Store | In scope. |
| Google Play | In scope. |
| Direct download | **Retained.** Never retired by a listing, on any platform where it remains possible. |

Store distribution is **additive**. Where a sandboxed store build and a
direct-download build can both ship for a platform, both ship, and every release
continues to publish the signed manifest and checksums that the update path
verifies against ([F8-R1](../../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria)).

**Paid signing identities are adopted**, and the licence rationale's stance
against them is narrowed to an exception rather than reversed. The reasoning
that produced that stance still describes something real — shipping is now
gated on a recurring subscription, and a lapse stops a release. That fragility
is now *carried* rather than avoided, and recorded as the cost of the decision
rather than argued away.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **The two mobile stores only** — the scope F8 recorded | It is the right *sequencing* and the wrong *scope*. It reaches the phone, which was the acute gap, but it leaves the desktop permanently behind a first-launch security dialogue on two platforms and unreachable on machines configured to refuse sideloaded software. Deciding the desktop listings are out because one of them is hard closes a question that was never really asked. |
| **Stores replace direct download** | Contradicts the product's own premise. A store build cannot update itself, cannot be pinned to a version, and cannot be audited against a published checksum by the person running it — three things a local-first, source-available finance application owes its user. It would also strand every existing installation behind an upgrade path that does not exist. |
| **Direct download only, indefinitely** | The status quo, and it does not reach a phone at all. The mobile client is a v2.0 feature that would ship with no way to install it. |
| **Defer the Mac App Store to a later version** | Defensible, and rejected as scoping by difficulty. The runtime work is the honest cost of the listing; recording it as in scope with its cost visible is better than recording it as out of scope with its cost hidden, which is what the specification did until now. |

## Consequences

### Positive

- The mobile client becomes installable, which it was not.
- The first-launch security dialogue disappears on the two desktop platforms
  that raise it, and the install documentation stops needing to explain it.
- The declarations, permission strings, deletion path and privacy answers that
  [F8](../../10-functional/features/f-platform/f8-app-store-distribution.md)
  specifies apply unchanged to four listings rather than two.

### Negative

- **A lapsed subscription now stops a release**, which is precisely the failure
  the licence rationale declined to accept. It is accepted now, on four
  platforms rather than none, and mitigated only by recording each identity with
  its expiry ([F8-R3](../../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria)).
- **The Mac App Store is a runtime re-architecture, not a submission.** Its cost
  is not comparable to the other three and is the largest unknown in the
  release.
- Four review processes, four sandboxing models, and four sets of listing copy
  that must stay true to the outbound-call catalogue.

### Neutral

- The signed update manifest remains the verification chain for direct-download
  installs. It is no longer the *sole* binary-integrity signal, which is the
  claim this record supersedes in ADR-0006 and ADR-0019.
- A store build must name the store as its update channel and must carry no
  self-update path at all
  ([F8-R20, F8-R21](../../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria)).
  That was already true of the mobile builds and now applies to the desktop
  store builds too.

## What this decision does not settle

Two sub-questions of the original open question are **not** answered by it, and
they are engineering unknowns rather than calls anybody can make:

- Does a sandboxed build keep a user-data path that survives upgrades?
- Does local-network discovery survive the sandbox?

Both are answerable only by building a sandboxed bundle and measuring it. The
decision makes them urgent rather than academic: a capability that is dead under
a sandbox may not be described in that platform's listing
([F8-R26](../../10-functional/features/f-platform/f8-app-store-distribution.md#acceptance-criteria)),
so until they are measured, that listing's copy cannot honestly be written. They
stay recorded as open in
[90-appendix/open-questions.md](../../90-appendix/open-questions.md).

## Revisit if

- A sandboxed build proves unable to keep a user-data path across upgrades, or
  unable to discover a peer on the local network. Either would make a desktop
  store listing a product with a missing capability rather than a second
  channel, and the choice would be between shipping it diminished and not
  shipping it.
- A signing-identity lapse actually blocks a release, which is the failure the
  licence rationale predicted and this decision accepted.

## Related

- [F8 App-store distribution](../../10-functional/features/f-platform/f8-app-store-distribution.md)
  — what has to be true before a listing's declarations can be made honestly
- [ADR-0006](0006-nativephp-desktop-shell.md) · [ADR-0019](0019-asymmetric-release-publish.md)
  — the two records this supersedes in part
- [ADR-0003](0003-hippocratic-3-0-license.md) · [90-appendix/license-rationale.md](../../90-appendix/license-rationale.md)
  — the stance this narrows
- [20-architecture/platform-matrix.md](../../20-architecture/platform-matrix.md)
  · [F1 Desktop shell](../../10-functional/features/f-platform/f1-desktop-shell.md)
