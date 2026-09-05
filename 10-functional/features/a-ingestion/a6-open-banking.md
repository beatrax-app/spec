# A6 — Open-banking import connector

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

An optional, off-by-default connector that fetches booked transactions and
balances from a bank through a PSD2 aggregator the **user** holds credentials
with — so the automatic-import convenience is available without the maintainer
ever being in the data path.

File import remains the recommended path. This exists for people who would
rather not download a statement every month, and it is constrained hard enough
that turning it on does not contradict the product's promise. The full
reasoning is [ADR-0020](../../../00-overview/decisions/0020-open-banking-byo-key-ais-only.md).

## Behaviour

### Off by default, behind an explicit acknowledgement

The connector is disabled until the user enables it. Enabling requires reading
and acknowledging a plain-language warning that third-party data access is
involved. The acknowledgement is recorded on the server with a short lifetime —
it is never a client-supplied flag, because a client-supplied flag is not an
acknowledgement.

### Bring your own key

The user registers with the aggregator themselves. The private key is generated
locally, written to a filesystem-permission-protected secrets file, and never
leaves the machine. There is no maintainer-operated aggregator account and no
shared client.

Secrets are written atomically — temporary file, flush, permission, rename — so
a crash mid-write cannot leave a partial credential. They are never stored in
the database.

### Account information only, structurally

The access scope covers balances, transactions, and accounts. **There is no
payment-initiation field in the scope type at all** — not a flag set false, but
an absence. Enabling payment initiation would require adding the capability, not
flipping a setting.

### The network boundary is one place, and it is checked

All aggregator traffic goes through a single client which:

- enforces HTTPS,
- checks the host against an allow-list **before** attaching any credential,
- refuses to follow redirects,
- rejects a strong-customer-authentication host that resolves to a loopback or
  private address.

### Consent, and what happens when it lapses

The consent flow uses a loopback callback with a state value that is
session-bound, single-use, constant-time compared, and rejected after a short
age. Consent has an expiry; when it lapses the app raises an alert and the sync
becomes a no-op rather than failing silently. Re-linking is a first-class
action.

### What is fetched, and how it lands

Only **booked** transactions are consumed. Pending ones are dropped: a pending
transaction that later books with different details would create a duplicate the
fingerprint cannot collapse.

Fetched rows are shaped to match the file-import equivalent field for field,
including the date normalisation, and land through the same preview pipeline and
the same fingerprint ([A3](a3-idempotency.md)). **A connected bank produces zero
net-new duplicates against statements the user already imported as files.**

Deduplication uses a caller-supplied idempotency key rather than a file hash,
because there is no file.

### Sync succeeds or it does not

The last-successful-sync timestamp is written only on success — never in a
cleanup path — so a failed sync cannot make the surface look healthy. An
authorisation failure raises a re-consent alert.

### Guided card import

For the card issuer, where no aggregator connection exists, the connector
surfaces a guided file-import affordance and the statement-ready nudge from
[A4](a4-email-scanning.md) rather than pretending a connection is possible.

## States

A connection is either enabled or not, with a consent expiry. There is no named
lifecycle beyond that.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| The authentication host resolves to loopback or a private address | Rejected before anything is persisted. |
| A secrets write fails mid-callback | The newly created connection row is deleted and any updated row is rolled back to its pre-update state. |
| Consent expired | The scheduled sync is a no-op; an alert tells the user to re-link. |
| The aggregator returns a pending transaction | Dropped. |
| The aggregator returns a booked transaction the user already imported by file | Classified as duplicate by fingerprint; no new row. |
| The user disconnects | Every connection row is cleared, not just the active one. |

### Known limitation — one live session at a time

The connection records are keyed per user and institution, but the secrets store
currently holds exactly **one** live aggregator session. Linking a second bank
rebinds the session to the second bank while the first connection row remains
enabled and schedulable.

The failure is loud rather than silent — the fetch path fails with a clear
message rather than fetching the wrong bank — and disconnecting clears every
row. But **only one bank is usably connected at a time.** The real fix is a
per-connection secret sub-record or a single-active-connection guard, and it is
outstanding.

### Known limitation — the secrets file is not per-user keyed

The secrets file is global to the installation with no per-user keying. The
runtime logs a warning when more than one user exists; it does not fail closed.
This is safe while the product ships single-user and is a **blocker on any real
second-user activation** — see
[ADR-0008](../../../00-overview/decisions/0008-multi-user-belongstouser.md).

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A6-R1** | The connector MUST be disabled by default. |
| **A6-R2** | Enabling MUST require an explicit acknowledgement of a plain-language third-party-data warning. |
| **A6-R3** | The acknowledgement MUST be recorded server-side with a bounded lifetime; a client-supplied flag MUST NOT be trusted. |
| **A6-R4** | The user MUST supply their own aggregator credentials; no shared or maintainer-operated account may exist. |
| **A6-R5** | The private key MUST be generated locally and MUST NOT leave the machine. |
| **A6-R6** | Credentials MUST be stored in a filesystem-permission-protected file written atomically, never in the database. |
| **A6-R7** | The access scope type MUST NOT contain a payment-initiation field. |
| **A6-R8** | All aggregator traffic MUST pass through a single client that enforces HTTPS, checks the host against an allow-list before attaching credentials, and refuses redirects. |
| **A6-R9** | An authentication host resolving to a loopback or private address MUST be rejected before persistence. |
| **A6-R10** | The consent callback state MUST be session-bound, single-use, constant-time compared, and age-limited. |
| **A6-R11** | Only booked transactions MUST be consumed; pending transactions MUST be dropped. |
| **A6-R12** | Fetched rows MUST land through the same preview pipeline and the same fingerprint as file imports. |
| **A6-R13** | A connected bank MUST produce zero net-new duplicates against statements already imported as files. |
| **A6-R14** | Deduplication MUST use a caller-supplied idempotency key. |
| **A6-R15** | The last-successful-sync timestamp MUST be written only on success. |
| **A6-R16** | Consent expiry MUST make the scheduled sync a no-op and MUST raise a user-visible alert. |
| **A6-R17** | Disconnecting MUST clear every connection row for the user, not only the active one. |
| **A6-R18** | Egress and scope constraints MUST be covered by tests that fail if the constraint regresses. |
| **A6-R19** | Where no aggregator connection is possible for a source, the surface MUST offer a guided file-import path rather than implying a connection exists. |
| **A6-R20** | *(Open)* Per-connection credential storage MUST exist before a second bank can be usably connected. Not yet satisfied — see [Known limitation](#known-limitation--one-live-session-at-a-time). |
| **A6-R21** | *(Open)* Per-user credential keying MUST exist before a second user account is activated. Not yet satisfied — see [Known limitation](#known-limitation--the-secrets-file-is-not-per-user-keyed). |

> `A6-R20` and `A6-R21` are stated as requirements because they are the
> conditions under which the feature is correct, and recorded as unsatisfied
> because they are.
>
> **They are no longer deferred.** Both were carried as accepted deferrals on the
> reasoning that v2.0 ships single-user with one bank, which made each a
> documented limitation rather than a defect. That reasoning is withdrawn: both
> are [in v2.0 scope and being built](../../../00-overview/roadmap.md#3--the-three-latent-risks-no-longer-deferred).
> Single-user and single-bank were the *condition* the deferral rested on, and
> closing these two removes the condition rather than the symptom.
>
> The requirements stay marked *(Open)* and the two "Known limitation" sections
> above stay as written, because the code is not merged. What changed is the
> schedule, not the state — and the state is what those sections describe.

## Related

- [ADR-0020](../../../00-overview/decisions/0020-open-banking-byo-key-ais-only.md) — the constrained shape
- [ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md) · [ADR-0008](../../../00-overview/decisions/0008-multi-user-belongstouser.md)
- [A3 Idempotency](a3-idempotency.md) — why a bank connection does not duplicate
- [G1 Privacy stance](../g-ux/g1-privacy.md)
- [40-quality/security.md](../../../40-quality/security.md)
