# J5 — Adding a device

**Status:** Accepted

> There is no account. There is no server. Two devices have to establish that
> they belong to the same person entirely between themselves, and the user has
> to be able to verify that nothing got in between.
>
> This is the v2.0 headline journey.

---

## Precondition

A working install on one device. A second device — a laptop, or a phone — with
Beatrax installed and no data.

## The path

### 1. The existing device offers a pairing

From the devices surface, the user starts a pairing. The device generates a
single-use, expiring secret and shows a QR code carrying it alongside the
device's public identity.

Where a camera is unavailable, the same payload is offered as a typed word code
from a standard wordlist.

*Exercises: [E2](../features/e-sync/e2-device-pairing.md).*

### 2. The new device generates its own identity

On first run the new device generates its own signing and key-agreement
keypairs. **The private halves never leave it** — there is no escrow and no
recovery that reconstructs them.

Generation is gated behind the app-lock, and the key file is encrypted at rest.

*Exercises: [E2](../features/e-sync/e2-device-pairing.md), [F3](../features/f-platform/f3-auth-and-app-lock.md).*

### 3. Scan, or type

The new device scans the code — camera-first on a phone — or the user types the
word code.

Where the two devices cannot see each other directly, the handshake propagates
over the relay, which carries the frames without being able to read them.

*Exercises: [E2](../features/e-sync/e2-device-pairing.md), [E3](../features/e-sync/e3-transport.md), [E5](../features/e-sync/e5-mobile-peer.md).*

### 4. Confirm the safety number — on both screens

Both devices display a safety number derived from both public identities. **Both
users must confirm it.**

This is the only defence against a machine-in-the-middle during pairing, and it
is mandatory rather than a dismissible advisory. The copy explains what the user
is comparing and why ([G5](../features/g-ux/g5-plain-language.md)).

If the numbers differ, the ceremony is abandoned.

*Exercises: [E2](../features/e-sync/e2-device-pairing.md), [G5](../features/g-ux/g5-plain-language.md).*

### 5. The group key is delivered

The existing device wraps the current at-rest key epoch to the new device's
public key and delivers it over the now-authenticated session.

A phone joining by import **deliberately does not mint its own epoch** — it waits
for the delivered ones, so the two devices do not diverge onto separate
keyrings.

*Exercises: [E4](../features/e-sync/e4-at-rest-encryption.md), [E3](../features/e-sync/e3-transport.md).*

### 6. Initial sync — blocking and resumable

The new device shows a **blocking** progress screen with no cancel and no
dismiss. A half-synced ledger presented as complete would be actively
misleading.

Progress reads from a durable cursor, so backgrounding the phone and returning
resumes rather than restarting. Completion requires that the key epochs arrived
and the operation log was re-projected.

*Exercises: [E5](../features/e-sync/e5-mobile-peer.md), [E1](../features/e-sync/e1-change-capture.md).*

### 7. Ongoing

Both devices sync directly over the local network when both are awake, and
through the relay when one is not. The phone dials out and never listens; that
is a platform constraint, not a demotion — in the merge it is an equal peer.

Concurrent edits to different fields of one row both survive. Concurrent edits to
the same field resolve by clock. Deletes win over concurrent edits.

*Exercises: [E1](../features/e-sync/e1-change-capture.md), [E3](../features/e-sync/e3-transport.md), [E5](../features/e-sync/e5-mobile-peer.md), [E6](../features/e-sync/e6-sync-status.md).*

### 8. Losing a device

Removing a device is a security operation, not a list edit: its trust is revoked
**first**, a fresh key epoch is minted, and that epoch is wrapped to every
remaining confirmed device.

**What it does not do is un-see what the device already synced.** Revocation
protects going forward. The copy says so.

*Exercises: [E4](../features/e-sync/e4-at-rest-encryption.md), [E2](../features/e-sync/e2-device-pairing.md), [G5](../features/g-ux/g5-plain-language.md).*

## Features exercised

[E1](../features/e-sync/e1-change-capture.md) ·
[E2](../features/e-sync/e2-device-pairing.md) ·
[E3](../features/e-sync/e3-transport.md) ·
[E4](../features/e-sync/e4-at-rest-encryption.md) ·
[E5](../features/e-sync/e5-mobile-peer.md) ·
[E6](../features/e-sync/e6-sync-status.md) ·
[F3](../features/f-platform/f3-auth-and-app-lock.md) ·
[G5](../features/g-ux/g5-plain-language.md)

## How this journey fails

| Failure | Why it matters |
|---------|----------------|
| The safety number is skippable | The only machine-in-the-middle defence is gone. |
| Private key material leaves a device | The whole model collapses. |
| Initial sync can be dismissed | The user acts on a half-synced ledger believing it complete. |
| Sync silently does nothing | Weeks of divergence discovered by accident. Worse than a visible failure. |
| The relay can read a blob | The zero-knowledge claim is false and the product's promise with it. |
| Concurrent edits to different fields lose one | Users learn not to trust two devices. |
| Revocation is described as retroactive | The user makes a security decision on a false premise. |
| A phone joining mints its own key epoch | Divergent keyrings; content one device cannot read. |

## Current status

Ten of the mobile peer's eleven plans are complete. The outstanding one is
surface-parity smoke testing plus **real-device acceptance on both mobile
platforms** — and until that runs, the import-from-another-device flow should not
be advertised as device-verified. See the
[roadmap](../../00-overview/roadmap.md#1--mobile-client-as-a-fully-synced-peer).

## Related

- [ADR-0015](../../00-overview/decisions/0015-multi-master-p2p-sync.md) · [ADR-0016](../../00-overview/decisions/0016-noise-transport-zero-knowledge-relay.md) · [ADR-0018](../../00-overview/decisions/0018-amounts-plaintext-at-rest.md)
- [J6 Recovery](j6-recovery.md)
