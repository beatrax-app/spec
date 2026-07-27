# Overrides

**Status:** Accepted

Every rule in this specification has a way to be broken. Pretending otherwise
produces one of two outcomes: a rule that gets quietly ignored, or a project that
cannot ship a fix at three in the morning.

This page says who may break a rule, when, and what they owe afterwards.

## Who

**The project lead** ([GOV-R24](README.md#the-gov-r-namespace)), identified in
the maintainer registry by the lead flag
([70-operations/maintainers.toml](../70-operations/maintainers.toml)).

Nobody else. An override is not a review outcome a second reviewer can grant.

## When

An override is for a situation the rule did not anticipate, not for a situation
the rule is inconvenient in.

| Legitimate | Not legitimate |
|------------|----------------|
| A security fix that must ship before a specification change can be written | "The gate is annoying today" |
| The pipeline is broken by something outside the change, blocking every merge | "My change is obviously fine" |
| A platform behaviour change forces an immediate response | "Writing the requirement will take twenty minutes" |
| A released artefact must be pulled | "Nobody will notice" |

The test: **would you be comfortable with the recorded justification being read
in a year?**

## What is never overridable

Some rules protect the user rather than the process, and no override applies:

| Never overridable | Why |
|-------------------|-----|
| Shipping code that phones home | It is the product's founding promise ([ADR-0004](../00-overview/decisions/0004-local-only-hosting.md)) |
| Skipping update signature or hash verification | It is the only binary-integrity signal ([F6](../10-functional/features/f-platform/f6-updates.md)) |
| Publishing a release without every platform build passing | A partial release is worse than a late one |
| Weakening a cryptographic guarantee to unblock a feature | The guarantee is the feature |
| Claiming a protection the implementation does not provide | Dishonesty is not a shortcut ([G5](../10-functional/features/g-ux/g5-plain-language.md)) |
| Removing a cross-user isolation test to make a suite green | It is a data-leak guard |
| Reusing or renumbering a requirement identifier | It silently invalidates history |

These are not overridable by the lead either. They are the boundary of what the
project is.

## What an override owes

1. **A record.** The change that carries the override states plainly that it is
   one, which rule, and why.
2. **A follow-up.** An issue, opened at the same time, to do properly what the
   override skipped — the specification change, the test, the threat model.
3. **A deadline.** Stated in the follow-up. An override without one becomes the
   new normal.

An override that skipped a specification change is not resolved until that
change has merged. The gate cannot enforce this, which is exactly why it is
written down.

## Overrides are visible

They are stated in the change that carries them, not in a side channel. Someone
reading history should be able to find every rule that was ever bent and why.

If the same rule is overridden repeatedly, **the rule is wrong** and the correct
response is a specification change — not a third override.

## The solo caveat

With one maintainer, "the lead approves an override" is one person agreeing with
themselves. That is a real weakness of this arrangement and it is stated rather
than dressed up.

The mitigations are the record, the follow-up, and the never-overridable list —
which is deliberately drawn to cover the things a tired person at three in the
morning would most regret.

## Related

- [change-lifecycle.md](change-lifecycle.md) · [canonical-spec.md](canonical-spec.md)
- [70-operations/maintainers.md](../70-operations/maintainers.md)
- [40-quality/definition-of-done.md](../40-quality/definition-of-done.md)
