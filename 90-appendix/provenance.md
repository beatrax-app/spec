# Provenance

**Status:** Accepted

Where the content of this specification came from, and what was deliberately
left behind.

This page exists because a specification written **after** the product it
describes has an obvious failure mode: inventing requirements that read well and
were never true. The defence is to say where every part came from.

## The sources

| Source | What it gave |
|--------|--------------|
| The product repository's decision records | [ADR-0001](../00-overview/decisions/0001-modular-architecture.md)–[ADR-0011](../00-overview/decisions/0011-code-comment-policy.md), ported without changing their decisions |
| Its architecture documentation | [20-architecture](../20-architecture/) — module boundaries, the data model, the ingestion pipeline, chain resolution, categorisation |
| Its per-module documentation | The behaviour, states, edge cases, and behavioural contracts throughout [10-functional](../10-functional/features/) |
| Its conventions documentation | [40-quality/code-comments.md](../40-quality/code-comments.md), including the mechanical and judgment rule tables |
| Its pipeline documentation | [40-quality/ci-cd.md](../40-quality/ci-cd.md), branch protection, the release sequence |
| Its legal documentation | [90-appendix/license-rationale.md](license-rationale.md), [90-appendix/data-retention.md](data-retention.md) |
| Its research and history documentation | Constraints and hazards that became requirements |
| Its planning corpus | The [roadmap](../00-overview/roadmap.md)'s three buckets, the requirement inventory, the deferred register |
| Its git history, tags, and releases | The release baseline — verified rather than assumed |
| Its readme, notice, security policy, and contributing guide | The voice, the licence posture, [30-repos](../30-repos/) |
| The module tree | The functional map, [20-architecture/component-model.md](../20-architecture/component-model.md) |
| The route surface | The navigation map in [10-functional/features/README.md](../10-functional/features/README.md) |

## What was verified rather than assumed

The release baseline. The latest tag was checked against the repository's actual
tags and branches rather than taken from a planning document:

- Seven tags exist; **`v1.3.0`**, dated 2026-06-14, is the newest and sits on the
  default branch.
- The former development line carried substantial merged work with no tag.
- That line is being promoted to **v2.0** and retired as a branch.

The [roadmap](../00-overview/roadmap.md) is built on that verification, and it
keeps shipped, landed-but-unreleased, and outstanding strictly apart.

## What was deliberately left in the product repository

Not everything belongs here. The split is **what and why** versus **where in the
code**.

| Left behind | Why |
|-------------|-----|
| Per-module implementation maps — which class, which file, which table | They change with every refactor. This specification names behaviour and contracts; the code is where the code is. |
| Local development setup and troubleshooting | Changes with the toolchain and must be tested against it. |
| Executable runbooks with real commands and flags | Same. [70-operations/runbooks.md](../70-operations/runbooks.md) states what each must guarantee; the product states how. |
| The release notes | They are generated from the commit history and belong with the releases. |
| Per-module test-running instructions | Toolchain detail. |
| Design explorations and interface sketches | Distilled into the shipped surfaces and into [60-brand](../60-brand/). |
| The internal codename | Not the product's name. Recorded in the [glossary](../00-overview/glossary.md#deliberately-not-used) so nobody reintroduces it. |
| Workflow scaffolding — plan files, discussion logs, pattern maps, review transcripts | Artefacts of a process, not reference documentation. The decisions they produced are in the decision records; the acceptance criteria they produced are in the feature docs. |
| Phase numbers | Identifiers here are requirements and decision records. Phase numbers have no relationship to them and reconciling the two would be noise ([roadmap](../00-overview/roadmap.md#open-questions)). |

## What was added rather than ported

The decision records from
[ADR-0012](../00-overview/decisions/0012-action-pinning.md) onward were written
for this specification. **None invents a decision.** Each records one already
made and evidenced in the product's code, its pipeline configuration, its
planning corpus, or a call the product owner took and this repository was asked
to record: action pinning, the organisation split, the merge model, the sync
topology, the transport, the envelope cutover, the plaintext set, the publish
asymmetry, the connector's constraints, and the store-distribution scope.

The `GOV-R`, `ARCH-R`, `Q-R`, `DES-R`, `OPS-R`, and `REPO-R` namespaces are new,
because the organisation is new. They codify practices already in force.

## Where sources disagreed

Recorded rather than silently resolved:

| Disagreement | Resolution |
|--------------|------------|
| The product's release-cadence document still describes a pre-public version series and names a graduation tag that shipped four releases ago | It is **stale**. [70-operations/releasing.md](../70-operations/releasing.md) is current; the product page needs updating or deleting ([roadmap](../00-overview/roadmap.md#conflicting-release-cadence-documentation)). |
| A planning document's headline requirement count disagreed with the count of identifiers it listed | Noted in the source itself. Neither number is used here; this specification counts its own. |
| Two phase entries covered the same comment-policy work, one recorded complete and one not started | The work is done; the duplicate entry is a planning artefact. Not carried over. |
| A dependency-version table in the product's stack documentation predates several upgrades | Superseded by the lock file. This specification names versions only where a decision depends on them. |
| This specification disagreed with **itself** about paid signing identities: [F8](../10-functional/features/f-platform/f8-app-store-distribution.md) recorded them as held and required, while [license-rationale.md](license-rationale.md), [20-architecture/platform-matrix.md](../20-architecture/platform-matrix.md), [F6](../10-functional/features/f-platform/f6-updates.md) and [J1](../10-functional/journeys/j1-first-run.md) all stated the opposite | **F8 is right**, checked against the release workflow, which refuses to publish an unsigned macOS or Windows build. All four are corrected as of 2026-09-05, alongside [ADR-0032](../00-overview/decisions/0032-all-four-stores-additive-to-direct-download.md). Correcting F6 meant restating what its verification chain *is*: the platform signature and the signed manifest are **independent** signals covering different moments — the platform checks an installer a person fetched, the manifest chain is the only thing covering an automatic update, and Linux still ships unsigned with nothing but the manifest. F6 gained `F6-R17` for the part that was load-bearing and unstated: the update path may not lean on the operating system's signature, and the framework behaviours that would are turned off by a build step that fails rather than ship one where the patch did not apply. Two further pages carried the same claim and had not been noticed at all — [30-repos/website.md](../30-repos/website.md), whose `REPO-R42` **required** the site to state that installers are unsigned, and [60-brand/surface-mapping.md](../60-brand/surface-mapping.md). Both are corrected. |
| [E5](../10-functional/features/e-sync/e5-mobile-peer.md) disagreed with itself: its open-questions section held three hardware gates open while a note under its own requirements table, and the [roadmap](../00-overview/roadmap.md), recorded all three as taken | **The open-questions section was stale.** `E5-R23` and `E5-R24` were taken on 2026-09-04 and `E5-R25` on 2026-09-05, on an iPhone 12 mini running iOS 26.5.2. A finished question is not moved to an accepted tension, it goes ([open-questions.md](open-questions.md)); the record of what the runs found stays under the requirements table where it was. Two questions took the section's place, and neither is the old one wearing a new coat: which file the iOS backup exclusion actually covers, and whether v2.0 ships without an Android device pass. |
| Three pages — [E5](../10-functional/features/e-sync/e5-mobile-peer.md), [E4](../10-functional/features/e-sync/e4-at-rest-encryption.md) and [40-quality/security.md](../40-quality/security.md) — stated that no mobile backup-exclusion bridge exists | **All three were wrong.** One build script writes both platforms' halves and the mobile build applies it; on Android the packaging command the release pipeline runs applies it, so it reaches every release build. `E4-R24` required *the absence* to be documented and there is no absence left, so it is marked withdrawn in place rather than quietly satisfied, and `E4-R25` carries what it was for: the bridge's reach, per platform, including what it does **not** cover. What the correction did not settle is whether the iOS exclusion reaches the file the app opens — it is set on the application-support tree while the bootstrap repoints the connection under the documents directory — so that is filed as an open question rather than answered. |
| Two decision records still describe the connector's secrets store as installation-wide, holding one live aggregator session, and not keyed per user — [ADR-0008](../00-overview/decisions/0008-multi-user-belongstouser.md) as a negative consequence and the condition its *revisit if* turns on, [ADR-0020](../00-overview/decisions/0020-open-banking-byo-key-ais-only.md) as two consequences and two revisit triggers | **Both stopped being true on 2026-09-05**, when `A6-R20` and `A6-R21` were satisfied together; the current state is in [A6](../10-functional/features/a-ingestion/a6-open-banking.md). **Neither record is edited.** [GOV-R9](../50-governance/README.md#the-gov-r-namespace) permits exactly one edit to an accepted record — a supersession stamp — and a stamp needs a superseding decision. Nothing here reverses a decision: ADR-0008's is the `BelongsToUser` trait and ADR-0020's is bring-your-own-key, AIS-only, and both stand as written. Writing a decision record in order to unlock the edit would be a decision record that records no decision, so the two are left as dated accounts of what was true when they were accepted. One consequence of that is worth naming: ADR-0008's revisit condition — the per-user secret-isolation gap becoming a blocker — can no longer fire, and nothing in this repository says so at the record itself. Filed as [an open question](open-questions.md#should-a-decision-record-whose-consequences-have-expired-say-so). |
| [F6-R5](../10-functional/features/f-platform/f6-updates.md#acceptance-criteria) required a preview channel, and the product publishes no manifest for one | **The requirement is not satisfied**, found while checking the signing claim above rather than looked for. The pipeline writes only the `latest` manifest set, for every tag shape, and the channel is fixed in the bundle's environment at build time rather than chosen by the reader. Marked *(Open)* with the gap stated, per the house rule for something not yet satisfied. |

## Open questions carried forward

Every unresolved question found in the sources, or created by this
specification's own scope, is recorded under an explicit heading in the document
it belongs to — never smoothed over
([GOV-R25](../50-governance/README.md#the-gov-r-namespace)).

They are indexed in [open-questions.md](open-questions.md).

## Related

- [00-overview/roadmap.md](../00-overview/roadmap.md) · [open-questions.md](open-questions.md)
- [30-repos/beatrax.md](../30-repos/beatrax.md#what-lives-here-versus-in-the-spec)
- [50-governance/canonical-spec.md](../50-governance/canonical-spec.md)
