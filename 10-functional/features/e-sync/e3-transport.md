# E3 — Encrypted transport, LAN-direct and relay

**Status:** Accepted · **Area:** E — Sync and devices

---

## Purpose

Getting operations from one device to another when both are on the same network,
and when one of them is asleep in a pocket — without a server that can read
anything.

The design is
[ADR-0016](../../../00-overview/decisions/0016-noise-transport-zero-knowledge-relay.md).

## Behaviour

### Sessions are mutually authenticated and forward-secret

Paired devices establish a session over their existing key-agreement keys, using
a handshake pattern chosen by what each side already knows: the shorter pattern
when the initiator already holds the responder's static key — the normal case
between paired devices — and the mutual-exchange pattern otherwise.

Sessions authenticate on exactly the identities pairing established
([E2](e2-device-pairing.md)). There is no second trust root, no certificate
authority, and no name to get wrong.

The handshake implementation is validated against the protocol's own published
test vectors. A hand-built handshake that is not vector-checked is a liability;
one that is, is the highest-risk component in the product and is treated as such
in review.

### Framing is bounded

Frames are length-prefixed with hard caps on frame size and operations per
frame. Every receive carries a timeout. A peer cannot wedge a session by sending
nothing, by sending too much, or by sending a length that promises more than it
delivers.

### Discovery has three rungs

1. **Local network discovery**, advertising a service record carrying the device
   identifier.
2. **A manually entered host and port**, for networks where discovery is blocked
   — guest networks and client-isolated wireless are common.
3. **The relay.**

### The relay knows nothing

The relay stores and forwards opaque blobs addressed to a recipient device
identifier. It performs **no cryptography at all** — the invariant is that its
code path contains no cryptographic call, and that is asserted by test rather
than described in a comment.

- Draining a mailbox requires a credential derived **per device**. A credential
  scoped to one device cannot drain or delete another's mailbox. A single
  relay-wide token is not accepted.
- That credential is refusable **on its face**. The relay must be able to tell
  that a presented credential is not about the device identifier in the request
  without consulting prior state — because a mailbox nobody has ever drained has
  no prior state to consult, and that first drain is the one carrying a new
  device's key epochs ([E4](e4-at-rest-encryption.md)). "Whoever asks first owns
  the mailbox" is not an acceptable answer for it.
- The credential is never shared between the local users of one install. Device
  identifiers are per user, so one shared credential both breaks the second
  user's leg and hands the relay a way to link two users as one household.
- Blobs expire: delivered ones shortly after delivery, undelivered ones after a
  longer window.
- There are caps on blob size and on pending blobs per recipient.
- **The relay is off by default.** No relay is configured unless the user
  configures one, and its address is a setting rather than a constant. Its
  credential is stored with owner-only file permissions.

### What the relay can still see

Message sizes, timing, and which device identifiers exchange traffic. Traffic
analysis is **not** defended against, and that is documented rather than
implied.

### Key material over the transport

Group-key epochs ([E4](e4-at-rest-encryption.md)) travel sealed to the
recipient's public key — confidential, but not sender-authenticated by the seal
alone. Each wrap therefore **also carries a detached signature by the sending
device**, verified against that device's still-confirmed registry key before the
epoch is read. Provenance rides with the wrap, not the channel, so a blob that
arrives raw from the relay — or from a revoked peer — is refused unless its
signature verifies.

A failed unseal is checked strictly and **rejects** the message — logged, not
thrown, and never appended.

### Catch-up

Two devices that have both moved on exchange from a watermark rather than
re-sending everything, with a bound on how many catch-up frames one session may
consume.

### Hosting

The desktop bundle runs the listener as a managed child process. Templates ship
for running it under a service manager on a self-hosted install. The mobile
client never listens — it dials out only ([E5](e5-mobile-peer.md)).

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Local discovery blocked by the network | Manual host entry, then the relay. |
| A peer that stops responding mid-session | The receive timeout ends the session. |
| A frame larger than the cap | Rejected. |
| A drain attempt with another device's credential | Refused. |
| A drain attempt against a mailbox nobody has ever drained | Refused unless the credential is about that device identifier. |
| A blob nobody collects | Expires after the undelivered window. |
| A forged or relay-delivered epoch wrap | Adopted only if its signature verifies against the sender's confirmed device key; otherwise refused, logged, not thrown. |
| A failed unseal | Strictly checked and rejected; logged, not thrown. |
| No relay configured | Sync works on the local network only. |
| The app locked when key material arrives | Logged and returned; never thrown. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E3-R1** | Sessions MUST be mutually authenticated and forward-secret. |
| **E3-R2** | Sessions MUST authenticate on the identities established by pairing; no second trust root may exist. |
| **E3-R3** | The handshake implementation MUST be validated against the protocol's published test vectors. |
| **E3-R4** | Frames MUST be length-prefixed with hard caps on frame size and operations per frame. |
| **E3-R5** | Every receive MUST carry a timeout. |
| **E3-R6** | Discovery MUST offer local-network discovery, manual host entry, and relay fallback, in that order. |
| **E3-R7** | The relay MUST contain no cryptographic operation, and this MUST be asserted by test. |
| **E3-R8** | Draining a mailbox MUST require a per-device credential; a relay-wide token MUST NOT be accepted. |
| **E3-R9** | A credential scoped to one device MUST NOT be able to drain or delete another device's mailbox. |
| **E3-R10** | Delivered and undelivered blobs MUST expire on documented schedules. |
| **E3-R11** | Blob size and pending blobs per recipient MUST be capped. |
| **E3-R12** | The relay MUST be off by default, and its address MUST be a user setting rather than a constant. |
| **E3-R13** | The relay credential MUST be stored with owner-only file permissions. |
| **E3-R14** | The metadata the relay can observe MUST be documented; traffic-analysis resistance MUST NOT be claimed. |
| **E3-R15** | A sealed epoch-key wrap MUST NOT be adopted unless it carries a detached signature by the sending device, verified against that device's still-confirmed registry key before the epoch is read — so a forged wrap is refused independent of the channel it arrived on. |
| **E3-R16** | A failed unseal MUST be checked strictly, MUST reject the message, and MUST NOT throw. |
| **E3-R17** | Catch-up MUST exchange from a watermark rather than re-sending the whole log. |
| **E3-R18** | The number of catch-up frames one session may consume MUST be bounded. |
| **E3-R19** | The desktop bundle MUST run the listener as a managed child process, and templates MUST ship for service-managed hosting. |
| **E3-R20** | Arrival of key material while the application is locked MUST be logged and returned, never thrown. |
| **E3-R21** | The relay's deliver endpoint MUST rate-limit per source and reject a burst, so no participant can flood a mailbox. |
| **E3-R22** | A drain credential MUST be bound to the device identifier it drains in a way the relay can verify without prior state, so a credential that is not about that identifier is refused even for a mailbox that has never been drained. |
| **E3-R23** | A drain credential MUST NOT be shared between the local users of one install. |

## Related

- [ADR-0016](../../../00-overview/decisions/0016-noise-transport-zero-knowledge-relay.md)
- [E1 Change capture](e1-change-capture.md) — what travels
- [E2 Device pairing](e2-device-pairing.md) — the identities
- [E4 At-rest encryption](e4-at-rest-encryption.md) — the key material
- [E5 Mobile peer](e5-mobile-peer.md) — dial-out only
- [40-quality/security.md](../../../40-quality/security.md)
