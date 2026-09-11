# E4 — At-rest encryption, revocation and rekey

**Status:** Accepted · **Area:** E — Sync and devices

---

## Purpose

Once several devices hold a copy of the household's whole financial history, the
copies themselves are the exposure — a phone in a taxi, a laptop backup on a
cloud drive, an old machine sold with the disk intact.

This feature encrypts the identifying content of that history at rest behind a
key released by the app-lock, and makes removing a device an operation that
actually changes the key rather than editing a list.

**What is and is not encrypted, and what that means honestly, is
[ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md).**
It should be read alongside this page.

## Behaviour

### One group key, versioned by epoch

A per-user group key encrypts the sensitive columns. Each generation is an
**epoch**; the keyring is append-only, so older ciphertext stays readable after a
rotation.

The key is derived from the user's passphrase through a memory-hard function and
released by the app-lock ([F3](../f-platform/f3-auth-and-app-lock.md)). A locked
device holds ciphertext it cannot read.

### A registry defines the encrypted set

A single registry lists exactly which columns are encrypted. It is the input to
a regression guard that fails the build if a registered column is read or
written raw — because that failure mode is silent at runtime and expensive to
find.

**Encrypted:** the identifying and descriptive columns — transaction
description, counterparty name and identifier, the raw parser payload,
transaction notes; counterparty display name, merchant name, and identifier; tax
notes; split-leg notes; notification title, body, parameters, and trigger kind.

**Deliberately plaintext:** amounts, dates, account references, type enums, and
the full-text index body. Aggregation and search depend on them. The consequence
— that an attacker with the file but not the key sees a complete dated amount
distribution and a plaintext shadow of descriptions — is stated plainly in the
ADR and must be stated plainly in the product's own copy.

### Decrypt before you compare

Every read of an encrypted column decrypts before matching, parsing, or
displaying. A predicate that compares ciphertext to a plaintext pattern never
matches; a display that renders ciphertext shows the user gibberish.

This is the failure mode the design is most prone to. It was common enough
during activation that closing it took a dedicated correctness pass across
matching, search, categorisation, transfer pairing, chain resolution, receipt
conflict handling, counterparty triage, migration merging, and garbage
collection.

### Work runs where the key is

A job dispatched from a request runs synchronously so it inherits the unlocked
key. A job that can only run from a scheduler, where no key exists, **skips with
a warning** rather than silently producing a wrong result. Enumerating which
origin a job has is part of shipping it.

### Enabling encryption on existing data

A one-time migration converts existing plaintext history to ciphertext:

1. A backup is taken **before** anything begins.
2. The conversion runs in bounded batches inside one outer transaction.
3. The first epoch is staged during the transaction and only moved into place
   **after** it commits, so a crash cannot leave a key file that references
   data that never landed.
4. Failure rolls back and clears the in-progress marker.
5. It is row-level idempotent: an already-converted row is detected by real
   verification, not by guessing at the shape of the stored value.
6. If the app is locked and no key is available, **no row is touched** and the
   migration returns quietly.

### Revocation rotates the key

Removing a device:

1. **Revokes its trust first** — so it cannot act during the rotation.
2. Mints a fresh epoch — forward-only; old epochs are not deleted.
3. Wraps the new epoch to every remaining confirmed device and enqueues it for
   delivery ([E3](e3-transport.md)).

Epoch delivery is idempotent on the epoch identity: a device that already has it
drops the duplicate with a warning and never logs key material.

### The one key that never rotates

Recognising the same shop across two rows without reading either needs a keyed
digest, so counterparty matching carries a **blind-index key**. That key is not
an epoch. It is minted once beside the first epoch, it is single-valued, and
nothing rotates it — rotation is what an epoch has, and an index that moved with
a rotation would stop matching every row written before it.

The consequence falls on two devices that each enabled encryption *before* they
were paired. Each holds its own key and each already has rows keyed under it, so
neither may adopt the other's: whichever gave way would orphan the digests only
it can read. Removing a device and pairing it again brings the same key back to
the same standoff, because nothing rotates it. Re-pairing is not a recovery.

The wrap carrying the peer's key therefore arrives, is declined, and arrives
again on the next pass, for as long as the two devices stay paired. A refusal
reported per delivery attempt is a log line nobody reads; reported once it is a
fact about the household. So it is raised **once per divergence**, to the
reader's alerts rather than to the log alone, and withdrawn when the two keys
are next found to agree — which is the only evidence either device ever gets
that the split has ended. An alert that outlives the fault it reported teaches
the reader to dismiss the next one unread.

What the copy may say is bounded by what a reader can reach. A bulk
re-derivation of the keyed columns exists in code, but it runs once in an
install's life behind a marker both devices stamped at enable time, and no
screen reaches it. Naming it sends the reader looking for a control that is not
there. The only recovery that exists is to set one device up again and let it
take its copy from the other, and that is what the copy says. It is the rule
[E6-R16](e6-sync-status.md#acceptance-criteria) states for a withheld hold,
applied to key material instead of to withheld operations.

### Passphrase changes re-wrap

Changing the passphrase re-wraps the keyring rather than re-encrypting the data.
The re-wrap is best-effort at the event boundary and raises a **critical alert**
if it fails — a silently failed re-wrap would lock the user out at the next
unlock.

### What this does and does not protect

It raises the cost of casual access to a copied file or a cloud-backed device
backup. It is **not** a defence against an attacker who has the file, has time,
and cares — the plaintext set is too informative for that. The product's copy
must say so.

### Key custody, and what each platform gives it

The unlocked data key is held by the platform's key store and the session holds
only an opaque handle to it: Keychain Services on macOS and iOS, DPAPI on
Windows, the Android Keystore, and a keyring-backed secret service on Linux
([F3](../f-platform/f3-auth-and-app-lock.md)). This protects the transient
unlocked copy only. The durable wraps stay passphrase-derived and custody never
touches them.

Linux is the one platform where "is a store available" is not the answer. With
no keyring reachable the shell falls back to a fixed-password store whose key is
published in its own upstream source; it reports itself available, and it does
encrypt. Custody there is **reported as unprotected** rather than assumed
protected, and the routes that would persist a wrap of the data key refuse. The
key stays where it was, because refusing to encrypt would strand every blob an
earlier build wrote on that machine — the connector secrets and the biometric
wrap among them. What changes is the claim, not the bytes.

### Mobile backup exclusion, and how far it reaches

A backup-exclusion bridge **exists** — one build script writing both platforms'
halves — and the mobile build applies it rather than leaving it for somebody to
remember.

On **Android** it turns off the manifest's backup flag and fills in both rule
files: the cloud-backup rules and the device-transfer rules, which the platform
reads independently of the flag, so doing one without the other would still let
a handset-to-handset transfer carry the database. The packaging command the
release pipeline runs applies it, so it reaches every release build.

On **iOS** there is no manifest flag; the exclusion is a per-URL resource value
set as each directory is created, and the patch sets it, reads it back, and logs
when it does not take. Two things are narrower there. No pipeline builds an iOS
artefact at all, so the bridge is applied by a local build rather than by CI.
And it is set on the application-support tree, on the premise that the database
lives there, while the mobile bootstrap repoints the live connection to a path
under the documents directory that nothing marks excluded
([E5](e5-mobile-peer.md#open-questions-and-known-gaps)).

So "no bridge exists" was wrong, and "the on-device database therefore sits
unprotected on a cloud-backed path" is wrong on Android. What is not established
is which file the iOS exclusion covers, and that is an open question rather than
an answer in either direction.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| The app is locked | No decryption; encrypted content is unavailable until unlock. |
| A scheduled job with no key | Skips with a warning. |
| An epoch already present | Dropped with a warning; no key material logged. |
| A crash mid-migration | Rolls back; the staged epoch is never moved into place. |
| A crash mid-keyring-write | The staged file is not renamed; the previous keyring stands. |
| A failed passphrase re-wrap | Raises a critical alert rather than failing silently. |
| A payload that cannot be decrypted under any epoch | Quarantined ([E1](e1-change-capture.md)). |
| Two devices holding different blind-index keys, each with rows keyed under its own | Neither adopts the other's; the divergence is reported once and withdrawn when the keys agree. |
| A device removed and paired again after such a divergence | The same key returns; nothing rotates it, so re-pairing is not a recovery. |
| Re-running the migration | Row-level idempotent by real verification. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E4-R1** | A per-user group key MUST encrypt the registered sensitive columns. |
| **E4-R2** | The keyring MUST be append-only so ciphertext from earlier epochs stays readable. |
| **E4-R3** | The group key MUST be minted from a cryptographic random source and held wrapped under a key derived from the app-lock credential through a memory-hard function. The key itself MUST NOT be derived from any credential, so changing a credential re-wraps rather than re-encrypts ([F3-R16](../f-platform/f3-auth-and-app-lock.md)). |
| **E4-R4** | The key MUST be released by the app-lock; a locked device MUST hold unreadable ciphertext. |
| **E4-R5** | A single registry MUST define the encrypted column set. |
| **E4-R6** | A regression guard MUST fail the build if a registered column is read or written raw. |
| **E4-R7** | Amounts, dates, account references, type enums, and the search index MUST remain plaintext, and the resulting disclosure MUST be documented. |
| **E4-R8** | Every read of an encrypted column MUST decrypt before matching, parsing, or displaying. |
| **E4-R9** | Work needing the key MUST run in a context where the key is available. |
| **E4-R10** | Work that can only run without the key MUST skip with a warning, never produce a silently wrong result. |
| **E4-R11** | Enabling encryption MUST take a backup before any conversion begins. |
| **E4-R12** | The conversion MUST run in bounded batches inside one outer transaction. |
| **E4-R13** | The first epoch MUST be staged during the transaction and moved into place only after it commits. |
| **E4-R14** | A failed conversion MUST roll back and clear the in-progress marker. |
| **E4-R15** | Conversion MUST be row-level idempotent, determined by real verification rather than by inspecting value shape. |
| **E4-R16** | With the app locked and no key available, the conversion MUST touch no row and MUST return quietly. |
| **E4-R17** | Removing a device MUST revoke its trust before minting a new epoch. |
| **E4-R18** | Rotation MUST be forward-only; earlier epochs MUST NOT be deleted. |
| **E4-R19** | A new epoch MUST be wrapped to every remaining confirmed device and enqueued for delivery. |
| **E4-R20** | Epoch delivery MUST be idempotent on epoch identity, and no key material may ever be logged. |
| **E4-R21** | A passphrase change MUST re-wrap the keyring, and a failed re-wrap MUST raise a critical alert. |
| **E4-R22** | The product's own copy MUST state honestly what at-rest encryption does and does not protect. |
| **E4-R23** | *(Withdrawn)* Unwired operating-system key custody MUST be documented as outstanding rather than implied to work. Withdrawn 2026-09-05: custody is wired on both shells, so there is no unwired custody left to document. What stands in its place — a platform store that answers and does not protect — is [F3-R37](../f-platform/f3-auth-and-app-lock.md#acceptance-criteria). |
| **E4-R24** | *(Withdrawn)* The absence of a mobile backup-exclusion bridge MUST be documented. Withdrawn 2026-09-05: the bridge exists and the mobile build applies it, so there is no absence left to document. What the requirement was for moves to `E4-R25`. |
| **E4-R25** | The mobile backup-exclusion bridge's reach MUST be documented per platform: what it excludes, whether the build applies it or a person must, and any path holding user data that it does not cover. |
| **E4-R26** | Key material the design never rotates MUST either converge across the group or have its divergence reported to the reader. Where two devices hold different values for a single-valued key and neither may adopt the other's without orphaning rows only it can read, the refusal MUST be reported once per divergence rather than once per delivery attempt, and MUST be withdrawn when the two are next found to agree. |
| **E4-R27** | Copy describing a key divergence MUST NOT name a remedy no surface reaches. Where a re-derivation exists in code that nothing a reader can operate will run, the copy MUST NOT name it; where rebuilding one device from its peer is the only recovery left, the copy MUST say so. |

> **`E4-R26` and `E4-R27` are satisfied** as of 2026-09-12. The divergence is
> raised through an alert row that is itself the idempotence key, so the report
> and the log line beside it have one cardinality between them and neither can
> be made to repeat per pass. It is withdrawn from the single branch that proves
> the split ended — a wrap arriving with a key equal to the one already held —
> because an alert only a reader can close, for a fault that fixed itself,
> teaches them to dismiss the next one unread. Both halves are pinned by test,
> the withdrawal included, and so are the two paths where the alert row itself
> cannot be written or taken down: a divergence nobody can resolve is worth
> reporting twice rather than losing to a failed write. The copy names setting
> one device up again from its peer and does not name the bulk re-derivation,
> which still has exactly one production caller behind a marker both devices
> stamp at enable time.

## Related

- [ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md) — read this alongside
- [E1 Change capture](e1-change-capture.md) · [E2 Device pairing](e2-device-pairing.md) · [E3 Transport](e3-transport.md)
- [E6-R16](e6-sync-status.md#acceptance-criteria) — the same rule about copy, for a withheld hold
- [F3 Authentication and app-lock](../f-platform/f3-auth-and-app-lock.md) — the release gate
- [F4 Backup and restore](../f-platform/f4-backup-restore.md)
- [40-quality/security.md](../../../40-quality/security.md)
