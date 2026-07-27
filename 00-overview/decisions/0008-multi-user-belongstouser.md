# ADR-0008: Multi-user readiness via BelongsToUser and explicit user_id filters

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

beatrax shipped v1.0 as a single-user application. The intent, from the outset,
was to share the dashboard with a partner once the product was proven. That
commitment shaped the schema from the first phase: every domain table holding
user-scoped data carries a `user_id` foreign key, and models use a shared trait
that auto-scopes queries.

The temptation to defer multi-user readiness was real. A single-user app could
have skipped the column, the trait, and the authorisation checks, and shipped
faster. The cost would have arrived the moment partner-sharing landed: a
multi-month migration to backfill user IDs across every transaction, rule, and
cached projection — and a high-stakes cutover where any missed query silently
leaks one user's data to the other. For a ledger that retains all history
forever, that cost compounds with every row.

## Decision

Every user-scoped model uses a shared `BelongsToUser` trait. The trait:

- Registers a global scope applying a `user_id` filter to every query the model
  issues, resolved through an injected auth-context collaborator.
- Asserts a non-null `user_id` on save; an insert without one throws before
  reaching the database.
- Provides an explicit for-a-given-user scope for the cases that legitimately
  operate outside the current session — background jobs that run per user, for
  instance.

Raw query-builder queries against user-scoped tables — the kind that bypass
Eloquent — must include an explicit `user_id` filter. Architecture invariants
enforce this for the tables where raw queries exist, and the pattern generalises.

Every user-scoped route ships a cross-user test: with two users each holding a
record, user A's request for user B's record returns **404**, not 403, not 200,
not the wrong record. The 404 is deliberate — a 403 reveals that the record
exists.

**The global scope is a safety net, not the primary guard.** It reads the
ambient current user and is a no-op in an unauthenticated queue or CLI context,
so write paths that can run outside a request re-assert ownership against an
explicitly passed user and bypass the scope rather than trusting it. Trusting
the scope alone in background code is a latent cross-user access path.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Single-user v1, schema-migrate to multi-user later** | The migration cost grows with every row, and history is never pruned. |
| **Per-user SQLite files** | Joining across users — the partner-sharing case where a category list is shared — would have needed a manual cross-file join layer. |
| **A "current user" query macro instead of a trait** | The trait carries both the scope and the on-save assertion; a macro covers only reads. |

## Consequences

### Positive

- **Cross-user leakage is structurally hard.** A developer writing a new query
  against a user-scoped table has to consciously fight the trait to drop the
  scope. The default is correct; the unsafe path requires explicit opt-out.
- **The second-user activation is bounded.** It requires a login UI, a profile
  switcher, an owner-managed user-creation flow, and one shared file. No schema
  changes, no backfill, no cutover risk.

### Negative

- **The `users` table itself is exempt**, because owner-managed flows read
  across it. Those use an explicit owner check instead, which is a second
  mechanism to get right.
- **Relationships still need thought.** A cross-user join inside a service must
  filter explicitly; architecture tests catch the shapes they know about, and
  review has to catch the rest.
- **Some secrets are not yet per-user.** The open-banking secrets store writes a
  single global file with no per-user keying and only warns when more than one
  user exists. That gap is documented in
  [A6](../../10-functional/features/a-ingestion/a6-open-banking.md) and must
  close before any real second-user activation.

### Neutral

- Backups capture all users together. A partner who wants their own copy uses
  the per-user export path.

## Revisit if

- A real shared-household surface is scheduled, at which point the per-user
  secret-isolation gap above becomes a blocker rather than a note.

## Related

- [ADR-0010](0010-recovery-codes-no-smtp.md) — the auth posture this model lives
  inside
- [20-architecture/data-model.md](../../20-architecture/data-model.md)
- [40-quality/security.md](../../40-quality/security.md)
