# ADR-0015: Full peer-to-peer multi-master sync, not hub-and-spoke

**Status:** Accepted
**Date:** 2026-06-14

## Context

Once Beatrax runs on a desktop and a phone, the two copies diverge. Reconciling
them is the largest single piece of design in the project, and the topology
choice constrains everything downstream — identity, transport, conflict
resolution, and what happens when a device is lost.

The constraint that rules out the industry default is
[ADR-0004](0004-local-only-hosting.md): there is no server, and adding one that
can read the data contradicts the product's founding promise. That leaves two
shapes:

- **Hub-and-spoke.** One device is designated primary; others sync through it.
  Simpler conflict resolution — the hub arbitrates — and simpler catch-up.
- **Multi-master peer-to-peer.** Every copy is equal; any pair can sync
  directly; the merge is symmetric.

The project lead's requirement was explicit: *no "main" device; maximum
resilience; all copies equal.*

## Decision

Full peer-to-peer multi-master sync.

- **Every device is a first-class peer.** There is no primary, no designated
  arbiter, and no device whose loss makes the others read-only.
- **Each device generates its own long-term identity on first run** — an Ed25519
  signing keypair and an X25519 key-agreement keypair. Private keys never leave
  the device that made them; there is no key escrow and no recovery path that
  reconstructs another device's private key.
- **Pairing is a deliberate, mutually-confirmed ceremony.** A QR code carries the
  new device's public identity plus a single-use, expiring secret; a typed
  word-code from a standard wordlist is the fallback when a camera is unusable.
  Both screens display a derived safety number and both users must confirm it
  before the pairing completes.
- **Merge is symmetric**, resolved by the op-log's per-field rules
  ([ADR-0014](0014-op-log-crdt-merge-engine.md)) rather than by asking a hub.
- **Removing a device is a security operation, not a list edit.** It revokes the
  device's trust, mints a fresh at-rest key epoch, and re-wraps that epoch to
  every remaining confirmed device
  ([ADR-0018](0018-amounts-plaintext-at-rest.md)).

**The threat model excludes a maliciously-paired device and a compromised
operating system.** A paired device legitimately holds the group key; if the user
pairs an attacker's device and confirms the safety number, the attacker has the
data. That is what the safety-number confirmation exists to prevent, and it is
where the design's guarantee ends. Recorded explicitly so nobody mistakes
revocation for a defence against a device that was trusted while it was
listening.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Hub-and-spoke with a designated primary** | Genuinely simpler. Lost on the product requirement: a primary is a single point of failure, and "which device is the real one" is exactly the question a local-first tool should not force a user to answer. |
| **A self-hosted sync server the user runs** | Reintroduces an operational component ([ADR-0005](0005-sqlite-wal.md) exists to avoid exactly this) and makes the phone dependent on a machine being awake. |
| **A hosted sync service, end-to-end encrypted** | Contradicts [ADR-0004](0004-local-only-hosting.md) and creates a target the maintainer becomes responsible for. The relay ([ADR-0016](0016-noise-transport-zero-knowledge-relay.md)) is the bounded version of this that survives the constraint. |
| **Account-based identity with a central directory** | Requires an account, which the product does not have and does not want. |

## Consequences

### Positive

- No device is special, so no device's loss is catastrophic to the others.
- No account, no server, no maintainer involvement in a user adding a device.
- The design composes with the app-lock: unlocking is what releases the key
  material sync needs, so a locked device syncs nothing.

### Negative

- **Pairing is a real ceremony with real friction.** Scanning a QR, or typing a
  word code, and confirming a safety number on two screens is more work than
  signing into an account. It is the price of not having the account.
- **Symmetric merge is harder to reason about** than a hub's arbitration, and it
  is why [ADR-0014](0014-op-log-crdt-merge-engine.md) needed a spike before
  anything downstream committed.
- **Catch-up between two devices that have both moved on** requires an exchange
  protocol with a watermark, not a simple pull.
- **Every device holds the full history**, so a phone carries the whole ledger.
  Acceptable for a personal-finance dataset; it would not be for a media library.

### Neutral

- The mobile client is a client-only peer in one respect — it dials out and does
  not run a listener or daemon — while remaining a full peer in the merge. That
  is a platform constraint, not a topology exception. See
  [E5](../../10-functional/features/e-sync/e5-mobile-peer.md).

## Revisit if

- The device count in a realistic household grows past the point where an
  all-pairs catch-up is efficient, which would mean designing an epidemic or
  gossip layer — an addition to this decision, not a reversal of it.

## Related

- [ADR-0014](0014-op-log-crdt-merge-engine.md) · [ADR-0016](0016-noise-transport-zero-knowledge-relay.md) · [ADR-0018](0018-amounts-plaintext-at-rest.md)
- [E2 Device identity and pairing](../../10-functional/features/e-sync/e2-device-pairing.md)
- [J5 Adding a device](../../10-functional/journeys/j5-adding-a-device.md)
- [40-quality/security.md](../../40-quality/security.md)
