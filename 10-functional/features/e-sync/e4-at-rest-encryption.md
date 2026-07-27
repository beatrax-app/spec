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

### Known gap — operating-system key custody

Custody adapters for the platform keychains are registered but **not wired**.
Until they are, the unlocked key follows session custody on every platform, with
no operating-system-level protection. On mobile there is additionally no
backup-exclusion bridge, so the on-device database sits on a cloud-backed path —
mitigated, not eliminated, by the at-rest encryption itself.

Both are recorded as outstanding rather than described as working.

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
| Re-running the migration | Row-level idempotent by real verification. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E4-R1** | A per-user group key MUST encrypt the registered sensitive columns. |
| **E4-R2** | The keyring MUST be append-only so ciphertext from earlier epochs stays readable. |
| **E4-R3** | The key MUST be derived from the user's passphrase through a memory-hard function. |
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
| **E4-R23** | Unwired operating-system key custody MUST be documented as outstanding rather than implied to work. |
| **E4-R24** | The absence of a mobile backup-exclusion bridge MUST be documented. |

## Related

- [ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md) — read this alongside
- [E1 Change capture](e1-change-capture.md) · [E2 Device pairing](e2-device-pairing.md) · [E3 Transport](e3-transport.md)
- [F3 Authentication and app-lock](../f-platform/f3-auth-and-app-lock.md) — the release gate
- [F4 Backup and restore](../f-platform/f4-backup-restore.md)
- [40-quality/security.md](../../../40-quality/security.md)
