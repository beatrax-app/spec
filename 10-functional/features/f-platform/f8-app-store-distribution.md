# F8 — App-store distribution

**Status:** Accepted · **Area:** F — Platform

---

## Purpose

Direct download reaches people who will fetch an installer and click past a
security dialogue. It does not reach a phone. The mobile client
([E5](../e-sync/e5-mobile-peer.md)) is the first surface where a vendor's store
is the only realistic way in, and a store is not a mirror of the release page: it
is a reviewer, a signing identity somebody has to hold and renew, and a set of
declarations about the product that are legally the developer's.

This feature owns what has to be true about Beatrax before those declarations can
be made **honestly** — which is the whole difficulty, because the forms are
written for a product with a server, and this one has none.

## Behaviour

### Scope

Two stores: the **iOS App Store** and **Google Play**, for the mobile client
only. Direct download stays the channel for the desktop bundle
([F1](f1-desktop-shell.md)) and is not retired by either listing.

The **Mac App Store** and the **Microsoft Store** are out of scope. The desktop
bundle embeds a static interpreter and relies on two hardened-runtime
relaxations to map it; the sandbox a Mac App Store build must run under ignores
one of them, so that listing needs a different runtime strategy rather than a
submission. Recorded here so the question is closed rather than reopened every
cycle.

### The paid-identity trade is already made

Store distribution was recorded as possibly forcing paid signing identities
"which the licence rationale currently declines". That framing no longer matches
the pipeline: the desktop release refuses to publish without a platform developer
identity and notarisation credentials, the Windows build signs through a hosted
signing service, and the mobile builds sign from a distribution certificate
against a registered team. Every one of those is a paid, renewable identity,
already held.

What the licence rationale describes — shipping unsigned and explaining the
dialogue — is the history, not the present. The specification has to say which
identities are held and when each expires, because an expiry nobody is watching
stops releases, and a store listing turns that from an inconvenience into an
outage.

### The upload key is a one-way door

One store holds the key that signs what users install, and enrolment happens once
per application with no way back. Enrol with a freshly generated key and every
existing direct-download install is signed by a stranger: it cannot be upgraded,
only uninstalled and replaced. For a local-first product an uninstall is not an
inconvenience — the ledger is the only copy, and it goes with the application.

So the existing release key has to be the one the store signs with, transferred
**before** the first rollout rather than after somebody notices.

### What the forms assume, and what is true here

Both stores' privacy forms are built around a developer who receives data. No
Beatrax-operated service exists to receive any, so the honest answer to
"collected" and "shared" is nothing — but that answer is only defensible if it is
derived from the enumerated outbound surface ([G1](../g-ux/g1-privacy.md)) rather
than asserted. Every optional feature the user turns on sends data to a third
party **the user chose and holds the credentials for**: their own mailbox, their
own aggregator, a relay they configure. The developer is not in that path, and
both stores exempt data that only ever moves between the device and a service the
user already has.

The declarations therefore have to be re-derived whenever that catalogue changes.
A store answer that has drifted from G1 is a false statement to a regulator, not
a stale document.

### Nothing may ride along in the bundle

A store artefact is built by a machine that also holds signing keys, a developer's
own ledger, and a development environment. None of those may reach a user, and
the check is to open the artefact — an exclusion list that names the wrong file,
or matches only at the root of a tree, fails silently and looks exactly like one
that works.

The same applies to the environment the bundle carries. A build that resolves to
development settings hands the first account the developer console
([F5](f5-dev-console.md)), and on a phone the first account is the only account.

### Accounts exist; they are local

The product has accounts — an owner created on first launch, optionally a partner
— and separately an app-lock. Nothing about either leaves the device, and there is
no server that could delete anything remotely.

Both stores require an application offering account creation to offer account
deletion, and neither distinguishes a local account from a hosted one. Beatrax
does offer it: in the application, confirmed by password, available to every
account rather than only the administrator, and removing the account's rows, its
files, its recovery codes, its sync identity and its keyring — so the deleted
account cannot be pushed back by a peer, because the device no longer holds what
syncing requires. What deletion cannot do is reach a paired device, and the copy
says so instead of implying a reach the product does not have.

### The store is the update channel

Beatrax updates itself on the desktop ([F6](f6-updates.md)). A store build must
not: both stores forbid an application replacing its own executable code outside
the store, and the mobile client's answer is already to name the store instead of
offering a banner. That has to hold by construction rather than by copy — no store
build may carry a reachable path that downloads and installs application code,
and no surface may describe one.

### Declarations that are not optional

- A **privacy manifest** naming every required-reason API category the shipped
  binary trips, and none it does not. The check reads symbols, not source, so the
  interpreter's own file-metadata and free-space calls are what decide it.
- An **encryption declaration**. The cryptography is real and is not the operating
  system's, which fixes the answer and carries a national declaration with it
  before that country can be a release territory.
- **Permission purpose strings** that name the product and the use actually made.
  A string inherited from a plugin describes that plugin's product, and one that
  names a capability the application does not have is simply untrue.
- **Permissions** on both platforms, where every one requested must have a named
  consumer in shipped code — and the merged artefact, not the source manifest, is
  what the store reads.
- A **financial-features** answer. Beatrax reads files the user supplies and,
  optionally, an account-information feed the user's own key unlocks. It moves no
  money, holds no funds, lends nothing and files nothing.
- An **application category**, which is not optional and cannot be blank.

### What review needs to see

A reviewer installing the application gets an empty ledger, a signup screen that
closes behind them, and an app-lock they set themselves. There is no credential to
hand over, so the notes have to describe the sequence specifically rather than
leave a reviewer to discover it, and the sample-data control has to be named
rather than hidden.

The sample data offered must never be a real household's.

### Store copy is bound by the same honesty rule

A listing is product copy. Everything [G1](../g-ux/g1-privacy.md) requires the
application to state plainly — that at-rest encryption leaves amounts, dates and
the search index readable, what a relay observes, that a paired device is trusted
— constrains what a listing may claim, and so does what actually works on each
platform. A capability that is dead on one of them may not be described as though
it were not.

## Edge cases

| Situation | Behaviour |
|-----------|-----------|
| A signing identity expiring | Recorded with its expiry; a lapse blocks release rather than shipping unsigned. |
| Enrolling with a newly generated upload key | Refused: existing installs could not upgrade, and the ledger is the only copy. |
| A required-reason category the binary trips but the manifest omits | The submission is rejected; the manifest is derived from symbols, not from intent. |
| A category the binary does not trip | Not declared; claiming a reason for an unused call is its own false statement. |
| A permission arriving from a dependency's manifest | Given a named consumer, or removed at merge. |
| A purpose string inherited from a plugin | Replaced; it describes somebody else's product. |
| The outbound-call catalogue changing | The store privacy declarations are re-derived before the next submission. |
| A store build reaching an update-install path | A release blocker, not a defect. |
| A reviewer creating the first account | Gets administrator rights, including the developer console; the console is closed on a store build, and the sequence is in the notes. |
| A partner account wanting to leave | Deletes its own account without the administrator. |
| A deleted account on a device still paired | Cannot return by sync; the device no longer holds the identity, log or keyring. |
| A paired device still holding the data | Stated plainly; deletion is device-scoped and says so. |
| An optional feature off | Nothing is sent, and the declaration says so. |
| A capability that does not work on one platform | Not claimed in that platform's listing. |

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **F8-R1** | Store distribution MUST NOT retire direct download, and every release MUST continue to publish the signed manifest and checksums. |
| **F8-R2** | Every store artefact MUST be signed by a recorded identity, and a build MUST fail rather than emit an unsigned or ad-hoc-signed one. |
| **F8-R3** | Every signing identity the release pipeline requires MUST be recorded with its expiry, and the specification's account of which identities are held MUST match what the pipeline requires. |
| **F8-R4** | The store signing key MUST be the existing release key, enrolled before the first production or open-testing rollout, so an existing installation upgrades rather than needing a reinstall. |
| **F8-R5** | Every submission MUST be produced in the artefact shape its store requires, and the pipeline MUST produce that shape rather than only the sideloadable one. |
| **F8-R6** | No signing key, credential, or other secret may appear inside a shipped mobile bundle, verified by inspecting the built artefact rather than the exclusion rules. |
| **F8-R7** | No database carrying data may ship inside a mobile bundle, verified by inspecting the built artefact. |
| **F8-R8** | Every shipped mobile bundle MUST resolve to production environment settings, and the developer console MUST NOT be reachable on one. |
| **F8-R9** | Every iOS submission MUST carry a privacy manifest declaring exactly the required-reason API categories the shipped binary's symbols trip, and no others. |
| **F8-R10** | The privacy manifest MUST declare tracking as false, and MUST omit rather than empty the collected-data-types and tracking-domains keys. |
| **F8-R11** | Every iOS submission MUST declare non-exempt encryption, and a country requiring its own encryption declaration MUST NOT be a release territory until that declaration is filed and its code ships in the bundle. |
| **F8-R12** | Every permission purpose string MUST name Beatrax and the use the application actually makes, and MUST NOT survive from a dependency's own text. |
| **F8-R13** | Every permission purpose string MUST be translated into every language the interface ships in. |
| **F8-R14** | The application category MUST be declared in the bundle and MUST NOT be blank. |
| **F8-R15** | Every store privacy declaration MUST be derived from the outbound-call catalogue, and MUST be re-derived before any submission that follows a change to it. |
| **F8-R16** | The financial-features declaration MUST record that the application provides no financial feature, and any change to that answer MUST be a specification change first. |
| **F8-R17** | The application MUST target the platform API level its store requires for a new submission, and that level MUST be pinned in this product rather than inherited from a dependency's default. |
| **F8-R18** | Every permission the shipped artefact requests MUST have a named consumer in shipped code, verified against the merged artefact rather than the source manifest. |
| **F8-R19** | No permission a store restricts to a use Beatrax does not make may be requested. |
| **F8-R20** | No store build may carry a reachable path that downloads or installs application code. |
| **F8-R21** | A store build MUST name the store as its update channel, and MUST NOT present the desktop's self-update copy or controls on any surface. A surface that switches its sentence on the platform but renders the control unconditionally does not satisfy this. |
| **F8-R22** | No dependency reaching a shipped mobile artefact may carry analytics, telemetry, or crash reporting, enforced by test across the mobile plugin manifests as well as the package manifests. |
| **F8-R23** | The review notes MUST describe, specifically, that the first launch creates a local account, that signup closes afterwards, that the app-lock credential is the reviewer's own, and how to load sample data. |
| **F8-R24** | Sample data offered for review MUST be reachable through an explicit control and MUST NOT be any real person's data. |
| **F8-R25** | Account deletion MUST be reachable in the application by every account that can be created, MUST remove that account's sync identity, operation log and keyring so a peer cannot restore it, and MUST state that a paired device keeps its own copy. |
| **F8-R26** | A store listing MUST NOT claim a protection the product does not provide, MUST NOT describe a smaller outbound surface than the catalogue, and MUST NOT describe a capability that does not work on that platform. |

## Related

- [F1 Desktop shell and packaging](f1-desktop-shell.md) — the direct-download channel this is additive to
- [F6 Updates and release verification](f6-updates.md) · [F7 Data locations, export and deletion](f7-data-locations.md)
- [E5 The mobile client as a synced peer](../e-sync/e5-mobile-peer.md)
- [G1 Privacy stance](../g-ux/g1-privacy.md) — the catalogue every declaration is derived from
- [F3 Authentication, app-lock and recovery](f3-auth-and-app-lock.md) · [F5 Developer mode and the dev console](f5-dev-console.md)
- [20-architecture/platform-matrix.md](../../../20-architecture/platform-matrix.md) · [90-appendix/license-rationale.md](../../../90-appendix/license-rationale.md)
