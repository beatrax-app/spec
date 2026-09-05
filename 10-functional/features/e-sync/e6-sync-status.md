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
| **Withheld** | A peer is holding changes back because this device cannot verify who signed them. |
| **Behind** | This device holds changes no peer has yet. |
| **All synced** | Every known device is up to date. |
| **Unknown** | Not enough information yet. |

Error outranks syncing, which outranks offline, which outranks withheld, which
outranks behind and all-synced, which outrank unknown. A device that is behind
must never let the overall status read as all-synced, and neither must one whose
peer is holding changes back.

**Behind** exists because the table did not previously have a word for it. A
device holding an undelivered change with no exchange under way is not syncing
— nothing is in progress — and it is not all-synced either. Without a name for
that state an implementation must borrow one, and the one it borrowed was
*Syncing*, which told the reader an exchange was happening that was not.

**Withheld** is the mirror of *Behind*, and it is named for the same reason.
*Behind* is work this device has not sent; *Withheld* is work a peer will not
send, because the device asking cannot verify the author that signed it
([E2](e2-device-pairing.md)). Nothing has failed: the entries are intact on the
device holding them, and the asking device's cursor for that author has not
moved, so they arrive in full if that author is ever confirmed.

What makes it a state of its own is **what clears it**. A device that is behind
catches up on the next exchange. A device being held from does not, at any number
of exchanges, because nothing an exchange does changes the answer. It therefore
ranks **above** *Behind*: a state no exchange can clear must not sit beneath one
that the next exchange will. It ranks **below** *Offline*, because an
unreachable peer is why nothing is moving at all. And it is never *Error* — a
signature this device cannot check is the mechanism working, not a fault.

It is also not, in general, a state the reader can act their way out of. Some
holds end when the reader confirms an identity a peer offered. Others end at no
act at all: a device may carry an author's history and still be unable to vouch
for that author's identity, so for that author no device in the household has a
confirmation to offer ([E2-R22](e2-device-pairing.md#acceptance-criteria)). The
state has to be reported in a way that is true of both.

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
| A peer holding operations for an author this device cannot verify | Status is withheld — not all-synced, and not error. |
| A device both behind and being held from | Status is withheld: the one of the two that the next exchange will not clear. |
| An author confirmed since the last exchange | The hold clears at once, without waiting for another exchange. |
| A hold whose author no device can vouch for | Reported with its count; no action is offered, and none is implied. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **E6-R1** | A single aggregate status MUST be computed across every device. |
| **E6-R2** | Status priority MUST place error above syncing, syncing above offline, behind and all-synced, and those above unknown; a device that is behind MUST outrank all-synced. |
| **E6-R3** | A device that is behind MUST prevent the aggregate reading as all-synced. |
| **E6-R4** | Each device's last successful exchange MUST be shown as a concrete time. |
| **E6-R5** | A device that has never synced MUST be shown as never synced, not as a zero interval. |
| **E6-R6** | A manual sync action MUST be available. |
| **E6-R7** | Quarantined operations MUST be visible with their reasons on a read-only, user-scoped surface. The per-entry detail MAY live in the developer console; the count and its plain-language warning MUST NOT. |
| **E6-R8** | The quarantine surface MUST NOT offer a force-apply action. |
| **E6-R9** | An unreachable peer MUST read as offline, not as error. A failure that cannot be classified as a verification failure MUST read as offline, and the aggregate status and the per-device label MUST be derived from one classification. |
| **E6-R10** | A cryptographic verification failure MUST read as error. |
| **E6-R11** | Relay configuration, network preferences, and the device list MUST be presented in one place. |
| **E6-R12** | Every status query MUST be scoped to the requesting user. |
| **E6-R13** | *(Open)* A peer holding operations back because this device cannot verify their author MUST prevent the aggregate reading as all-synced, and MUST read as a state of its own rather than as an error or a failure. Not yet satisfied — the status vocabulary has no word for it, so a device short an entire replaced phone's history reads as all devices up to date. |
| **E6-R14** | *(Open)* The withheld state MUST outrank behind, and MUST rank below offline. Not yet satisfied — the state it ranks does not exist yet. |
| **E6-R15** | *(Open)* The aggregate status and the per-peer withheld detail MUST be derived from one classification of what is still held, so a reader who confirms an author is never told a hold has ended on one surface and not on another. Not yet satisfied — the stored report is read per surface, and a row records a past exchange rather than what is still held now. |
| **E6-R16** | *(Open)* Copy describing a hold MUST NOT assert an action the reader can always take. A hold whose author no peer is able to vouch for offers no confirmation at all, and the wording MUST stay true in that case. Not yet satisfied — the surfaces this governs are being built, and the first drafts of them named an act rather than a condition. |

> **`E6-R13` through `E6-R16` are not satisfied.** They are being built against
> the widened relay of [E2-R22](e2-device-pairing.md#acceptance-criteria), which
> is what makes the last of the four load-bearing: once a device relays for an
> author it cannot vouch for, a held entry exists that **no** reader anywhere can
> confirm their way out of. Any sentence promising otherwise is false for that
> reader, and the promise has already had to be taken back out of three places
> that were justifying the ranking by the act it offers rather than by what
> clears it.

## Related

- [E1 Change capture](e1-change-capture.md) — the quarantine source
- [E2 Device pairing](e2-device-pairing.md) — the device list
- [E3 Transport](e3-transport.md) — the relay setting
- [E5 Mobile peer](e5-mobile-peer.md) — the mobile status surface
- [F5 Developer mode](../f-platform/f5-dev-console.md)
