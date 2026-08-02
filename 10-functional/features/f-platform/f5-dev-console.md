# F5 — Developer mode and the dev console

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

The application never phones home ([ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md)),
so when something goes wrong the only person who can diagnose it is the person
at the keyboard. The dev console is what makes that possible without a terminal.

It is also, by construction, the most dangerous surface in the product — it runs
commands, reads logs, and queries the database — which is why it is gated three
ways.

## Behaviour

### Gated, and hidden rather than forbidden

Every route requires the developer flag on the account **and** carries explicit
middleware. A non-developer gets not-found, never forbidden — the surface stays
invisible to probing rather than merely closed.

### Running commands

An allow-list registry is the authority on what may run. The spawner checks the
registry **before constructing a process**, so an unknown name never reaches the
shell. Every argument is escaped, and arguments are additionally validated
against the command's own declared rules at the controller.

That is three independent guards, deliberately.

**Schema-destructive commands are absent from the registry entirely.** Adding one
would be a visible change in review, not a runtime decision.

Destructive commands additionally require a triple gate: an advanced toggle that
resets on every sign-in, an explicit confirmation, and typing the application's
name — compared in constant time. Downstream handlers re-validate all three
rather than trusting the dispatching event.

Commands run detached and stream their output, so the request returns
immediately and a long-running command does not hold a worker. The stream
reconnects with an offset, so a dropped connection resumes rather than
restarting.

### Everything is audited

Every command writes an opening record and a closing record with its exit code
and duration. A single sanctioned writer is the only path to an audit record,
enforced by architecture test. The record shape is fixed and its action values
come from a closed set rather than free text.

A worker that dies leaves an opening record with no close, which is exactly the
signal a maintainer needs.

### Secrets never reach disk

Log output is scrubbed at three points — as it is written, as an audit excerpt is
capped, and again as it is read — in a fixed order: known credential literals
first, then bearer tokens, then token-shaped strings, then the size cap.

The set of known credential literals is cached and **invalidated whenever a
credential changes**, so a rotated credential is scrubbed from the very next
line. It is not user-scoped, because the log file and the audit database are
shared on one machine.

### Reading logs

Log reading is a bounded single-shot poll from an offset rather than a held
connection. An earlier streaming implementation held the only worker for the
duration and stalled every other request in the application — a real defect
worth recording so it is not reintroduced. Log rotation is detected by inode
comparison.

### Querying

The query panel is read-only, defended three ways: a parse-time check that the
statement is a select and that there is exactly one statement, a connection
placed in read-only mode with a wall-clock cap, and an audit record on every
successful query.

Rejections name their reason.

### Queue and system surfaces

Pending, failed, and batched jobs, with bulk retry behind a single confirmation
and bulk delete behind the full triple gate. A system snapshot, the diagnostics
panel ([F4](f4-backup-restore.md)), the sync quarantine view
([E6](../e-sync/e6-sync-status.md)), and a worker heartbeat that the boot probe
reads.

The snapshot renders effective configuration and environment, so every
secret-bearing value is masked before it reaches the page. The match is on the
key, and it covers plural forms: a retired key list is as sensitive as the key
in use, and a rule written for the singular alone does not see it. A key whose
sensitivity is uncertain is masked — an over-masked diagnostic row costs a
reader one lookup, while an under-masked one publishes a secret to anything
that can read the page, including a screenshot or a support bundle.

The heartbeat is written from the worker's own loop rather than an event
listener, because the listener form does not fire reliably under the worker.

### The palette

Development commands appear in the command palette ([G6](../g-ux/g6-keyboard.md))
only for developers, filtered **server-side as the data is produced** — not
hidden in the client. Only the safe tier appears there at all.

### The queue dashboard

Where a development-only queue dashboard is available it is registered only when
both the development flag and the package are present, and its embed carries the
appropriate framing restriction. Its imports are confined to one file, enforced
by architecture test, so no shipped code path can pull it in
([ADR-0007](../../../00-overview/decisions/0007-database-queue-driver.md)).

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A non-developer following a bookmark | Not-found. |
| A command name not in the registry | Refused before a process is constructed. |
| A required argument omitted | Refused with a clear message rather than an opaque failure. |
| A run finishing between two polls | The registry entry survives both; the closing audit record is durable. |
| A worker dying mid-run | An opening record with no close; surfaced as an orphan. |
| A credential rotated mid-output | The next line uses the new pattern; already-written lines keep the old redaction. |
| A retired key list alongside the key in use | Both are masked in the snapshot; the plural name is not a way out of the rule. |
| A benign key whose name resembles a secret | Masked. The rule errs toward masking, and the cost is one lookup. |
| A query with a trailing statement | Rejected as multiple statements; semicolons inside quoted literals pass. |
| A failed job pruned from the queue | The lifecycle log survives independently. |
| The queue dashboard package absent | Registration is skipped silently. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F5-R1** | Every development route MUST require the developer flag and MUST carry explicit middleware. |
| **F5-R2** | A non-developer MUST receive not-found, never forbidden. |
| **F5-R3** | A command allow-list registry MUST be the authority on what may run. |
| **F5-R4** | The registry MUST be checked before any process is constructed. |
| **F5-R5** | Every argument MUST be escaped, and MUST additionally be validated against the command's declared rules. |
| **F5-R6** | Schema-destructive commands MUST be absent from the registry. |
| **F5-R7** | Destructive-tier commands MUST require an advanced toggle, an explicit confirmation, and a typed application name compared in constant time. |
| **F5-R8** | The advanced toggle MUST reset on every sign-in. |
| **F5-R9** | Downstream handlers MUST re-validate all three gates rather than trusting the dispatching event. |
| **F5-R10** | Commands MUST run detached and stream output, and the stream MUST resume from an offset after a dropped connection. |
| **F5-R11** | Every command MUST write an opening and a closing audit record, the latter carrying exit code and duration. |
| **F5-R12** | A single sanctioned writer MUST be the only path to an audit record, enforced by architecture test. |
| **F5-R13** | Audit action values MUST come from a closed set, never free text. |
| **F5-R14** | Log output MUST be scrubbed as written, as an audit excerpt is capped, and again as read. |
| **F5-R15** | Scrubbing order MUST be credential literals, then bearer tokens, then token-shaped strings, then the size cap. |
| **F5-R16** | The credential-literal set MUST be invalidated whenever a credential changes. |
| **F5-R17** | Log reading MUST be a bounded single-shot poll, never a held connection. |
| **F5-R18** | Log rotation MUST be detected. |
| **F5-R19** | The query panel MUST be read-only, enforced by a parse-time check, a read-only connection with a wall-clock cap, and an audit record. |
| **F5-R20** | A rejected query MUST name its reason. |
| **F5-R21** | Bulk queue deletion MUST require the full triple gate. |
| **F5-R22** | The worker heartbeat MUST be written from the worker's own loop, not an event listener. |
| **F5-R23** | Development commands MUST be filtered out of the palette server-side for non-developers, and only the safe tier may appear at all. |
| **F5-R24** | Queue-dashboard imports MUST be confined to a single file, enforced by architecture test. |
| **F5-R25** | The queue dashboard MUST be registered only when both the development flag and the package are present. |
| **F5-R26** | The system snapshot MUST mask every secret-bearing configuration and environment value, matching singular and plural key forms alike, and MUST resolve an uncertain key toward masking. |

## Related

- [ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md) — why this exists
- [ADR-0007](../../../00-overview/decisions/0007-database-queue-driver.md)
- [F4 Backup, restore and recovery](f4-backup-restore.md) — the diagnostics panel
- [E6 Sync status and health](../e-sync/e6-sync-status.md) — the quarantine view
- [G6 Keyboard and command palette](../g-ux/g6-keyboard.md)
- [40-quality/security.md](../../../40-quality/security.md)
