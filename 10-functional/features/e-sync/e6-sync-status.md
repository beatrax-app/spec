# E6 — Sync status and health

**Status:** Accepted · **Area:** E — Sync and devices

---

## Purpose

Sync that works invisibly is the goal. Sync that *appears* to work invisibly
while silently doing nothing is the nightmare — the user makes a change on one
device, assumes it propagated, and finds out weeks later that it did not.

This feature is the honesty layer: what state sync is in, when it last
succeeded, and what it refused to apply.

## Behaviour

### A single aggregate status

One status, computed from every device's state, with a strict priority so the
worst thing wins:

| Status | Meaning |
|--------|---------|
| **Error** | Something failed and needs attention. |
| **Syncing** | An exchange is in progress. |
| **Offline** | No peer is reachable. |
| **All synced** | Every known device is up to date. |
| **Unknown** | Not enough information yet. |

Error outranks syncing, which outranks offline and all-synced, which outrank
unknown. A device that is behind must never let the overall status read as
all-synced.

### Last-synced, per device

The status surface names each device and when it last successfully exchanged.
"Synced two minutes ago" is a fact the user can check against reality; a green
tick is not.

### A manual sync action

Because the user should never have to wonder whether waiting will help.

### The quarantine surface

Operations the merge layer refused ([E1](e1-change-capture.md)) are visible on a
**read-only**, user-scoped health surface with their reasons, inside the
developer console ([F5](../f-platform/f5-dev-console.md)).

Read-only is deliberate: a quarantined operation is evidence of a defect, and
the right response is to fix the defect, not to hand the user a button that
force-applies something the system refused for a reason.

### Settings live with devices

The relay address, the pause-on-mobile-data preference, and the device list all
sit in one place, so "how is sync configured" is one screen rather than four.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| No devices paired | Status is unknown; the surface explains rather than showing a false green. |
| One device behind, one up to date | Status is not all-synced. |
| A device never seen | Shown as never synced, not as zero minutes ago. |
| A quarantined operation | Visible with its reason; not user-fixable from that surface. |
| The relay unreachable | Status is offline, not error — an unreachable peer is normal. |
| A verification failure | Status is error — that is not normal. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E6-R1** | A single aggregate status MUST be computed across every device. |
| **E6-R2** | Status priority MUST place error above syncing, syncing above offline and all-synced, and those above unknown. |
| **E6-R3** | A device that is behind MUST prevent the aggregate reading as all-synced. |
| **E6-R4** | Each device's last successful exchange MUST be shown as a concrete time. |
| **E6-R5** | A device that has never synced MUST be shown as never synced, not as a zero interval. |
| **E6-R6** | A manual sync action MUST be available. |
| **E6-R7** | Quarantined operations MUST be visible with their reasons on a read-only, user-scoped surface. |
| **E6-R8** | The quarantine surface MUST NOT offer a force-apply action. |
| **E6-R9** | An unreachable peer MUST read as offline, not as error. |
| **E6-R10** | A cryptographic verification failure MUST read as error. |
| **E6-R11** | Relay configuration, network preferences, and the device list MUST be presented in one place. |
| **E6-R12** | Every status query MUST be scoped to the requesting user. |

## Related

- [E1 Change capture](e1-change-capture.md) — the quarantine source
- [E2 Device pairing](e2-device-pairing.md) — the device list
- [E3 Transport](e3-transport.md) — the relay setting
- [E5 Mobile peer](e5-mobile-peer.md) — the mobile status surface
- [F5 Developer mode](../f-platform/f5-dev-console.md)
