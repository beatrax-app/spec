# G1 — Privacy stance and the outbound-call surface

**Status:** Accepted · **Area:** G — Cross-cutting UX

---

## Purpose

Every other feature is a claim. This one is the checkable version of it.

The product's founding promise is that nothing leaves the machine
([ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md)). That is
only credible if the outbound surface is small enough to enumerate exhaustively,
and if the enumeration is maintained as a requirement rather than as marketing.

## Behaviour

### The complete outbound-call surface

**This table is exhaustive.** A network call not on it is a defect.

| Call | Default | Purpose | Disableable |
|------|---------|---------|-------------|
| **Update check** | On | Fetches the signed release manifest ([F6](../f-platform/f6-updates.md)). | Yes |
| **Mail provider API** | Off | Fetches receipt messages with the user's own grant ([A4](../a-ingestion/a4-email-scanning.md)). | Yes — it is off until enabled |
| **Exchange-rate fetch** | Off | Refreshes rates; a bundled snapshot works offline ([B10](../b-ledger/b10-multi-currency.md)). | Yes — it is off until enabled |
| **Open-banking aggregator** | Off | Fetches booked transactions from the user's own aggregator account ([A6](../a-ingestion/a6-open-banking.md)). | Yes — it is off until enabled |
| **Sync peers** | Off | Peer-to-peer exchange with the user's own devices ([E3](../e-sync/e3-transport.md)). | Yes — no peers until paired |
| **Sync relay** | Off | Ciphertext-only store-and-forward, to a relay the user configures. | Yes — none until configured |
| **External-link opening** | On demand | Opens a link the user clicked, gated by an allow-list ([C9](../c-insight/c9-community-corpus.md)). | Only by not clicking |

**With every optional feature off, the only outbound call is the update check —
and that can be disabled too.** At that point the application makes no network
call at all.

### What is absent, and must stay absent

| Absent | Enforcement |
|--------|-------------|
| Telemetry, analytics, usage pings | No such dependency may be introduced; the release gate checks. |
| A remote error reporter | Same. |
| A cloud database or account | There is no account system to have one. |
| A corpus-fetch service | The corpus ships inside the application. |
| Outbound mail | No mail capability exists in the bundle, enforced by architecture test. |
| Payment initiation | Structurally absent from the connector's scope type ([ADR-0020](../../../00-overview/decisions/0020-open-banking-byo-key-ais-only.md)). |

### The surface is bound to the machine

Every request whose server address is not a loopback address is refused with
not-found ([F6](../f-platform/f6-updates.md)). The application is not
*accidentally* reachable from the network even if a port is exposed: a
self-hoster who wants it reachable widens the gate deliberately, and the default
is loopback only ([ARCH-R22](../../../20-architecture/README.md)).

Every authenticated response carries a no-store cache directive, so a browser
does not write a transaction list to disk.

The offline application shell **never caches financial pages**
([G4](g4-pwa.md)) — an offline cache of somebody's transactions on a shared
device is a leak with no upside.

### Honesty about what is not protected

Three things must be stated plainly in the product's own copy, not only here:

1. **At-rest encryption does not encrypt everything.** Amounts, dates, and the
   search index are plaintext by necessity
   ([ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md)).
   An attacker with the file but not the key sees a complete dated amount
   distribution and a plaintext shadow of descriptions.
2. **The relay sees metadata.** Sizes, timing, and which device identifiers
   exchange traffic. Traffic analysis is not defended against.
3. **A paired device is trusted.** Revocation rotates the key going forward; it
   does not un-see what was already synced
   ([ADR-0015](../../../00-overview/decisions/0015-multi-master-p2p-sync.md)).

Overstating protection is worse than the gap it hides, because a user who
believes the wrong thing makes worse decisions than one who knows the truth.

### The user can always see and leave

Data locations, export, and deletion are first-class and documented in
[F7](../f-platform/f7-data-locations.md).

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| Every optional feature off, updates off | Zero outbound calls. |
| A request from a non-loopback address | Not-found, unless the operator widened the gate. |
| An external link with a non-allow-listed host | Refused before the shell is invoked. |
| Running outside the desktop shell | External-link opening no-ops with a logged URL. |
| A dependency introducing telemetry transitively | Caught by the release gate. |
| Log output containing a credential | Scrubbed at three points ([F5](../f-platform/f5-dev-console.md)). |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G1-R1** | The outbound-call surface MUST be enumerable, and this catalogue MUST be its complete enumeration. |
| **G1-R2** | Every outbound call the application itself initiates, other than the update check, MUST be off by default. |
| **G1-R20** | Handing a URL to the operating system's browser is not a call the application makes and is therefore not disableable; it MUST still pass the applicable allow-list first, and it MUST NOT carry any data beyond the URL the user clicked. |
| **G1-R3** | The update check MUST be disableable. |
| **G1-R4** | With every optional feature and the update check disabled, the application MUST make no outbound network call. |
| **G1-R5** | No telemetry, analytics, or usage-reporting dependency may exist in the shipped bundle. |
| **G1-R6** | No remote error-reporting dependency may exist in the shipped bundle. |
| **G1-R7** | No outbound mail capability may exist in the shipped bundle, enforced by architecture test. |
| **G1-R8** | Payment initiation MUST be structurally absent, not merely disabled. |
| **G1-R9** | The community corpus MUST ship inside the application; no corpus fetch may occur. |
| **G1-R10** | Every non-loopback request MUST be refused with not-found. A gate the operator has explicitly widened ([ARCH-R22](../../../20-architecture/README.md)) is the one exception; a bundle nobody has widened MUST refuse. This governs the application's own HTTP surface; the sync listener is a separate process on its own port, deliberately not loopback-bound, whose gate is the mutually-authenticated handshake ([E3](../e-sync/e3-transport.md)). |
| **G1-R11** | Every authenticated response MUST carry a no-store cache directive. |
| **G1-R12** | The offline application shell MUST NOT cache financial pages. |
| **G1-R13** | External links MUST pass an HTTPS check and a host allow-list before being opened. |
| **G1-R14** | The product's own copy MUST state that at-rest encryption leaves amounts, dates, and the search index in plaintext. |
| **G1-R15** | The product's own copy MUST state what metadata a relay can observe. |
| **G1-R16** | The product's own copy MUST state that a paired device is trusted and that revocation is not retroactive. |
| **G1-R17** | The release gate MUST check that no forbidden dependency has been introduced, including transitively. |
| **G1-R18** | The data a user's machine sends to a third party MUST be limited to what the enabled feature's own protocol requires. |
| **G1-R19** | Data locations, export, and deletion MUST be discoverable from within the application. |

## Related

- [ADR-0004](../../../00-overview/decisions/0004-local-only-hosting.md) · [ADR-0015](../../../00-overview/decisions/0015-multi-master-p2p-sync.md) · [ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md) · [ADR-0020](../../../00-overview/decisions/0020-open-banking-byo-key-ais-only.md)
- [F7 Data locations, export and deletion](../f-platform/f7-data-locations.md)
- [40-quality/security.md](../../../40-quality/security.md)
- [90-appendix/data-retention.md](../../../90-appendix/data-retention.md)
