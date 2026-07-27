# ADR-0016: Noise XX/IK transport with a zero-knowledge relay fallback

**Status:** Accepted
**Date:** 2026-06-15

## Context

Two paired devices ([ADR-0015](0015-multi-master-p2p-sync.md)) need to exchange
op-log entries. Two situations exist and they need different answers:

- **Both online, same network.** A direct connection is possible, and it is the
  fast, private, dependency-free path.
- **One offline.** The phone is in a pocket; the laptop is closed. Something has
  to hold the ops until the peer comes back, or sync only ever happens when both
  devices are awake and adjacent — which in practice means it never happens.

TLS was the obvious transport candidate and is a poor fit here: it authenticates
by certificate chain against a public PKI, and these peers authenticate by
mutually-confirmed device identity. Self-signed certificates plus manual pinning
reimplements the authentication the device identities already provide, badly.

The store-and-forward problem is where most local-first products quietly
introduce a server that can read the data. That is not available here
([ADR-0004](0004-local-only-hosting.md)).

## Decision

**Transport: the Noise Protocol Framework** over the devices' existing X25519
keys, with XChaCha20-Poly1305 as the cipher and BLAKE2b as the hash.

- **Noise IK** when the initiator already knows the responder's static public
  key — the normal case between paired devices, and one round trip fewer.
- **Noise XX** for the mutual-authentication case where identities are exchanged
  in the handshake.
- Sessions are forward-secret and mutually authenticated. The implementation is
  validated against the protocol's official test vectors, because a hand-rolled
  handshake that is not vector-checked is a liability rather than an asset.
- Frames are length-prefixed with hard caps on both frame size and operations
  per frame, and every receive carries a timeout, so a peer cannot wedge a
  session by sending nothing or by sending too much.

**Discovery: mDNS on the local network**, advertising a service record carrying
the device identifier. Three levels, in order: mDNS discovery, a manually
entered host and port, then the relay.

**Fallback: a zero-knowledge store-and-forward relay.**

- The relay holds opaque ciphertext blobs addressed to a recipient device
  identifier. It stores and forwards them verbatim.
- **It performs no cryptography at all.** The invariant is checkable and is
  checked: there is not a single cryptographic call in the relay's code path,
  asserted by test.
- Authorisation to drain a mailbox is a per-device derived credential, not a
  relay-wide token — a credential scoped to device A cannot drain or delete
  device B's mailbox.
- Blobs expire: delivered ones shortly after delivery, undelivered ones after a
  longer window. There are caps on blob size and on pending blobs per recipient.
- **The relay is off by default.** No relay is configured unless the user
  configures one, and the user chooses which one. Its address is a setting, not
  a constant.

**Sealed epoch delivery is only trusted over an authenticated channel.** The
group-key epochs that ride this transport are sealed to a recipient's public key
in a form that is confidential but not sender-authenticated. Handling one is
therefore only ever legal from a channel that has already authenticated the
sender as a confirmed peer. Anything arriving raw from the relay is not that
channel.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **TLS with self-signed certificates and pinning** | Reimplements, badly, the authentication the device identities already provide, and drags in a certificate lifecycle nobody wants to operate. |
| **A relay that can read the data** | Contradicts the product's founding promise, and makes the maintainer responsible for a high-value target. |
| **LAN-only, no fallback** | Sync would only happen when both devices are awake and adjacent. In practice that means the phone is permanently behind. |
| **An off-the-shelf mesh VPN** | The leading candidates have proprietary control planes, which conflicts with the project's source-available commitment and reintroduces a third party in the trust path. |
| **A library implementation of Noise** | Considered; the PHP ecosystem's options were thin enough that a vector-validated hand-built state machine over the platform's libsodium primitives was judged the lower risk. That judgment is the part of this decision most worth revisiting. |

## Consequences

### Positive

- The relay operator — including the maintainer, if one is ever run — learns
  nothing but blob sizes, timing, and recipient identifiers.
- LAN-direct sync needs no third party at all, and is the default path.
- The transport authenticates on exactly the identities pairing established, with
  no second trust root.

### Negative

- **A hand-built handshake is a hand-built handshake.** Vector validation
  mitigates but does not eliminate the risk. This is the single highest-risk
  component in the codebase and should be treated that way in review.
- **Traffic analysis is not defended against.** The relay sees who talks to whom
  and how much. Documented rather than hidden.
- **mDNS does not survive every network.** Guest networks, client isolation, and
  some corporate wireless block it, which is why manual host entry exists as the
  middle rung.
- Running a relay is an operational task the user takes on if they want the
  fallback.

### Neutral

- The mobile client dials out only and never listens, so the phone never needs an
  inbound path. See [E5](../../10-functional/features/e-sync/e5-mobile-peer.md).

## Revisit if

- A well-maintained, audited Noise implementation for the platform appears, at
  which point replacing the hand-built state machine is a clear win.
- Traffic-analysis resistance becomes a stated requirement, which would mean
  padding and cover traffic — a new ADR.

## Related

- [ADR-0015](0015-multi-master-p2p-sync.md) · [ADR-0014](0014-op-log-crdt-merge-engine.md) · [ADR-0018](0018-amounts-plaintext-at-rest.md)
- [E3 Encrypted transport, LAN-direct and relay](../../10-functional/features/e-sync/e3-transport.md)
- [40-quality/security.md](../../40-quality/security.md)
