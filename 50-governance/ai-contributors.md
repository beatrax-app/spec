# AI contributors

**Status:** Accepted

Beatrax was built with heavy AI assistance, deliberately and openly — the product
repository says so in its own readme. This page states the rules that made that
work, and that apply to anyone else contributing the same way.

## The position

**AI-assisted contribution is welcome.** It is not second-class, and it does not
get a lower bar.

It also does not get a **higher** one. A pull request is judged on whether it
satisfies the requirement it cites, passes the gates, and is code somebody can
maintain. How it was written is not a property of the change.

**There is nothing to disclose.** An AI is a tool, like an IDE, a linter, or a
search engine, and this project does not ask which of those you used either. A
disclosure requirement would imply the code needs a different kind of scrutiny
because of its provenance — but the scrutiny every contribution gets is already
the right amount, and review is there for a reason. Requiring a declaration
would also be unenforceable, which is the worst property a rule can have: it
would be obeyed by the careful and ignored by everyone else, leaving reviewers
with a signal that means nothing.

## The rules

### 1. You are the author

The sign-off is yours ([dco.md](dco.md)). You are certifying that you have the
right to submit this under the project's licence and that you understand the
contribution.

**An AI cannot sign off.** If you cannot explain what a change does and why, you
cannot certify it, and you should not open the pull request.

### 2. The judgment rules bind identically

The comment policy's judgment rules — prefer self-documenting code, comment only
genuine complexity, architecture goes in documentation, nothing is deferred in a
comment — are binding on every contributor, human or AI-assisted
([40-quality/code-comments.md](../40-quality/code-comments.md)).

This one matters in practice. Generated code tends toward narrating what the
next line does, which is exactly what the policy forbids and what the mechanical
test catches. Strip it before opening the pull request rather than after CI
tells you.

### 3. No invented requirements

The gate requires citing an identifier that already exists
([canonical-spec.md](canonical-spec.md)). An identifier that does not exist fails
the gate — but a **plausible-looking, existing, unrelated** identifier passes it
and fails review.

Do not let a model choose the citation. Choose it yourself, from the requirement
the change actually satisfies.

### 4. No invented facts in documentation

Every requirement in this specification is traceable to something real. Where a
source is silent, the honest answer is an **explicit open question**, not a
confident-sounding invention ([GOV-R25](README.md#the-gov-r-namespace)).

Generated documentation is prone to filling gaps smoothly. A smoothly-filled gap
in a specification is worse than a visible hole, because nobody knows to check
it.

### 5. Verify against the code, not the plan

A generated change describes what it intended to do. Whether it did is a
different question, answered by reading the diff and running the tests.

### 6. Security-relevant code gets extra scrutiny

Cryptography, authentication, the sync transport, the encryption boundary, and
the outbound surface are reviewed line by line regardless of provenance. The
[security](../40-quality/security.md) page names them.

### 7. No secrets, ever

Never paste credentials, tokens, a real database, or real financial data into a
tool. The product's whole premise is that this data does not leave the user's
machine; a contributor's tooling is not an exception.

Use the shipped fixtures.

## What AI assistance is genuinely good at here

Recorded because it is true, not as encouragement to skip review:

- Mechanical sweeps across many files — the comment-policy sweep covered roughly
  1 435 backend files, and doing it by hand would not have happened.
- Exhaustive edge-case enumeration in specification prose.
- Test scaffolding from a stated requirement.
- Cross-referencing a large document tree consistently.

## What it is bad at

- Knowing which requirement a change actually satisfies.
- Noticing that a plausible-looking merge strategy is wrong for a table.
- Resisting the urge to fill a gap with something that reads well.
- Judging whether an abstraction is the right one rather than a defensible one.

Those are the reviewer's job, and they are the reason review is not optional.

## Related

- [contributing.md](contributing.md) · [dco.md](dco.md) · [canonical-spec.md](canonical-spec.md)
- [40-quality/code-comments.md](../40-quality/code-comments.md) · [40-quality/definition-of-done.md](../40-quality/definition-of-done.md) · [40-quality/security.md](../40-quality/security.md)
