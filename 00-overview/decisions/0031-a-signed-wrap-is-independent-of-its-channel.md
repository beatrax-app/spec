# ADR-0031: A signed epoch wrap is trusted on its signature, not on its channel

**Status:** Accepted
**Date:** 2026-09-05
**Supersedes:** two claims in
[ADR-0016](0016-noise-transport-zero-knowledge-relay.md) — that a sealed epoch
wrap is only ever legal from a channel that has already authenticated the
sender, and that the relay performs no cryptography at all. Everything else in
that record stands: the Noise IK/XX transport, the discovery ladder, blob
opacity and expiry, and the relay being off by default.

## Context

ADR-0016 settled the transport and, in the same breath, settled how a sealed
group-key epoch may be accepted. The epochs it described were **sealed but not
sender-authenticated**: confidential to the recipient, and carrying nothing that
said who sent them. Given that shape, only one rule was available — trust the
channel, because the payload cannot vouch for itself:

> Handling one is therefore only ever legal from a channel that has already
> authenticated the sender as a confirmed peer. Anything arriving raw from the
> relay is not that channel.

The payload has since changed shape. `E3-R15` requires a sealed wrap to carry a
**detached signature by the sending device**, verified against that device's
still-confirmed registry key before the epoch is read. That requirement is
implemented: `GdkEpochControlHandler` looks the sender up among the user's
confirmed devices, refuses an unconfirmed or unknown one, rebuilds the signing
message and rejects the wrap outright if the signature does not verify.

So the two rules now disagree about the same wrap. ADR-0016 says a wrap drained
from a relay mailbox must be refused because the relay is not an authenticated
channel. `E3-R15` says the same wrap is safe, because a forged one cannot
produce a signature that verifies against a confirmed device's key. An
implementation draining a mailbox has to pick, and nothing said which wins.

A second claim in ADR-0016 has been overtaken the same way. It said of the relay
that **"it performs no cryptography at all … not a single cryptographic call in
the relay's code path, asserted by test."** `E3-R8` requires the relay to decide
whether a presented credential may drain a given mailbox, and `E3-R22` requires
that binding to be verifiable *without prior state*. Deciding it needs a stored
verifier and a constant-time comparison, and the relay's drain registry duly
computes a SHA-256 digest and compares with `hash_equals`. The absolute was
never true of the shipped relay; what is true, and what the zero-knowledge test
actually asserts, is narrower and better.

## Decision

**A sealed epoch wrap is trusted on its signature, and its channel is
irrelevant.**

- A wrap MUST carry a detached signature by the sending device, verified against
  that device's still-confirmed registry key before the epoch is read
  (`E3-R15`).
- A wrap that verifies MAY be adopted whatever path delivered it — a Noise
  session, a relay mailbox drain, or a pairing frame.
- A wrap that does not verify MUST be refused, on every path, including one that
  authenticated its sender at the transport layer. **The channel is no longer a
  reason to accept, and it was never a sufficient reason to.**

**The relay's zero-knowledge property is about payloads, not about primitives.**

- The relay MUST perform no cryptographic operation *on a blob* and MUST never
  look inside one: no libsodium call, and no decode of a blob's contents,
  anywhere in its code path.
- The digest and constant-time comparison that authorise a drain (`E3-R8`,
  `E3-R22`) are permitted, and touch the credential rather than the payload.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Keep the channel precondition alongside the signature** | Belt and braces, but the belt is the wrong shape. It forbids relay delivery of a wrap that is provably authentic, which is the one delivery path that exists when the peers are never awake at the same time — the case ADR-0016 built the relay for. |
| **Keep the precondition and drain only over Noise** | A mailbox drained over a Noise session to the *relay* still authenticates the relay, not the sender. The precondition cannot be satisfied by the relay path however it is dressed up, so this reduces to abandoning relay epoch delivery. |
| **Edit ADR-0016 in place** | Forbidden, and rightly: the record of changing our mind is the valuable part, and a reader who followed the old rule deserves to find out why it moved rather than to find it silently gone. |
| **Restate the relay's crypto carve-out as "no cryptography except…"** | An exception list attached to an absolute invites the next primitive to be argued in. Naming the *object* — blobs, never their contents — is the invariant that survives a new primitive. |

## Consequences

### Positive

- Relay epoch delivery becomes legal, which is what makes a key rotation reach a
  device that is never awake at the same time as its peer.
- The rule that remains is the stronger one. A signature verified against a
  confirmed registry key refuses a forged wrap that arrives over a
  *fully authenticated* channel; the channel precondition never could.
- The relay's zero-knowledge claim becomes checkable against what the relay
  actually does, so the assertion protects something rather than being an
  absolute the code has already left behind.

### Negative

- The gateway's own code comment still carries ADR-0016's precondition as a
  SECURITY PRECONDITION, and one stale comment on a security-relevant seam is
  worth more confusion than several elsewhere. It is a code change, tracked
  separately from this record.
- A signature check is a per-wrap cost on a path that previously trusted the
  channel wholesale. The wrap count is bounded per pass, so the cost is bounded.

### Neutral

- Nothing changes for LAN-direct delivery, which satisfied both rules already.

## Revisit if

- Epoch wraps gain sender authentication at the seal itself, at which point the
  detached signature is redundant rather than load-bearing.
- The relay is ever asked to do something to a blob rather than with a
  credential, which would be a new decision and not an extension of this one.

## Related

- [ADR-0016](0016-noise-transport-zero-knowledge-relay.md) — the record this supersedes in part
- [ADR-0015](0015-multi-master-p2p-sync.md) · [ADR-0014](0014-op-log-crdt-merge-engine.md)
- [E3 Encrypted transport, LAN-direct and relay](../../10-functional/features/e-sync/e3-transport.md)
- [E4 At-rest encryption](../../10-functional/features/e-sync/e4-at-rest-encryption.md)
