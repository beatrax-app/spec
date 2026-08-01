# Platform matrix

**Status:** Accepted

What runs where, and what differs.

## Targets

| Target | Form | Status |
|--------|------|--------|
| **macOS** | Disk image, ad-hoc signed | Shipped |
| **Windows** | Installer, unsigned | Shipped |
| **Linux** | Portable image and native package, unsigned | Shipped |
| **Mobile** | Native shell rendering the same interface | v2.0, [E5](../10-functional/features/e-sync/e5-mobile-peer.md) |
| **Self-hosted** | The application on a machine the household controls | Shipped |
| **Local development** | Containerised toolchain | — |

### macOS on Intel

The published disk image is **Apple-Silicon only**. The hosted build runners are
all Apple Silicon, and building an Intel bundle there under emulation routinely
overruns the job timeout. Intel users build from source, and the install
documentation says so plainly rather than shipping something that will not run.

## What differs by platform

| Concern | Desktop bundle | Self-hosted | Mobile |
|---------|----------------|-------------|--------|
| Runtime | Bundled | Host-provided | Bundled |
| Data location | Per-platform user-data directory | Project directory | On-device application storage |
| Queue worker | Managed child process | Service-managed | Platform scheduler |
| Sync listener | Runs | Runs | **Never** — dial-out only |
| Biometrics | Platform API | Web authentication | Secure enclave |
| File-open intake | Native or process arguments | Not applicable | Not applicable |
| Notifications | Operating-system delivery | In-application only | Platform local notifications |
| Theme signal | Reported by the shell | Browser preference | Reported by the shell |
| Language signal | `Accept-Language` from the webview | `Accept-Language` from the browser | `Accept-Language` from the webview |

Storage paths resolve through a **single path authority**
([ARCH-R8](README.md#the-arch-r-namespace)), which is what makes the
per-platform redirection work at all. A raw path helper outside it fails an
architecture test.

The mobile runtime is detected **structurally** — by the shape of the paths the
platform provisions — rather than by an environment flag, because the flag is
not reliable at every stage of request handling.

## The runtime version floor

Two constraints interact:

- The desktop bundle's runtime version is whatever the shell's bundled runtime
  provides.
- The development environment tracks the next version.

The quality gate therefore runs a **matrix across both**, so code drifting
toward a construct only the newer version supports is caught before it breaks a
release build ([40-quality/ci-cd.md](../40-quality/ci-cd.md)).

**No runtime extension outside the bundle's supported set may be used.** Anything
requiring a separate install is unavailable in the shipped product, and the
codebase uses none.

## The file-open path, per platform

One platform delivers a native open-file event. The others deliver it through
process arguments on cold start and a second-instance signal afterwards.

**All paths converge on the same intake gate** — extension allow-list, size
bound, canonicalisation — before anything else happens
([F1](../10-functional/features/f-platform/f1-desktop-shell.md)).

## Distribution

Direct download from the release host, with signed manifests and published
checksums ([F6](../10-functional/features/f-platform/f6-updates.md)). Two
channels: stable, published as a draft for review; preview, published
immediately ([ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md)).

No paid operating-system signing identity is held, and the trade-off is
documented rather than hidden
([the rationale](../90-appendix/license-rationale.md#why-no-paid-signing-certificates)).

**Store distribution is not yet scoped.** Which stores, whether they force paid
signing identities, and whether their sandboxing survives local-network
discovery and background sync are all
[open questions](../00-overview/roadmap.md#open-questions).

## Related

- [ADR-0006](../00-overview/decisions/0006-nativephp-desktop-shell.md) · [ADR-0019](../00-overview/decisions/0019-asymmetric-release-publish.md)
- [F1 Desktop shell](../10-functional/features/f-platform/f1-desktop-shell.md) · [E5 Mobile peer](../10-functional/features/e-sync/e5-mobile-peer.md)
- [70-operations/releasing.md](../70-operations/releasing.md)
