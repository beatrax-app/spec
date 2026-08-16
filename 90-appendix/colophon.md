# Colophon

**Status:** Accepted

The open-source projects Beatrax is built on, named.

The rest of this specification names tools by role rather than by product — a
choice that keeps requirements from decaying every time a dependency is
replaced ([tooling.md](../40-quality/tooling.md)). This page is the deliberate
exception. Credit is not a requirement, and a project that depends this heavily
on other people's work should say whose.

The list is generated from the product repository's `composer.json` and
`package.json`; it is the canonical source the website's colophon renders.

## The runtime

| Project | What it does here |
|---------|-------------------|
| **PHP 8.5** | The language. Property hooks, asymmetric visibility, and the typed-constant work of recent releases are used throughout, which is why the floor is a current version rather than a comfortable one. |
| **Laravel 13** | The application framework — routing, container, queue, scheduler, migrations, and the console layer every operational command is built on. |
| **Livewire 4** | Server-rendered interactivity. Every surface in the app is a Livewire component, which is what keeps the whole product in one language instead of two. |
| **Flux** | The Livewire component library behind the modals, popovers, and form controls. |
| **NativePHP** | Packages the application as a real native app — desktop on macOS, Windows, and Linux, and the mobile clients — providing the native window, tray, biometric, and OS-notification surfaces. |
| **SQLite** | The store. One file, WAL mode, on the user's own disk ([ADR-0005](../00-overview/decisions/0005-sqlite-wal.md)). |

## Reading financial data

| Project | What it does here |
|---------|-------------------|
| **genkgo/camt** | Parses CAMT.053, the ISO 20022 bank statement — the richest of the supported formats. |
| **league/csv** | The CSV reader behind every per-bank export shape. |
| **brick/money**, **brick/math** | Exact decimal money. No floating-point arithmetic touches a balance. |
| **jschaedl/iban-validation** | Validates and normalises IBANs before they become counterparty identities. |
| **spatie/pdf-to-text** | Extracts text from credit-card PDF statements, via `pdftotext`. |
| **zbateson/mail-mime-parser** | Parses `.eml` and `.mbox` receipts for the email-scanning path. |
| **dompdf/dompdf** | Renders the per-year tax export as PDF. |

## Connecting to the outside, when asked to

| Project | What it does here |
|---------|-------------------|
| **guzzlehttp/guzzle** | The HTTP client for the optional connectors. |
| **google/apiclient**, **league/oauth2-google** | Gmail receipt scanning, read-only, opt-in. |
| **thenetworg/oauth2-azure** | The Microsoft Graph equivalent. |
| **league/oauth2-client** | The shared OAuth plumbing beneath both. |
| **firebase/php-jwt** | Signs the assertions the open-banking connector needs. |

## Sync

| Project | What it does here |
|---------|-------------------|
| **amphp** (`http-server`, `socket`, `websocket-client`, `websocket-server`) | The asynchronous runtime behind the sync daemon, the LAN transport, and the relay. |
| **ext-sodium** | Ed25519 and X25519 identities, XChaCha20-Poly1305, Argon2id, and sealed boxes — the primitives the whole sync design rests on ([ADR-0015](../00-overview/decisions/0015-multi-master-p2p-sync.md), [ADR-0016](../00-overview/decisions/0016-noise-transport-zero-knowledge-relay.md)). |

## Structure and operations

| Project | What it does here |
|---------|-------------------|
| **nwidart/laravel-modules** | The module boundary the architecture is built on ([component-model.md](../20-architecture/component-model.md)). |
| **spatie/laravel-data** | Typed data objects across the Public seams between modules. |
| **spatie/laravel-activitylog** | The audit trail. |
| **laravel/fortify** | Authentication scaffolding, adapted for a local-only, account-free product. |
| **monolog/monolog** | Logging. |
| **symfony/process**, **symfony/yaml** | Process control for the daemons; YAML for the community corpus. |
| **doctrine/sql-formatter** | Formats SQL in the developer console. |

## The interface

| Project | What it does here |
|---------|-------------------|
| **Tailwind CSS 4** | The styling system, driven by the design tokens ([design-tokens.md](../20-architecture/contracts/design-tokens.md)). |
| **Vite** | The asset pipeline. |
| **Alpine.js** | The small client-side interactions Livewire leaves to the browser. |
| **ApexCharts** | The forecast, report, and net-worth charts. |
| **Fuse.js** | Client-side fuzzy matching in the command palette. |
| **Axios** | The HTTP client for the few direct browser calls. |

## The quality gate

| Project | What it does here |
|---------|-------------------|
| **Pest** | The test runner, including the architecture tests that enforce the module boundary and the comment policy. |
| **Larastan** / **PHPStan** | Static analysis at maximum level, in strict mode. |
| **Laravel Pint** | Formatting. |
| **Docker** | The containerised toolchain; the host needs only a container runtime. |

## Also

Beyond the dependency list: **Conventional Commits**, **git-cliff** and
**Semantic Versioning** for release discipline, the **Hippocratic License** for the terms
([license-rationale.md](license-rationale.md)), and the **Noise Protocol
Framework** as the design the transport handshake follows.

## Related

- [tooling.md](../40-quality/tooling.md) — the same ground by role, not by name
- [platform-matrix.md](../20-architecture/platform-matrix.md) — what runs where
- [references.md](references.md) — the standards and formats, as opposed to the software
