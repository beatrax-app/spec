# ADR-0027: A confirmed device may introduce another, and the reader confirms it

**Status:** Accepted
**Date:** 2026-09-03

## Context

A household replaces a phone. The new phone pairs with the Mac and receives
everything. It never paired with the phone it replaced, so it holds no key for
it — and [E2-R12](../../10-functional/features/e-sync/e2-device-pairing.md)
allows only a confirmed device's key to verify a signature, while E2-R13 requires
an op signed by an unknown device to be quarantined and never applied.

**Measured on the paired pair rather than reasoned about.** The Mac's op log
holds 6,802 entries: 6,603 its own, 44 the current phone's, and **155 signed by
the phone that was replaced**. Those 155 are the ones a new phone cannot verify.

What that costs is *not* the data. [ADR-0024](0024-peer-row-id-aliases.md)'s
companion fix made a device re-capture rows whose only create op came from a
peer, so **zero** rows on that log have their only create signed by the replaced
phone — every row is separately covered by an op the Mac signed itself. What
remains is a quarantine of 155 entries on the new phone that **no later state can
ever clear**, and a sync-health screen reporting a fault the reader cannot act
on. E2-R13 is being honoured exactly, and the result is a permanent false alarm.

The obvious repair — the Mac hands the new phone the replaced phone's public key
— is what E2-R7 and E2-R8 forbid: a safety number is displayed on **both**
devices and confirmed on both, and one of those devices no longer exists.

## Decision

**A confirmed device MAY relay another confirmed device's public identity, and
the receiving reader MUST confirm it before any signature verifies against it.**

- The relayed key arrives as an **introduction**, never as trust. It is stored
  unconfirmed and verifies nothing until the reader acts.
- The device list shows it as introduced-by, naming the device that vouched for
  it, with the fingerprint E2-R10 already requires.
- Confirmation is the reader's, on one device, because the other end of the
  original ceremony is gone. The two-party rule (E2-R7, E2-R8) is unchanged for
  **pairing**; this is a separate, weaker act that grants verification only.
- A relayed key MUST NOT grant transport authentication, epoch delivery, or
  anything else a paired device may do. It verifies historical signatures and
  nothing more.
- Revocation (E2-R14) removes an introduced device exactly as it removes a
  paired one.

The trust statement E2-R17 already requires gains a sentence: a device you
confirm this way was vouched for by a device you paired with, and you are
trusting that pairing rather than a ceremony with the device itself.

**The catch-up filter ships with it, not instead of it.** A sender must not
offer an op whose author the receiver cannot verify. That is only decidable if
the receiver says which authors it can verify, so the catch-up request carries
that list, and the sender withholds every other author. The two halves are one
mechanism rather than two: the authors a sender withholds are exactly the
authors it may introduce, so the same exchange that narrows the delta names the
device whose confirmation would widen it again.

Two properties follow, and both are load-bearing:

- **The narrowing is not silent.** A withheld author is reported to the
  receiver with a count, and the receiver holds that count against the
  introduction it can act on. The alternatives table calls silence this
  option's cost; this is the price of removing it.
- **A watermark MUST NOT advance over an op the receiver did not admit.** A
  cursor is a claim to have consumed history. Spending it on an op that
  quarantined makes the refusal permanent, and an introduction confirmed
  afterwards would then rescue nothing — the ops it can now verify are already
  behind the cursor and no peer will offer them again.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Send no op the receiver cannot verify — filter at catch-up, *and nothing else* | Not rejected — adopted, as the paragraph above says, and it is not sufficient alone. On its own it answers the symptom: the receiver's log no longer contains the history, so a later reprojection is built from less than the household has, and nothing on any screen says which device's history is missing or how to get it back. It is the defence; the introduction is the repair. |
| Drop rather than quarantine an op from a device with no key | Same objection, and it makes E2-R13 conditional on a state the reader cannot see. A refusal that is not recorded is the failure mode [ADR-0025](0025-primary-key-collisions-are-quarantined.md) was written about. |
| Re-pair every peer by hand after a replacement | The status quo. It does not work: the replaced phone is *gone*, so there is no second party to pair with. The 155 entries stay quarantined however many pairings the reader performs. |
| Relay the key and trust it automatically | Removes the ceremony rather than moving it, and makes a compromised paired device able to introduce a key of its own choosing that verifies history silently. |

## Consequences

### Positive

- A quarantine that could never be cleared becomes one the reader can clear,
  deliberately, having seen the fingerprint and who vouched for it.
- A device replaced years in can still reproject the household's full history.

### Negative

- A second, weaker trust path exists, and it must stay weaker: if an introduced
  key ever grants more than signature verification, this becomes a way for one
  compromised device to admit another.
- The reader is asked to confirm something they cannot cross-check against a
  second screen. The UI must say that plainly rather than imitating the pairing
  ceremony's language.

### Neutral

- Nothing changes for a household whose devices all paired with each other.

## Revisit if

- Transport or epoch delivery is ever proposed for an introduced device. That is
  the boundary this decision rests on.

## Related

- [E2 Device pairing](../../10-functional/features/e-sync/e2-device-pairing.md) —
  E2-R7, E2-R8, E2-R12, E2-R13, E2-R14, E2-R17, E2-R18, E2-R19, E2-R20, E2-R21
- [ADR-0015](0015-multi-master-p2p-sync.md) — the threat model this sits inside
- [ADR-0024](0024-peer-row-id-aliases.md) — the re-capture that already covers
  the row data, which is why this is about a false alarm and not about loss
