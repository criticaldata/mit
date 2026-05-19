#!/usr/bin/env python3
"""
Generate a funding summary from data/funding/*/funding.yaml.
Awarded grants are shown expanded; all other statuses are collapsed.
Run from the repo root. Prints Markdown to stdout.
"""

import io
import sys
import yaml
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FUNDING_DIR = Path("data/funding")
PEOPLE_DIR  = Path("data/people")

STATUS_ORDER = ["awarded", "submitted", "drafting", "prospect", "rejected", "withdrawn"]
STATUS_LABELS = {
    "awarded":   "Awarded",
    "submitted": "Submitted",
    "drafting":  "Drafting",
    "prospect":  "Prospect",
    "rejected":  "Rejected",
    "withdrawn": "Withdrawn",
}


def load_funding():
    by_status = {s: [] for s in STATUS_ORDER}
    for yaml_file in sorted(FUNDING_DIR.glob("*/funding.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"YAML error in {yaml_file}: {e}", file=sys.stderr)
                continue
        if not data:
            continue
        data["_slug"] = yaml_file.parent.name
        status = data.get("status", "")
        if status in by_status:
            by_status[status].append(data)
    return by_status


def resolve_lead(slug):
    if not slug:
        return ""
    person_file = PEOPLE_DIR / slug / "person.yaml"
    if person_file.exists():
        with open(person_file, encoding="utf-8") as f:
            p = yaml.safe_load(f) or {}
        name = p.get("name", slug)
        return f"[{name}](../people/{slug}/person.yaml)"
    return slug


def amount_cell(record):
    awarded = record.get("amount_awarded")
    requested = record.get("amount_requested")
    currency = record.get("currency", "USD")
    val = awarded or requested
    if not val:
        return ""
    label = f"{currency} {val:,}" if isinstance(val, (int, float)) else f"{currency} {val}"
    return f"{label}{'*' if not awarded and requested else ''}"


def funding_table(records):
    rows = ["| Fund | Agency | Grant # | Lead | Amount | Submission |",
            "|---|---|---|---|---|---|"]
    for r in records:
        slug  = r["_slug"]
        title = r.get("title") or slug
        link  = f"[{title}]({slug}/funding.yaml)"
        agency = r.get("agency") or ""
        grant  = r.get("grant_number") or ""
        lead   = resolve_lead(r.get("lead"))
        amount = amount_cell(r)
        date_sub = str(r.get("date_submission", "")) if r.get("date_submission") else ""
        rows.append(f"| {link} | {agency} | {grant} | {lead} | {amount} | {date_sub} |")
    return "\n".join(rows)


def main():
    if not FUNDING_DIR.exists():
        sys.exit(f"Directory not found: {FUNDING_DIR}. Run from the repo root.")

    by_status = load_funding()
    total = sum(len(v) for v in by_status.values())

    print("# Funding\n")
    for status in STATUS_ORDER:
        records = by_status[status]
        if not records:
            continue
        label = STATUS_LABELS[status]
        table = funding_table(records)
        if status == "awarded":
            print(f"## {label} ({len(records)})\n")
            print(table)
            print()
        else:
            print(f"<details>\n<summary><strong>{label} ({len(records)})</strong></summary>\n")
            print(table)
            print("\n</details>\n")

    print(f"---\n_Generated from `data/funding/` — {total} records total._")


if __name__ == "__main__":
    main()
