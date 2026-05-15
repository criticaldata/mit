#!/usr/bin/env python3
"""
Import Notion CSV exports (People, Projects, Events) into YAML records.
Run from repo root: py scripts/import_notion.py

People:   creates new person.yaml; updates existing with whatsapp, timezone,
          email_secondary, skills, institution if those fields are currently empty.
Projects: creates new project.yaml files; skips existing slugs.
Events:   creates new event.yaml files; skips existing slugs.
"""

import csv
import io
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PEOPLE_DIR  = Path("data/people")
PROJECTS_DIR = Path("data/projects")
EVENTS_DIR  = Path("data/events")
IMPORT_DIR  = Path("data/notion_import")

PEOPLE_CSV   = IMPORT_DIR / "People 306e4faff87f80acbe9ede6a68457018.csv"
PROJECTS_CSV = IMPORT_DIR / "Projects 307e4faff87f8087a01cecae925e4b61.csv"
EVENTS_CSV   = IMPORT_DIR / "Events 318e4faff87f80129fcadd3eee157f1e.csv"

# Manual slug overrides: generated-slug -> correct-existing-slug
PERSON_SLUG_OVERRIDES = {
    "leo-anthony-celi":          "leo-celi",
    "ryohei-yamamoto-kobayashi": "ryohei-kobayashi-yamamoto",
}

# ── helpers ──────────────────────────────────────────────────────────────────

def slugify(text):
    """Lowercase kebab-case slug from freeform text."""
    text = re.sub(r'\(https?://[^)]+\)', '', text)   # strip notion URLs
    text = re.sub(r'\([^)]*\)', '', text)             # strip parentheticals
    text = text.strip()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def person_slug(name):
    s = slugify(name)
    return PERSON_SLUG_OVERRIDES.get(s, s)


def extract_name(notion_ref):
    """'Foo Bar (https://...)' -> 'Foo Bar'"""
    m = re.match(r'^(.+?)\s*\(https?://', notion_ref.strip())
    return m.group(1).strip() if m else notion_ref.strip()


def parse_notion_date(s):
    """Parse 'February 19, 2026' or '2026-02-19' -> 'YYYY-MM-DD' or None."""
    s = s.strip()
    if not s:
        return None
    for fmt in ('%B %d, %Y', '%Y-%m-%d'):
        try:
            return datetime.strptime(s, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    return None


def parse_date_range(s):
    """'March 23, 2026 → March 25, 2026' -> (start, end)"""
    s = s.strip()
    if '→' in s:
        parts = [p.strip() for p in s.split('→')]
        return parse_notion_date(parts[0]), parse_notion_date(parts[1])
    return parse_notion_date(s), None


def split_list(s):
    """Split comma-separated Notion multi-select into a cleaned list."""
    if not s:
        return []
    items = re.split(r',\s*(?=[A-Z(])', s)  # split on comma before capital/paren
    return [i.strip() for i in items if i.strip()]


def skills_list(s):
    if not s:
        return []
    return [t.strip().lower() for t in re.split(r'[,\n]+', s) if t.strip()]


def tags_from_research_area(s):
    if not s:
        return []
    return [slugify(t) for t in re.split(r'[,/&]+', s) if t.strip()]


def read_yaml(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False,
                  sort_keys=False, width=120)


def gitkeep(folder):
    gk = folder / 'updates' / '.gitkeep'
    gk.parent.mkdir(parents=True, exist_ok=True)
    if not gk.exists():
        gk.touch()


# ── group / type maps ─────────────────────────────────────────────────────────

def group_to_status(group):
    groups = {g.strip().lower() for g in group.split(',')}
    if groups & {'lcp', 'mit critical data'}:
        return 'active'
    return 'collaborator'


def group_to_role(group):
    groups = {g.strip().lower() for g in group.split(',')}
    if 'visiting scholars' in groups:
        return 'Visiting Scientist'
    if 'students' in groups:
        return 'PhD Student'
    return 'Affiliate'


PROJECT_STATUS_MAP = {
    'active':             'active',
    'nearing completion': 'active',
    'completed':          'completed',
    'on hold':            'on-hold',
    'archived':           'archived',
}

EVENT_STATUS_MAP = {
    'completed':     'completed',
    'in planning':   'planned',
    'not confirmed': 'prospect',
    'in progress':   'confirmed',
    'in progress ':  'confirmed',
}

EVENT_TYPE_MAP = {
    'datathon':          'hackathon',
    'workshop':          'workshop',
    'meeting':           'other',
    'lab meeting':       'other',
    'seminar':           'seminar',
    'conference':        'conference',
    'congress':          'conference',
    'lecture':           'lecture',
    'webinar':           'webinar',
}

def map_event_type(s):
    s = s.lower()
    for k, v in EVENT_TYPE_MAP.items():
        if k in s:
            return v
    return 'other'


# ── people ────────────────────────────────────────────────────────────────────

def import_people():
    print("\n── PEOPLE ──────────────────────────────")
    created = updated = skipped = 0

    with open(PEOPLE_CSV, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        name = row.get('Name', '').strip()
        if not name:
            continue

        slug = person_slug(name)
        yaml_path = PEOPLE_DIR / slug / 'person.yaml'
        notion_email = row.get('Email', '').strip()
        whatsapp     = row.get('WhatsApp', '').strip()
        group        = row.get('Group', '').strip()
        affiliation  = row.get('Affiliation', '').strip()
        timezone     = row.get('Time Zone', '').strip()
        research     = row.get('Research Area', '').strip()
        skills_raw   = row.get('Skills', '').strip()

        if yaml_path.exists():
            # UPDATE existing record with missing fields only
            data = read_yaml(yaml_path)
            changed = False

            existing_email = data.get('email', '')
            if notion_email and notion_email != existing_email:
                if not data.get('email_secondary'):
                    data['email_secondary'] = notion_email
                    changed = True

            if whatsapp and not data.get('whatsapp'):
                data['whatsapp'] = f'"{whatsapp}"' if not whatsapp.startswith('"') else whatsapp
                changed = True

            if timezone and not data.get('timezone'):
                data['timezone'] = timezone.strip()
                changed = True

            if affiliation and not data.get('institution'):
                data['institution'] = affiliation
                changed = True

            if research and not data.get('research_interests'):
                data['research_interests'] = research
                changed = True

            sk = skills_list(skills_raw)
            if sk and not data.get('skills'):
                data['skills'] = sk
                changed = True

            if changed:
                write_yaml(yaml_path, data)
                print(f"  updated  {slug}")
                updated += 1
            else:
                print(f"  no-op    {slug}")
                skipped += 1

        else:
            # CREATE new record
            primary_email = notion_email
            data = {'name': name}
            if primary_email:
                data['email'] = primary_email
            data['role']   = group_to_role(group)
            data['status'] = group_to_status(group)
            if affiliation:
                data['institution'] = affiliation
            if timezone:
                data['timezone'] = timezone.strip()
            if whatsapp:
                data['whatsapp'] = f'"{whatsapp}"' if not whatsapp.startswith('"') else whatsapp
            if research:
                data['research_interests'] = research
            sk = skills_list(skills_raw)
            if sk:
                data['skills'] = sk

            write_yaml(yaml_path, data)
            gitkeep(PEOPLE_DIR / slug)
            print(f"  created  {slug}")
            created += 1

    print(f"  → {created} created, {updated} updated, {skipped} no-op")


# ── projects ──────────────────────────────────────────────────────────────────

def import_projects():
    print("\n── PROJECTS ────────────────────────────")
    created = skipped = 0

    with open(PROJECTS_CSV, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        title = row.get('Project Name', '').strip()
        if not title:
            continue

        slug = slugify(title)
        yaml_path = PROJECTS_DIR / slug / 'project.yaml'

        if yaml_path.exists():
            print(f"  exists   {slug} — skipped")
            skipped += 1
            continue

        # resolve lead slug
        lead_raw = row.get('Project Lead', '').strip()
        lead_name = extract_name(lead_raw) if lead_raw else ''
        lead_slug = person_slug(lead_name) if lead_name else ''

        # resolve team slugs
        team_raw = row.get('Team Members', '').strip()
        team_slugs = []
        if team_raw:
            for ref in split_list(team_raw):
                n = extract_name(ref)
                if n:
                    team_slugs.append(person_slug(n))

        status_raw = row.get('Status', '').strip().lower()
        status     = PROJECT_STATUS_MAP.get(status_raw, 'active')

        data = {
            'title':       title,
            'status':      status,
            'lead':        lead_slug,
        }
        if team_slugs:
            data['team'] = team_slugs

        start = parse_notion_date(row.get('Start Date', ''))
        end   = parse_notion_date(row.get('Target End Date', ''))
        if start:
            data['start_date'] = start
        if end:
            data['end_date'] = end

        github = row.get('GitHub Repository', '').strip()
        if github and github.startswith('http'):
            data['github_repo'] = github

        desc = row.get('Description', '').strip()
        if desc:
            data['description'] = desc

        tags = tags_from_research_area(row.get('Research Area', ''))
        if tags:
            data['tags'] = tags

        write_yaml(yaml_path, data)
        gitkeep(PROJECTS_DIR / slug)
        print(f"  created  {slug}")
        created += 1

    print(f"  → {created} created, {skipped} skipped (already exist)")


# ── events ────────────────────────────────────────────────────────────────────

def import_events():
    print("\n── EVENTS ──────────────────────────────")
    created = skipped = 0

    with open(EVENTS_CSV, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        name = row.get('Name', '').strip()
        if not name:
            continue

        date_str = row.get('Event Date', '').strip()
        start, end = parse_date_range(date_str)

        # build slug: type-name-year (or just name if no date)
        year = start[:4] if start else ''
        slug = slugify(f"{name}-{year}" if year else name)

        yaml_path = EVENTS_DIR / slug / 'event.yaml'
        if yaml_path.exists():
            print(f"  exists   {slug} — skipped")
            skipped += 1
            continue

        status_raw = row.get('Status', '').strip().lower()
        status     = EVENT_STATUS_MAP.get(status_raw, 'prospect')

        event_type_raw = row.get('Event Type', '').strip()
        event_type     = map_event_type(event_type_raw)

        location = row.get('Location', '').strip()
        city = country = ''
        if ',' in location:
            parts = [p.strip() for p in location.rsplit(',', 1)]
            city, country = parts[0], parts[1]
        elif location:
            country = location

        lead_raw  = row.get('Event Lead', '').strip()
        lead_name = extract_name(lead_raw) if lead_raw else ''
        lead_slug = person_slug(lead_name) if lead_name else ''

        data = {
            'title':  name,
            'type':   event_type,
            'status': status,
        }
        if start:
            data['date_start'] = start
        if end:
            data['date_end'] = end
        if city:
            data['city'] = city
        if country:
            data['country'] = country
        if lead_slug:
            data['lead'] = lead_slug

        desc = row.get('Description', '').strip()
        if desc:
            data['description'] = desc

        funding = row.get('Funding', '').strip()
        if funding and funding.lower() not in ('', 'n/a', 'non applicable', 'unnecessary'):
            data['tags'] = ['healthcare-ai']

        write_yaml(yaml_path, data)
        gitkeep(EVENTS_DIR / slug)
        print(f"  created  {slug}")
        created += 1

    print(f"  → {created} created, {skipped} skipped (already exist)")


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    for d in (PEOPLE_DIR, PROJECTS_DIR, EVENTS_DIR):
        if not d.exists():
            sys.exit(f"Directory not found: {d}. Run from repo root.")
    if not IMPORT_DIR.exists():
        sys.exit(f"Import directory not found: {IMPORT_DIR}")

    import_people()
    import_projects()
    import_events()
    print("\nDone.")
