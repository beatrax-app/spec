# beatrax-app/spec tasks. `just` to list.
default:
    @just --list

# Run every check CI runs.
ci: integrity typos links markdown

# Verify identifiers resolve, none duplicated, links unbroken.
integrity:
    python3 scripts/integrity.py

# Spell check.
typos:
    typos

# Link check.
links:
    lychee --no-progress .

# Markdown lint.
markdown:
    markdownlint-cli2 "**/*.md"

# Build the docs site locally into ./book.
docs:
    rm -rf src && mkdir src && cp README.md src/ && cp LICENSE.md src/ && \
        for d in [0-9]*-*; do cp -r "$d" "src/$d"; done && \
        python3 scripts/gen_summary.py src && mdbook build

# Regenerate a repo's CODEOWNERS from 70-operations/maintainers.toml.
codeowners repo:
    python3 scripts/gen_codeowners.py {{repo}}

# Self-test the governance gate against a sample citation, e.g. `just check-gate "Spec: A1-R1"`.
check-gate text:
    echo "{{text}}" > /tmp/_beatrax_gate.txt && \
        python3 scripts/spec_check.py --spec-dir . --text-file /tmp/_beatrax_gate.txt

# Check whether a version manifest is stageable, e.g. `just stageable 2.0.0`.
stageable version:
    python3 scripts/check_stageable.py {{version}}
