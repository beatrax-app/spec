# A4 — Email-receipt scanning

**Status:** Accepted · **Area:** A — Ingestion

---

## Purpose

A bank statement says `PAYPAL EUROPE 19,99`. The receipt in the user's inbox
says which Google Play subscription that was, what it cost in its original
currency, and which card funded it. Scanning the inbox is how Beatrax turns an
anonymous line into a labelled one.

This feature owns the connection and the fetch. What happens to a fetched
message is [A5](a5-receipt-matching.md).

## Behaviour

### Provider APIs only; never IMAP

Only Gmail and Microsoft Graph are supported, through their own APIs with the
user's own OAuth grant. IMAP is not supported at all — the language's bundled
IMAP extension was unbundled and its underlying library has been unmaintained
for two decades, and the project declines to depend on either it or the
libraries that wrap it.

iCloud Mail is out of scope: there is no supported API.

### The grant is the user's, and it stays local

The authorisation flow runs on the user's machine with a loopback redirect, so
the callback never leaves it. Tokens are written to a
filesystem-permission-protected secrets file, never to the database, and never
into any component property that could be serialised into a page.

The authorisation request carries a state value that is single-use,
session-bound, age-limited, and compared in constant time. A mismatch produces a
generic error that does not reveal whose state it was.

The redirect URI is computed on the server; a value supplied in the query string
is never trusted.

### Three scans, three jobs

| Scan | Cadence | What it does |
|------|---------|--------------|
| **Incremental** | Roughly every fifteen minutes per inbox | Walks the provider's change cursor and fetches anything new. |
| **Backfill** | User-triggered, over a chosen window | Walks history to establish the initial corpus. |
| **Discovery** | Daily per user | A broad, metadata-only keyword sweep that finds senders the user might want to promote. **It never stores message bodies.** |

Jobs are unique per inbox, so a scheduled tick and a manual trigger collapse
into one run rather than racing.

### Messages are stored deliberately, and only where needed

An incremental or backfill scan writes each fetched message's raw bytes to a
per-user, per-inbox path with owner-only permissions, then records its metadata.
The blob is written before the metadata row, and a failed metadata write removes
the blob, so an orphan is not left behind.

Discovery stores nothing but sender metadata. The user reviews discovered
senders and promotes the ones they want before any body is fetched.

### Cursors, and what happens when they expire

Each provider has its own change-cursor model, and each expires. When a cursor
is rejected, the scan falls back to a date-bounded walk anchored at a
deterministic point behind the last successful scan, with a hard cap on how many
messages that fallback may pull.

For the Microsoft provider the baseline is taken in two phases with the delta
anchor set to a timestamp captured *before* the walk began, so messages arriving
during a multi-hour backfill are not skipped.

### Rate limits and consent failures are distinct

A rate-limited response moves the inbox to a rate-limited state, records the
attempt, and retries on an escalating schedule that honours the provider's
suggested delay. A consent failure — a revoked or invalid grant — moves the
inbox to a re-authorisation state and raises a single de-duplicated alert. The
alert never contains token material.

Everything else is an error state that a retry can leave.

### Outbound requests are host-checked

Every request the mail clients make is validated against an allow-list before
credentials are attached — including the URLs the provider itself supplies for
pagination. A malformed response substituting an attacker-controlled host would
otherwise receive a valid bearer token.

### The statement-ready nudge

A metadata-only rule watches for a card issuer's "your statement is ready"
message and raises a reminder. It reads **only sender and subject** — never the
message body — and matches the sender domain by exact equality so a lookalike
domain cannot trigger it.

## States

An inbox's scan state moves through:

| State | Meaning |
|-------|---------|
| `idle` | Nothing running. |
| `discovering` | Metadata-only sweep in progress. |
| `scanning` | Fetching messages. |
| `backfilling` | Historical walk in progress. |
| `rate_limited` | Backing off; retries scheduled. |
| `needs_reauth` | The grant failed. Terminal until the user re-authorises. |
| `error` | Something else failed. Recoverable to idle. |

A single state machine is the only thing that may write these states, the retry
counter, or the cursor columns. Transitions take a row lock and set a busy
timeout so concurrent workers serialise rather than clobber.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A callback arrives with no matching state row | Rejected with a generic error. |
| A new inbox is added while another is scanning | Different lock keys; no conflict. |
| A worker dies mid-scan | The failure hook only fires on final retry exhaustion, so a hard crash can leave the state as scanning. The next scheduled run recovers it. |
| Token refresh fails once, then succeeds | No alert — the de-duplication guard sees no previously open alert. |
| The user revokes consent at the provider | The next refresh raises a re-consent condition and the inbox moves to re-authorisation. |
| The same message is fetched twice | Idempotent: the provider message identifier is the deduplication key. |
| An inbox is removed | Orphaned message blobs are reaped by a cleanup pass. |
| A discovered sender is promoted while a scan is reading the list | The promotion runs in its own transaction. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **A4-R1** | Only provider APIs MUST be used. No IMAP code path may exist anywhere in the product. |
| **A4-R2** | OAuth tokens MUST be stored in a filesystem-permission-protected secrets file, never in the database. |
| **A4-R3** | Secrets MUST NOT appear in any component property that could be serialised into a rendered page. |
| **A4-R4** | The authorisation flow MUST use a loopback redirect computed on the server; a caller-supplied redirect URI MUST NOT be trusted. |
| **A4-R5** | The authorisation state value MUST be single-use, bound to the requesting session, age-limited, and compared in constant time. |
| **A4-R6** | A state mismatch MUST produce a generic error that does not reveal which user the state belonged to. |
| **A4-R7** | A single state machine MUST be the sole writer of inbox scan state, retry counters, and cursor columns. |
| **A4-R8** | Scan jobs MUST be unique per inbox so a scheduled tick and a manual trigger cannot run concurrently. |
| **A4-R9** | Message bytes MUST be written with owner-only permissions. |
| **A4-R10** | A failed metadata write MUST remove the already-written message blob. |
| **A4-R11** | The discovery scan MUST NOT store message bodies; only sender metadata. |
| **A4-R12** | An expired cursor MUST trigger a date-bounded fallback walk with an explicit hard cap on messages fetched. |
| **A4-R13** | The Microsoft baseline MUST be anchored to a timestamp captured before the historical walk begins. |
| **A4-R14** | A rate-limited response MUST move the inbox to a rate-limited state and retry on an escalating schedule honouring the provider's suggested delay. |
| **A4-R15** | A consent failure MUST move the inbox to a re-authorisation state and raise exactly one de-duplicated alert. |
| **A4-R16** | No alert or log line may contain token material. |
| **A4-R17** | Every outbound request MUST be validated against a host allow-list before credentials are attached, including provider-supplied pagination URLs. |
| **A4-R18** | Re-fetching a message already recorded MUST be a no-op. |
| **A4-R19** | The statement-ready nudge MUST read only sender and subject, and MUST match the sender domain by exact equality. |
| **A4-R20** | Removing an inbox MUST cause its stored message blobs to be reaped. |
| **A4-R21** | Cross-user reads and writes of inboxes or secrets MUST return not-found, never forbidden. |

## Related

- [A5 Receipt matching and chain hints](a5-receipt-matching.md) — what happens next
- [A3 Idempotency](a3-idempotency.md) — receipts are the main enrichment source
- [G1 Privacy stance](../g-ux/g1-privacy.md) — this is one of the four optional outbound surfaces
- [ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md)
- [40-quality/security.md](../../../40-quality/security.md)
