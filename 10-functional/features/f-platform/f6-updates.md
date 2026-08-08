# F6 — Updates and release verification

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

Beatrax ships without paid operating-system code-signing identities
([the rationale](../../../90-appendix/license-rationale.md#why-no-paid-signing-certificates)).
The signed update manifest is therefore **the sole binary-integrity signal**,
which makes this feature security-critical rather than a convenience.

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

### Channels

Two, live from the first release: stable and preview. The bundle defaults to
stable; the user can opt into preview. See
[ADR-0019](../../../00-overview/decisions/0019-asymmetric-release-publish.md).

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
| A non-loopback request to any route | Not-found. |
| A probe checking the health body | Byte-stable across calls. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F6-R1** | The update manifest's signature MUST be verified against a public key embedded in the bundle before anything else is read from it. |
| **F6-R2** | A manifest failing verification MUST be logged and MUST NOT produce a user-facing banner. |
| **F6-R3** | Every downloaded binary MUST be verified against the manifest's declared hash before any install step. |
| **F6-R4** | No update path may skip signature or hash verification. |
| **F6-R5** | Stable and preview channels MUST both exist, with stable as the default. |
| **F6-R6** | A manifest older than the staleness threshold MUST raise a banner that does not offer an install. |
| **F6-R7** | Skipped versions MUST persist per user and MUST NOT resurface. |
| **F6-R8** | Update checking MUST be disableable, and with it disabled no outbound call may occur from this feature. |
| **F6-R9** | The update request MUST carry no user-identifying data. |
| **F6-R10** | Every release MUST publish checksums and the signed manifest, and the manual verification recipe MUST be documented. |
| **F6-R11** | The health endpoint MUST return a deterministic object with no timestamp. |
| **F6-R12** | The health endpoint MUST be authentication-free but loopback-restricted. |
| **F6-R13** | Every non-loopback request MUST be refused with not-found. |
| **F6-R14** | Loopback detection MUST cover the full loopback range, the IPv6 loopback, and the IPv4-mapped IPv6 form, compared in binary form. |
| **F6-R15** | A request with no server address MUST pass, for command-line and test contexts. |
| **F6-R16** | Every authenticated response MUST carry a no-store cache directive. |

## Related

- [ADR-0019](../../../00-overview/decisions/0019-asymmetric-release-publish.md)
- [90-appendix/license-rationale.md](../../../90-appendix/license-rationale.md#why-no-paid-signing-certificates)
- [G1 Privacy stance](../g-ux/g1-privacy.md) — the enumerated outbound surface
- [70-operations/releasing.md](../../../70-operations/releasing.md)
- [F1 Desktop shell](f1-desktop-shell.md)
