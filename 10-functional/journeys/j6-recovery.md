# J6 — Recovery

**Status:** Accepted

> There is no support team, no password-reset email, and no cloud copy. Every
> recovery path has to work without any of them — and where a path genuinely
> does not exist, the product has to say so rather than implying one.

---

## Precondition

Something has gone wrong.

## Forgotten password

### Recovery codes

The primary path. Ten single-use codes, generated at account creation and shown
once. The user enters a code and their username and sets a new password; the
code is consumed atomically and cannot be reused.

Every attempt writes an audit record. A failure against a username that does not
exist records **no user**, so the audit trail cannot be used to enumerate
accounts, and the mismatch message is constant either way.

### The owner resets the partner

Where a household has two accounts, the owner can force the partner to set a new
password on next sign-in. The partner cannot do the reverse.

### The command on the machine

The last resort. It runs where the database lives and requires access to that
machine.

### Where the path ends

**If the user has lost their password, lost their recovery codes, and there is
no other owner, and they cannot open a terminal — there is no route back in.**
That is the honest end of the design
([ADR-0010](../../00-overview/decisions/0010-recovery-codes-no-smtp.md)), and the
documentation states it rather than implying a rescue.

*Exercises: [F3](../features/f-platform/f3-auth-and-app-lock.md).*

## Forgotten app-lock code

Not the same as a forgotten password. The at-rest key is wrapped twice — once
under the code, once under the account password — so a forgotten code is
recovered by re-wrapping from the password path. **The data is not lost.**

Disabling the lock, or re-enabling it, mints a new key and clears every
biometric enrolment.

*Exercises: [F3](../features/f-platform/f3-auth-and-app-lock.md), [E4](../features/e-sync/e4-at-rest-encryption.md).*

## A lost or stolen device

Remove it from the devices list. Trust is revoked first, a fresh key epoch is
minted, and it is wrapped to every remaining confirmed device.

**Revocation is forward-looking.** It does not un-see what the device already
synced. If the device is unlocked in someone else's hands, the data on it is
theirs; at-rest encryption raises the cost of access to a locked one but is not
a guarantee ([ADR-0018](../../00-overview/decisions/0018-amounts-plaintext-at-rest.md)).

*Exercises: [E2](../features/e-sync/e2-device-pairing.md), [E4](../features/e-sync/e4-at-rest-encryption.md).*

## A corrupted or lost database

### Restore from a backup

The ordering is the safety contract:

1. Decrypt and integrity-check to a temporary location. A wrong passphrase or a
   corrupt backup fails **before** the live database is touched.
2. Take a pre-restore snapshot of what is about to be replaced, exempt from
   retention pruning.
3. Swap atomically.
4. Verify afterwards through the application's own connection.

Restore requires maintenance mode or an explicit override, and explicit
confirmation in a non-interactive context.

### Restore from a peer

Where another device is paired and current, a fresh install can pair to it and
receive the full history through initial sync — the operation log replays
deterministically.

That is a second, independent copy that costs nothing to maintain, and it is one
of the strongest arguments for pairing a second device at all.

*Exercises: [F4](../features/f-platform/f4-backup-restore.md), [E1](../features/e-sync/e1-change-capture.md), [E5](../features/e-sync/e5-mobile-peer.md).*

## Something is wrong but not obviously

The diagnostics command walks its probes: runtime version, store configuration,
backup freshness, search-index health. Exit codes distinguish clean, warning,
and critical, and a probe never throws.

Persistent problems surface as banner alerts ordered by severity. Alerts are
never deleted, so the history of what went wrong survives.

Inside the application, the developer console shows logs, queue state, the sync
quarantine, and a read-only query surface.

*Exercises: [F4](../features/f-platform/f4-backup-restore.md), [F5](../features/f-platform/f5-dev-console.md), [E6](../features/e-sync/e6-sync-status.md).*

## An import went wrong

It did not, in the sense that matters: preview writes nothing, and confirm is
idempotent on the fingerprint. Re-importing the same file produces no new rows.

Where a **transformation** was wrong — a mistyped transaction, a bad
categorisation — the healing passes correct it: retyping re-runs against the
completed account graph, and rule re-application is explicit and idempotent and
never overwrites a manual edit.

*Exercises: [A2](../features/a-ingestion/a2-import-wizard.md), [A3](../features/a-ingestion/a3-idempotency.md), [B3](../features/b-ledger/b3-rules-engine.md), [B5](../features/b-ledger/b5-chain-resolution.md).*

## An interrupted encryption migration

It backs up first, runs in bounded batches inside one transaction, stages the
first key epoch and only moves it into place after the transaction commits, and
rolls back on failure. With the application locked and no key available it
touches nothing and returns quietly.

*Exercises: [E4](../features/e-sync/e4-at-rest-encryption.md), [F4](../features/f-platform/f4-backup-restore.md).*

## Features exercised

[F3](../features/f-platform/f3-auth-and-app-lock.md) ·
[F4](../features/f-platform/f4-backup-restore.md) ·
[F5](../features/f-platform/f5-dev-console.md) ·
[F7](../features/f-platform/f7-data-locations.md) ·
[E1](../features/e-sync/e1-change-capture.md) ·
[E2](../features/e-sync/e2-device-pairing.md) ·
[E4](../features/e-sync/e4-at-rest-encryption.md) ·
[E6](../features/e-sync/e6-sync-status.md) ·
[A3](../features/a-ingestion/a3-idempotency.md) ·
[G2](../features/g-ux/g2-error-model.md)

## How this journey fails

| Failure | Why it matters |
|---------|----------------|
| A restore touches the live database before verifying the backup | A recovery attempt destroys what was left. |
| No pre-restore snapshot | A wrong restore is unrecoverable. |
| A forgotten app-lock code loses the data | A convenience feature becomes a data-loss event. |
| Recovery-code failures reveal whether a username exists | Account enumeration. |
| The end of the recovery path is not documented | The user discovers it at the worst possible moment. |
| Revocation is described as retroactive | A security decision made on a false premise. |
| A diagnostic probe throws | The tool for finding out what is wrong is itself broken. |

## Related

- [ADR-0010](../../00-overview/decisions/0010-recovery-codes-no-smtp.md) · [ADR-0018](../../00-overview/decisions/0018-amounts-plaintext-at-rest.md)
- [J5 Adding a device](j5-adding-a-device.md) — why a second device is also a backup
- [70-operations/runbooks.md](../../70-operations/runbooks.md)
