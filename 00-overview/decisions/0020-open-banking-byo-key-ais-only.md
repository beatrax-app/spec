# ADR-0020: Open banking is bring-your-own-key, AIS-only, and off by default

**Status:** Accepted
**Date:** 2026-07-19

## Context

File import is the recommended path and always has been: the bank already
exports CAMT.053, MT940, or CSV, and reading a file the user downloaded involves
no third party at all. But it is manual, and users asked for the automatic
version.

A live bank connection is the single biggest threat to the product's founding
promise ([ADR-0004](0004-local-only-hosting.md)). The standard shape of this
feature — the vendor holds an aggregator contract, the vendor's servers see the
user's transactions, the app fetches from the vendor — is exactly what beatrax
exists not to be.

Open banking was deferred out of two consecutive milestones for precisely this
reason before it was finally scoped in a shape that survives the constraint.

## Decision

The connector ships, and it is constrained on four axes at once.

1. **Bring your own key.** The user registers with the aggregator themselves and
   holds their own credentials. There is no beatrax-operated aggregator account,
   no shared client, and no relationship between the maintainer and the user's
   bank. The private key is generated locally and never leaves the machine.

2. **Account-information only, structurally.** The access scope is modelled as a
   fixed set of booleans covering balances, transactions, and accounts. There is
   **no payment-initiation field in the type at all** — not a flag set to false,
   but an absence. A future contributor cannot enable payment initiation by
   flipping a boolean, because there is no boolean. This is the code-level
   expression of [P7](../vision.md#p7--it-informs-it-never-transacts).

3. **Off by default, with an explicit acknowledgement.** The feature is disabled
   until the user enables it, enabling requires acknowledging a plain-language
   warning about third-party data access, and the acknowledgement is recorded
   server-side with a short time-to-live rather than trusted from the client.

4. **The data path is machine-to-aggregator, direct.** The user's machine talks
   to the aggregator; no beatrax infrastructure is in the path, because there is
   none. Fetched transactions land through the existing import-preview pipeline
   and the existing fingerprint, so a bank connection produces zero net-new
   duplicates against statements the user already imported by file.

Supporting constraints, each enforced rather than documented:

- The HTTP client is the single network boundary, with a host allow-list checked
  before any credential is attached, HTTPS only, and redirects disabled.
- Credentials live in a filesystem-permission-protected secrets file written
  atomically — never in the database, and never in a component property that
  could be serialised into a page.
- The consent callback carries a session-bound, single-use, short-lived state
  value compared in constant time.
- Only booked transactions are consumed. Pending ones are dropped, because a
  pending transaction that later books with different details would create a
  duplicate the fingerprint cannot collapse.
- Falsifiable egress and scope tests assert the constraints rather than
  describing them.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **A maintainer-operated aggregator account** | Puts the maintainer in the data path and in a regulated relationship. Contradicts the product's promise and its operating model. |
| **No connector; file import only** | The honest baseline, and the recommended path still. Lost only because the constrained shape above genuinely preserves the promise. |
| **Direct bank APIs without an aggregator** | Per-bank onboarding, per-bank certificates, per-bank review. Not tractable for a one-person project. |
| **On by default once configured** | The warning exists because the trade is real; defaulting it on makes the warning theatre. |

## Consequences

### Positive

- Users who want automatic import get it without the maintainer ever seeing a
  transaction.
- The AIS-only constraint is structural, so it cannot regress by accident.
- Imported rows deduplicate against file imports for free, because they ride the
  same fingerprint.

### Negative

- **The user does the aggregator onboarding themselves**, including key
  generation and registration. That is real friction and it is the price of the
  maintainer not being in the path.
- **Consent expires** and the user has to re-link periodically. The app raises an
  alert rather than failing silently, but it is recurring maintenance.
- **One live session, system-wide.** The connection schema is keyed per user and
  institution, but the secrets store currently holds exactly one live session —
  so linking a second bank rebinds the session while the first connection row
  remains enabled. The failure is loud rather than silent, and disconnecting
  clears all rows, but only one bank is usably connected at a time. This is a
  known limitation, not a design intent; see
  [A6](../../10-functional/features/a-ingestion/a6-open-banking.md).
- **The secrets file is not per-user keyed**, which is safe today because the
  product ships single-user and unsafe the moment a second user exists. It is a
  blocker on any real multi-user activation
  ([ADR-0008](0008-multi-user-belongstouser.md)).

### Neutral

- The aggregator is a configuration choice rather than a hard-coded vendor, so
  supporting a second one is an adapter rather than a redesign.

## Revisit if

- The single-session limitation blocks a real user with two banks, which forces
  the per-connection secret sub-record.
- A second user is activated, which forces per-user secret keying first.

## Related

- [ADR-0004](0004-local-only-hosting.md) · [ADR-0008](0008-multi-user-belongstouser.md)
- [A6 Open-banking connector](../../10-functional/features/a-ingestion/a6-open-banking.md)
- [A3 Idempotency and fingerprinting](../../10-functional/features/a-ingestion/a3-idempotency.md)
- [G1 Privacy stance](../../10-functional/features/g-ux/g1-privacy.md)
