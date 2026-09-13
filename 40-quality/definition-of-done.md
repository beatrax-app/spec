# Definition of done

**Status:** Accepted

A change is done when every box below is ticked. Not most of them.

## For any change

- [ ] **It cites a requirement identifier that already exists on the canonical
      spec**, in a commit trailer and in the pull-request body
      ([Q-R23](README.md#the-q-r-namespace)). One narrow exception, for a
      requirement that did not exist when the work merged:
      [below](#when-the-requirement-postdates-the-work).
- [ ] The commit subject is conventional, and every commit carries a sign-off
      matching its author.
- [ ] Formatting, static analysis, and the full test suite pass.
- [ ] Hygiene passes — spelling, links, markdown, workflow lint.
- [ ] Nothing is deferred in a comment
      ([code-comments.md](code-comments.md)). If work remains, the work is not
      done.
- [ ] Nothing in the interface is a placeholder or a control that does nothing
      ([G5](../10-functional/features/g-ux/g5-plain-language.md)).

## For a behavioural change

- [ ] **The specification change merged first.** The implementation cites the
      identifier the specification change created
      ([50-governance/change-lifecycle.md](../50-governance/change-lifecycle.md)).
- [ ] Every new requirement has a test.
- [ ] The commit subject reads as release-note copy, in the user's language,
      saying what changed for them — it is what the release body will carry.
- [ ] The behaviour was walked in a browser, on both desktop and phone widths.

## When the requirement postdates the work

One exception to the citation box above, and it is narrow.

A requirement minted to *describe* code that has already merged cannot be cited
by the change that implemented it. There was no identifier to put in the trailer
when that commit was written, and no later pull request repairs it: the gate
runs per pull request against that pull request's own text, so a citation added
afterwards passes for the later change and leaves the original exactly as
uncited as it was. Amending the merged commit is not the way out either —
published history is not traded for one word.

For that case, the box is ticked by a **record** in the implementing repository
naming, for each such identifier, the seam that implements it and the commit
that merged it
([GOV-R26](../50-governance/README.md#the-gov-r-namespace)).

**Why a record is enough here.** An identifier that appears nowhere in the
implementation repository cannot be told apart from an identifier nobody
implemented. Both answer a search with nothing, and the second is a release
blocker while the first is bookkeeping. The record separates them, and it
separates them once — the alternative is that every future audit re-derives the
same seams by hand from the same diffs and has to be believed. That cost is not
hypothetical: of the eleven v2.0 requirements this rule was written for, two
re-derivations came back different from the audit that had attributed them.

**What the record is not.** It is not a citation. The implementing change stays
uncited, the gate's answer about it does not change, and this section is not a
second way to satisfy
[GOV-R2](../50-governance/README.md#the-gov-r-namespace). It ticks one box, for
one requirement, on the stated ground that the box was unreachable.

### What does not qualify

- **A trailer that could have carried the identifier.** Where the identifier
  stood on the canonical specification's default branch for the life of the
  implementing pull request and the trailer left it out, that is a missing
  trailer, not a missing opportunity. The box stays unticked. It closes when a
  later change on that same seam carries the trailer, or by a recorded override
  ([overrides.md](../50-governance/overrides.md)) — not here.
- **Work that has not merged yet.** If the code is still in flight, the
  specification change goes first and the trailer names it
  ([GOV-R27](../50-governance/README.md#the-gov-r-namespace)). A record written
  for work that could still have cited its requirement is the failure this
  exception exists to survive, wearing the exception's clothes.
- **The record and the work in the same pull request.** The same thing said
  another way: two changes in flight at once are ordered, not recorded.
- **An entry that cannot be checked.** An entry naming no commit, or naming a
  commit that does not implement the requirement, is worse than no entry — it
  answers the audit's question wrongly and stops anyone asking again. The
  implementing commit is derived against the seam the requirement is about, not
  taken from whichever pull request touched the file last.
- **An entry standing in for the requirement.** The requirement still lives on
  the canonical specification, written and reviewed as prose. The record lives
  in the implementing repository and points at it.

Where the two merge timestamps are close enough that the judgement is genuinely
arguable — the narrowest case on record is twenty-six seconds — the record says
which pull request was already open and waiting, and a reviewer rules on it. A
call that could honestly go either way is an override to record, not a box to
tick quietly.

## For a new user-scoped surface

- [ ] A cross-user test asserts not-found
      ([Q-R9](README.md#the-q-r-namespace)).
- [ ] Every query that can run outside a request filters by user explicitly.

## For a new table or column

- [ ] The migration is a **new forward migration**; no shipped migration was
      edited.
- [ ] It is registered in the merge registry if it must sync, and that
      registration is covered by the schema guard.
- [ ] It is registered in the sensitive-column registry if it holds identifying
      text.
- [ ] Money columns are minor-unit integers with a currency, cast through the
      money boundary.
- [ ] A state column has exactly one sanctioned mutator, with an architecture
      test and, where supported, database triggers.

## For a new ingestion path

- [ ] An idempotency test proves a re-run produces no new rows
      ([Q-R10](README.md#the-q-r-namespace)).
- [ ] Failures are typed.
- [ ] The parser writes nothing to the database.

## For a new module

- [ ] Its public surface is declared and narrow.
- [ ] It ships its own architecture invariants alongside its contracts
      ([Q-R8](README.md#the-q-r-namespace)).
- [ ] It appears in [20-architecture/component-model.md](../20-architecture/component-model.md).
- [ ] Its tables are registered in both registries above.

## For anything touching money

- [ ] No floating-point number appears anywhere on the path.
- [ ] Currency mixing raises.
- [ ] Roll-ups are split-aware.
- [ ] An absent money value raises rather than defaulting to zero.

## For anything touching encrypted columns

- [ ] Every read decrypts before matching, parsing, or displaying.
- [ ] Work needing the key runs where the key is, or skips **with a warning**.
- [ ] The registry-keyed regression guard passes.

## For anything touching the outbound surface

- [ ] It appears in [G1](../10-functional/features/g-ux/g1-privacy.md), or it
      does not ship.
- [ ] It is off by default unless it is the update check.
- [ ] It is disableable.
- [ ] Its host is allow-listed before credentials are attached.

## For a security-relevant change

- [ ] A threat model was written **before** implementation.
- [ ] Each identified threat is verified closed against the implementation.
- [ ] No key material can reach a log or a rendered page.

## Before a release

- [ ] Every goal in the version manifest is satisfied
      ([70-operations/versions/](../70-operations/versions/)).
- [ ] The generated notes read as release notes end to end, with no subject
      that only makes sense to the person who wrote it.
- [ ] Any breaking change has **release-note prominence**, not one line among
      the rest.
- [ ] The branch ruleset's required status checks still name the jobs that
      actually run ([ci-cd.md](ci-cd.md#keeping-the-ruleset-honest)).
- [ ] Every platform bundle smoke-tested green.
- [ ] Manual verification of the signed manifest was performed at least once
      against the recipe published for users.

## What "done" is not

- Not "the tests pass". Tests passing is the floor.
- Not "it works on my machine". The runtime matrix exists for that reason.
- Not "I'll add the test after". A requirement without a test is a claim.
- Not "the documentation can follow". For a behavioural change the specification
  goes **first**, not after.
- Not "a record instead of a citation". The record above exists because the
  citation was impossible, never because it was inconvenient
  ([GOV-R27](../50-governance/README.md#the-gov-r-namespace)).

## Related

- [50-governance/change-lifecycle.md](../50-governance/change-lifecycle.md)
- [testing-strategy.md](testing-strategy.md) · [ci-cd.md](ci-cd.md) · [security.md](security.md)
- [70-operations/releasing.md](../70-operations/releasing.md)
