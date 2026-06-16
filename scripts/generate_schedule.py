#!/usr/bin/env python3
"""
Generate the lab presentation schedule from data/talks/*.yaml.
Outputs a table covering the next 4 months:
  - Every Tuesday gets a row (blank if no talk scheduled)
  - Non-Tuesday days with a talk are also included

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
    """Return a dict of date -> list of talk data."""
    talks = {}
    for f in sorted(TALKS_DIR.glob("*/*.yaml")):
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
        talks.setdefault(d, []).append(data)
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
            name = f"[{name}](../people/{link_slug}/)"
    return name


def render_talk(d, t):
    """Return a table row string for a single talk on date d."""
    d_str = d.strftime("%a %d %b %Y")
    status = t.get("status", "")
    if status == "cancelled":
        return f"| {d_str} | ~~cancelled~~ | | | |"
    speaker = t.get("speaker") or ""
    affiliation = t.get("speaker_affiliation") or ""
    link_slug = t.get("speaker_link")
    if link_slug:
        person_file = PEOPLE_DIR / link_slug / "person.yaml"
        if person_file.exists():
            speaker = f"[{speaker}](../people/{link_slug}/)"
    title = t.get("title") or ""
    if t.get("slides_url"):
        title = f"[{title}]({t['slides_url']})"
    elif t.get("recording_url"):
        title = f"[{title} (recording)]({t['recording_url']})"
    time_str = t.get("time", "")
    t_str = f"{d_str} {time_str}" if time_str else d_str
    talk_type = t.get("type", "")
    return f"| {t_str} | {speaker} | {affiliation} | {title} | {talk_type} |"


def main():
    if not TALKS_DIR.exists():
        sys.exit(f"Directory not found: {TALKS_DIR}. Run from the repo root.")

    talks = load_talks()
    today = date.today()
    tuesday_set = set(tuesdays(today, MONTHS_AHEAD))

    # All dates to render: Tuesdays + any non-Tuesday day with a talk
    end = max(tuesday_set) if tuesday_set else today
    extra = {d for d in talks if d not in tuesday_set and today <= d <= end}
    all_dates = sorted(tuesday_set | extra)

    rows = ["| Date | Speaker | Affiliation | Title | Type |",
            "|---|---|---|---|---|"]

    for d in all_dates:
        day_talks = talks.get(d)
        if day_talks:
            for t in day_talks:
                rows.append(render_talk(d, t))
        else:
            rows.append(f"| {d.strftime('%a %d %b %Y')} | | | | |")

    print("# Lab Presentation Schedule\n")
    print("\n".join(rows))
    booked = sum(1 for t in tuesday_set if t in talks)
    total = len(tuesday_set)
    print(f"\n_{booked}/{total} Tuesday slots filled — generated from `data/talks/`_")


if __name__ == "__main__":
    main()
