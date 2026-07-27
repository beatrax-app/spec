# ADR-0017: Envelope budgeting replaces category-linked pots

**Status:** Accepted
**Date:** 2026-07-04

## Context

Two features arrived from different directions and ended up overlapping.

**Savings pots** shipped in v1.3: named virtual sub-balances carved out of one
real account, reconciling so that the real balance always equals allocated plus
unallocated. A pot could be linked either to a savings goal or to a budget
category.

**Category budgets** shipped in v1.2: a flat per-category monthly spending
ceiling with progress tracking.

A feature-gap comparison against a mature zero-based budgeting product found the
flat ceiling to be the single biggest capability gap. Real envelope budgeting
needs a ready-to-assign pool, an assign-every-unit monthly grid, money movement
between categories, balance rollover with explicit overspend handling, and
template auto-fill. Category-linked pots were an approximation of the same idea
built on a different mechanism — an allocation over one account's balance rather
than a monthly assignment across the whole budget.

Keeping both would mean two answers to "how much have I set aside for
groceries", stored differently, reconciling differently, and disagreeing when
money moved between accounts.

## Decision

Envelope (zero-based) budgeting replaces category-linked pots.

- **Category-linked pots are retired.** Pots can no longer be created or edited
  with a category link. Only a goal link, or no link, remains available.
- **On upgrade, every category-linked pot is archived** and its balance released
  to its account's unallocated pool. The user re-assigns that money into the
  appropriate envelope by hand.
- **Goal-linked pots are unaffected** and keep working exactly as before.
- **Envelope budgeting is anchored at an activation point**, so carryover folds
  forward from the moment the user activated envelopes rather than from the
  beginning of history.
- **Split transactions are a hard prerequisite** and shipped first: an envelope
  budget cannot be honest if an eighty-unit shop that was sixty groceries and
  twenty household counts entirely against one envelope.

**This is a user-visible breaking change and is why v2.0 is a major release**
([roadmap](../roadmap.md#the-v14--v20-promotion)).

## Alternatives considered

| Option | Why it lost |
|--------|-------------|
| **Keep both, with category-linked pots as an alternative view** | Two sources of truth for the same question, disagreeing whenever money moved between accounts. |
| **Migrate category-linked pot balances into envelope assignments automatically** | Tempting, and rejected. A pot balance is a stock; an envelope assignment is a flow for a specific month. Guessing which month to attribute an accumulated balance to would produce a budget the user did not author and cannot audit. Archiving and asking is honest. |
| **Extend category budgets in place without the pot retirement** | Leaves the overlap, and the retired mechanism keeps accruing balances nobody looks at. |
| **Defer envelope budgeting past v2.0** | It was the largest identified capability gap, and the split-transaction work it needed was already sequenced. |

## Consequences

### Positive

- One answer to "how much is set aside for this category", month by month, with
  explicit rollover.
- Splits make category roll-ups honest across the whole product, not just in the
  budget.
- Pots become a single, clear thing: virtual sub-balances of a real account,
  optionally tied to a goal.

### Negative

- **Users lose a working feature and get manual work in exchange.** Anyone using
  category-linked pots must re-assign that money themselves. This needs
  prominence in the release notes, not a line in a changelog.
- **The retirement is one-way.** There is no downgrade path that reconstructs
  category-linked pots.
- Onboarding gains a first-month assignment step, because an empty envelope grid
  is not a useful starting state.

### Neutral

- The underlying pot movement model — no stored balance column, balance is the
  signed sum of movements — is unchanged. Only the link target narrowed.

## Revisit if

- Nothing foreseeable. Reversing this would mean reintroducing the overlap the
  decision exists to remove.

## Related

- [D1 Envelope budgeting](../../10-functional/features/d-money/d1-envelope-budgeting.md)
- [D3 Savings pots](../../10-functional/features/d-money/d3-pots.md)
- [B7 Split transactions](../../10-functional/features/b-ledger/b7-splits.md)
- [70-operations/versions/2.0.0.toml](../../70-operations/versions/2.0.0.toml)
