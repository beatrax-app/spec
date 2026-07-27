# Glossary

**Status:** Accepted

Terms this spec uses precisely. Where a word has a loose everyday meaning and a
narrow beatrax meaning, the narrow one is what the spec means.

## Product and domain

| Term | Meaning |
|------|---------|
| **Account** | A per-user record for one bank account, PayPal balance, or credit card. Carries a starting balance so forecasts have a bootstrap point. Card and PayPal accounts get synthetic IBAN placeholders (`ICS-CARD`, `PAYPAL`, `MIG…`) because the source format carries no real one. |
| **Transaction** | One row in the canonical ledger. Immutable when imported; user-created cash-book rows are deletable. |
| **Counterparty** | The merchant, bank, person, government body, or self-account on the other side of a transaction. Resolved from the raw description and IBAN, then reused. |
| **Chain** | A resolved link between two transactions that are the same money seen from two accounts — PayPal→bank, or card→bank via a bulk settlement. Recorded in `chain_links`, indexed on `transactions.pair_transaction_id`. |
| **Funding chain** | The PayPal shape specifically: a merchant-side debit on PayPal plus the funding-side debit on the bank or card PayPal pulled from. |
| **Bulk settlement** | The single monthly SEPA debit an issuer (ICS) takes from the bank to cover a whole card statement. Decomposing it into its per-line card transactions is one of the two chain shapes. |
| **Candidate** | A match the resolver found but is not confident enough to write as confirmed. Surfaces in a review queue for the user to confirm or reject. Confirming teaches the alias bridge. |
| **Alias bridge** | The `known_counterparty_ibans` table: a per-user learnt mapping from an IBAN observed on one account to the account it actually belongs to. It is what makes resolution sharpen over time. |
| **Recurring series** | A detected repeating charge — same counterparty, comparable amount, regular cadence. Always suggested, never auto-applied. |
| **Drift** | A recurring series whose latest charge moved outside the user's threshold. Produces a drift alert with prior→current amounts and annualised impact. |
| **Anomaly** | A single charge that is unusual against the user's own baseline: much larger than typical for that merchant or category, large at a brand-new merchant, or an apparent duplicate inside a short window. |
| **Envelope** | A category with a monthly assigned amount in the zero-based budget. Balances roll over month to month; overspend is handled explicitly. |
| **Pot** | A named virtual sub-balance carved out of one real account. Has no stored balance column — its balance is the signed sum of its movement rows. |
| **Ready to assign** | The zero-based budgeting pool: income received minus everything assigned to envelopes this month. The month is budgeted when it reaches zero. |
| **Cleared / reconciled** | A transaction's reconciliation status. `uncleared` → `cleared` → `reconciled`. Reconciled rows are locked against mutation. |
| **Split** | One transaction divided into two or more category legs whose signed amounts sum exactly to the parent. Roll-ups count the legs, never both legs and parent. |
| **Triage** | Any queue where the system defers to the user: uncategorised transactions, unknown counterparties, chain candidates, recurring suggestions. |
| **Cash book** | Manual entry of cash and other off-bank spending into the same ledger, through the same recording pipeline, against a synthetic per-user Cash account. |

## Ingestion

| Term | Meaning |
|------|---------|
| **Source format** | One of the declared input shapes: `asn-csv`, `asn-camt053`, `asn-mt940`, `ics-pdf`, `paypal-csv`, plus generic CSV presets, `.eml`, `.mbox`, and the open-banking adapter. Declared by the user; never sniffed from content. |
| **CAMT.053** | The ISO 20022 bank-to-customer statement XML. The canonical bank source when a bank offers it. |
| **MT940** | The legacy SWIFT statement format. Fallback when CAMT.053 is unavailable. |
| **Adapter** | The per-format parser. Streams typed source rows; never touches the database. |
| **Canonical transaction** | The single normalised DTO every source format converges on before the ledger sees it. |
| **Fingerprint** | The v3 idempotency key: a hash over user, account, dates, amount, currency, and normalised counterparty. The unique index on it is what makes re-import a no-op. |
| **Preview / confirm** | The two-phase import. Preview runs every stage and writes nothing; confirm is the single write boundary. |
| **NEW / DUPLICATE / ENRICHED / ERROR** | The four dispositions a preview row can carry. `ENRICHED` means a stronger source arrived for a row that already exists. |
| **Enrichment** | An update to an existing row from a stronger later source. Appends provenance to `enriched_from`; never overwrites it. |
| **Receipt matcher** | A parser that recognises a specific sender's email receipt (PayPal, ICS, Google Play) and extracts its per-line breakdown and chain hints. |
| **Statement summary** | The statement-level metadata CAMT.053 and MT940 carry — opening balance, closing balance, period dates — that the per-row pipeline does not see. |

## Sync and cryptography

| Term | Meaning |
|------|---------|
| **Op-log** | The append-only, per-device-signed log of every local mutation. The source of truth; SQLite is its materialised view. |
| **HLC** | Hybrid Logical Clock. A `(physical-millis, counter)` pair giving a total order across devices without a coordinating server. |
| **Materialised view** | The claim that the SQLite database can be deterministically rebuilt by replaying the merged op-log from scratch. |
| **LWW-per-field** | Last-writer-wins, resolved independently per column rather than per row, so two devices editing different fields of the same row both keep their edit. |
| **G-Counter / OR-Set** | The two non-LWW CRDT strategies in the merge registry, for monotonic counters and observed-remove sets respectively. |
| **Tombstone** | A delete represented as an op-log entry rather than a row removal, so the delete itself converges. |
| **Quarantine** | Where the replayer puts an op it refuses to apply — wrong user, unknown device key, forged signature, unknown table, undecryptable payload. It logs rather than throwing. |
| **Device identity** | The long-term Ed25519 signing keypair plus X25519 key-agreement keypair a device generates on first run. Private keys never leave the device. |
| **Safety number** | A short human-verifiable fingerprint derived from two devices' public identities, shown on both screens during pairing. |
| **Word code** | The BIP39-wordlist typed fallback when a QR code cannot be scanned. |
| **Noise XX / Noise IK** | The two handshake patterns used for the mutually-authenticated, forward-secret transport session. |
| **Zero-knowledge relay** | The store-and-forward fallback for offline peers. Holds opaque ciphertext blobs, performs no cryptography, and can address a mailbox but never read one. |
| **GDK** | Group Data Key. The per-user symmetric key that encrypts sensitive columns at rest. Wrapped per device; released by the app-lock. |
| **Epoch** | One generation of the GDK. Rotation mints a new epoch; the keyring is append-only so older ciphertext stays readable. |
| **Rekey / revocation** | Removing a device: revoke its trust, mint a fresh epoch, and re-wrap that epoch to every remaining confirmed device. |
| **App-lock** | The PIN or biometric gate, separate from account login, whose unlock releases the at-rest key. |

## Governance and process

| Term | Meaning |
|------|---------|
| **Canonical spec** | This repository. No behavioural change lands in any org repo without citing an identifier that already exists here. |
| **Requirement ID** | `<feature>-R<n>`, e.g. `A2-R4`. Permanent, never reused, never renumbered. Lives inside its feature doc. |
| **ADR** | Architecture Decision Record. Immutable once accepted; superseded by a new one rather than edited. |
| **`Spec:` trailer** | The commit and PR-body line that cites the identifiers a change implements. The governance gate reads it. |
| **DCO** | Developer Certificate of Origin. Every commit carries a `Signed-off-by` matching its author. |
| **Version manifest** | A TOML file under `70-operations/versions/` locking the requirement IDs a release is committed to. |
| **Landed-but-unreleased** | Work merged into the development line and covered by tests, but not yet in a tagged release. The bulk of v2.0 is currently in this state — see the [roadmap](roadmap.md). |

## Deliberately not used

| Avoid | Use instead | Why |
|-------|-------------|-----|
| "open source" | "source-available" | The Hippocratic License 3.0 is not OSI-approved. Saying otherwise sets a false expectation. See [the rationale](../90-appendix/license-rationale.md). |
| "cloud sync" | "peer-to-peer device sync" | There is no cloud that can read anything. |
| "server" (for the relay) | "relay" | It stores and forwards ciphertext; calling it a server implies it holds state it can use. |
| "AI categorisation" | "rule and memory categorisation" | There is no model. The matchers are deterministic. |
| "diederik" | "beatrax" | The internal codename appears in some historical artefacts and command names. The product is beatrax. |
