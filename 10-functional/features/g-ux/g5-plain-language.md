# G5 — Plain language and in-product help

**Status:** Accepted · **Area:** G — Cross-cutting UX

---

## Purpose

beatrax handles domain vocabulary most people have never needed: statement
formats, settlement chains, hybrid logical clocks, group data keys. The user
does not need to learn any of it, and the product must not make them.

At the same time, the product must not lie to make itself easier to describe.
The tension between those two is what this feature is about.

## Behaviour

### The user's vocabulary, not the system's

Interface copy uses the words the user already has. Implementation vocabulary
stays in this specification and in the code.

| Say | Not |
|-----|-----|
| "Where the money came from" | "Chain resolution" |
| "This subscription went up" | "Drift threshold exceeded" |
| "Money set aside" | "Envelope carryover" |
| "Devices that share your data" | "Confirmed peers" |
| "Nobody else can read it" | "XChaCha20-Poly1305 sealed" |

The exception is where a technical term is the *only* accurate one and the user
is about to make a decision that depends on understanding it — a safety number
during pairing, for instance. Then the term is used **and explained in the same
breath**, rather than replaced with something friendlier and vaguer.

### Never claim more protection than exists

Where the honest answer is uncomfortable, the copy says the uncomfortable thing:

- At-rest encryption does **not** encrypt everything; amounts and the search
  index are readable ([ADR-0018](../../../00-overview/decisions/0018-amounts-plaintext-at-rest.md)).
- A relay sees **metadata** even though it cannot read content.
- A paired device is **trusted**, and removing it later does not un-share what it
  already saw.
- Uninstalling does **not** delete your data.
- If you lose both your password and your recovery codes and there is no other
  owner, the only route is a command on the machine.

These are recorded as requirements in [G1](g1-privacy.md) and
[F3](../f-platform/f3-auth-and-app-lock.md) precisely so they cannot quietly be
softened.

### Help sits where the question arises

Explanations live next to the thing they explain rather than in a manual nobody
opens. The data-locations page is inside the application
([F7](../f-platform/f7-data-locations.md)). Rate disclosure sits on the converted
figure ([B10](../b-ledger/b10-multi-currency.md)). Chain provenance sits on the
chain link ([B5](../b-ledger/b5-chain-resolution.md)). Categorisation provenance
sits on the transaction being re-categorised
([B2](../b-ledger/b2-categorisation.md)).

### British-leaning English, calmly

One voice across the product, the website, and this specification. Calm and
precise rather than enthusiastic. No exclamation marks in system copy, no
congratulatory interstitials, no cheerful euphemism for a failure.

### Numbers explain themselves

A figure that is derived says what it was derived from: which rate, as of when,
from which source; which rule assigned this category; how many observations a
projection is based on, or that there are too few
([D2](../d-money/d2-goals.md)).

### Nothing is deferred in the interface

The interface never contains a placeholder, a "coming soon", or a control that
does nothing. Where a setting is reserved for future behaviour it **says so
explicitly** rather than appearing functional
([C9](../c-insight/c9-community-corpus.md)) — which is the same discipline the
comment policy applies to code
([ADR-0011](../../../00-overview/decisions/0011-code-comment-policy.md)).

### Translation

The product has a translated readme and no translated interface. Interface
translation is not currently in scope, and this page does not imply otherwise.

## Acceptance criteria

| ID | Requirement |
|----|-------------|
| **G5-R1** | Interface copy MUST use the user's vocabulary; implementation vocabulary MUST stay out of it. |
| **G5-R2** | Where a technical term is unavoidable for a decision, it MUST be used and explained in place. |
| **G5-R3** | Copy MUST NOT claim more protection than the implementation provides. |
| **G5-R4** | The plaintext set under at-rest encryption MUST be stated in the product's own copy. |
| **G5-R5** | The metadata a relay can observe MUST be stated in the product's own copy. |
| **G5-R6** | The trust boundary of a paired device MUST be stated in the product's own copy. |
| **G5-R7** | That uninstalling does not delete data MUST be stated in the product's own copy. |
| **G5-R8** | The limits of the recovery paths MUST be stated plainly. |
| **G5-R9** | Explanations MUST sit next to the thing they explain, not in a separate manual. |
| **G5-R10** | A derived figure MUST be able to show what it was derived from. |
| **G5-R11** | The product MUST use one voice, British-leaning, calm and precise. |
| **G5-R12** | The interface MUST NOT contain placeholders, coming-soon copy, or controls that do nothing. |
| **G5-R13** | A setting reserved for future behaviour MUST say so explicitly. |
| **G5-R14** | Interface translation MUST NOT be implied where it does not exist. |

## Related

- [G1 Privacy stance](g1-privacy.md) — the honesty requirements this enforces
- [G2 Error and remedy model](g2-error-model.md)
- [60-brand/brand-rules.md](../../../60-brand/brand-rules.md) — the voice
- [ADR-0011](../../../00-overview/decisions/0011-code-comment-policy.md) — the same discipline in code
