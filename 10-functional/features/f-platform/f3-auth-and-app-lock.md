# F3 — Authentication, app-lock and recovery

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

Two separate protections, deliberately separate:

- **Authentication** — who you are. A username and password, plus recovery when
  that fails.
- **The app-lock** — a fast gate in front of the data, independent of login, and
  the thing that releases the at-rest encryption key
  ([E4](../e-sync/e4-at-rest-encryption.md)).

Conflating them would mean either logging out to lock the screen, or a lock that
does not actually protect anything.

## Behaviour

### Authentication

The first account created is the **owner**. Signup then closes: the route
returns not-found once any account exists, and the check is repeated inside the
creating transaction so two concurrent first-launch signups cannot both create
an owner. Under the concurrency semantics of the store, the transaction is
promoted to a write lock before the existence check, because two readers would
otherwise both see an empty table.

The owner can add a partner. A partner is created with an initial password and a
forced change on first sign-in. **The owner can reset the partner; the partner
cannot reset the owner.** Every owner-only surface returns not-found to a
non-owner, never forbidden, so the surface stays hidden from probing.

Passwords have a minimum length enforced on every write path.

The forced-change guard exempts the change-password page and sign-out, so a
flagged user can always either comply or leave.

### Recovery, without email

There is no outbound mail ([ADR-0010](../../../00-overview/decisions/0010-recovery-codes-no-smtp.md)),
so three paths exist:

1. **Recovery codes.** Ten single-use codes generated at account creation and
   shown **once**, drawn from a phone-readable alphabet that excludes visually
   ambiguous characters, hashed with the same scheme as passwords. Each code is
   matched and consumed atomically inside one transaction under a row lock. Every
   attempt — success or failure — writes an audit record, and a failure against
   an unknown username records no user, so the audit trail cannot be used to
   enumerate accounts. The mismatch message is constant regardless of whether the
   username existed.
2. **Owner resets partner**, which forces the partner to choose their own
   password next time.
3. **A command run on the machine**, as the last resort.

Codes within a batch are distinct, ensured by the generator before the write.

### The app-lock

A numeric code, and optionally a device biometric, gating the application
independently of login.

**How the key is protected.** Enabling the lock mints a fresh random data key and
wraps it twice under one derivation salt: once under the code for daily use, once
under the account password as the recovery path — so a forgotten code can be
recovered by re-wrapping rather than by losing the data.

Enabling mints a **new** key each time, which invalidates every existing
biometric enrolment; enabling and disabling both clear enrolments.

**What confirms what.** Enabling requires the account password. Disabling and
changing require the current code. De-enrolling a biometric requires the current
code. Recovering a forgotten code requires the account password. Changing the
idle preset requires nothing.

**Changing the code re-wraps** the encryption keyring, best-effort, so the
at-rest key survives.

**Failures back off.** A wrong code increments a counter and escalates the delay;
a hard cap signs the user out and raises an alert. A corrupted wrap is a
**non-counting** failure — it is not the user's fault — and also raises an alert.
A successful unlock re-arms every biometric credential.

**Biometrics** enrol only once a code exists, validate both the relying party
and the full origin, and give each device its own wrap secret rather than
sharing the code's. A credential that fails repeatedly disarms until the next
successful code unlock. The signature counter is updated only after a successful
assertion and a non-increasing counter is rejected, which is the replay defence.

**Idle locking is server-authoritative.** The server compares the last activity
timestamp; the client cannot decide it is still active. Polling traffic must not
count as activity, so the heartbeat is a distinct request rather than a side
effect of the framework's own polling. Backgrounding starts a short grace timer
before locking.

**The code is never in an input field.** Digits accumulate in transient client
state and are never a serialisable component property, so they cannot appear in
a rendered snapshot.

**A user with no lock enabled is never veiled and never locked**, enforced on
both the client and the server.

**Key custody** is pluggable per platform so a bundle can hold the unlocked key
in an operating-system protected store. Where that is unavailable the adapter
passes through unchanged, and where it cannot recover the key the caller falls
back to a code unlock. The desktop and mobile adapters are **registered but not
yet wired** ([E4](../e-sync/e4-at-rest-encryption.md)) — the unlocked key
currently follows session custody everywhere.

### The route surface

The lock screen, its verification endpoints, sign-out, and the mobile lock route
are exempt from the lock. Biometric **enrolment** is deliberately not exempt: it
needs the key that a locked session does not have.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Two concurrent first-launch signups | The write lock serialises; the second aborts. |
| A duplicate partner username | Surfaced as a validation error on the field. |
| A reused recovery code | Invisible; the constant mismatch message fires. |
| Probing for a partner that does not exist | Not-found, identical to the not-owner response. |
| A corrupted key wrap | Non-counting failure, plus an alert. |
| A wrong code repeatedly | Escalating backoff, then sign-out and an alert. |
| A biometric failing repeatedly | That credential disarms until the next code unlock. |
| A locked session receiving a biometric enrolment request | Refused — enrolment is not exempt. |
| Sign-in with the recovery wrap intact | The session unlocks with the key in hand; the code screen is skipped. |
| Sign-in where the recovery wrap cannot unwrap | The session starts locked rather than unlocked-without-a-key. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F3-R1** | The first account created MUST be the owner, and signup MUST close once any account exists. |
| **F3-R2** | The existence check MUST be repeated inside the creating transaction, under a write lock, so concurrent signups cannot both succeed. |
| **F3-R3** | A partner MUST be created with a forced password change on first sign-in. |
| **F3-R4** | The owner MUST be able to reset the partner; the partner MUST NOT be able to reset the owner. |
| **F3-R5** | Owner-only surfaces MUST return not-found to a non-owner, never forbidden. |
| **F3-R6** | A minimum password length MUST be enforced on every write path. |
| **F3-R7** | The forced-change guard MUST exempt the change-password page and sign-out. |
| **F3-R8** | Ten single-use recovery codes MUST be generated at account creation and shown exactly once. |
| **F3-R9** | Recovery codes MUST be hashed with the same scheme as passwords and MUST be distinct within a batch. |
| **F3-R10** | The recovery alphabet MUST exclude visually ambiguous characters. |
| **F3-R11** | A recovery code MUST be matched and consumed atomically under a row lock. |
| **F3-R12** | Every recovery attempt MUST write an audit record, and a failure against an unknown username MUST record no user. |
| **F3-R13** | The recovery mismatch message MUST be constant regardless of whether the username existed. |
| **F3-R14** | A command-line reset path MUST exist as the last resort and MUST require access to the machine. |
| **F3-R15** | No outbound mail capability may exist in the shipped bundle. |
| **F3-R16** | Enabling the app-lock MUST mint a fresh data key wrapped under both the code and the account password. |
| **F3-R17** | Enabling or disabling the lock MUST clear every biometric enrolment. |
| **F3-R18** | Changing the code MUST re-wrap the encryption keyring. |
| **F3-R19** | A wrong code MUST escalate a backoff and MUST sign the user out at a hard cap, raising an alert. |
| **F3-R20** | A corrupted key wrap MUST be a non-counting failure and MUST raise an alert. |
| **F3-R21** | A successful unlock MUST re-arm every biometric credential. |
| **F3-R22** | Biometric enrolment MUST require an existing code and MUST validate both the relying party and the full origin. |
| **F3-R23** | Each biometric credential MUST have its own wrap secret. |
| **F3-R24** | A repeatedly failing biometric credential MUST disarm until the next successful code unlock. |
| **F3-R25** | The biometric signature counter MUST be updated only after a successful assertion, and a non-increasing counter MUST be rejected. |
| **F3-R26** | Idle locking MUST be decided on the server; the client MUST NOT be trusted to report activity. |
| **F3-R27** | Framework polling traffic MUST NOT count as user activity. |
| **F3-R28** | Code digits MUST NOT be held in a serialisable component property or a form input. |
| **F3-R29** | A user with no lock enabled MUST never be veiled or locked, enforced on both client and server. |
| **F3-R30** | Key custody MUST be pluggable per platform, MUST pass through where unavailable, and MUST fall back to a code unlock where it cannot recover the key. |
| **F3-R31** | Sign-in MUST unlock the session where the recovery wrap succeeds, and MUST start locked where it does not. |
| **F3-R32** | Biometric enrolment MUST NOT be exempt from the lock. |
| **F3-R33** | *(Open)* Operating-system key custody MUST be wired on desktop and mobile. Registered but not yet wired. |

## Related

- [ADR-0010](../../../00-overview/decisions/0010-recovery-codes-no-smtp.md) · [ADR-0008](../../../00-overview/decisions/0008-multi-user-belongstouser.md)
- [E4 At-rest encryption](../e-sync/e4-at-rest-encryption.md) — what the unlock releases
- [E5 Mobile peer](../e-sync/e5-mobile-peer.md) — the mobile unlock path
- [F1 Desktop shell](f1-desktop-shell.md) — lock on window close
- [J6 Recovery](../../journeys/j6-recovery.md)
