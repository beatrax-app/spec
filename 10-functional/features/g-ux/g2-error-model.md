# G2 — Error and remedy model

**Status:** Accepted · **Area:** G — Cross-cutting UX

---

## Purpose

There is no support channel. There is no crash report. When something fails, the
message on the screen is the entire help the user gets — so it has to say what
happened, why, and what to do next.

This is not a screen. It is a property every other feature has to exhibit.

## Behaviour

### Every error names a remedy

A message that says only what went wrong is half an error. Every user-facing
failure states the situation and the next action, in that order.

| Bad | Good |
|-----|------|
| "Import failed." | "This file is a PayPal export, but the bank format was selected. Choose PayPal CSV and try again." |
| "Invalid amount." | "Amounts must sum exactly to the transaction total. 12.40 is still unallocated." |
| "Sync error." | "This device has not synced since Tuesday. Check that the other device is awake and on the same network, or configure a relay." |

### Failure is typed, not stringly

Callers branch on the kind of failure, never on message text. A message can then
be rewritten without breaking behaviour, and a caller cannot accidentally match
two unrelated failures.

### Diagnostics and messages are separate

The user gets plain language. The full detail — stack trace, file, stage, row
index — goes to the local log, where the developer console
([F5](../f-platform/f5-dev-console.md)) can read it. Showing a stack trace to
someone reconciling their bank account helps nobody.

### One bad item never kills a batch

A row that fails becomes an error row and the batch continues
([A2](../a-ingestion/a2-import-wizard.md)). A rule that throws leaves its
transaction uncategorised ([B2](../b-ledger/b2-categorisation.md)). An
operation the merge layer refuses is quarantined
([E1](../e-sync/e1-change-capture.md)). A trigger that fails does not break the
event that caused it ([C8](../c-insight/c8-notifications.md)).

The pattern is consistent: degrade the item, not the operation.

### Silence is a decision, and it is documented

Some failures are deliberately silent:

- A file the operating system offers that fails the intake gate is logged and
  dropped, because returning an error would betray the application's presence
  ([F1](../f-platform/f1-desktop-shell.md)).
- A receipt matching no matcher is a miss, not an error
  ([A5](../a-ingestion/a5-receipt-matching.md)).
- A cross-user lookup returns not-found, never forbidden — forbidden confirms the
  record exists.
- A background lifecycle action against a missing record no-ops.

Each of these is stated in its own feature rather than left as an absence.

### Loud where loud is right

The other half of the same discipline:

- A missing money column raises rather than returning zero.
- Mixing currencies raises rather than producing a total.
- A missing exchange rate in a fold raises rather than leaking a foreign figure.
- An index write failure rolls back its import chunk.
- A schema mismatch on a decoded payload fails loudly.
- A failed key re-wrap raises a critical alert.

The rule: **fail silently where the failure is information, fail loudly where
the failure would corrupt a number.**

### Recoverable states are recoverable

Any state a user can be interrupted into has a documented way out: an
interrupted import re-confirms idempotently, an interrupted encryption migration
rolls back, an inbox in an error state returns to idle, a stuck resolver run is
visible and re-dispatchable.

### Alerts, not modals

Persistent problems surface as banner alerts ordered by severity
([F4](../f-platform/f4-backup-restore.md)) rather than as modals that block
work. A backup that is overdue does not need to interrupt somebody mid-
reconciliation.

Alerts are never deleted; acknowledgement is a one-way stamp, so the history of
what went wrong survives.

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G2-R1** | Every user-facing failure MUST state what happened and what to do next. |
| **G2-R2** | Failures MUST be typed; callers MUST NOT branch on message text. |
| **G2-R3** | Full diagnostics MUST go to the local log only and MUST NOT be shown to the user. |
| **G2-R4** | A failing item in a batch MUST degrade that item, never the batch. |
| **G2-R5** | Every deliberate silence MUST be documented in the feature that defines it. |
| **G2-R6** | A cross-user lookup MUST return not-found, never forbidden. |
| **G2-R7** | A failure that would corrupt a monetary figure MUST raise rather than degrade. |
| **G2-R8** | A missing money value MUST raise rather than defaulting to zero. |
| **G2-R9** | Mixing currencies MUST raise rather than producing a total. |
| **G2-R10** | Every interruptible operation MUST have a documented recovery path. |
| **G2-R11** | Persistent problems MUST surface as banner alerts rather than blocking modals. |
| **G2-R12** | Alerts MUST be ordered by severity and MUST never be deleted. |
| **G2-R13** | Error messages MUST NOT contain credential material, and log output MUST be scrubbed. |

## Related

- [G5 Plain language and in-product help](g5-plain-language.md)
- [A2 Import preview and confirm](../a-ingestion/a2-import-wizard.md) — the per-row error model
- [E1 Change capture](../e-sync/e1-change-capture.md) — quarantine as degradation
- [F4 Backup and recovery](../f-platform/f4-backup-restore.md) · [F5 Developer mode](../f-platform/f5-dev-console.md)
