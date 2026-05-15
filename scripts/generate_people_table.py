#!/usr/bin/env python3
"""
Generate lab member tables from data/people/*/person.yaml.
Run from the repo root. Prints Markdown to stdout.
"""

import sys
import yaml
from pathlib import Path
from datetime import date, datetime


PEOPLE_DIR = Path("data/people")


def load_people():
    active, collaborators, alumni = [], [], []
    for yaml_file in sorted(PEOPLE_DIR.glob("*/person.yaml")):
        with open(yaml_file, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"YAML error in {yaml_file}: {e}", file=sys.stderr)
                continue
        if not data or not data.get("name"):
            continue
        data["_slug"] = yaml_file.parent.name
        status = data.get("status", "")
        if status == "active":
            active.append(data)
        elif status == "collaborator":
            collaborators.append(data)
        elif status == "alumni":
            alumni.append(data)
    return active, collaborators, alumni


def fmt_date_range(start, end):
    def parse(d):
        if isinstance(d, (date, datetime)):
            return d
        return datetime.strptime(str(d), "%Y-%m-%d")

    if not start:
        return "TBD"
    try:
        s = parse(start).strftime("%b %Y")
        e = parse(end).strftime("%b %Y") if end else "present"
        return s if s == e else f"{s}–{e}"
    except Exception:
        return f"{start}–{end or 'present'}"


def photo_cell(person):
    photo = person.get("photo")
    if not photo:
        return ""
    slug = person["_slug"]
    src = f"data/people/{slug}/{photo}"
    first = person.get("name", "").split()[0]
    return f'<img src="{src}" alt="{first}" width="120"/>'


def member_table(people):
    people = sorted(people, key=lambda p: p.get("name", "").lower())
    rows = ["| Name | Role | Email | Photo |", "|---|---|---|---|"]
    for p in people:
        slug = p["_slug"]
        name = f"[{p['name']}](data/people/{slug}/person.yaml)"
        rows.append(f"| {name} | {p.get('role', '')} | {p.get('email', '')} | {photo_cell(p)} |")
    return "\n".join(rows)


def visitor_table(people):
    people = sorted(people, key=lambda p: p.get("name", "").lower())
    rows = ["| Name | Dates | Role | Institution | Email | Photo |", "|---|---|---|---|---|---|"]
    for p in people:
        slug = p["_slug"]
        name = f"[{p['name']}](data/people/{slug}/person.yaml)"
        dates = fmt_date_range(p.get("start_date"), p.get("end_date"))
        rows.append(
            f"| {name} | {dates} | {p.get('role', '')} | {p.get('institution', '')} | {p.get('email', '')} | {photo_cell(p)} |"
        )
    return "\n".join(rows)


def main():
    if not PEOPLE_DIR.exists():
        sys.exit(f"Directory not found: {PEOPLE_DIR}. Run from the repo root.")

    active, collaborators, alumni = load_people()

    print("# Lab Members\n")
    print(f"## Active ({len(active)})\n")
    print(member_table(active))
    print(f"\n## Current Visitors & Collaborators ({len(collaborators)})\n")
    print(visitor_table(collaborators))
    print(f"\n## Alumni ({len(alumni)})\n")
    print(visitor_table(alumni))
    print(f"\n---\n_Generated from `data/people/` — {len(active) + len(collaborators) + len(alumni)} records total._")


if __name__ == "__main__":
    main()
