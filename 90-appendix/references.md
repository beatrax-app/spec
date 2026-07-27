# References

**Status:** Accepted

The standards, formats, and protocols this specification depends on. Named so a
reader can find them, and so a future contributor knows which document to
consult rather than guessing at behaviour.

## Requirement language

- **RFC 2119** — the meaning of `MUST`, `SHOULD`, and `MAY`, as used throughout
  this specification.

## Financial data formats

- **ISO 20022** — the message standard. beatrax consumes the bank-to-customer
  statement message (`camt.053`) and handles every sub-version the supported
  banks export ([A1](../10-functional/features/a-ingestion/a1-source-formats.md)).
- **MT940** — the legacy SWIFT customer statement message, including its
  structured narrative conventions and its transaction-type codes.
- **SEPA** — the payment area whose direct debits and credit transfers appear in
  every Dutch statement, and whose bulk settlement mechanism is one of the two
  chain shapes ([B5](../10-functional/features/b-ledger/b5-chain-resolution.md)).
- **IBAN** — the account-number standard. Structural validation uses the standard
  checksum, not a national-format assumption
  ([B4](../10-functional/features/b-ledger/b4-counterparties.md)).
- **ISO 4217** — currency codes, which travel with every monetary value
  ([ADR-0009](../00-overview/decisions/0009-brick-money-multi-currency.md)).
- **ISO 8601** — date and time representation.

## Regulatory

- **PSD2** — the directive under which the open-banking connector operates. The
  connector is **account-information only**, structurally
  ([ADR-0020](../00-overview/decisions/0020-open-banking-byo-key-ais-only.md)).
- **SCA** — the strong-customer-authentication requirement the consent flow
  satisfies by redirecting to the bank's own authentication.

## Cryptography

- **Ed25519** — device signing, and release-manifest signing.
- **X25519** — key agreement between devices.
- **The Noise Protocol Framework** — the handshake patterns used for the sync
  transport. The implementation is validated against the framework's published
  test vectors ([E3](../10-functional/features/e-sync/e3-transport.md)).
- **XChaCha20-Poly1305** — authenticated encryption for the transport, for
  at-rest columns, and for encrypted backups.
- **BLAKE2b** — the hash used inside the handshake.
- **Argon2id** — memory-hard key derivation for the at-rest key and for backup
  passphrases.
- **SHA-256 / SHA-512** — fingerprints and release-binary verification.
- **HMAC** — relay drain credentials.
- **BIP-39 wordlist** — the typed pairing fallback and safety-number rendering.
  The wordlist only; none of the derivation scheme it is normally part of
  ([E2](../10-functional/features/e-sync/e2-device-pairing.md)).
- **WebAuthn** — biometric enrolment and assertion on the web surface
  ([F3](../10-functional/features/f-platform/f3-auth-and-app-lock.md)).

## Distributed systems

- **Hybrid Logical Clocks** — the ordering scheme for the operation log,
  following Kulkarni and Demirbaş. A physical component plus a counter, giving a
  total order without a coordinator
  ([ADR-0014](../00-overview/decisions/0014-op-log-crdt-merge-engine.md)).
- **CRDTs** — the merge families the registry implements: last-writer-wins per
  field, grow-only counters, and observed-remove sets
  ([20-architecture/contracts/op-log.md](../20-architecture/contracts/op-log.md)).
- **mDNS / DNS-SD** — local-network peer discovery.

## Statistics

- **Median and median absolute deviation** — the robust statistics behind
  unusual-charge detection, chosen over mean and standard deviation because a
  small sample with an outlier is exactly the shape mean-based statistics handle
  worst ([C4](../10-functional/features/c-insight/c4-anomaly.md)).
- **Linear interpolation between closest ranks** — the percentile method used
  for forecast bands, matching the default of every mainstream statistical tool
  ([C5](../10-functional/features/c-insight/c5-forecasting.md)).
- **Levenshtein distance** — fuzzy name similarity in chain resolution and in
  search suggestions.

## Process and licensing

- **Semantic Versioning** — as read in
  [20-architecture/contracts/versioning.md](../20-architecture/contracts/versioning.md).
- **Keep a Changelog** — the changelog's shape. It is the single source of
  release notes ([70-operations/releasing.md](../70-operations/releasing.md)).
- **Conventional Commits** — commit subjects
  ([GOV-R16](../50-governance/README.md#the-gov-r-namespace)).
- **Developer Certificate of Origin 1.1** — the sign-off
  ([50-governance/dco.md](../50-governance/dco.md)).
- **Hippocratic License 3.0** — the product's licence
  ([ADR-0003](../00-overview/decisions/0003-hippocratic-3-0-license.md)).
- **CC BY-SA 4.0** — this specification's licence ([LICENSE.md](../LICENSE.md)).
- **Contributor Covenant 2.1** — the code of conduct
  ([30-repos/dot-github.md](../30-repos/dot-github.md)).

## A note on versions

This page names standards, not library versions. Library versions live in the
product repository's lock file, which is authoritative and current — a version
table in a specification is stale the week after it is written, and the product
repository already has one that proves the point
([provenance.md](provenance.md#where-sources-disagreed)).

## Related

- [provenance.md](provenance.md) · [open-questions.md](open-questions.md)
- [40-quality/security.md](../40-quality/security.md)
