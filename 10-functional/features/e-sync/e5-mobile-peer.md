# E5 — The mobile client as a synced peer

**Status:** Accepted · **Area:** E — Sync and devices

> **This is the last feature outstanding before v2.0 can ship.** Ten of eleven
> plans are complete; the final one is surface-parity smoke testing plus
> real-device acceptance on both mobile platforms. See the
> [roadmap](../../../00-overview/roadmap.md#1--mobile-client-as-a-fully-synced-peer).

---

## Purpose

A phone that shows a remote view of a desktop's data is useless the moment the
desktop is asleep — which for a laptop is most of the day. The mobile client
therefore holds **its own encrypted copy** and participates in merge as a full
peer.

## Behaviour

### A full peer in merge; a client in transport

The phone holds its own encrypted database and merges like any other device
([E1](e1-change-capture.md)). What it does **not** do is run a listener or a
daemon: it dials out, syncs, and stops.

That is a platform constraint — mobile operating systems do not let an
application hold a listening socket in the background — not a topology
exception. In the merge the phone is equal.

### First launch

A fresh install runs its own migrations directly rather than shelling out, then
routes the user to a welcome flow. A phone with no data offers to **import from
another device**, which is a pairing ([E2](e2-device-pairing.md)) followed by an
initial sync.

During the import flow the phone deliberately **does not mint its own key
epoch**. It waits for the desktop's epochs, so the two devices do not end up on
divergent keyrings. The deferral is driven by a durable marker rather than a URL
parameter, so re-entering the flow still behaves correctly.

Credentials entered during the flow are held server-side for the duration and
never rendered into the page.

### Unlocking

Biometric unlock is the primary path, with the passphrase as the fallback.

Two cases differ:

- **Warm re-lock** — the key is still in the session; the biometric prompt
  releases it.
- **Cold start** — no session key; the key must be recovered from the platform's
  secure enclave, gated on biometric authentication. On one platform that
  recovery is asynchronous and completes by signal, so the key never crosses the
  bridge as a value.

A failed or cancelled biometric never releases the key. An entry missing from the
enclave — after a device restore, or an eviction — falls back cleanly to
passphrase unlock rather than failing.

A periodic passphrase re-authentication floor applies, so biometrics alone
cannot hold a device open indefinitely.

### Pairing on a phone

Camera-first, with the typed word code as fallback. The safety number must be
confirmed on both screens, exactly as on the desktop.

### Initial sync is blocking and resumable

After pairing, the phone shows a **blocking** progress screen with no cancel and
no dismiss — a half-synced ledger presented as complete would be actively
misleading.

Progress is read from a durable cursor, so the screen survives being backgrounded
and resumes rather than restarting. Applied counts are recomputed from the local
log at each step rather than accumulated in memory. In the import case,
completion additionally requires that the key epochs have arrived and the log has
been re-projected.

### Ongoing sync

A sync attempt tries the local network first with one bounded retry, then falls
back to the relay. By default it syncs on any network; the user can opt into
pausing on mobile data.

A background pull runs on the platform's own scheduler, fanning out over the
users on the device, and **skips cleanly when no identity is unlocked** rather
than failing.

### Status

The phone shows its own sync status ([E6](e6-sync-status.md)) and a manual
sync-now action.

## Open questions and known gaps

**No backup-exclusion bridge.** On one platform the on-device database sits on a
cloud-backed path with no way to mark it excluded. At-rest encryption
([E4](e4-at-rest-encryption.md)) mitigates this; it does not eliminate it. A
native bridge is required and does not exist.

**Local notification delivery is not hardware-verified.** The plugin is
installed and the adapter is wired, but the on-device proof that a banner
actually fires is outstanding. Whether v2.0 advertises mobile notifications or
ships them present-but-unadvertised is an **undecided product question** — see
the [roadmap](../../../00-overview/roadmap.md#open-questions).

**Real-device pairing acceptance is outstanding.** The cross-device handshake
works at the code level with full round-trip coverage, but two-device hardware
acceptance has not been run, and the "import from another device" flow should not
be advertised as device-verified until it has.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A fresh install with no data | Welcome flow offering import from another device. |
| Re-entering the pairing route without the original parameters | The durable marker still defers epoch minting correctly. |
| A cancelled biometric prompt | No key released. |
| An enclave entry missing after a device restore | Falls back to passphrase unlock. |
| Backgrounding during initial sync | Resumes from the durable cursor. |
| No network during initial sync | The blocking screen waits; it does not report completion. |
| A background pull with no unlocked identity | Skips cleanly. |
| Mobile data with the pause preference set | No sync until a suitable network. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E5-R1** | The mobile client MUST hold its own encrypted local copy and participate as a full merge peer. |
| **E5-R2** | The mobile client MUST NOT run a listener or a background daemon; it MUST dial out only. |
| **E5-R3** | First launch MUST run migrations in-process rather than shelling out. |
| **E5-R4** | A fresh install MUST offer an import-from-another-device flow. |
| **E5-R5** | During import the client MUST NOT mint its own key epoch; it MUST wait for delivered epochs. |
| **E5-R6** | The epoch deferral MUST be driven by a durable marker, not a URL parameter. |
| **E5-R7** | Credentials entered during setup MUST be held server-side and MUST NOT be rendered into the page. |
| **E5-R8** | Biometric unlock MUST be the primary path with the passphrase as fallback. |
| **E5-R9** | A cold start MUST recover the key from the platform secure enclave, gated on biometric authentication. |
| **E5-R10** | Where the platform requires it, enclave recovery MUST complete by signal without the key crossing the bridge as a value. |
| **E5-R11** | A failed or cancelled biometric MUST NOT release the key. |
| **E5-R12** | A missing enclave entry MUST fall back cleanly to passphrase unlock. |
| **E5-R13** | A periodic passphrase re-authentication floor MUST apply. |
| **E5-R14** | Pairing MUST be camera-first with a typed word-code fallback and mandatory safety-number confirmation. |
| **E5-R15** | Initial sync MUST present a blocking progress screen with no cancel and no dismiss. |
| **E5-R16** | Initial-sync progress MUST be read from a durable cursor and MUST resume rather than restart. |
| **E5-R17** | Applied counts MUST be recomputed from the local log at each step. |
| **E5-R18** | In the import case, completion MUST additionally require delivered epochs and a re-projected log. |
| **E5-R19** | A sync attempt MUST try the local network first with a bounded retry before falling back to the relay. |
| **E5-R20** | Syncing on mobile data MUST be the default, with an explicit user opt-out. |
| **E5-R21** | Background pull MUST fan out over the device's users and MUST skip cleanly when no identity is unlocked. |
| **E5-R22** | The client MUST show its own sync status and offer a manual sync action. |
| **E5-R23** | The on-device database MUST be excluded from platform cloud backup where the platform supports it. |
| **E5-R24** | Mobile local notification delivery MUST be verified on real hardware before being advertised. |
| **E5-R25** | *(Open)* Two-device pairing MUST be verified on real hardware before the import flow is advertised as device-verified. Not yet satisfied. |
| **E5-R26** | A failure to persist the key to platform secure storage MUST fail closed: the key MUST NOT be written to the session store in cleartext as a fallback, and the failure is surfaced rather than hidden. |

> `E5-R25` is the one outstanding item that makes this feature the last one
> before v2.0. `E5-R23` and `E5-R24` were verified on real hardware on
> 2026-09-04 (iPhone 12 mini, iOS 26.5.2).

## Related

- [E1](e1-change-capture.md) · [E2](e2-device-pairing.md) · [E3](e3-transport.md) · [E4](e4-at-rest-encryption.md) · [E6](e6-sync-status.md)
- [G4 Responsive and installable PWA](../g-ux/g4-pwa.md) — the surface the mobile client renders
- [F3 Authentication and app-lock](../f-platform/f3-auth-and-app-lock.md)
- [00-overview/roadmap.md](../../../00-overview/roadmap.md)
