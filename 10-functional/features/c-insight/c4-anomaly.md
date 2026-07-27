# C4 — Unusual-charge alerts

**Status:** Accepted · **Area:** C — Insight and alerts

---

## Purpose

Drift alerts ([C3](c3-drift-alerts.md)) watch known recurring commitments. This
feature watches everything else: a charge much larger than usual for that
merchant, a large charge at a merchant never seen before, or an apparent
duplicate inside a short window.

It is the closest beatrax comes to fraud detection, and it is deliberately
framed as "this looks unusual" rather than "this is wrong" — because the user
knows things the statistics do not.

## Behaviour

### One alert per transaction, with every reason

A transaction produces **at most one** alert, carrying every reason that
tripped. Three detectors run and their reasons aggregate in a canonical order:

**Large versus typical.** A robust median-and-deviation score over a rolling
window of that counterparty's history. Robust statistics rather than mean and
standard deviation, because a small sample with an outlier is exactly the shape
mean-based statistics handle worst. Where the merchant has too few prior
observations, it falls back to a percentile over the category. Where both are
too thin, it declines to fire.

**Large at a new merchant.** Fires only when there is no prior transaction for
the counterparty **and** the charge is large against the user's own overall
distribution for that direction and currency. A first charge that is ordinary in
size is not interesting.

**Apparent duplicate.** An earlier sibling with the same counterparty, exact
amount and currency, and direction, inside a short backward window. Backward-only
with a deterministic tie-break, so exactly one alert fires regardless of the
order in which the two are evaluated. It does not fire when both sides belong to
an approved recurring series — a monthly charge that arrives twice because the
period boundary moved is not a duplicate.

A minimum-amount floor gates all three, so small charges never generate noise.

### Sensitivity is the user's

Both the sensitivity and the minimum floor are user settings. Nothing about
"unusual" is universal.

### Marking something as expected

"Mark as expected" creates a **narrow, server-computed** suppression rule: this
counterparty, this detector, this direction, this currency, within a band around
the observed amount. The band is computed on the server; a client-supplied band
is never trusted.

Suppression is applied **before** the alert is written, so a suppressed reason
never produces a row at all. If every reason is suppressed, nothing is written.

Suppression rules are visible and removable in settings. Removing one from
settings deletes that rule and leaves the alert dismissed. Undoing from the alert
itself deletes every rule that alert created **and re-opens the alert** — the
only path that moves an alert backwards.

A synthetic "large" reason contributed by the new-merchant detector is excluded
from suppression matching, so a per-merchant band cannot mute a new merchant's
own signal.

### Where it runs

Detection is queued so it never slows an import. A one-time full-history
backfill runs on first activation, claimed atomically so a crash mid-walk does
not cause it to re-run. An hourly sweep is the durable safety net for anything
the reactive path missed, and the same sweep revives expired snoozes.

Concurrent evaluation paths for the same transaction collapse on a uniqueness
key.

### The surface

Alerts appear on the same page as drift, behind a type switch, with the same
lifecycle tabs. Each shows its reason chips. There is a dashboard tile and a
navigation badge.

## States

The lifecycle mirrors drift, with one difference: **dismissed can return to
open**, which is what makes the undo work. Acknowledged is terminal. There is no
general escape hatch — idempotent no-ops live in the actions, not in the state
machine.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Thin history for both merchant and category | The detector declines; nothing fires. |
| A duplicate pair inside an approved recurring series | Does not fire. |
| Concurrent reactive, backfill, and sweep evaluation | Collapse on a uniqueness key. |
| A backfill crash mid-walk | The claim is already stamped, so it does not re-run; the hourly sweep is the backstop. |
| An alert with only duplicate or new-merchant reasons | The suppression band falls back to the alert transaction's own amount, since there is no per-merchant typical. |
| Two reasons where one is suppressed | The alert is written with the surviving reason only. |
| Every reason suppressed | No row is written. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **C4-R1** | A transaction MUST produce at most one alert, aggregating every tripped reason. |
| **C4-R2** | Reasons MUST aggregate in a canonical order. |
| **C4-R3** | The large-versus-typical detector MUST use robust statistics, not mean and standard deviation. |
| **C4-R4** | Where a merchant has too few observations, the detector MUST fall back to a category-level comparison, and MUST decline where both are too thin. |
| **C4-R5** | The new-merchant detector MUST require both no prior transaction for the counterparty and a large amount against the user's own distribution. |
| **C4-R6** | The duplicate detector MUST look backward only, with a deterministic tie-break, so exactly one alert fires per pair. |
| **C4-R7** | The duplicate detector MUST NOT fire when both sides belong to an approved recurring series. |
| **C4-R8** | A minimum-amount floor MUST gate every detector, and MUST be user-configurable. |
| **C4-R9** | Sensitivity MUST be user-configurable. |
| **C4-R10** | Suppression bands MUST be computed on the server; a client-supplied band MUST NOT be trusted. |
| **C4-R11** | Suppression MUST be evaluated before insertion; a fully suppressed alert MUST NOT be written. |
| **C4-R12** | A synthetic large reason from the new-merchant detector MUST be excluded from suppression matching. |
| **C4-R13** | Suppression rules MUST be visible and removable in settings. |
| **C4-R14** | Removing a rule from settings MUST leave the alert dismissed; undoing from the alert MUST remove every rule it created and re-open the alert. |
| **C4-R15** | Dismissed-to-open MUST be the only backward transition, and it MUST exist only for the undo path. |
| **C4-R16** | Acknowledged MUST be terminal, and the state machine MUST NOT provide a general escape hatch. |
| **C4-R17** | Detection MUST run on the queue and MUST NOT slow an import. |
| **C4-R18** | First activation MUST run a one-time full-history backfill, claimed atomically so a crash does not cause a re-run. |
| **C4-R19** | An hourly sweep MUST act as the durable safety net and MUST revive expired snoozes. |
| **C4-R20** | Concurrent evaluations of the same transaction MUST collapse on a uniqueness key. |
| **C4-R21** | Every background query MUST filter by user explicitly. |
| **C4-R22** | Alerts MUST share the alerts surface with drift, behind a type switch, and MUST show their reasons. |
| **C4-R23** | Cross-user reads and writes MUST return not-found. |

## Related

- [C3 Subscription drift alerts](c3-drift-alerts.md) — the shared surface and lifecycle
- [C2 Recurring detection](c2-recurring.md) — the duplicate exclusion
- [C8 Notifications](c8-notifications.md)
- [40-quality/security.md](../../../40-quality/security.md) — this feature shipped with a full threat model
