# E2 — Device identity and pairing

**Status:** Accepted · **Area:** E — Sync and devices

---

## Purpose

There is no account, no server, and no directory. Two devices therefore have to
establish that they belong to the same person entirely between themselves — and
the user has to be able to verify that nothing got in between.

## Behaviour

### Identity is self-generated and never leaves

On first run a device generates its own long-term signing keypair and its own
key-agreement keypair. **The private halves never leave the device.** There is no
escrow, no backup that reconstructs them, and no recovery path that produces
another device's private key.

Key generation is gated behind the app-lock ([F3](../f-platform/f3-auth-and-app-lock.md)),
and the key file is encrypted at rest.

### Pairing is a deliberate ceremony

An existing device shows a QR code carrying its public identity and a
single-use, expiring secret. The new device scans it. Where a camera is
unusable, the same payload is available as a typed word code drawn from a
standard wordlist.

Both devices then display a **safety number** derived from both public
identities. **Both users must confirm it before pairing completes.** This is the
only defence against a machine-in-the-middle during pairing, and it is
mandatory — not a dismissible advisory.

Pairing tokens are stored hashed, are single-use, and expire.

### The device list

Every paired device appears with a name, a last-seen time, and its own
verifiable fingerprint. Devices can be renamed. Only **confirmed** devices count
as trusted: their keys are what the merge layer verifies signatures against
([E1](e1-change-capture.md)), and an unconfirmed device's operations are
quarantined rather than applied.

### A device the household can no longer pair with

A phone is replaced. The new one pairs with the desktop and receives
everything, but it never paired with the phone it replaced, so it holds no key
for it and every operation that phone signed is unverifiable to it — permanently,
because the second party to that ceremony no longer exists.

Two things answer this, and they are one mechanism.

**Catch-up sends nothing the receiver cannot verify.** The request names the
authors the asking device can verify; the answer carries only those, and says
how many operations it withheld and for which author. A device therefore never
quarantines an operation it was never going to be able to read, and the
narrowing this causes is a number on the asking device's screen rather than a
silence.

**A confirmed device may introduce another.** For an author it withheld and has
itself confirmed, it relays that device's public identity. The relayed identity
arrives as an *introduction*: stored unconfirmed, listed as introduced-by the
device that vouched for it, shown with a fingerprint derived here from the key
that arrived, and verifying nothing at all until the reader confirms it.

Confirming an introduction is not pairing and is deliberately weaker. It is one
reader on one device, because the other end of the original ceremony is gone,
and what it grants is signature verification and only that — never transport
authentication, never epoch delivery, never anything else a paired device may
do. Removal takes an introduced device off the list exactly as it takes a
paired one off.

### Signed work travels further than the identity that signed it

A device serves catch-up for **every author it holds a signing key for** — one
it paired with, whatever became of that pairing, and one it knows only through
an introduction it confirmed. Relaying signed data grants nobody anything: the
receiving device verifies every operation against a key it confirmed itself, and
one it cannot verify is held exactly as before. The relay is a courier, not a
second voucher.

Relaying the *identity* onward is the opposite, and it does not happen. Only a
device this one has itself paired with may be introduced, because a vouch made
on the strength of a vouch is a chain, and a chain launders the two-party
ceremony the whole grant rests on. So an author reachable here only through an
introduction is counted in the withheld report **with no identity beside it**,
which is why that report has to reach a reader on its own.

The household's only voucher is not necessarily its only holder. Two phones that
each paired with the desktop and never with each other both confirm what the
desktop introduces, and from then on either can hold history the other can read.
Retire the desktop and, without this, that history would be stranded for good.

### Removal is a security operation

Removing a device revokes its trust, mints a fresh at-rest key epoch, and
re-wraps that epoch to every remaining confirmed device — see
[E4](e4-at-rest-encryption.md). It is not a list edit.

### Pairing across a relay

Where the two devices cannot see each other directly, the pre-confirmation
handshake propagates over the zero-knowledge relay ([E3](e3-transport.md)) so
two devices with separate databases can still complete the ceremony. The relay
carries the frames; it cannot read them.

### Where the guarantee ends

**A device that is paired is trusted.** If the user pairs an attacker's device
and confirms the safety number, the attacker has the data. Revoking afterwards
rotates the key going forward but does not un-see what was already synced.

This is stated plainly rather than implied, because the safety-number
confirmation is the whole defence and the user needs to know that it matters.

**A device you confirm from an introduction was vouched for by a device you
paired with.** There is no second screen to compare against, and the trust
being extended is the trust already placed in the voucher. That is why an
introduction grants reading old signatures and nothing further: a compromised
paired device can offer a key, and the worst it can then do is make history it
already had the power to write appear verifiable.

## States

A pairing moves `pending` → `awaiting_confirm` → `confirmed`, falling to
`expired` on timeout. A single state machine owns the transitions.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A QR code that cannot be scanned | The typed word-code fallback. |
| An expired pairing token | Rejected; the ceremony restarts. |
| A reused pairing token | Rejected — single use. |
| Safety numbers that do not match | The user must not confirm; the ceremony is abandoned. |
| An unconfirmed device's operations arriving | Quarantined, not applied. |
| Two devices that cannot see each other | The handshake propagates over the relay. |
| App-lock engaged during key generation | Generation is gated; it does not proceed without the unlock. |
| A device removed and then re-paired | It is a new pairing, mutually confirmed afresh, and it receives the whole keyring — every epoch, the current one last. A device holding only the current epoch could neither read history nor rebuild from the log (E4-R2, E1-R6), and re-pairing is a new grant of trust rather than a partial restoration of the old one. |
| Operations signed by a device the receiver cannot verify | Not sent, and the count withheld is reported to the receiver. |
| An introduction the reader never confirms | Nothing verifies against it, and the operations it would have unlocked stay with the peer that holds them. |
| An introduction naming a device the reader already paired with | The pairing stands; a weaker grant cannot widen or narrow it. |
| An author this device knows only through a confirmed introduction | Its operations are served to any device that can verify them; its identity is never relayed onward. |
| An author this device removed, whose history a peer still needs | Still served. Removal is one reader's decision about their own trust, not a deletion of what that device wrote. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E2-R1** | Each device MUST generate its own long-term signing and key-agreement keypairs on first run. |
| **E2-R2** | Private key material MUST NOT leave the device that generated it under any circumstances. |
| **E2-R3** | No escrow or recovery mechanism may reconstruct another device's private key. |
| **E2-R4** | Key generation MUST be gated behind the app-lock, and the key file MUST be encrypted at rest. |
| **E2-R5** | Pairing MUST offer a QR code carrying the public identity and a single-use, expiring secret. |
| **E2-R6** | A typed word-code fallback MUST be available and MUST carry the same payload. |
| **E2-R7** | Both devices MUST display a safety number derived from both public identities. |
| **E2-R8** | Confirmation of the safety number MUST be mandatory on both devices before pairing completes. |
| **E2-R9** | Pairing tokens MUST be stored hashed, MUST be single-use, and MUST expire. |
| **E2-R10** | The device list MUST show each device's name, last-seen time, and verifiable fingerprint. |
| **E2-R11** | Devices MUST be renameable. |
| **E2-R12** | Only confirmed devices' keys MUST be used to verify operation signatures. |
| **E2-R13** | Operations signed by an unconfirmed or unknown device MUST be quarantined, never applied. |
| **E2-R14** | Removing a device MUST revoke its trust and trigger a key-epoch rotation and re-wrap. |
| **E2-R15** | The pre-confirmation handshake MUST be able to propagate over the relay for devices that cannot see each other. |
| **E2-R16** | A single state machine MUST own pairing state, with pending, awaiting-confirmation, confirmed, and expired states. |
| **E2-R17** | The trust boundary — that a paired device is trusted, and revocation does not retroactively protect — MUST be stated to the user in plain language. |
| **E2-R18** | A confirmed device MAY relay another confirmed device's public identity. A relayed identity MUST be stored unconfirmed, MUST name the device that vouched for it, and MUST verify nothing until the reader confirms it. |
| **E2-R19** | A relayed identity, once confirmed, MUST grant signature verification only — never transport authentication, epoch delivery, or any other capability of a paired device. Where the reader has paired with that device, in either direction, the pairing answers for it and the relayed identity grants nothing. The grant is to the reader; what the reader may then serve for an author it can verify is E2-R22. |
| **E2-R20** | Catch-up MUST NOT send an operation whose author the receiving device has declared it cannot verify, and MUST report to that device how many operations were withheld and for which author. The count MUST be taken over the authors the answering device could have served (E2-R22), so that an author it can verify and the asker cannot is reported rather than absent. The report MUST reach a reader on the receiving device whether or not an identity for that author accompanies it. |
| **E2-R21** | A catch-up cursor MUST NOT advance over an operation whose author the receiving device could not verify, so that confirming an introduction later still delivers it. |
| **E2-R22** | Catch-up MUST serve operations for every author the answering device holds a signing key for — a device it paired with, in any state of that pairing, and a device it holds only through a confirmed introduction — narrowed by what the receiving device has declared it can verify (E2-R20). The answering device MUST NOT relay that author's identity onward: only a device it has itself paired with may be introduced. |

> **`E2-R18` through `E2-R21` are satisfied**, and `E2-R22` with them. The four
> shipped on 2026-09-05 and were hardened the same day: the withheld count now
> reaches a reader whether or not an identity accompanies it, an introduction can
> no longer outlive the removal of the device it names, and the cursor hold is
> proved as a sequence — one frame carrying a verifiable author beside an
> unverifiable one, a confirmation, and the same operations landing on the next
> exchange. `E2-R22` widened what a device relays for on the same day.
>
> **The markers stood for a day longer than the state did, and that is worth
> keeping visible.** They were added on 2026-09-05 at 03:31 and the code that
> satisfies them merged at 03:48; the ruling that classified them into v2.0 scope
> was written thirteen hours after that and still said "the code is not merged",
> because it was recording a schedule rather than reading the branch. Two
> separate readers had to reconcile this page's classification with its state,
> and neither time did a check do it. What closes that is the manifest gate,
> which now refuses a goal whose page and whose roadmap bucket disagree.

## Related

- [ADR-0015](../../../00-overview/decisions/0015-multi-master-p2p-sync.md) — the topology and threat model
- [ADR-0027](../../../00-overview/decisions/0027-a-confirmed-device-may-introduce-another.md) — why E2-R18 and E2-R19 exist, and the boundary they rest on
- [E1 Change capture](e1-change-capture.md) — what the keys sign
- [E3 Transport](e3-transport.md) — what the keys authenticate
- [E4 At-rest encryption](e4-at-rest-encryption.md) — revocation and rekey
- [F3 Authentication and app-lock](../f-platform/f3-auth-and-app-lock.md)
- [J5 Adding a device](../../journeys/j5-adding-a-device.md)
