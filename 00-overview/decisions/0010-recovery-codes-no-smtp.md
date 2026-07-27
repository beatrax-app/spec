# ADR-0010: Password reset via recovery codes; no SMTP-based reset

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

Multi-user partner-sharing means real authentication: usernames, hashed
passwords, sessions, logout, and the question every application eventually has
to answer — what happens when the user forgets their password?

The default framework answer is an SMTP-relayed reset email with a one-time
token. In a hosted deployment that flow is load-bearing: the provider runs SMTP,
deliverability is a known cost of doing business, and the user trusts the
address on file.

beatrax does not run SMTP. The desktop bundle ships to end users' machines; it
cannot ship a working outbound relay. Three options were on the table:

- **Wire SMTP through the user's own mail provider.** Possible only if the user
  has already granted mailbox OAuth for receipt scanning — and even then,
  sending mail is a different scope than a read-only scan. The scope upgrade is
  intrusive, the failure modes are silent (mail "sent" but spam-binned), and the
  user has to be online to use it.
- **Forfeit password reset entirely.** Forgetting the password locks the user
  out permanently. Unacceptable for a tool people use daily and forget their
  password to once a year.
- **Recovery codes, plus an owner-resets-partner path, plus a CLI fallback.** No
  outbound mail; codes generated at account creation and shown once; the
  owner-as-admin path mirrors what every team product offers; the CLI is the
  last-resort escape hatch.

## Decision

Three SMTP-free reset paths, in declining order of what the user reaches for
first:

1. **Recovery codes.** At account creation, and on demand from a rotation
   command, the system generates ten one-time-use codes, hashes them with the
   same hasher used for passwords, and displays the plaintext once for the user
   to print or paste into a password manager. Each code is one row; a successful
   reset marks it consumed through a state transition that a single state
   machine is the sole mutator of.
2. **Owner-resets-partner.** In a shared install the owner sees a force-password-change
   action against every non-owner user. It flips the partner's flag and signs
   them out; on next login the partner sets a new password from the in-app
   prompt.
3. **A reset command run on the machine where the database lives.** The
   last-resort path: rewrites the target user's password hash and sets the
   force-change flag. Owners use it if they have lost both their password and
   their recovery codes and nobody else holds owner rights on the install.

SMTP-based reset is explicitly deferred. It reopens only on evidence that the
three paths above are failing real users.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **SMTP via the user's mailbox OAuth** | The scope upgrade plus deliverability plus an online-to-reset requirement was disproportionate weight to ship alongside multi-user activation. Deferred, not rejected forever. |
| **Security questions** | Known weak against social engineering, and specifically weak against the "partner shares the install" threat model. |
| **A magic link printed on the installer** | Would need a separate physical artefact, and recovery codes already provide the same "thing you have" channel. |
| **The OS keychain for credential storage** | Three different stories across macOS, Windows, and Linux, and the codebase already hashes passwords against a single scheme. |

## Consequences

### Positive

- **No outbound mail surface to defend.** The shipped bundle exposes no SMTP
  client, no mail sends, no queued mail jobs, and an architecture invariant
  enforces that.
- Stolen-database resistance: recovery codes hash to the same scheme as
  passwords, so a database dump yields neither.

### Negative

- **Account creation gains a mandatory ritual.** The user must save ten codes
  before continuing, behind an explicit acknowledgement. This matches what
  two-factor setup already trains users to do, but it is a step.
- **The CLI fallback assumes shell access.** A partner who installed from a
  `.dmg` and has never opened a terminal cannot self-rescue if both the owner
  and their recovery codes are unavailable. The documentation has to say so
  plainly rather than implying a rescue that does not exist.

### Neutral

- The framework's password-reset-token table exists but goes unused.

## Revisit if

- Evidence accumulates that real users lose both their password and their
  recovery codes often enough to justify the SMTP surface.

## Related

- [ADR-0008](0008-multi-user-belongstouser.md)
- [F3 Authentication, app-lock and recovery](../../10-functional/features/f-platform/f3-auth-and-app-lock.md)
- [J6 Recovery](../../10-functional/journeys/j6-recovery.md)
