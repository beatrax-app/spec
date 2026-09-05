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

### Lock on window close

The shell posts `WindowHidden`/`WindowClosed` from its own process, which holds
no session cookie, onto a route with no session middleware. No listener bound to
such an event can reach the focused window's session — on any route — and a
closing window cannot be told it is closing either, because the shell removes it
from its window map before it notifies. The listener therefore records the fact
device-locally and the window engages the lock on its own next request, where
the session is the reader's.

This is verified in the repository, not only in a bundle: the suite persists the
window's session, drives the real event POST, reloads that session from its
handler, and asserts the reader is sent to the lock screen. An architecture
guard fails any future listener that reaches session or authentication state
from a shell event.

Residual: a process killed without notice — force quit, power cut, OOM — records
no demand, and that session is covered by the idle lock alone.

### Known gap — what a shell event records does not outlive its request

Every event the shell posts is its own request, so state held in memory for the
life of one is constructed fresh for the next. Two behaviours above are built
that way, and neither accumulates.

The **watchdog's** rolling counter is held that way, so it starts empty at every
exit and never reaches the threshold: a crash storm raises no alert today. The
**window's focus state** is written by the focus listeners and read from other
requests entirely — by the watchdog before it escalates, and by notification
delivery before it decides whether to show a toast — so every reader sees the
constructed default, *focused*. An unfocused window is therefore never observed
as unfocused, and no operating-system notification is delivered at all.

Both are still what the product intends, which is why the rows below stay and
say so rather than being deleted. The fix is the shape the lock uses above —
leave the fact where the next request can read it — and it is not taken yet
because it changes a user-visible operating-system notification that only a real
bundle can judge.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A path pointing at a non-existent file | Canonicalisation fails; logged and dropped. |
| A file deleted between drop and sign-in | The intent is cleared; the user lands on the dashboard. |
| The window unfocused when a notification fires | Delivered to the operating system — intended, and [not what happens](#known-gap--what-a-shell-event-records-does-not-outlive-its-request). |
| The window focused | Not delivered; the in-app surface shows it. This is the answer every window gets, focused or not. |
| A background-process crash storm | One alert on threshold crossing — intended, and [not what happens](#known-gap--what-a-shell-event-records-does-not-outlive-its-request). |
| Running outside the bundle | Listeners that call into the shell do not register; the ones that only record a fact do, so the round-trip is provable off-bundle. |
| First launch before the database file exists | The migrator creates it. |
| An oversized file | Rejected by the size bound. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F1-R1** | Installers MUST ship for macOS, Windows, and Linux, each carrying its own runtime and dependencies. |
| **F1-R2** | Every platform-specific import MUST live in a single module, enforced by architecture test. |
| **F1-R3** | A listener that calls into the shell MUST NOT register outside the bundle. A listener that only records what a shell event reported MUST register everywhere, so the round-trip it begins is provable without a bundle build. |
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
| **F1-R15** | *(Open)* Repeated background-process exits within a rolling window MUST raise an alert; a single crash MUST NOT. Not yet satisfied — the rolling counter does not survive the request that writes it, so the threshold is never crossed ([Known gap](#known-gap--what-a-shell-event-records-does-not-outlive-its-request)). |
| **F1-R16** | Outside the bundle, the absence of the theme signal MUST be the documented fallback trigger. |
| **F1-R17** | Storage paths MUST resolve through the single path authority, enforced by architecture test. |
| **F1-R18** | Lock-on-window-close MUST act on the focused window's session, and MUST be verified to. |

## Related

- [ADR-0006](../../../00-overview/decisions/0006-nativephp-desktop-shell.md)
- [F3 Authentication and app-lock](f3-auth-and-app-lock.md) — what close locks
- [F6 Updates](f6-updates.md) · [F7 Data locations](f7-data-locations.md)
- [A5 Receipt matching](../a-ingestion/a5-receipt-matching.md) — the file-drop consumer
- [C8 Notifications](../c-insight/c8-notifications.md)
- [20-architecture/platform-matrix.md](../../../20-architecture/platform-matrix.md)
