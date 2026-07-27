# Frequently asked questions

**Status:** Accepted

The questions people actually ask before installing beatrax, answered once so
the website, the README, and any future support material all say the same
thing.

Answers are deliberately short and self-contained: the website emits them as
structured data, where each answer has to stand alone without its surrounding
context. Where an answer states a limitation, that limitation is the point —
these are the questions where a reassuring half-answer is worse than none.

## The basics

### What does beatrax cost?

Nothing. There is no paid tier, no trial, no licence key and no upsell. There
is also no service to run, which is why there is nothing to bill for.

### Do I need an account?

No. There is no sign-up, no login to a server, and no password to reset,
because there is no server holding anything. You install the application and
it works.

### Does it work offline?

Yes, completely. Every core feature — import, categorisation, budgets,
forecasting, reports, search — runs with no network at all. Only the optional
connectors reach outside your machine.

### Which platforms does it run on?

macOS, Windows and Linux as a desktop application. The interface is also
installable on a phone as a progressive web app, and full mobile clients are
in development for v2.0.

### Is my data sent anywhere?

No. There is no telemetry, no analytics, no crash reporting and no hosted copy
of your ledger. The database is a SQLite file in your own application-support
directory.

## Getting your transactions in

### Does beatrax connect to my bank?

Not by default. You export a statement from your bank and drop the file in.
There is an optional open-banking connector, off by default, which needs your
own aggregator API key — but file import is the primary path, deliberately.

### Do you need my banking password?

Never. beatrax does no screen-scraping and never logs in as you. It reads
files your bank already gives you.

### Which file formats does it read?

CAMT.053, MT940 and CSV from banks, PDF statements from ICS credit cards,
PayPal transaction exports, and email receipts from Gmail or Microsoft if you
connect a mailbox.

### Will it work with my bank?

If your bank exports CAMT.053 or MT940 — which most European banks do — then
yes. A handful of banks additionally have their CSV shape recognised
automatically. The banks and formats page lists what is verified and what is
expected to work.

### What happens if I import the same file twice?

Nothing. Every row is fingerprinted, so re-importing a statement you have
already imported changes nothing and creates no duplicates.

### Can I import my budget from another app?

Yes, from YNAB, nYNAB and Actual Budget. Categories, budget history,
transactions, splits and cleared status come across, and anything that cannot
be mapped is reported rather than dropped silently.

## Sync and multiple devices

### How does sync work without a server?

Your devices talk directly to each other. Each holds a full encrypted copy and
they reconcile through a signed log of changes. When both are on the same
network they sync directly; when one is asleep, changes wait in a relay that
only ever holds encrypted data it cannot read.

### Can you read my data when it syncs?

No. Sync is end-to-end encrypted between devices you have paired and verified
yourself. The relay holds ciphertext with no key, and there is no beatrax
account or server that ever sees your ledger.

### Can two people share a ledger?

Two devices belonging to the same person sync today. A genuine
shared-household surface, with separate users and permissions, is a deliberate
future milestone rather than something that ships now.

### What if I lose a device?

Remove it from your device list. That rotates the shared key and re-wraps it
to the devices you kept, so the removed one cannot read anything sent
afterwards.

## Safety and the awkward questions

### What happens if I lose everything?

The data is gone, and nobody can recover it — which is the same property that
means nobody can hand it to anyone else. beatrax can produce an encrypted
backup and reminds you to; where you keep it is your decision.

### Is beatrax open source?

The source is public, buildable and modifiable. The licence adds ethical-use
clauses, which is the one thing that prevents it being certified by the Open
Source Initiative. Both of those are true and the licence page explains the
trade rather than picking the flattering half.

### Can I use it for my business?

Yes, subject to the licence's ethical-use clauses. Be aware it is a personal
ledger rather than bookkeeping software — no double-entry accounting, no VAT
return, no invoicing.

### What happens if the project stops?

The build on your disk keeps working, the data is a plain SQLite file you can
read with any tool, and the source is public and forkable. There is no server
to switch off and no subscription to cancel.

### Who is behind it?

It is built by NightWorks.io, and it is a small project rather than a funded
company. That is the honest trade against the paid alternatives: no
subscription, and also no support desk.

## Related

- [../00-overview/vision.md](../00-overview/vision.md) — the principles these answers rest on
- [bank-coverage.md](bank-coverage.md) — the long answer to "will it work with my bank?"
- [license-rationale.md](license-rationale.md) — the long answer to "is it open source?"
