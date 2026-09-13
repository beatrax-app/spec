# ADR-0033: The relay carries pairing material, not the ledger, and "zero-knowledge" is retired

**Status:** Accepted
**Date:** 2026-09-13
**Supersedes:** two claims in
[ADR-0016](0016-noise-transport-zero-knowledge-relay.md) — that the relay is the
store-and-forward fallback that holds op-log entries until an offline peer comes
back, and that it holds opaque ciphertext blobs — and the same second claim
where [ADR-0004](0004-local-only-hosting.md) restates it. Everything else in both
records stands: the Noise IK/XX transport and its framing, the discovery ladder,
expiry and caps, the per-device drain credential, and the relay being off by
default.

## Context

Two sentences about the relay have been in this specification since it was
written, and both are false of the product it describes.

**One: that op-log entries wait in the relay when a peer is asleep.** They do
not. An operation travels only inside a mutually-authenticated session between
two paired devices ([E3](../../10-functional/features/e-sync/e3-transport.md)).
A relay holds blobs, not sessions, and no format exists for sealing an op-log
entry to a mailbox. The mobile sync pass dials the local network, then reaches
the relay for key material only; its own comment says the relay "carries no ops
— only epoch wraps". When neither device can see the other, the changes wait on
the device that made them. The product's own copy has said so on the relay
setting since 2026-09-05, when the sweep of screens that stated one condition
and enforced another reached it, and a test pins the sentence — including that
it must not promise a pull the phone cannot make. Since then the specification
and the shipped string have been contradicting each other outright, and the
shipped string was the honest one.

**Two: that what the relay holds is opaque ciphertext.** Half of it is. The key
handovers are sealed to the receiving device's public key, and whoever runs the
relay cannot open them. The pairing frames are not sealed at all: they are JSON,
handed to the mailbox as written. Between the accepting frame, the confirming
frame and the mailbox addressing that carries either, a relay operator can read

- both device identifiers — the accepting frame names the responder, the
  confirming frame names both, and every mailbox row is addressed from one to
  the other regardless;
- the responder's Ed25519 signing key and X25519 key-agreement key, as hex;
- the pairing token's hash;
- the responder's device name, which on a desktop is a neutral platform label
  and on a phone is the name the operating system reports for it — often one a
  person chose, and sometimes one carrying their own name.

Only the confirming frame is signed. The accepting frame is not, so "signed but
not encrypted" is true of one of the two and would be a second overstatement if
said of both.

None of this is a defect. A pairing frame is public-key material and the name of
a device, exchanged before any shared secret exists, and the safety number the
two readers compare is what makes a swapped key fail. It is a defect in the
*description*: a reader who believes the relay holds only ciphertext concludes
that nominating one reveals nothing, and that conclusion is wrong.

### The term is the third problem

"Zero-knowledge relay" is what the glossary and ADR-0016's own title call it.
The name is doing work the design does not do. Whatever a reader takes
"zero-knowledge" to mean — the proof systems it names in cryptography, or the
industry's looser "the operator cannot read it even if it wants to" — neither
survives contact with a plaintext pairing frame. The relay's real discipline is
narrower and stronger for being checkable: it performs no cryptographic
operation on a blob and never looks inside one, asserted by test
([E3-R7](../../10-functional/features/e-sync/e3-transport.md#acceptance-criteria),
[ADR-0031](0031-a-signed-wrap-is-independent-of-its-channel.md)). That is a
statement about what the relay *does*. "Zero-knowledge" is a statement about
what it *could* do, and it is not true.

A term whose outside meaning is the overclaim cannot be repaired with a house
definition. The glossary already retires two words on exactly this ground —
"cloud sync" and, for the relay, "server" — because the connotation promises
more than the thing delivers. This is the same move, applied to a word the
specification was making the promise with rather than one it was avoiding.

## Decision

**A relay's job is pairing, and only pairing.**

- An op-log entry MUST NOT be delivered over a relay. Operations cross only a
  mutually-authenticated session between two paired devices.
- A relay exists so that two devices that cannot reach each other directly can
  complete the pairing ceremony and exchange group-key epochs.
- Where a peer is unreachable, changes wait on the device that made them until
  both are awake on the same network. That is the answer, and it is stated
  rather than implied.

**What a relay holds is described in both halves, always.**

- Key handovers are sealed to the receiving device and cannot be read by the
  relay. Their envelope is not sealed: it names both device identifiers and the
  epoch, and carries the sender's signature.
- Pairing frames are not sealed. Any description of the relay that names the
  sealed half MUST name the unsealed one in the same breath, together with the
  metadata a relay sees — sizes, timing, and which device identifiers exchange
  traffic.

**The term "zero-knowledge relay" is retired.**

- The thing is a **pairing relay**, or simply a relay. The word names the job,
  which is what makes "a transaction never crosses it" read as a description
  rather than a surprise.
- "Zero-knowledge" is added to the glossary's deliberately-not-used list, in
  both its relay and its sync forms.
- **ADR-0016 keeps its title and its filename.** The record is immutable and its
  title is a fact about what was decided on 2026-06-15. Renaming it would edit
  the history this repository keeps decisions for.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Redefine "zero-knowledge" in the glossary to mean what the relay actually does** | Publishes a private meaning for a public term. The glossary exists to stop a reader importing an outside definition; it cannot do that for a word whose outside definition *is* the overclaim. A reader who never opens the glossary is the one being misled, and that reader is most of them. |
| **Correct the sentences and keep the term** | The sentences are downstream of the name. Every surface that inherited "zero-knowledge relay" inherited the claim with it, which is how one phrase in one ADR reached the public website. Leaving the source in place schedules the next recurrence. |
| **Say less about the relay** | The tempting option and the worst one. A page that goes quiet about what a relay holds has not become accurate, it has become unfalsifiable — and this product's whole argument is that its privacy claims are checkable. [G1](../../10-functional/features/g-ux/g1-privacy.md) and [G5](../../10-functional/features/g-ux/g5-plain-language.md) already forbid it. |
| **Seal the pairing frames and keep the claim true** | A code change, and one that buys little: the frames carry public keys and a device label, and a receiver with no shared secret yet has nothing to unseal with. Sealing to the recipient's X25519 key would be possible for the confirming frame and is worth considering on its own merits — but it would not be a reason to describe today's relay as though it were already done. |
| **Edit ADR-0016 and ADR-0004 in place** | Forbidden, and for the same reason [ADR-0031](0031-a-signed-wrap-is-independent-of-its-channel.md) refused it: the record of changing our mind is the valuable part. Both records get a note naming the claims that no longer hold and pointing here. |

## Consequences

### Positive

- The specification and the product's own copy agree. The in-app relay help,
  which was already accurate, stops being the only honest description in the
  organisation.
- A reader deciding whether to nominate a relay can now decide on what it would
  actually learn: that two identified devices paired, when, and how big the
  frames were.
- "Pairing relay" makes the scope self-evident. The old name invited the
  question "so my transactions go through it?", and the honest answer needed a
  paragraph.

### Negative

- Removing "zero-knowledge" removes a phrase that read well. The replacement is
  longer everywhere it appears, because the truth has two halves and both have
  to be said.
- ADR-0016's filename and title keep a term the rest of the specification no
  longer uses. That is a deliberate inconsistency and is recorded here so it is
  not later mistaken for an oversight.

### Neutral

- No requirement changes meaning. [E3-R7](../../10-functional/features/e-sync/e3-transport.md#acceptance-criteria)
  (no cryptography on a blob, never look inside one) and
  [E3-R14](../../10-functional/features/e-sync/e3-transport.md#acceptance-criteria)
  (document the metadata, claim no traffic-analysis resistance) were accurate
  and stay as written. `E3-R24` and `G1-R22` are added for what crosses a relay
  and for saying so in the product's own copy, neither of which anything
  previously required.
- Nothing changes about LAN-direct sync, which is where operations have always
  travelled.

## Revisit if

- Relay delivery of op-log entries is ever built, which would need a sealed
  op-envelope format and would be a new decision rather than an extension of
  this one.
- Pairing frames gain a seal, at which point the unsealed half of the
  description shrinks to the mailbox addressing and the metadata.

## Related

- [ADR-0016](0016-noise-transport-zero-knowledge-relay.md) — the record this supersedes in part
- [ADR-0004](0004-local-only-hosting.md) — the same claim, restated
- [ADR-0031](0031-a-signed-wrap-is-independent-of-its-channel.md) · [ADR-0015](0015-multi-master-p2p-sync.md)
- [E2 Device pairing](../../10-functional/features/e-sync/e2-device-pairing.md) · [E3 Encrypted transport, LAN-direct and relay](../../10-functional/features/e-sync/e3-transport.md)
- [G1 Privacy](../../10-functional/features/g-ux/g1-privacy.md) · [40-quality/security.md](../../40-quality/security.md)
