# Security

**Status:** Accepted

Beatrax holds a household's complete financial history on their own machine.
This page states what it defends against, what it does not, and the practices
that follow.

## The threat model

### In scope

| Threat | Defence |
|--------|---------|
| **A copied database file** | At-rest encryption of identifying columns, behind a passphrase-derived key released by the app-lock ([E4](../10-functional/features/e-sync/e4-at-rest-encryption.md)) |
| **A cloud-backed device backup** | The same, with the honest caveat below |
| **A lost or stolen device** | The app-lock, plus revocation that rotates the group key ([E2](../10-functional/features/e-sync/e2-device-pairing.md)) |
| **An observer on the network** | Mutually authenticated, forward-secret sessions ([E3](../10-functional/features/e-sync/e3-transport.md)) |
| **A machine-in-the-middle during pairing** | The mandatory safety-number confirmation on both screens |
| **A hostile relay operator** | The relay holds ciphertext and performs no cryptography, asserted by test |
| **A hostile input file** | Typed parse failures, disabled external-entity resolution, size and line caps, archive-bomb and traversal guards, and pattern-length caps on user-supplied match expressions ([C9-R23](../10-functional/features/c-insight/c9-community-corpus.md#acceptance-criteria)) |
| **A hostile aggregator response** | Host allow-list before credentials, HTTPS only, no redirects, private-address rejection |
| **A tampered update** | Signature verification before anything is read from a manifest, hash verification before any install |
| **Cross-user data access** | Structural user scoping, explicit filters in background contexts, not-found on every cross-user surface, and a default scope that fails closed on an unauthenticated web request ([ARCH-R21](../20-architecture/README.md#the-arch-r-namespace)). Every authenticated `GET` route — all seventy-six, enumerated against the live router rather than against a list — has been probed or reasoned; the pass that closed this found and fixed a real cross-user leak in the developer console's "Last command" tile. |
| **Credential leakage into logs** | Three-point scrubbing with cache invalidation on rotation ([F5](../10-functional/features/f-platform/f5-dev-console.md)) |
| **Credential leakage into rendered pages** | A registry-backed architecture test on serialisable component properties |
| **Script injected via rendered financial text** | A nonce-based Content-Security-Policy on authenticated responses, so bank- and email-derived text renders as data and cannot execute even if an output sink is missed |
| **Injection through the developer console** | Registry allow-list, argument escaping, and controller validation — three independent guards |
| **Spreadsheet formula injection in exports** | Escaping on every free-text cell |
| **Enumeration of accounts** | Constant messages, not-found rather than forbidden, audit rows that record no user on an unknown-username failure, and equal work on the account-not-found path so timing does not distinguish it ([F3-R34](../10-functional/features/f-platform/f3-auth-and-app-lock.md#acceptance-criteria)) |

### Explicitly out of scope

| Threat | Why |
|--------|-----|
| **A compromised operating system** | A user-space application cannot defend against it. |
| **A maliciously-paired device** | A paired device legitimately holds the group key. The safety-number confirmation is the defence, and it is the user's to perform. |
| **A household member escalating to operator access** | Every user added to an instance is a co-equal, fully-trusted operator: any of them may enable developer mode (the SQL console and all-user visibility) and back up or restore the whole database. Partner accounts are a convenience, not a privilege boundary. Ordinary per-user data scoping ([ARCH-R6](../20-architecture/README.md#the-arch-r-namespace)) still applies to routine reads and writes. |
| **Traffic analysis against a relay** | Sizes, timing, and recipient identifiers are observable. Documented, not defended. |
| **An attacker with the database file, the time, and the motivation** | The plaintext set is too informative. See below. |

## The honest statement about at-rest encryption

**It does not encrypt everything.** Amounts, dates, account references, type
enums, and the full-text index body are plaintext, because aggregation and
search depend on them
([ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md)).

An attacker with the file but not the key sees a complete dated per-account
distribution of amounts, plus a plaintext shadow of descriptions and counterparty
names in the search index. That is a great deal.

**What it actually buys** is raising the cost of casual access to a copied file
or a cloud-backed device backup. It is **not** a defence against a determined
attacker with the file.

The product's own copy must say this
([G1-R14](../10-functional/features/g-ux/g1-privacy.md#acceptance-criteria)).
Overstating protection is worse than the gap it hides.

## Cryptographic choices

| Use | Choice |
|-----|--------|
| Device signing | Ed25519 |
| Key agreement | X25519 |
| Session transport | Noise handshake patterns over the above, with XChaCha20-Poly1305 and BLAKE2b |
| At-rest and backup encryption | XChaCha20-Poly1305, chunked and authenticated |
| Key derivation | Argon2id, memory-hard |
| Epoch delivery | Sealed to a recipient public key — confidential but not sender-authenticated, so **only ever handled from an already-authenticated channel** |
| Password and recovery-code hashing | The framework's standard scheme |
| Safety numbers | Derived from both public identities, rendered as words |
| Pairing fallback | A standard wordlist |

**On post-quantum:** the encrypted-backup construction is symmetric throughout,
so the known quantum attacks against public-key cryptography have nothing to
attack; a 256-bit symmetric key leaves a 128-bit margin under the known
quadratic speedup, and the memory-hard derivation bounds brute force by memory.
A post-quantum key exchange is deliberately **not** used: there is no recipient
public key in that construction, and the passphrase's entropy is the real floor.

The sync transport's key agreement **is** classical, and that is a real
forward-secrecy exposure against a future adversary recording traffic today. It
is stated rather than glossed.

## Practices

| Practice | Requirement |
|----------|-------------|
| Secrets in filesystem-permission-protected files, written atomically | Never in the database, never in a component property |
| Constant-time comparison for every secret comparison | Including callback state and confirmation phrases |
| Single-use, session-bound, age-limited callback state, with a PKCE S256 challenge bound to the flow | On every authorisation flow ([A4-R22](../10-functional/features/a-ingestion/a4-email-scanning.md#acceptance-criteria)) |
| Host allow-lists before credentials are attached | On every outbound client, including provider-supplied pagination URLs |
| Loopback-only binding, widened only on purpose | Every non-loopback request refused with not-found unless the operator explicitly widened the gate; the default is loopback only ([ARCH-R22](../20-architecture/README.md)) |
| No-store cache directives on authenticated responses | So a browser does not write a transaction list to disk |
| A nonce-based Content-Security-Policy on authenticated responses | Inline scripts carry a per-response nonce; untrusted financial text can never execute as script |
| Escalating backoff with a hard cap | On the app-lock, with an alert at the cap |
| Replay defence on biometric assertions | Non-increasing counters rejected |
| Read-only enforced three ways on the query panel | Parse check, connection mode, and audit record |
| Never log key material | Including on the duplicate-epoch path |

## Reporting

Through private vulnerability reporting, never the public tracker. Scope, safe
harbour, and response targets are in
[30-repos/dot-github.md](../30-repos/dot-github.md).

## Threat modelling as a practice

Features touching money movement or personal data get a threat model **before**
implementation and a verification pass afterwards. The anomaly feature shipped
with all twenty-two identified threats closed and verified against the
implementation — that is the standard, not an exception.

## Known outstanding items

Recorded rather than described as solved:

| Item | Status |
|------|--------|
| Operating-system key custody | Registered, **not wired**. The unlocked key follows session custody on every platform ([F3](../10-functional/features/f-platform/f3-auth-and-app-lock.md)). No longer a deferral: `F3-R33` is [in v2.0 scope and being built](../00-overview/roadmap.md#3--the-three-latent-risks-no-longer-deferred). |
| Mobile backup exclusion | No native bridge exists; the on-device database sits on a cloud-backed path, mitigated by at-rest encryption ([E5](../10-functional/features/e-sync/e5-mobile-peer.md)). |
| Per-user connector secrets | A single global secrets file with no per-user keying; a blocker on second-user activation ([A6](../10-functional/features/a-ingestion/a6-open-banking.md)). No longer a deferral: `A6-R20` and `A6-R21` are [in v2.0 scope and being built](../00-overview/roadmap.md#3--the-three-latent-risks-no-longer-deferred). |
| Lock on window close | Not verified to act on the focused window's session ([F1](../10-functional/features/f-platform/f1-desktop-shell.md)). |

## Related

- [ADR-0015](../00-overview/decisions/0015-multi-master-p2p-sync.md) · [ADR-0016](../00-overview/decisions/0016-noise-transport-zero-knowledge-relay.md) · [ADR-0018](../00-overview/decisions/0018-amounts-plaintext-at-rest.md) · [ADR-0020](../00-overview/decisions/0020-open-banking-byo-key-ais-only.md)
- [G1 Privacy stance](../10-functional/features/g-ux/g1-privacy.md)
- [ci-cd.md](ci-cd.md) · [code-standards.md](code-standards.md)
