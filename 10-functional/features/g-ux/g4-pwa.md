# G4 — Responsive and installable PWA

**Status:** Accepted · **Area:** G — Cross-cutting UX

---

## Purpose

The desktop bundle is the primary surface, but the phone is where a household
actually checks a balance. Making every screen phone-legible and installable was
the prerequisite for the mobile sync peer ([E5](../e-sync/e5-mobile-peer.md)) —
you cannot ship a mobile client for an interface that only works at desk width.

## Behaviour

### Every surface, not most of them

Every authenticated surface is legible and operable at phone width. Not a
reduced subset, not a "mobile view" of three screens — the whole application.

The patterns are consistent:

- Dense tables become card lists.
- Wide power surfaces — the import preview, the dev console, the budget grid —
  scroll horizontally **inside their own container**, so the page body never
  scrolls sideways.
- Modals become bottom sheets.
- Navigation collapses to a drawer with a top bar.
- The transaction list gains infinite scroll, with a **cap on accumulated rows**
  so a long scroll does not exhaust the device.

### Installable

A manifest and an icon set make the application installable to a home screen in
standalone display mode.

### The offline shell caches the shell, and nothing else

A service worker serves the application shell when the network is unavailable,
plus an offline page.

**It never caches financial pages.** An offline cache of somebody's transaction
list, sitting in a browser profile on a shared or lost device, is a leak with no
compensating benefit. This is privacy by construction rather than by
configuration.

The service worker is versioned with the application, so an upgrade does not
leave a stale shell serving against a new backend.

### Charts respond

Charts resize with their container rather than rendering at a fixed width and
overflowing.

### The relationship to the mobile client

The PWA is the *interface*; the mobile client ([E5](../e-sync/e5-mobile-peer.md))
is a native shell that renders it, holds its own encrypted database, and
participates in sync. Improvements here benefit both, which is why this shipped
first.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No network, application installed | The shell serves; financial pages show the offline page rather than stale data. |
| A wide table on a phone | Scrolls inside its container. |
| A long transaction list on a phone | Infinite scroll, capped. |
| An application upgrade | The versioned service worker updates with it. |
| A full-page surface in the native shell | Layout must be composed the way the shell requires, not by the attribute form that silently produces an empty body. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G4-R1** | Every authenticated surface MUST be legible and operable at phone width. |
| **G4-R2** | Dense tables MUST become card lists at phone width. |
| **G4-R3** | Wide content MUST scroll inside its own container; the page body MUST NOT scroll horizontally. |
| **G4-R4** | Modals MUST become bottom sheets at phone width. |
| **G4-R5** | Navigation MUST collapse to a drawer with a top bar at phone width. |
| **G4-R6** | The transaction list MUST support infinite scroll with a cap on accumulated rows. |
| **G4-R7** | A manifest and icon set MUST make the application installable in standalone display mode. |
| **G4-R8** | A service worker MUST serve the application shell and an offline page when the network is unavailable. |
| **G4-R9** | The service worker MUST NOT cache financial pages under any circumstances. |
| **G4-R10** | The service worker MUST be versioned with the application. |
| **G4-R11** | Charts MUST resize with their container. |

## Related

- [E5 Mobile peer](../e-sync/e5-mobile-peer.md) — what this unblocked
- [G1 Privacy stance](g1-privacy.md) — why financial pages are never cached
- [G3 Accessibility](g3-accessibility.md)
- [20-architecture/platform-matrix.md](../../../20-architecture/platform-matrix.md)
