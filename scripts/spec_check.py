#!/usr/bin/env python3
"""Governance gate: verify a PR cites spec identifiers that actually exist.

Canonical here in the spec repo; every implementation repo runs it via the
reusable workflow (.github/workflows/spec-check.yml). See 50-governance/.

Enforces:
  GOV-R2  a citation is present
  GOV-R3  every cited identifier exists on spec@main
  GOV-R28 a citation is read from a `Spec:` trailer and from nowhere else, and
          an identifier named anywhere else is reported as named-but-not-cited
          rather than as absent

Ordering (GOV-R4) — that a behavioural change's spec PR merged first — is not
machine-checked here yet; it is verified in review. Hardening this is tracked in
the spec repo, and any change to this script cites GOV-R11.

Usage:
  spec_check.py --spec-dir <path to spec checkout> --text-file <PR body+commits>
Exit 0 = pass, 1 = fail (with guidance), 2 = usage error.
"""
from __future__ import annotations
import argparse, os, re, sys, pathlib

# Identifiers the spec defines.
REQ_DEF = re.compile(r"^\|\s*\*\*([A-Z]+\d*-R\d+)\*\*\s*\|", re.M)
ADR_FILE = re.compile(r"^0*(\d{3,4})-.*\.md$")
CITE_ANY = re.compile(r"\b([A-Z]+\d*-R\d+|ADR-\d{3,4})\b")
SPEC_TRAILER = re.compile(r"^[ \t]*Spec:[ \t]*(\S.*)$", re.M | re.I)


def defined_ids(spec_dir: pathlib.Path) -> set[str]:
    ids: set[str] = set()
    for p in spec_dir.rglob("*.md"):
        if ".git" in p.parts:
            continue
        ids.update(REQ_DEF.findall(p.read_text(encoding="utf-8", errors="ignore")))
    dec = spec_dir / "00-overview" / "decisions"
    if dec.is_dir():
        for f in dec.iterdir():
            m = ADR_FILE.match(f.name)
            if m:
                ids.add(f"ADR-{int(m.group(1)):04d}")
    return ids


def cited_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for line in SPEC_TRAILER.findall(text):
        ids.update(CITE_ANY.findall(line))
    return ids


def named_ids(text: str) -> set[str]:
    """Identifiers the text names anywhere other than on a `Spec:` line.

    A sentence is not a citation and this does not make it one: the trailer
    stays the only form that passes, because it is a parseable and deliberate
    act where "unlike A3-R23" and "superseded by A3-R23" are neither.

    This exists so the gate can tell *cites nothing* apart from *names it three
    lines above and never put it in a trailer*. It could not draw that
    distinction before, and both read as uncited — which is how four v2
    identifiers were graded uncited for being documented in the wrong shape
    (GOV-R28).
    """
    return set(CITE_ANY.findall(SPEC_TRAILER.sub("", text)))


GUIDANCE = """
This change does not cite a spec identifier that exists on spec@main.

The beatrax spec is canonical: every change references something already in
https://github.com/beatrax-app/spec

Add a `Spec:` trailer to a commit AND the PR body, for example:

    Spec: B2-R1

  - Implementing something specified?  Cite the requirement.
  - Changing behaviour?  Open a spec PR first, then cite the new ID.
  - Routine maintenance (deps, formatting, CI)?  Cite GOV-R12.
  - Named it in a sentence already?  Only the `Spec:` line is read.

Guide: https://github.com/beatrax-app/spec/blob/main/50-governance/contributing.md
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec-dir", required=True)
    ap.add_argument("--text-file", required=True)
    a = ap.parse_args()

    spec_dir = pathlib.Path(a.spec_dir)
    if not spec_dir.is_dir():
        print(f"::error::spec dir not found: {spec_dir}")
        return 2

    cwd = pathlib.Path.cwd().resolve()
    text_path = pathlib.Path(a.text_file).resolve()
    if not text_path.is_relative_to(cwd):
        print("::error::text-file must be within the working directory")
        return 2
    text = text_path.read_text(encoding="utf-8", errors="ignore")
    defined = defined_ids(spec_dir)
    if not defined:
        print("::error::no identifiers found in spec checkout — cannot verify")
        return 2

    cited = cited_ids(text)
    # Reported, never counted. An identifier that does not resolve is not a
    # citation under any reading, so naming one in prose says nothing worth
    # printing; one that does resolve is the ambiguous case worth naming.
    named = ", ".join(sorted({i for i in named_ids(text) if i in defined} - cited))

    if not cited:
        if named:
            print(f"::error::no `Spec:` trailer found; the text names {named} outside one")
            print(f"""
A citation is read from a line beginning `Spec:` and from nowhere else, so this
text cites nothing. What it does name, in prose, the specification defines:
{named}. If this change implements that, the fix is the trailer — on a commit
and in the pull-request body:

    Spec: {named}""")
        else:
            print("::error::no `Spec:` citation found")
        print(GUIDANCE)
        return 1

    unknown = sorted(i for i in cited if i not in defined)
    if unknown:
        print(f"::error::cited identifiers do not exist on spec@main: {', '.join(unknown)}")
        print(GUIDANCE)
        return 1

    print(f"spec-check: OK — cites {', '.join(sorted(cited))}")
    if named:
        print(f"::warning::named but not cited: {named} — named outside a `Spec:` "
              "line, so this change does not cite it. Add it to the trailer if "
              "this change implements it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
