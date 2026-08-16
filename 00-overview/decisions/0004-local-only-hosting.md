# ADR-0004: Local-only hosting; no cloud, telemetry, or remote logging

**Status:** Accepted
**Date:** 2026-05-27
**Graduated from:** product-repo Phase 17, decision D-32

## Context

The data Beatrax processes — full bank-account history, credit-card statements,
email receipts, the funding chains between every account — is the single most
sensitive class of personal data the average person holds outside their medical
records. It includes who they pay, how much, when, where, and what for. It maps
to relationships, locations, health conditions, political affiliations, and
vulnerabilities.

For that class of data, the default posture every other personal-finance product
takes — "we collect it, we store it on our servers, we promise not to misuse
it" — was never an option. The privacy story has to be provable, not promised.

Three failure modes that any cloud component would introduce, even a seemingly
innocent one, decided the posture:

- **A telemetry SDK pinging home with "anonymous" usage data** betrays which
  features a user uses, which inevitably correlates to which life events they
  are tracking.
- **A remote error reporter** ships stack traces containing local variable
  contents — balances, merchant names, IBAN fragments. Even with scrubbing, the
  residual leak is unacceptable.
- **A cloud sync option**, even "encrypted at rest", creates a high-value target
  the maintainer becomes legally responsible for protecting, and changes the
  user's threat model from "my laptop" to "my laptop plus a third-party server".

The decision is to take cloud off the table entirely, not to take it "off by
default".

## Decision

Beatrax is a local-only application.

- **All data is stored on the user's machine** — the SQLite database in the
  per-OS user-data directory; backups alongside it; OAuth tokens in a
  filesystem-permission-protected secrets directory on the same machine.
- **No telemetry.** No metrics SDK, no analytics, no feature-usage pings, no
  crash reporter that contacts an external service.
- **No remote logging.** Logs land on disk. The in-app log tailer reads them
  locally; nothing is shipped off the machine.
- **No cloud sync.** Device sync is peer-to-peer and end-to-end encrypted; the
  optional relay holds ciphertext only and can decrypt nothing. See
  [ADR-0016](0016-noise-transport-zero-knowledge-relay.md).
- **Controlled outbound exceptions only**, each user-visible and each
  disableable:
  - The updater contacts GitHub's releases API to check for new versions. The
    manifest is Ed25519-signed and every binary is hash-verified against it.
  - Email-receipt scanning contacts Google's or Microsoft's API with the user's
    own OAuth token, if the user enabled it.
  - Online exchange-rate refresh contacts a rate source, if the user enabled it;
    a bundled offline snapshot is the fallback.
  - The open-banking connector contacts the aggregator the user configured, if
    the user enabled it. See [ADR-0020](0020-open-banking-byo-key-ais-only.md).

With every optional feature off, the shipped bundle makes no outbound network
call except the update check, and that too can be turned off.

The OAuth dance runs on the user's machine — a loopback redirect URI keeps the
callback local, tokens stay in the local secrets file, and subsequent API calls
go directly from the user's machine to the provider. The maintainer's
infrastructure is never in the loop, because there is none.

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Cloud sync, opt-in only** | Opt-in becomes default-on for any sufficiently-pushed feature, and running cloud infrastructure for a single-user product is disproportionate to the benefit. |
| **Telemetry with the option to disable** | The presence of the SDK creates the leak whether or not the user opts in. |
| **Remote error reporting with PII scrubbing** | The residual risk after scrubbing is too high for this data class. |

## Consequences

### Positive

- The privacy claim is structurally true rather than policy-true.
- The outbound surface is small enough to enumerate exhaustively, which is what
  makes [G1 Privacy stance](../../10-functional/features/g-ux/g1-privacy.md)
  checkable rather than aspirational.

### Negative

- **No support channel for crash reports.** A user who hits a bug has to share
  logs by hand. The in-app log surface and a diagnostics-bundling command make
  this practical, but it is friction.
- **Release verification is partly the user's responsibility.** Because the app
  does not phone home with crash data, a bad release cannot be detected in the
  field. The release pipeline compensates with a per-platform smoke test before
  publishing.
- **No usage data to prioritise with.** Product decisions are made from
  reasoning and from what users say, not from what an analytics dashboard shows.

### Neutral

- Cross-machine data movement is a first-class feature rather than an absence —
  it just happens peer-to-peer rather than through a server.

## Revisit if

- Nothing currently foreseeable. This is a founding constraint; changing it
  changes the product.

## Related

- [ADR-0003](0003-hippocratic-3-0-license.md) — the licence that makes the claim
  auditable
- [ADR-0006](0006-nativephp-desktop-shell.md) — the shell that ships Beatrax as
  a local app rather than a hosted service
- [ADR-0015](0015-multi-master-p2p-sync.md) — how multi-device works without
  contradicting this
- [G1 Privacy stance](../../10-functional/features/g-ux/g1-privacy.md)
- [F7 Data locations, export and deletion](../../10-functional/features/f-platform/f7-data-locations.md)
