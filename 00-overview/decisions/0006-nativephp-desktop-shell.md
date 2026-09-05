# ADR-0006: NativePHP as the desktop shell

**Status:** Accepted; the "absence of paid OS signing" claim below is superseded
by [ADR-0032](0032-all-four-stores-additive-to-direct-download.md)
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

> **One claim in this record no longer holds, and one revisit condition has
> fired.** Paid signing identities are held, so the updater's verification chain
> is not the sole binary-integrity signal it is described as below. And
> app-store distribution has reached the sandboxing constraint the last
> "revisit if" bullet anticipated: a Mac App Store build's sandbox ignores one
> of the two hardened-runtime relaxations the bundle relies on to map its static
> interpreter, so that listing needs a different runtime strategy
> ([ADR-0032](0032-all-four-stores-additive-to-direct-download.md),
> [F8](../../10-functional/features/f-platform/f8-app-store-distribution.md)).
> The decision — NativePHP as the desktop shell — stands, as does everything
> else below.

## Context

Beatrax has to install like a desktop app. A finance dashboard the user opens
every morning cannot demand a terminal session, a serve command, and a browser
bookmark. The target user installs from a `.dmg`, an `.exe`/`.msi`, or an
`.AppImage`/`.deb`, double-clicks an icon, and lands in the dashboard.

The codebase, however, is Laravel — server-rendered Blade plus Livewire, not
React. That constrains the shell choice sharply.

## Decision

Beatrax ships as a desktop application via NativePHP, which bundles PHP, the
application, and an Electron-based Chromium shell into a per-platform installer.

- **The desktop bundle** is produced by the framework's native-build command,
  invoked from the release workflow on three platform runners. Each produces its
  platform's native installer.
- **The bundled runtime** carries its own PHP binary, its own installed
  dependencies, and the application code. The user installs none of these by
  hand.
- **Storage paths** resolve through the single path-authority service to per-OS
  user-data directories, so the database survives app upgrades
  ([ADR-0005](0005-sqlite-wal.md)).
- **The OAuth callback** uses a loopback redirect URI — the one flow that needs
  an HTTP listener works inside the shell because the shell exposes one.

The NativePHP code is quarantined inside a single Desktop module. Every
`Native\Laravel\*` and `Native\Desktop\*` import outside that module is forbidden
by architecture invariant, and the narrower shell contract is restricted to a
single allow-listed action plus a fallback. The rest of the application runs
unchanged whether it is hosted by the desktop shell or by the local development
environment.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Tauri with a React rewrite** | Would have thrown away the Livewire investment that earned its keep over eleven phases, and added a second testing pipeline. |
| **Electron with a React rewrite** | Same rejection as Tauri. |
| **A static binary that opens the user's browser at a local port** | Works on Linux; on macOS and Windows the first-launch experience never feels native enough to recommend to a non-technical partner. Cross-platform inconsistency was worse than a single shell choice. |
| **A PWA installed via the browser** | Service-worker install flows are unreliable, and the OAuth loopback URI needs a local HTTP listener the PWA model does not provide. The PWA still ships — as the phone surface, not as the desktop shell. |

## Consequences

### Positive

- One source tree, three platform installers, built in parallel by the release
  workflow.
- Local development is identical to production except for a handful of surfaces
  gated on a runtime flag.
- The user's data, the PHP runtime, and the SQLite store all stay on the machine,
  which is what makes [ADR-0004](0004-local-only-hosting.md) practical.

### Negative

- **The PHP version floor is whatever the shell's bundled runtime supports.**
  Diverging would mean shipping a build that runs against a PHP version the
  developer never tested against, so the development environment matches the
  bundle. The CI matrix runs both the bundled version and the next one to catch
  forward-compatibility breakage early.
- **No PHP extensions outside the supported set.** Anything needing a PECL
  install is unavailable in the shipped bundle. The codebase uses none.
- **Electron's footprint.** A Chromium runtime per install. Accepted as the cost
  of not rewriting the frontend.

### Neutral

- The updater that ships with the shell fetches release manifests, verifies an
  Ed25519 signature against a key embedded in the bundle, verifies each binary's
  hash against the manifest, and applies on next launch. That chain is the sole
  binary-integrity signal in the absence of paid OS signing — see
  [the licence rationale](../../90-appendix/license-rationale.md#why-no-paid-signing-certificates).

## Revisit if

- NativePHP's release cadence stops tracking the Laravel versions the project
  depends on.
- App-store distribution forces sandboxing constraints the Electron shell cannot
  satisfy — an open question on the [roadmap](../roadmap.md#open-questions).

## Related

- [ADR-0004](0004-local-only-hosting.md) · [ADR-0005](0005-sqlite-wal.md)
- [ADR-0007](0007-database-queue-driver.md) — what the bundle cannot carry
- [F1 Desktop shell and packaging](../../10-functional/features/f-platform/f1-desktop-shell.md)
- [20-architecture/platform-matrix.md](../../20-architecture/platform-matrix.md)
