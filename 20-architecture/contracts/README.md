# Contracts

**Status:** Accepted

The seams that two independently-changing things have to agree on. A contract
page exists where breaking the agreement silently produces a wrong answer rather
than an obvious failure.

| Contract | Between | Breaking it looks like |
|----------|---------|------------------------|
| [module-boundary.md](module-boundary.md) | Any two modules | A change to one module's interior silently breaks another |
| [op-log.md](op-log.md) | Any two devices | Two peers resolve the same conflict differently and diverge without noticing |
| [versioning.md](versioning.md) | Any two versions | A user upgrades and their data means something else |
| [design-tokens.md](design-tokens.md) | The product and the website | The two surfaces drift into looking like different products |

## Why these four

Each is a place where the failure is **silent**. A broken function signature
fails loudly at analysis time and needs no contract page. A merge strategy that
one device reads differently from another produces two databases that both look
correct and disagree — and nobody finds out until a number is wrong.

## Related

- [20-architecture/README.md](../README.md) — the `ARCH-R` namespace
- [50-governance/cross-repo-ci.md](../../50-governance/cross-repo-ci.md) — how contract compliance is checked across repositories
