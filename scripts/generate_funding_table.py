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


DATE_FIELD = {
    "awarded":   ("date_end",        "End Date"),
    "submitted": ("date_submission",  "Submitted"),
    "drafting":  ("date_submission",  "Due"),
    "prospect":  ("date_submission",  "Due"),
    "rejected":  ("date_submission",  "Submitted"),
    "withdrawn": ("date_submission",  "Submitted"),
}

# Statuses that show title instead of grant number
SHOW_TITLE = {"submitted", "drafting", "prospect"}


def funding_table(records, status):
    date_field, date_label = DATE_FIELD.get(status, ("date_submission", "Date"))
    use_title = status in SHOW_TITLE
    mid_header = "Title" if use_title else "Grant #"
    rows = [f"| Fund | Agency | {mid_header} | {date_label} |",
            "|---|---|---|---|"]
    for r in records:
        slug   = r["_slug"]
        link   = f"[{slug}]({slug}/funding.yaml)"
        agency = r.get("agency") or ""
        mid    = r.get("title") or "" if use_title else r.get("grant_number") or ""
        date   = str(r.get(date_field, "")) if r.get(date_field) else ""
        rows.append(f"| {link} | {agency} | {mid} | {date} |")
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
        table = funding_table(records, status)
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
