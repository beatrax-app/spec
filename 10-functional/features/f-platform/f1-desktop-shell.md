# F1 — Desktop shell and packaging

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

Beatrax has to install like a desktop application: download, double-click, and
you are in the dashboard. No terminal, no server to start, no browser bookmark.

This feature owns the shell that makes that true, and the quarantine that keeps
the rest of the product testable without it.

The shell choice is [ADR-0006](../../../00-overview/decisions/0006-nativephp-desktop-shell.md).

## Behaviour

### Three platforms, one source tree

Installers for macOS, Windows, and Linux — the latter as both a portable and a
native package. Each carries its own runtime, its own dependencies, and the
application. The user installs none of them by hand.

Every platform-specific import lives in **one place**, enforced by architecture
test. Everything else in the product runs unchanged whether hosted by the shell
or by a plain local environment, which is what keeps the rest of the suite
testable without a bundle.

### First launch

A fixed chain: the shell boots, the framework boots, pending migrations run,
the application key is minted if a sentinel says it has not been, and the first
window renders.

Every step is idempotent, so the chain runs on every launch without side
effects. The key-mint step is guarded by a sentinel file that is checked
**before** anything that would need the key to read existing data — regenerating
a key over an existing encrypted database would destroy it.

### Files opened from the operating system

Dropping a supported file on the application, or opening one with it, routes
into the import or receipt flow.

Every path the operating system offers passes an intake gate first: an extension
allow-list, a size bound, and path canonicalisation so nothing traverses out of
where it claims to be. **A rejected path is logged and dropped silently** —
returning an error to the operating system would betray the application's
presence and its handling.

If nobody is signed in, the intent is remembered and resumed after sign-in.

The platforms differ in how they deliver this — one has a native event, the
others deliver it through process arguments and a second-instance signal — and
all paths converge on the same gate before anything else happens.

### Closing the window

The first close asks whether to quit or keep running, with an option to
remember. The choice is stored per user and re-validated against the allowed
options on the way in.

**Either outcome locks the application immediately** — no grace period. A hidden
window is still a window someone can bring back.

### Operating-system notifications

The shell is the delivery adapter for notifications ([C8](../c-insight/c8-notifications.md)),
consulting the suppression decision, then the window's focus state, then the
per-device detail preference. A focused window means no operating-system toast —
the in-app surface is already showing it.

### Watchdog

Repeated background-process exits inside a rolling window raise an alert. A
single transient crash does not — that is noise.

### Theme

The shell can report the operating system's theme preference. Outside the
bundle that signal is simply absent, and **its absence is itself the signal**:
the layout falls back to the browser's own preference query.

### Known risk — lock on window close

The lock-on-close listener fires on the shell's own internal channel, and it has
**not been verified** that this always carries the focused window's session. If
it does not, the session that gets locked could be a different one, and the
lock-on-close guarantee would silently not hold.

This cannot be verified outside a real bundle build. The client-side privacy
veil and the server-side idle lock still cover backgrounding in the meantime.
Recorded as an open follow-up rather than described as working.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A path pointing at a non-existent file | Canonicalisation fails; logged and dropped. |
| A file deleted between drop and sign-in | The intent is cleared; the user lands on the dashboard. |
| The window unfocused when a notification fires | Delivered to the operating system. |
| The window focused | Not delivered; the in-app surface shows it. |
| A background-process crash storm | One alert on threshold crossing. |
| Running outside the bundle | Shell-coupled listeners do not register at all. |
| First launch before the database file exists | The migrator creates it. |
| An oversized file | Rejected by the size bound. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F1-R1** | Installers MUST ship for macOS, Windows, and Linux, each carrying its own runtime and dependencies. |
| **F1-R2** | Every platform-specific import MUST live in a single module, enforced by architecture test. |
| **F1-R3** | No shell-coupled listener may register outside the bundle. |
| **F1-R4** | The first-launch chain MUST be idempotent across launches. |
| **F1-R5** | Application-key generation MUST be sentinel-guarded and MUST run before anything that would read existing encrypted data. |
| **F1-R6** | A key MUST NOT be regenerated where an existing database is present. |
| **F1-R7** | Every operating-system-supplied path MUST pass an extension allow-list, a size bound, and path canonicalisation. |
| **F1-R8** | A rejected path MUST be logged and dropped silently; no error may be returned to the operating system. |
| **F1-R9** | A file opened while signed out MUST be remembered and resumed after sign-in. |
| **F1-R10** | Every platform's file-open path MUST converge on the same intake gate. |
| **F1-R11** | The close-behaviour choice MUST be stored per user and re-validated against the allowed options. |
| **F1-R12** | Either close outcome MUST lock the application immediately, with no grace period, where the user has the app-lock enabled; where they do not, no close outcome may lock or veil the session ([F3-R29](f3-auth-and-app-lock.md)). |
| **F1-R13** | Notification delivery MUST consult suppression, then window focus, then the per-device detail preference. |
| **F1-R14** | A focused window MUST suppress the operating-system notification. |
| **F1-R15** | Repeated background-process exits within a rolling window MUST raise an alert; a single crash MUST NOT. |
| **F1-R16** | Outside the bundle, the absence of the theme signal MUST be the documented fallback trigger. |
| **F1-R17** | Storage paths MUST resolve through the single path authority, enforced by architecture test. |
| **F1-R18** | *(Open)* Lock-on-window-close MUST be verified to act on the focused window's session. Not yet verified — see [Known risk](#known-risk--lock-on-window-close). |

## Related

- [ADR-0006](../../../00-overview/decisions/0006-nativephp-desktop-shell.md)
- [F3 Authentication and app-lock](f3-auth-and-app-lock.md) — what close locks
- [F6 Updates](f6-updates.md) · [F7 Data locations](f7-data-locations.md)
- [A5 Receipt matching](../a-ingestion/a5-receipt-matching.md) — the file-drop consumer
- [C8 Notifications](../c-insight/c8-notifications.md)
- [20-architecture/platform-matrix.md](../../../20-architecture/platform-matrix.md)
