# Bank coverage

**Status:** Accepted

Which banks Beatrax can read, and on what evidence.

Beatrax does not integrate with banks. It reads **statement files**, so the
question is never "is this bank supported?" but "does this bank export a format
Beatrax parses?" ([A1](../10-functional/features/a-ingestion/a1-source-formats.md)).
That makes the answer for most of Europe *yes*, because CAMT.053 and MT940 are
standards rather than per-bank integrations.

This page is a reference list, not a compatibility guarantee. It is organised
by how strong the evidence is, and the distinction matters more than the names.

## The two tiers

| Tier | What it means |
|------|---------------|
| **Verified** | A shape Beatrax explicitly recognises, with an adapter or a header profile and tests behind it. Detected automatically on upload. |
| **Expected** | The institution publishes CAMT.053 and/or MT940 to customers, which Beatrax parses generically. Not individually tested by the maintainers. |

An **Expected** entry that does not work is a bug worth reporting — a parse
failure on a conforming file is a defect, not an unsupported bank. Corrections
to this list are welcome from anyone who has actually tried it; that is the
only way the tier of an entry ever changes.

## Verified

| Institution | Country | Formats |
|-------------|---------|---------|
| ASN Bank | NL | CAMT.053, MT940, CSV (own shape) |
| ING | NL | CSV (own shape), CAMT.053, MT940 |
| International Card Services (ICS) | NL | Monthly PDF statements |
| N26 | DE / EU | CSV (own shape) |
| Revolut | EU / UK | CSV (own shape) |
| PayPal | International | Transaction details CSV |

## Expected — reads via CAMT.053 or MT940

Grouped by country. Inclusion means the institution documents a CAMT.053 or
MT940 export for account holders; availability sometimes differs between
personal and business products, and between a bank and its subsidiaries.

### Netherlands

ABN AMRO · Rabobank · SNS · RegioBank · Triodos Bank · Knab · bunq ·
Van Lanschot · NIBC

### Belgium

KBC · Belfius · BNP Paribas Fortis · ING Belgium · Argenta · Crelan · AXA Bank

### Germany

Deutsche Bank · Commerzbank · the Sparkassen · the Volksbanken and
Raiffeisenbanken · DKB · Postbank · comdirect · GLS Bank · Triodos Germany

### Austria

Erste Bank and the Sparkassen · Raiffeisen · Bank Austria · BAWAG P.S.K. ·
Oberbank

### France

BNP Paribas · Crédit Agricole · Société Générale · Crédit Mutuel · La Banque
Postale · LCL

### Spain

Santander · BBVA · CaixaBank · Banco Sabadell · Bankinter

### Italy

Intesa Sanpaolo · UniCredit · Banco BPM · BPER Banca

### Nordics

Nordea · Danske Bank · SEB · Swedbank · Handelsbanken · DNB · OP Financial
Group

### Switzerland

UBS · PostFinance · the Cantonal banks · Raiffeisen Switzerland

### Ireland

Bank of Ireland · AIB · Permanent TSB

### Poland, Czechia, and Central Europe

PKO Bank Polski · mBank · ING Bank Śląski · Santander Bank Polska ·
Česká spořitelna · Komerční banka · ČSOB · OTP Bank

### Portugal, Greece, and the rest of the euro area

Millennium BCP · Caixa Geral de Depósitos · Novo Banco · Alpha Bank ·
Eurobank · National Bank of Greece · Bank of Cyprus · Luminor · SEB Baltics

## The United Kingdom

MT940 is available from the business products of the large UK banks
(Barclays, HSBC, Lloyds, NatWest, Santander UK). Personal current accounts
generally export CSV instead, in per-bank shapes that Beatrax reads only where
someone has contributed the header profile. The UK is therefore weaker
territory than the euro area, and honestly so.

## Outside Europe

There is no CAMT.053 or MT940 convention to lean on. Generic CSV import works,
but the column mapping is the user's to do, and Beatrax's counterparty and
chain resolution assume IBAN-shaped identifiers throughout. Treat non-European
use as possible rather than supported.

## How an entry gets promoted

A bank moves from **Expected** to **Verified** when a header profile or adapter
lands with a fixture and a test, in the same way any other ingestion shape does.
Contributing a real export file (with amounts and identifiers redacted) is the
useful first step.

## Related

- [A1 — source formats](../10-functional/features/a-ingestion/a1-source-formats.md)
- [A2 — import wizard](../10-functional/features/a-ingestion/a2-import-wizard.md)
- [references.md](references.md) — the ISO 20022 and MT940 standards themselves
