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

**Sign-in is metered.** It is the one credential gate that leads straight to
the ledger, and it was for a long time the only one with no cap on how often it
could be tried: recovery is capped, and a wrong code escalates a backoff and
signs the user out at a hard cap. The account password now has a cap of its
own, counted per username so that an unknown one is metered exactly like a
known one and the counter answers nothing about which it was. It is a ceiling
on a machine's rate, not a lockout — the window is short enough that a reader
who has mistyped their own password waits seconds, and the whole of it is
released by a successful sign-in.

**A meter counted on a typed username can be spent by anybody who can type it.**
That is the price of counting an unknown name exactly like a known one, and it
is worth paying; what it must not cost is a household held off its own ledger by
a stranger. The correct password is not the way out. The meter is read before
the credential precisely so that a right password and a wrong one cost the same
under it, and reordering the two would answer in timing what the constant
message refuses to answer in words — so the order stands, and a second
credential opens the meter instead. A **recovery code** presented at the
sign-in screen clears that username's meter and is consumed doing it: it is the
credential the stranger does not hold. It is audited like any other recovery
attempt, it answers the same constant mismatch message, and it is counted on the
recovery sheet's own limiter rather than given a second allowance over the same
ten secrets.

The escape is shown on the refusal itself, which is what keeps it from becoming
an oracle: the refusal is decided before any account is looked up, so a username
nobody has is offered the escape exactly as one somebody has. The response to a
run of wrong codes differs from the app-lock's on purpose. There a hard cap ends
the session, because a guesser at a settings panel is already holding an
unlocked one; at the sign-in screen there is no session to end, so further
attempts are all there is to withhold.

The forced-change guard exempts the change-password page and sign-out, so a
flagged user can always either comply or leave.

### Recovery, without email

There is no outbound mail ([ADR-0010](../../../00-overview/decisions/0010-recovery-codes-no-smtp.md)),
so three paths exist:

1. **Recovery codes.** Ten single-use codes generated at account creation and
   shown **once**, drawn from a phone-readable alphabet that excludes visually
   ambiguous characters, hashed with the same scheme as passwords. Each code is
   matched and consumed atomically: a redemption spends exactly one code, and a
   code already spent cannot be spent again however many attempts are in flight.
   The comparison itself is deliberately outside that transaction — see
   [below](#a-row-lock-the-shipped-database-does-not-take). Every
   attempt — success or failure — writes an audit record, and a failure against
   an unknown username records no user, so the audit trail cannot be used to
   enumerate accounts. The mismatch message is constant regardless of whether the
   username existed.
2. **Owner resets partner**, which forces the partner to choose their own
   password next time.
3. **A command run on the machine**, as the last resort.

Codes within a batch are distinct, ensured by the generator before the write.

**A fresh sheet costs the account password.** A signed-in reader can retire their
standing sheet and mint ten new ones from settings. What comes out is a bearer
credential that outlives the session that asked for it: a later password change
ends every other session ([F3-R35](#acceptance-criteria)) and does not retire a
sheet. A confirmation is therefore not proof here — whoever holds the session
simply answers it — so regeneration takes the account password as well, the same
proof in-app account deletion takes. The command on the machine stays exempt:
access to the machine is its proof.

**So does one minted for somebody else.** The owner can set a partner's password
and mint a partner's sheet ([F3-R4](#acceptance-criteria)). Owner-only is an
*authority*, not a proof: it is a property of the session, so a session in the
wrong hands carries it whole. Both writes therefore cost the owner's own account
password — the owner's and not the partner's, because the partner's credential is
not available to the surface that replaces it (that the owner does not hold it is
the reason the surface exists), and because what is being exercised is the owner's
authority. Proof matches the authority being used, not the credential being
rewritten. Neither write is retired by the partner's own later password change:
one *set* that password, and the other issues the codes that reset it.

**And so does an account minted for a reader who does not exist yet.** The owner
can add a household member, choosing that member's first password
([F3-R3](#acceptance-criteria)). Creating is not rewriting: there is no standing
credential to prove knowledge of, and the reader who will hold the account cannot
consent, because they do not exist. What is left is the owner's authority — which
is what the rule has been the whole way down — so the owner's own password is the
proof here too. What it produces is durable in the same way the sheet is: the
owner changing their own password afterwards does not revoke the account, and no
partner is signed out and puzzled, because there is nobody yet to notice. The
**first** account on an install is a different act and stays exempt: there is no
owner then, so there is no authority to prove and nothing to prove it with
([F3-R1](#acceptance-criteria)).

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

**Key custody** is pluggable per platform, and both shells are wired: the
unlocked key goes to the operating system's key store and the session holds only
an opaque handle to it ([E4](../e-sync/e4-at-rest-encryption.md)). Where no such
store is available — a self-hosted install, a build running outside the bundle —
the adapter passes through unchanged and the key follows the session, exactly as
it always did on the web. Where a store holds the key and cannot give it back,
the caller falls back to a code unlock.

**A store that answers is not the same as a store that protects**, and one
desktop platform offers the first without the second: a Linux machine with no
keyring reachable falls back to a fixed-password store whose key is published in
its own upstream source, and that store reports itself available and does
encrypt. Custody is asked what the
machine actually gives it rather than what the bundle intended, and an
installation that has no protected store is told so instead of being told
nothing.

### The route surface

The lock screen, its verification endpoints, sign-out, and the mobile lock route
are exempt from the lock. Biometric **enrolment** is deliberately not exempt: it
needs the key that a locked session does not have.

### A row lock the shipped database does not take

`F3-R11` said "under a row lock" until 2026-09-13. SQLite has no row lock, and
Laravel's SQLite grammar compiles `lockForUpdate()` to an empty string — asked
for the SQL, the driver returns `select * from "user_recovery_codes" where …`
and nothing more. The requirement named a mechanism the shipped database does
not implement, and the call that appeared to satisfy it was decorative.

What the redemption actually costs is the reason this matters. A fixed ten
bcrypt comparisons run per attempt, so that response time cannot separate an
unknown username from a wrong code (F3-R13) — **3.5 seconds, measured.** The
connection runs `transaction_mode = IMMEDIATE`, which takes the database-wide
write lock at `BEGIN`, and both shells serve one request at a time. Holding
that transaction across the hashing therefore freezes the whole application for
three and a half seconds, and this endpoint needs no credential to reach.

So the requirement now states the property rather than a mechanism: spend
exactly one code, never spend a spent one, and keep the hashing out of the
transaction that spends it. Atomicity is carried by a compare-and-set — a
single `UPDATE … WHERE id = ? AND used_at IS NULL`, whose affected-row count is
the answer — which needs no row lock and cannot be interleaved.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Two concurrent first-launch signups | The write lock serialises; the second aborts. |
| A duplicate partner username | Surfaced as a validation error on the field. |
| A reused recovery code | Invisible; the constant mismatch message fires. |
| Probing for a partner that does not exist | Not-found, identical to the not-owner response. |
| A corrupted key wrap | Non-counting failure, plus an alert. |
| A wrong password repeatedly | Metered per username; further attempts are refused for the rest of the window. |
| A wrong password repeatedly, then a recovery code | The code clears that username's meter and is consumed; the recovery sheet's own cap bounds the guessing. |
| A stranger spending somebody else's sign-in meter | Refused for the window, and the account holder's recovery sheet opens it without waiting. |
| A wrong code repeatedly | Escalating backoff, then sign-out and an alert. |
| A biometric failing repeatedly | That credential disarms until the next code unlock. |
| A locked session receiving a biometric enrolment request | Refused — enrolment is not exempt. |
| Sign-in with the recovery wrap intact | The session unlocks with the key in hand; the code screen is skipped. |
| Sign-in where the recovery wrap cannot unwrap | The session starts locked rather than unlocked-without-a-key. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F3-R1** | Signup MUST close once any account exists, and the owner MUST be the surviving account created first; deleting the owner MUST promote the oldest remaining account rather than leave the instance unadministered ([F8-R25](f8-app-store-distribution.md)). |
| **F3-R2** | The existence check MUST be repeated inside the creating transaction, under a write lock, so concurrent signups cannot both succeed. |
| **F3-R3** | A partner MUST be created with a forced password change on first sign-in. |
| **F3-R4** | The owner MUST be able to reset the partner; the partner MUST NOT be able to reset the owner. |
| **F3-R5** | Owner-only surfaces MUST return not-found to a non-owner, never forbidden. |
| **F3-R6** | A minimum password length MUST be enforced on every write path. |
| **F3-R7** | The forced-change guard MUST exempt the change-password page and sign-out. |
| **F3-R8** | Ten single-use recovery codes MUST be generated at account creation and shown exactly once. |
| **F3-R9** | Recovery codes MUST be hashed with the same scheme as passwords and MUST be distinct within a batch. |
| **F3-R10** | The recovery alphabet MUST exclude visually ambiguous characters. |
| **F3-R11** | A recovery code MUST be matched and consumed atomically: a redemption MUST spend exactly one code, and a code already spent MUST NOT be spendable again however many attempts are in flight. The hashing that decides the match MUST NOT be held inside the consuming transaction. |
| **F3-R12** | Every recovery attempt MUST write an audit record, and a failure against an unknown username MUST record no user. |
| **F3-R13** | The recovery mismatch message MUST be constant regardless of whether the username existed. |
| **F3-R14** | A command-line reset path MUST exist as the last resort and MUST require access to the machine. |
| **F3-R15** | No first-party code may construct, queue or send mail, and the shipped bundle MUST configure no deliverable mail transport. The framework's own mailer is present and unreachable; an architecture test MUST assert both halves. |
| **F3-R16** | Enabling the app-lock MUST mint a fresh data key wrapped under both the code and the account password. |
| **F3-R17** | Enabling or disabling the lock MUST clear every biometric enrolment. |
| **F3-R18** | Changing the code MUST re-wrap the encryption keyring. |
| **F3-R19** | A wrong code MUST escalate a backoff and MUST sign the user out at a hard cap, raising an alert. |
| **F3-R20** | A corrupted key wrap MUST be a non-counting failure and MUST raise an alert. |
| **F3-R21** | A successful code unlock MUST re-arm every biometric credential; a successful biometric assertion MUST re-arm only the credential that made it, and an unlock through the recovery wrap MUST re-arm none. |
| **F3-R22** | Biometric enrolment MUST require an existing code and MUST validate both the relying party and the full origin. |
| **F3-R23** | Each biometric credential MUST have its own wrap secret. |
| **F3-R24** | A repeatedly failing biometric credential MUST disarm until the next successful code unlock. |
| **F3-R25** | The biometric signature counter MUST be updated only after a successful assertion, and a non-increasing counter MUST be rejected. |
| **F3-R26** | Idle locking MUST be decided on the server; the client MUST NOT be trusted to report activity. |
| **F3-R27** | Framework polling traffic MUST NOT count as user activity. |
| **F3-R28** | Code digits MUST NOT be held in a serialisable component property or a form input. |
| **F3-R29** | A user with no lock enabled MUST never be veiled or locked, enforced on both client and server. |
| **F3-R30** | Key custody MUST be pluggable per platform, MUST pass through where unavailable, and MUST fall back to a code unlock where it cannot recover the key. |
| **F3-R31** | Where the app-lock is enabled, sign-in MUST unlock the session where the recovery wrap succeeds and MUST start locked where it does not; where it is not enabled, sign-in MUST leave the session unlocked. |
| **F3-R32** | Biometric enrolment MUST NOT be exempt from the lock. |
| **F3-R33** | Operating-system key custody MUST be wired on desktop and mobile: the unlocked data key MUST be held by the platform key store, and the session MUST hold only an opaque handle to it. |
| **F3-R34** | The authentication path MUST equalise work on the account-not-found branch, performing and discarding a hash of equivalent cost, so response time does not distinguish a missing username from a wrong password. |
| **F3-R35** | A password change or recovery reset MUST invalidate the account's other sessions. |
| **F3-R36** | The app-lock wraps of the data key MUST use a memory-hard KDF at MODERATE limits, and the PIN MUST be six to ten digits, so a stolen database file resists offline brute-force of the wrap key. Operating-system key custody (F3-R33) now stands beside it on macOS, Windows, iOS, Android and keyring-backed Linux; where the platform offers no store that protects, this is the whole defence. |
| **F3-R37** | Custody MUST NOT fail closed where the platform key store is absent, unreachable, or does not protect what it holds. An absent or unreachable store MUST degrade to session custody; a store that answers but does not protect MAY keep the key, and MUST be reported as providing no protection at rest. In every such case the custodian MUST report the custody it is actually providing, and nothing may claim a protection it is not being given. A store that is present and refuses a write is none of these: it MUST fail closed rather than let the raw key land in a persisted session. |
| **F3-R38** | Sign-in with the account password MUST be rate-limited. The limit MUST be counted on the username as typed and normalised, so an unknown username is metered identically to a known one and the limiter reveals nothing about which it was; it MUST be enforced in the action rather than on the route, because the credential arrives on the Livewire update endpoint that route middleware does not cover; and a successful sign-in MUST clear it. The refusal MUST NOT distinguish a throttled known username from a throttled unknown one ([F3-R13](#acceptance-criteria), [F3-R34](#acceptance-criteria)). |
| **F3-R39** | Regenerating a recovery sheet for one's own account from a signed-in session MUST require the account password, not a confirmation alone. A sheet outlives the session that minted it and is not retired by a later password change, so without the password a borrowed unlocked session becomes a credential the account holder cannot revoke. The command-line path stays exempt: access to the machine is its proof ([F3-R14](#acceptance-criteria)). |
| **F3-R40** | An owner acting on a partner's credentials — setting the partner's password, or minting the partner's recovery sheet — MUST require the owner's own account password. Owner-only authority is a property of the session and is carried by a session in the wrong hands, so it cannot stand as proof of the actor. The proof MUST be the owner's rather than the partner's, because the partner's credential is not available to the surface that replaces it and because the authority being exercised is the owner's. Neither write is retired by the partner's own later password change ([F3-R4](#acceptance-criteria), [F3-R35](#acceptance-criteria)). |
| **F3-R41** | Creating an additional account from a signed-in session MUST require the creating owner's own account password. There is no credential of the new account to prove knowledge of and nobody able to consent, because the reader does not exist yet; what is being exercised is the owner's authority, so the owner is who must be proved present. The account that results is durable access the owner's own later password change does not revoke. Creating the **first** account on an install MUST stay exempt: there is no owner then, so there is no authority to prove and nothing to prove it with ([F3-R1](#acceptance-criteria), [F3-R3](#acceptance-criteria)). |
| **F3-R42** | A valid recovery code presented at sign-in MUST clear that username's sign-in meter and MUST be consumed doing so. The order in [F3-R38](#acceptance-criteria) MUST NOT change: the meter is still read before the account password, so the escape MUST be judged on the code alone and MUST NOT be reached by checking the password first. The attempt MUST be audited as a recovery attempt ([F3-R12](#acceptance-criteria)) and MUST answer the constant mismatch message ([F3-R13](#acceptance-criteria)). It MUST be counted on the recovery sheet's own limiter rather than given a second allowance over the same ten secrets, and it MUST NOT end the session at a cap the way [F3-R19](#acceptance-criteria) does, because the caller holds none. Whatever the sign-in screen shows about the escape MUST be shown for a throttled unknown username exactly as for a throttled known one, so the refusal stays indistinguishable ([F3-R13](#acceptance-criteria), [F3-R34](#acceptance-criteria)). |

> **`F3-R33` landed on 2026-09-05**, the same day the deferral it was carried
> under was reversed. "Registered but not yet wired" had been stale for months:
> both adapters were bound and both were used, and nothing held either binding
> in place, because every suite runs on the pass-through custodian and would
> have stayed green if a binding were deleted.
>
> What the wiring found is `F3-R37`. The availability probe answers *yes* on a
> Linux desktop with no keyring, so such a machine had been reporting the same
> protection as one with a keyring. Custody now asks which store the shell
> settled on, and reports *unprotected* for every answer it cannot positively
> identify.

## Related

- [ADR-0010](../../../00-overview/decisions/0010-recovery-codes-no-smtp.md) · [ADR-0008](../../../00-overview/decisions/0008-multi-user-belongstouser.md)
- [E4 At-rest encryption](../e-sync/e4-at-rest-encryption.md) — what the unlock releases
- [E5 Mobile peer](../e-sync/e5-mobile-peer.md) — the mobile unlock path
- [F1 Desktop shell](f1-desktop-shell.md) — lock on window close
- [J6 Recovery](../../journeys/j6-recovery.md)
