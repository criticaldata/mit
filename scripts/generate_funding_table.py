#!/usr/bin/env python3
"""
Generate a funding summary from data/funding/*/funding.yaml.
Awarded and in-progress grants are shown expanded; other statuses collapsed.
Run from the repo root. Prints Markdown to stdout.
"""

import io
import sys
import yaml
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FUNDING_DIR = Path("data/funding")
PEOPLE_DIR  = Path("data/people")

ALL_STATUSES = [
    "awarded", "drafting", "under-revision",
    "submitted", "prospect", "rejected", "withdrawn",
]

# Groups define sections in render order.
# expanded=True -> ## heading; False -> <details> block
GROUPS = [
    {
        "label":    "Awarded",
        "statuses": ["awarded"],
        "expanded": True,
    },
    {
        "label":    "In Progress",
        "statuses": ["drafting", "under-revision"],
        "expanded": True,
    },
    {
        "label":    "Submitted",
        "statuses": ["submitted"],
        "expanded": False,
    },
    {
        "label":    "Prospect",
        "statuses": ["prospect"],
        "expanded": False,
    },
    {
        "label":    "Rejected / Withdrawn",
        "statuses": ["rejected", "withdrawn"],
        "expanded": False,
    },
]

DATE_FIELD = {
    "awarded":        ("date_end",        "End Date"),
    "under-revision": ("date_submission", "Submitted"),
    "submitted":      ("date_submission", "Submitted"),
    "drafting":       ("date_submission", "Due"),
    "prospect":       ("date_submission", "Due"),
    "rejected":       ("date_submission", "Submitted"),
    "withdrawn":      ("date_submission", "Submitted"),
}

# Statuses that show title instead of grant number
SHOW_TITLE = {"drafting", "under-revision", "submitted", "prospect"}

STATUS_LABELS = {
    "awarded":        "Awarded",
    "under-revision": "Under Revision",
    "submitted":      "Submitted",
    "drafting":       "Drafting",
    "prospect":       "Prospect",
    "rejected":       "Rejected",
    "withdrawn":      "Withdrawn",
}


def load_funding():
    by_status = {s: [] for s in ALL_STATUSES}
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


def funding_table(records, statuses):
    multi_status = len(statuses) > 1

    # Pick date label: use the first status's label (they share the same field for mixed groups)
    date_field, date_label = DATE_FIELD.get(statuses[0], ("date_submission", "Date"))

    # For mixed-status groups, always show title (grant # may not exist yet)
    use_title = multi_status or statuses[0] in SHOW_TITLE
    mid_header = "Title" if use_title else "Grant #"

    if multi_status:
        rows = [f"| Fund | Agency | Status | {mid_header} | {date_label} |",
                "|---|---|---|---|---|"]
    else:
        rows = [f"| Fund | Agency | {mid_header} | {date_label} |",
                "|---|---|---|---|"]

    for r in records:
        slug   = r["_slug"]
        link   = f"[{slug}]({slug}/funding.yaml)"
        agency = r.get("agency") or ""
        mid    = r.get("title") or "" if use_title else r.get("grant_number") or ""
        r_status = r.get("status", "")
        df, _  = DATE_FIELD.get(r_status, ("date_submission", ""))
        date   = str(r.get(df, "")) if r.get(df) else ""
        if multi_status:
            status_label = STATUS_LABELS.get(r_status, r_status)
            rows.append(f"| {link} | {agency} | {status_label} | {mid} | {date} |")
        else:
            rows.append(f"| {link} | {agency} | {mid} | {date} |")

    return "\n".join(rows)


def main():
    if not FUNDING_DIR.exists():
        sys.exit(f"Directory not found: {FUNDING_DIR}. Run from the repo root.")

    by_status = load_funding()
    total = sum(len(v) for v in by_status.values())

    print("# Funding\n")
    for group in GROUPS:
        records = []
        for s in group["statuses"]:
            records.extend(by_status.get(s, []))
        if not records:
            continue
        label = group["label"]
        table = funding_table(records, group["statuses"])
        if group["expanded"]:
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
