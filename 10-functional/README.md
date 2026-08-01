# Functional specification

**Status:** Accepted

What beatrax does, expressed as behaviour a user can observe and a test can
check.

| Page | Contents |
|------|----------|
| [features/](features/) | Fifty-two features across seven areas, each with numbered requirements |
| [journeys/](journeys/) | Seven end-to-end paths, each naming the features it exercises |

## The contract

This section is **what the technical specification is written against**. Every
architectural and implementation decision must trace to a requirement here, not
the other way round.

A technical choice citing no requirement is unjustified and should be challenged
in review ([50-governance/canonical-spec.md](../50-governance/canonical-spec.md)).

## The areas

| Area | Covers |
|------|--------|
| **[A — Ingestion](features/a-ingestion/)** | How money gets in: parsers, the import pipeline, idempotency, receipts, open banking, cash, migration |
| **[B — The ledger](features/b-ledger/)** | The canonical record: transactions, categorisation, rules, counterparties, chains, transfers, splits, reconciliation, search, currency |
| **[C — Insight](features/c-insight/)** | What beatrax notices: the dashboard, recurring, drift, anomalies, forecasting, the calendar, reports, notifications |
| **[D — Money management](features/d-money/)** | Envelope budgeting, goals, pots, tax |
| **[E — Sync](features/e-sync/)** | The v2.0 headline: change capture, pairing, transport, at-rest encryption, the mobile peer, status |
| **[F — Platform](features/f-platform/)** | The shell, setup, authentication, backup, the dev console, updates, data locations |
| **[G — Cross-cutting UX](features/g-ux/)** | Properties every feature must exhibit: privacy, errors, accessibility, responsiveness, language, keyboard |

## Traceability

```text
Journey  ──exercises──▶  Feature  ──contains──▶  Requirement  ◀──implements──  Code
                                                      ▲
                                                      └──cites──  Architecture doc
```

All three links are checked by CI.

## Nothing here was invented

Every requirement derives from the product repository — its shipped code, its
documentation, its planning corpus, or its history. Where a source is silent or
two sources disagree, the document says so under an explicit open-question
heading rather than guessing
([90-appendix/provenance.md](../90-appendix/provenance.md)).

## Related

- [00-overview/vision.md](../00-overview/vision.md) — the principles these features express
- [20-architecture/](../20-architecture/) — the shape they produce
- [70-operations/versions/](../70-operations/versions/) — which requirements a release locks
