# F6 — Updates and release verification

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

An update puts a binary on the machine that nobody inspected, so the question
this feature answers is why that binary should be trusted. There are two answers
now, and they are independent of each other.

The operating system holds one. Paid signing identities **are** held — a
developer identity with notarisation on macOS, a hosted signing service on
Windows — and the release build refuses to publish a bundle without them
([F8-R2](f8-app-store-distribution.md#acceptance-criteria),
[ADR-0032](../../../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md)).
That signature is the platform's to check, at install and at launch, on an
installer a person fetched by hand.

This feature holds the other, and it is the only one that covers an
**automatic** update. Every release is described by a manifest signed with the
project's own key; the application verifies that signature, then the binary's
hash, before any install step runs. A platform signature says nothing about what
an updater fetched afterwards — and on macOS the one update path that did lean
on it, the differential download that validates a delta against the running
bundle's own signature, is deliberately turned off, so the manifest chain is
what stands there.

**Neither supersedes the other, and neither is redundant.** Linux ships unsigned
and has no platform signature at all, so on that platform this chain remains the
only binary-integrity signal there is. That is what makes the feature
security-critical rather than a convenience.

## Behaviour

### The verification chain

1. The application fetches the release manifest for its channel.
2. It verifies the manifest's signature against a public key **embedded in the
   bundle**. A manifest that fails verification is logged and **no banner is
   shown** — a failed signature is not a user-facing prompt, it is a silent
   refusal.
3. Only then does it read the manifest's declared hashes.
4. A downloaded binary is verified against the declared hash before any install
   step runs.

Nothing about this chain may be bypassed. A download path that skips
verification is a release blocker rather than a bug.

**And it may not lean on the platform's signature instead.** Two of the
framework updater's own behaviours would: automatic download with
install-on-quit, which puts a binary in place without the chain running at all,
and the macOS differential download, whose only integrity check is the operating
system's signature of the running bundle. Both are turned off in the shipped
bundle by a build step that fails the build rather than emit one where the patch
did not apply.

### Channels

Two by design: stable and preview. Stable resolves the `latest` manifest for the
running platform, preview resolves a `beta` one, and the bundle defaults to
stable. See
[ADR-0019](../../../00-overview/decisions/0019-asymmetric-release-publish.md),
and the known gap below for what is actually published.

### Known gap — the preview channel resolves a manifest nobody publishes

The release pipeline writes only the `latest` set, for every tag shape, release
candidates included. A bundle set to preview therefore asks for a file that is
never published, and gets nothing back for as long as it asks.

There is no in-app switch either. The channel is read from the bundle's
environment at build time, so opting into preview is a rebuild rather than a
setting.

`F6-R5` is marked *(Open)* on both counts. Neither affects the stable channel,
and the verification chain is the same chain either way.

### The banner

A new version raises a banner. A manifest that has not moved for a long time
raises a **staleness** banner that does **not** offer an install — the user
should investigate first, because a stale manifest may mean the fetch is broken
rather than that no release exists.

Skipping a version persists per user, and skipped versions do not resurface.

### Update checking is optional and disclosed

The check is one of the outbound calls the privacy stance enumerates
([G1](../g-ux/g1-privacy.md)). It can be turned off, and with it off the
application makes no outbound call at all unless another optional feature is on.

The request carries no user-identifying data beyond what any HTTP request
carries.

### Verifying by hand

Every release publishes checksums and the signed manifest, and the verification
recipe is documented so a user can reproduce the same chain the auto-updater
runs. That reproducibility is what makes the chain trustworthy rather than
merely present.

### Health

A health endpoint returns a small, deterministic object: status, application
version, runtime version, and store version — **and no timestamp**, so an
external probe can equality-check the whole body without normalising a volatile
field.

The endpoint is authentication-free but still loopback-restricted, so it is
reachable by a local probe and by nothing else.

### Loopback restriction

Every request whose server address is not a loopback address is refused with
not-found. The check covers the full loopback range, the IPv6 loopback, and the
IPv4-mapped IPv6 form, compared in binary rather than as text. Requests with no
server address — command-line and test contexts — pass.

Every authenticated response carries a no-store cache directive, so a browser
never caches a transaction list to disk.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A manifest failing signature verification | Logged; no banner. |
| A binary whose hash does not match | The install aborts. |
| A manifest fetch succeeding but the download failing | A warning; the banner stays without claiming success. |
| A manifest older than the staleness threshold | A staleness banner with no install offer. |
| A version the user skipped | Does not resurface. |
| Update checking disabled | No outbound call. |
| A non-loopback request to any route | Not-found, unless the operator widened the gate. |
| A probe checking the health body | Byte-stable across calls. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F6-R1** | The update manifest's signature MUST be verified against a public key embedded in the bundle before anything else is read from it. |
| **F6-R2** | A manifest failing verification MUST be logged and MUST NOT produce a user-facing banner. |
| **F6-R3** | Every downloaded binary MUST be verified against the manifest's declared hash before any install step. |
| **F6-R4** | No update path may skip signature or hash verification. |
| **F6-R5** | *(Open)* Stable and preview channels MUST both exist, with stable as the default. Not yet satisfied — nothing publishes a preview manifest, and the channel is fixed at build time rather than chosen; see [Known gap](#known-gap--the-preview-channel-resolves-a-manifest-nobody-publishes). |
| **F6-R6** | Where update checking is enabled, a manifest older than the staleness threshold MUST raise a banner that does not offer an install; where it is disabled, no staleness banner may be raised. |
| **F6-R7** | Skipped versions MUST persist per user and MUST NOT resurface. |
| **F6-R8** | Update checking MUST be disableable, and with it disabled no outbound call may occur from this feature. |
| **F6-R9** | The update request MUST carry no user-identifying data. |
| **F6-R10** | Every release MUST publish checksums and the signed manifest, and the manual verification recipe MUST be documented. |
| **F6-R11** | The health endpoint MUST return a deterministic object with no timestamp. |
| **F6-R12** | The health endpoint MUST be authentication-free but loopback-restricted. |
| **F6-R13** | Every non-loopback request MUST be refused with not-found. A gate the operator has explicitly widened ([ARCH-R22](../../../20-architecture/README.md)) is the one exception; a bundle nobody has widened MUST refuse. This governs the application's own HTTP surface; the sync listener is a separate process on its own port, deliberately not loopback-bound, whose gate is the mutually-authenticated handshake ([E3](../e-sync/e3-transport.md)). |
| **F6-R14** | Loopback detection MUST cover the full loopback range, the IPv6 loopback, and the IPv4-mapped IPv6 form, compared in binary form. |
| **F6-R15** | A request with no server address MUST pass, for command-line and test contexts. |
| **F6-R16** | Every authenticated response MUST carry a no-store cache directive. |
| **F6-R17** | The update path MUST NOT rely on an operating-system code signature for its integrity guarantee. An updater behaviour that would install without the manifest chain running, or whose only integrity check is the operating system's signature of the running bundle, MUST be disabled in the shipped bundle, and a build that cannot disable it MUST fail rather than ship it. |

## Related

- [ADR-0019](../../../00-overview/decisions/0019-asymmetric-release-publish.md)
- [90-appendix/license-rationale.md](../../../90-appendix/license-rationale.md#why-no-paid-signing-certificates)
- [G1 Privacy stance](../g-ux/g1-privacy.md) — the enumerated outbound surface
- [70-operations/releasing.md](../../../70-operations/releasing.md)
- [F1 Desktop shell](f1-desktop-shell.md)
