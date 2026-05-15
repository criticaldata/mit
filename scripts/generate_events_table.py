#!/usr/bin/env python3
"""
Generate an events summary from data/events/<year>/<slug>/event.yaml.
Upcoming events are shown expanded, sorted by date.
Completed and cancelled events are collapsed at the bottom.
Run from the repo root. Prints Markdown to stdout.
"""

import io
import sys
import yaml
from datetime import date, datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

EVENTS_DIR = Path("data/events")
PEOPLE_DIR = Path("data/people")

UPCOMING_STATUSES = {"confirmed", "planned", "prospect"}
COLLAPSED_STATUSES = [
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
]

STATUS_LABEL = {
    "confirmed": "Confirmed",
    "planned":   "Planned",
    "prospect":  "Prospect",
    "completed": "Completed",
    "cancelled": "Cancelled",
}


def load_events():
    events = []
    for yaml_file in EVENTS_DIR.glob("*/*/event.yaml"):
        with open(yaml_file, encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"YAML error in {yaml_file}: {e}", file=sys.stderr)
                continue
        if not data or not data.get("title"):
            continue
        year_dir  = yaml_file.parent.parent.name
        slug      = yaml_file.parent.name
        data["_slug"]     = slug
        data["_year_dir"] = year_dir
        data["_path"]     = f"{year_dir}/{slug}/event.yaml"
        events.append(data)
    return events


def parse_date(val):
    if not val:
        return None
    if isinstance(val, (date, datetime)):
        return val if isinstance(val, date) else val.date()
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").date()
    except ValueError:
        return None


def fmt_date(val):
    d = parse_date(val)
    return d.strftime("%d %b %Y") if d else ""


def fmt_date_range(start, end):
    s = parse_date(start)
    e = parse_date(end)
    if not s:
        return "TBD"
    if not e or s == e:
        return s.strftime("%d %b %Y")
    if s.month == e.month and s.year == e.year:
        return f"{s.day}–{e.strftime('%d %b %Y')}"
    return f"{s.strftime('%d %b')}–{e.strftime('%d %b %Y')}"


def location(event):
    parts = [event.get("city", ""), event.get("country", "")]
    loc = ", ".join(p for p in parts if p)
    virtual = event.get("virtual")
    if virtual is True:
        loc = "Virtual" if not loc else f"{loc} (virtual)"
    elif virtual == "hybrid":
        loc = loc + " (hybrid)" if loc else "Hybrid"
    return loc


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


def events_table(events):
    rows = ["| Date | Event | Location | Type | Status | Lead |",
            "|---|---|---|---|---|---|"]
    for e in events:
        date_str = fmt_date_range(e.get("date_start"), e.get("date_end"))
        title    = e["title"]
        if e.get("url"):
            title = f"[{title}]({e['url']})"
        else:
            title = f"[{title}]({e['_path']})"
        loc      = location(e)
        etype    = e.get("type", "")
        status   = STATUS_LABEL.get(e.get("status", ""), e.get("status", ""))
        lead     = resolve_lead(e.get("lead"))
        rows.append(f"| {date_str} | {title} | {loc} | {etype} | {status} | {lead} |")
    return "\n".join(rows)


def sort_key_asc(e):
    d = parse_date(e.get("date_start"))
    return d if d else date(9999, 12, 31)


def sort_key_desc(e):
    d = parse_date(e.get("date_start"))
    return d if d else date(1900, 1, 1)


def main():
    if not EVENTS_DIR.exists():
        sys.exit(f"Directory not found: {EVENTS_DIR}. Run from the repo root.")

    all_events = load_events()

    upcoming = sorted(
        [e for e in all_events if e.get("status") in UPCOMING_STATUSES],
        key=sort_key_asc,
    )

    print("# Events\n")
    print(f"## Upcoming ({len(upcoming)})\n")
    if upcoming:
        print(events_table(upcoming))
    else:
        print("_No upcoming events scheduled._")
    print()

    for status_key, status_label in COLLAPSED_STATUSES:
        group = sorted(
            [e for e in all_events if e.get("status") == status_key],
            key=sort_key_desc,
            reverse=True,
        )
        if not group:
            continue
        print(f"<details>\n<summary><strong>{status_label} ({len(group)})</strong></summary>\n")
        print(events_table(group))
        print("\n</details>\n")

    total = len(all_events)
    print(f"---\n_Generated from `data/events/` — {total} records total._")


if __name__ == "__main__":
    main()
