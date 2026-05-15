#!/usr/bin/env python3
"""
Generate the lab presentation schedule from data/talks/*.yaml.
Outputs a table of every Tuesday for the next 4 months, with talk
details filled in where a matching YAML file exists.

Run from the repo root:
    py scripts/generate_schedule.py
"""

import io
import sys
import yaml
from pathlib import Path
from datetime import date, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TALKS_DIR = Path("data/talks")
PEOPLE_DIR = Path("data/people")
MONTHS_AHEAD = 4


def load_talks():
    """Return a dict of date -> talk data."""
    talks = {}
    for f in TALKS_DIR.glob("*.yaml"):
        with open(f, encoding="utf-8") as fh:
            try:
                data = yaml.safe_load(fh)
            except yaml.YAMLError as e:
                print(f"YAML error in {f}: {e}", file=sys.stderr)
                continue
        if not data or not data.get("date"):
            continue
        d = data["date"]
        if not isinstance(d, date):
            try:
                from datetime import datetime
                d = datetime.strptime(str(d), "%Y-%m-%d").date()
            except ValueError:
                continue
        talks[d] = data
    return talks


def tuesdays(start: date, months: int):
    """Yield every Tuesday from the first Tuesday >= start through ~months months."""
    # Advance to the next Tuesday (weekday 1)
    days_until = (1 - start.weekday()) % 7
    current = start + timedelta(days=days_until)
    end = date(start.year + (start.month + months - 1) // 12,
               (start.month + months - 1) % 12 + 1,
               start.day)
    while current <= end:
        yield current
        current += timedelta(weeks=1)


def resolve_speaker(talk):
    name = talk.get("speaker", "")
    affiliation = talk.get("speaker_affiliation")
    if affiliation:
        name = f"{name} ({affiliation})"
    link_slug = talk.get("speaker_link")
    if link_slug:
        person_file = PEOPLE_DIR / link_slug / "person.yaml"
        if person_file.exists():
            name = f"[{name}](data/people/{link_slug}/person.yaml)"
    return name


def main():
    if not TALKS_DIR.exists():
        sys.exit(f"Directory not found: {TALKS_DIR}. Run from the repo root.")

    talks = load_talks()
    today = date.today()

    rows = ["| Date | Speaker | Affiliation | Title | Type |",
            "|---|---|---|---|---|"]

    for tuesday in tuesdays(today, MONTHS_AHEAD):
        d_str = tuesday.strftime("%a %d %b %Y")
        t = talks.get(tuesday)
        if t:
            status = t.get("status", "")
            if status == "cancelled":
                rows.append(f"| {d_str} | ~~cancelled~~ | | | |")
                continue
            speaker = t.get("speaker", "")
            affiliation = t.get("speaker_affiliation", "")
            link_slug = t.get("speaker_link")
            if link_slug:
                person_file = PEOPLE_DIR / link_slug / "person.yaml"
                if person_file.exists():
                    speaker = f"[{speaker}](data/people/{link_slug}/person.yaml)"
            title = t.get("title", "")
            if t.get("slides_url"):
                title = f"[{title}]({t['slides_url']})"
            elif t.get("recording_url"):
                title = f"[{title} (recording)]({t['recording_url']})"
            time_str = t.get("time", "")
            if time_str:
                d_str = f"{d_str} {time_str}"
            talk_type = t.get("type", "")
            rows.append(f"| {d_str} | {speaker} | {affiliation} | {title} | {talk_type} |")
        else:
            rows.append(f"| {d_str} | | | | |")

    print("# Lab Presentation Schedule\n")
    print("\n".join(rows))
    booked = sum(1 for t in tuesdays(today, MONTHS_AHEAD) if t in talks)
    total = sum(1 for _ in tuesdays(today, MONTHS_AHEAD))
    print(f"\n_{booked}/{total} slots filled — generated from `data/talks/`_")


if __name__ == "__main__":
    main()
