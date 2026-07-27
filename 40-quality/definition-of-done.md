# Definition of done

**Status:** Accepted

A change is done when every box below is ticked. Not most of them.

## For any change

- [ ] **It cites a requirement identifier that already exists on the canonical
      spec**, in a commit trailer and in the pull-request body
      ([Q-R23](README.md#the-q-r-namespace)).
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
- [ ] A changelog entry exists under the unreleased heading, in the user's
      language, saying what changed for them.
- [ ] The behaviour was walked in a browser, on both desktop and phone widths.

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
- [ ] The changelog's unreleased section is complete and reads as release notes.
- [ ] Any breaking change has **release-note prominence**, not a changelog line.
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

## Related

- [50-governance/change-lifecycle.md](../50-governance/change-lifecycle.md)
- [testing-strategy.md](testing-strategy.md) · [ci-cd.md](ci-cd.md) · [security.md](security.md)
- [70-operations/releasing.md](../70-operations/releasing.md)
