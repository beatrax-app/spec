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

### One registration, one secret per bank, one store per person

The credential store is addressed by **who** and by **which bank**: one
permission-protected file per user account, holding the aggregator registration
that user made once and one record per connected bank — that bank's session, its
consent expiry and its authentication host. Two banks share one registration and
hold two consents, so linking a second bank leaves the first one fetchable and on
its own schedule. The bank a consent callback is finishing travels in the
callback's own state rather than in the store, because a store that could only
hold one answer could not say which.

Every read and every write of credential material names a user. There is no
address to a credential in the store that does not, so reading another account's
connector secret is unrepresentable rather than discouraged — including from the
scheduled fetch, which takes the owner from the connection it is syncing rather
than from whoever is signed in.

Deleting an account removes that account's connector file, not only the
device-wide sweep that runs for the last account on a device.

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

A connection is either enabled or not, with a consent expiry. A user may hold
several connections at once, each with its own consent expiry, and one expiring
says nothing about the others. There is no named lifecycle beyond that.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| The authentication host resolves to loopback or a private address | Rejected before anything is persisted. |
| A secrets write fails mid-callback | The newly created connection row is deleted and any updated row is rolled back to its pre-update state. |
| Consent expired | The scheduled sync is a no-op; an alert tells the user to re-link. |
| The aggregator returns a pending transaction | Dropped. |
| The aggregator returns a booked transaction the user already imported by file | Classified as duplicate by fingerprint; no new row. |
| A second bank is linked | The first bank keeps its session, consent and schedule; both remain fetchable. |
| The user disconnects | Every connection row is cleared, not just the active one, and the reader's whole secrets file is deleted. |

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
| **A6-R20** | Connector credentials MUST be stored per connection. Linking a second bank MUST leave the first bank's session, consent and schedule intact, and both MUST be fetchable. |
| **A6-R21** | Connector credentials MUST be keyed per user, and the store MUST offer no address to credential material that does not name a user, so one account cannot read another's connector secret by any path — including the scheduled fetch and any console command. |

> **`A6-R20` and `A6-R21` were satisfied together on 2026-09-05.** They are two
> axes of one file, and splitting them would have meant migrating that file
> twice. Both were carried as accepted deferrals on the reasoning that v2.0 ships
> single-user with one bank; that reasoning was withdrawn, and closing the two
> removed the condition rather than the symptom.
>
> A store written before the keying is adopted rather than discarded: its owner
> is derived from the connection row naming the institution it holds, or from the
> only account on the installation where it names none, and a store that answers
> neither question is left exactly where it is. No shape of it forces a
> re-authorisation.

## Related

- [ADR-0020](../../../00-overview/decisions/0020-open-banking-byo-key-ais-only.md) — the constrained shape
- [ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md) · [ADR-0008](../../../00-overview/decisions/0008-multi-user-belongstouser.md)
- [A3 Idempotency](a3-idempotency.md) — why a bank connection does not duplicate
- [G1 Privacy stance](../g-ux/g1-privacy.md)
- [40-quality/security.md](../../../40-quality/security.md)
