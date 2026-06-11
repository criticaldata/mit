#!/usr/bin/env python3
"""
Generate a static website from all YAML records under data/.

Output: data/site/
Run from the repo root:
    python scripts/generate_site.py
"""

from __future__ import annotations

import html
import json
import re
import shutil
from datetime import date, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SITE_DIR = DATA_DIR / "site"
ASSETS_DIR = SITE_DIR / "assets"
PHOTOS_DIR = ASSETS_DIR / "photos"

PEOPLE_DIR = DATA_DIR / "people"
PROJECTS_DIR = DATA_DIR / "projects"
EVENTS_DIR = DATA_DIR / "events"
FUNDING_DIR = DATA_DIR / "funding"
OUTPUTS_DIR = DATA_DIR / "outputs"
TALKS_DIR = DATA_DIR / "talks"

NAV = [
    ("index.html", "Dashboard"),
    ("people/index.html", "People"),
    ("projects/index.html", "Projects"),
    ("events/index.html", "Events"),
    ("funding/index.html", "Funding"),
    ("outputs/index.html", "Outputs"),
    ("talks/index.html", "Talks"),
]

STATUS_COLORS = {
    "active": "success",
    "confirmed": "success",
    "planned": "info",
    "prospect": "muted",
    "scheduled": "info",
    "awarded": "success",
    "published": "success",
    "accepted": "success",
    "completed": "muted",
    "alumni": "muted",
    "cancelled": "danger",
    "rejected": "danger",
    "withdrawn": "danger",
    "draft": "warning",
    "submitted": "info",
    "in-review": "info",
    "under-revision": "warning",
    "on-hold": "warning",
    "archived": "muted",
    "collaborator": "info",
}


def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"YAML error in {path}: {e}")
            return {}


def esc(val) -> str:
    if val is None:
        return ""
    return html.escape(str(val))


def parse_date(val):
    if not val:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").date()
    except ValueError:
        return None


def fmt_date(val) -> str:
    d = parse_date(val)
    return d.strftime("%d %b %Y") if d else ""


def fmt_date_range(start, end) -> str:
    s = parse_date(start)
    e = parse_date(end)
    if not s:
        return "TBD"
    if not e or s == e:
        return s.strftime("%d %b %Y")
    if s.month == e.month and s.year == e.year:
        return f"{s.day}–{e.strftime('%d %b %Y')}"
    return f"{s.strftime('%d %b')}–{e.strftime('%d %b %Y')}"


def leads(record: dict) -> list[str]:
    if record.get("leads"):
        return [s for s in record["leads"] if s]
    lead = record.get("lead")
    return [lead] if lead else []


def members(record: dict) -> set[str]:
    involved = set(leads(record))
    for m in record.get("team") or []:
        if m:
            involved.add(m)
    return involved


def badge(status: str) -> str:
    if not status:
        return ""
    kind = STATUS_COLORS.get(status.lower(), "muted")
    return f'<span class="badge badge-{kind}">{esc(status)}</span>'


def rel_href(from_path: str, target: str) -> str:
    """Return relative href from a page path to a target page path."""
    from_dir = Path(from_path).parent
    target_path = Path(target)
    try:
        return str(Path("../" * len(from_dir.parts)) / target_path).replace("\\", "/")
    except ValueError:
        return target


def link_person(slug: str, people: dict, page: str = "index.html") -> str:
    if not slug:
        return ""
    person = people.get(slug)
    name = person["name"] if person else slug
    href = rel_href(page, f"people/{slug}.html")
    return f'<a href="{href}">{esc(name)}</a>'


def link_list(items: list[str], people: dict, page: str, builder) -> str:
    if not items:
        return '<span class="muted">—</span>'
    return ", ".join(builder(item) for item in items)


def field_row(label: str, value: str) -> str:
    if not value:
        return ""
    return f"""
    <div class="field">
      <dt>{esc(label)}</dt>
      <dd>{value}</dd>
    </div>"""


def section(title: str, body: str) -> str:
    if not body.strip():
        return ""
    return f"""
    <section class="card">
      <h2>{esc(title)}</h2>
      {body}
    </section>"""


def layout(title: str, page_path: str, body: str, depth: int = 0) -> str:
    prefix = "../" * depth
    nav_links = []
    for href, label in NAV:
        full = prefix + href
        active = "active" if href == page_path or (
            href.endswith("/index.html") and page_path.startswith(href.replace("index.html", ""))
        ) else ""
        nav_links.append(f'<a class="nav-link {active}" href="{full}">{label}</a>')

    generated = datetime.now().strftime("%d %b %Y %H:%M")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{esc(title)} · MIT Critical Data</title>
  <link rel="stylesheet" href="{prefix}assets/style.css"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{prefix}index.html">
        <span class="brand-mark">MIT</span>
        <span class="brand-name">Critical Data</span>
      </a>
      <nav class="site-nav">{"".join(nav_links)}</nav>
    </div>
  </header>
  <main class="container page">
    {body}
  </main>
  <footer class="site-footer">
    <div class="container footer-inner">
      <p>Lab operations database · Generated {generated}</p>
      <p><a href="https://github.com/criticaldata/mit" target="_blank" rel="noopener">View source on GitHub</a></p>
    </div>
  </footer>
  <script src="{prefix}assets/app.js"></script>
</body>
</html>"""


# ── loaders ───────────────────────────────────────────────────────────────────

def load_people() -> dict[str, dict]:
    people = {}
    for f in sorted(PEOPLE_DIR.glob("*/person.yaml")):
        d = load_yaml(f)
        if not d.get("name"):
            continue
        slug = f.parent.name
        d["_slug"] = slug
        people[slug] = d
    return people


def load_projects() -> list[dict]:
    rows = []
    for f in sorted(PROJECTS_DIR.glob("*/project.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        d["_slug"] = f.parent.name
        rows.append(d)
    return rows


def load_events() -> list[dict]:
    rows = []
    for f in sorted(EVENTS_DIR.glob("*/*/event.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        year = f.parent.parent.name
        slug = f.parent.name
        d["_slug"] = slug
        d["_year"] = year
        d["_id"] = f"{year}/{slug}"
        rows.append(d)
    return rows


def load_funding() -> list[dict]:
    rows = []
    for f in sorted(FUNDING_DIR.glob("*/funding.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        d["_slug"] = f.parent.name
        rows.append(d)
    return rows


def load_outputs() -> list[dict]:
    rows = []
    for f in sorted(OUTPUTS_DIR.glob("*/*/output.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        year = f.parent.parent.name
        slug = f.parent.name
        d["_slug"] = slug
        d["_year"] = year
        d["_id"] = f"{year}/{slug}"
        rows.append(d)
    return rows


def load_talks() -> list[dict]:
    rows = []
    for f in sorted(TALKS_DIR.glob("*/*.yaml")):
        d = load_yaml(f)
        if not d.get("title"):
            continue
        d["_file"] = f.stem
        d["_year"] = f.parent.name
        rows.append(d)
    return rows


def copy_photos(people: dict[str, dict]) -> None:
    if PHOTOS_DIR.exists():
        shutil.rmtree(PHOTOS_DIR)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
    for slug, person in people.items():
        photo = person.get("photo")
        if not photo:
            continue
        src = PEOPLE_DIR / slug / photo
        if not src.exists():
            continue
        dest_dir = PHOTOS_DIR / slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest_dir / photo)


def photo_html(slug: str, person: dict, depth: int) -> str:
    photo = person.get("photo")
    if not photo:
        return ""
    prefix = "../" * depth
    src = f"{prefix}assets/photos/{slug}/{photo}"
    return f'<img class="avatar" src="{src}" alt="{esc(person.get("name", ""))}"/>'


def multiline(text: str) -> str:
    if not text or not str(text).strip():
        return ""
    return "<br/>".join(esc(line) for line in str(text).strip().splitlines())


def tags_html(tags) -> str:
    if not tags:
        return ""
    pills = "".join(f'<span class="tag">{esc(t)}</span>' for t in tags)
    return f'<div class="tags">{pills}</div>'


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_css() -> None:
    css = """/* MIT Critical Data lab site — matches criticaldata.mit.edu palette */
:root {
  --background: 0 0% 100%;
  --foreground: 0 0% 3.9%;
  --card: 0 0% 100%;
  --muted: 0 0% 96.1%;
  --muted-foreground: 0 0% 45.1%;
  --border: 0 0% 89.8%;
  --primary: 0 0% 9%;
  --primary-foreground: 0 0% 98%;
  --radius: 0.5rem;
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --danger: 0 84% 60%;
  --info: 217 91% 60%;
}

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif;
  background: hsl(var(--background));
  color: hsl(var(--foreground));
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

a { color: hsl(var(--primary)); text-decoration: none; }
a:hover { text-decoration: underline; }

.container { width: 100%; max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }

.site-header {
  position: sticky; top: 0; z-index: 50;
  border-bottom: 1px solid hsl(var(--border));
  background: hsl(var(--background) / 0.95);
  backdrop-filter: blur(8px);
}

.header-inner {
  display: flex; align-items: center; justify-content: space-between;
  min-height: 4rem; gap: 1rem; flex-wrap: wrap;
}

.brand { display: flex; align-items: baseline; gap: 0.5rem; text-decoration: none; color: inherit; }
.brand:hover { text-decoration: none; }
.brand-mark { font-weight: 700; letter-spacing: -0.02em; }
.brand-name { font-weight: 500; color: hsl(var(--muted-foreground)); }

.site-nav { display: flex; flex-wrap: wrap; gap: 0.25rem 0.75rem; }
.nav-link {
  font-size: 0.875rem; font-weight: 500; color: hsl(var(--muted-foreground));
  padding: 0.35rem 0.5rem; border-radius: calc(var(--radius) - 2px);
  text-decoration: none;
}
.nav-link:hover, .nav-link.active {
  color: hsl(var(--foreground)); background: hsl(var(--muted)); text-decoration: none;
}

.page { padding: 2rem 1.5rem 4rem; }

.page-header { margin-bottom: 2rem; }
.page-header h1 { margin: 0 0 0.5rem; font-size: 2rem; font-weight: 700; letter-spacing: -0.03em; }
.page-header p { margin: 0; color: hsl(var(--muted-foreground)); }

.stats {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem; margin-bottom: 2rem;
}

.stat-card {
  border: 1px solid hsl(var(--border)); border-radius: var(--radius);
  padding: 1.25rem; background: hsl(var(--card));
  transition: border-color 0.15s, box-shadow 0.15s;
}
.stat-card:hover { border-color: hsl(var(--foreground) / 0.2); box-shadow: 0 1px 3px hsl(0 0% 0% / 0.06); }
.stat-card a { color: inherit; text-decoration: none; }
.stat-card a:hover { text-decoration: none; }
.stat-value { font-size: 2rem; font-weight: 700; line-height: 1; margin-bottom: 0.35rem; }
.stat-label { font-size: 0.875rem; color: hsl(var(--muted-foreground)); }

.card {
  border: 1px solid hsl(var(--border)); border-radius: var(--radius);
  padding: 1.5rem; margin-bottom: 1.5rem; background: hsl(var(--card));
}
.card h2 { margin: 0 0 1rem; font-size: 1.125rem; font-weight: 600; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
@media (max-width: 768px) { .grid-2 { grid-template-columns: 1fr; } }

.toolbar {
  display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
  margin-bottom: 1.25rem;
}
.search-input {
  flex: 1; min-width: 220px; max-width: 420px;
  padding: 0.55rem 0.85rem; border: 1px solid hsl(var(--border));
  border-radius: var(--radius); font: inherit; background: hsl(var(--background));
}
.search-input:focus { outline: 2px solid hsl(var(--primary) / 0.15); border-color: hsl(var(--primary)); }

.filter-pills { display: flex; flex-wrap: wrap; gap: 0.35rem; }
.filter-pill {
  font-size: 0.8125rem; padding: 0.3rem 0.65rem; border-radius: 999px;
  border: 1px solid hsl(var(--border)); background: transparent; cursor: pointer; color: inherit;
}
.filter-pill.active, .filter-pill:hover {
  background: hsl(var(--primary)); color: hsl(var(--primary-foreground)); border-color: hsl(var(--primary));
}

.record-list { display: flex; flex-direction: column; gap: 0.75rem; }

.record-row {
  display: grid; grid-template-columns: 1fr auto; gap: 0.75rem 1.5rem;
  align-items: center; padding: 1rem 1.25rem;
  border: 1px solid hsl(var(--border)); border-radius: var(--radius);
  background: hsl(var(--card)); text-decoration: none; color: inherit;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.record-row:hover { border-color: hsl(var(--foreground) / 0.2); box-shadow: 0 1px 3px hsl(0 0% 0% / 0.06); text-decoration: none; }
.record-row.hidden { display: none; }

.record-title { font-weight: 600; margin-bottom: 0.2rem; }
.record-meta { font-size: 0.875rem; color: hsl(var(--muted-foreground)); }
.record-aside { display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem; }

.detail-header {
  display: flex; gap: 1.5rem; align-items: flex-start; margin-bottom: 1.5rem;
}
.detail-header .avatar {
  width: 96px; height: 96px; border-radius: var(--radius); object-fit: cover;
  border: 1px solid hsl(var(--border));
}
.detail-title { margin: 0 0 0.35rem; font-size: 1.75rem; font-weight: 700; letter-spacing: -0.03em; }
.detail-subtitle { color: hsl(var(--muted-foreground)); margin: 0; }

.fields { display: grid; gap: 0.85rem; }
.field { display: grid; grid-template-columns: 140px 1fr; gap: 0.75rem; font-size: 0.9375rem; }
.field dt { font-weight: 500; color: hsl(var(--muted-foreground)); margin: 0; }
.field dd { margin: 0; }

.badge {
  display: inline-flex; align-items: center; font-size: 0.75rem; font-weight: 500;
  padding: 0.15rem 0.55rem; border-radius: 999px; text-transform: capitalize;
  border: 1px solid transparent; white-space: nowrap;
}
.badge-success { background: hsl(var(--success) / 0.12); color: hsl(var(--success)); }
.badge-info { background: hsl(var(--info) / 0.12); color: hsl(var(--info)); }
.badge-warning { background: hsl(var(--warning) / 0.15); color: hsl(32 95% 35%); }
.badge-danger { background: hsl(var(--danger) / 0.12); color: hsl(var(--danger)); }
.badge-muted { background: hsl(var(--muted)); color: hsl(var(--muted-foreground)); }

.tags { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.5rem; }
.tag {
  font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 999px;
  background: hsl(var(--muted)); color: hsl(var(--muted-foreground));
}

.muted { color: hsl(var(--muted-foreground)); }
.prose { white-space: pre-wrap; }

.site-footer {
  border-top: 1px solid hsl(var(--border));
  padding: 1.5rem 0; margin-top: 2rem;
  font-size: 0.875rem; color: hsl(var(--muted-foreground));
}
.footer-inner { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; }
.footer-inner p { margin: 0; }

.year-group { margin-bottom: 1.75rem; }
.year-group h3 { font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.06em; color: hsl(var(--muted-foreground)); margin: 0 0 0.75rem; }
"""
    write(ASSETS_DIR / "style.css", css)


def write_js() -> None:
    js = """document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.querySelector('[data-search-input]');
  const list = document.querySelector('[data-record-list]');
  if (!searchInput || !list) return;

  const rows = [...list.querySelectorAll('[data-record-row]')];

  function applyFilters() {
    const q = searchInput.value.trim().toLowerCase();
    const activePill = document.querySelector('.filter-pill.active');
    const status = activePill ? activePill.dataset.filter : 'all';

    rows.forEach((row) => {
      const text = (row.dataset.search || row.textContent || '').toLowerCase();
      const rowStatus = row.dataset.status || '';
      const matchSearch = !q || text.includes(q);
      const matchStatus = status === 'all' || rowStatus === status;
      row.classList.toggle('hidden', !(matchSearch && matchStatus));
    });
  }

  searchInput.addEventListener('input', applyFilters);

  document.querySelectorAll('.filter-pill').forEach((pill) => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach((p) => p.classList.remove('active'));
      pill.classList.add('active');
      applyFilters();
    });
  });
});
"""
    write(ASSETS_DIR / "app.js", js)


def generate_index(people, projects, events, funding, outputs, talks) -> None:
    upcoming = sorted(
        [e for e in events if e.get("status") in {"confirmed", "planned", "prospect"}],
        key=lambda e: parse_date(e.get("date_start")) or date(9999, 12, 31),
    )[:8]
    active_projects = [p for p in projects if p.get("status") == "active"]
    scheduled_talks = sorted(
        [t for t in talks if t.get("status") == "scheduled"],
        key=lambda t: parse_date(t.get("date")) or date(9999, 12, 31),
    )[:6]

    stats = [
        ("people/index.html", len(people), "People"),
        ("projects/index.html", len(projects), "Projects"),
        ("events/index.html", len(events), "Events"),
        ("funding/index.html", len(funding), "Funding"),
        ("outputs/index.html", len(outputs), "Outputs"),
        ("talks/index.html", len(talks), "Talks"),
    ]
    stat_cards = "".join(
        f"""<a class="stat-card" href="{href}">
          <div class="stat-value">{count}</div>
          <div class="stat-label">{label}</div>
        </a>"""
        for href, count, label in stats
    )

    upcoming_rows = ""
    for e in upcoming:
        href = f"events/{e['_id']}.html"
        upcoming_rows += f"""
        <a class="record-row" href="{href}">
          <div>
            <div class="record-title">{esc(e['title'])}</div>
            <div class="record-meta">{fmt_date_range(e.get('date_start'), e.get('date_end'))} · {esc(e.get('city') or '')}{', ' + esc(e.get('country')) if e.get('country') else ''}</div>
          </div>
          <div class="record-aside">{badge(e.get('status', ''))}</div>
        </a>"""

    talk_rows = ""
    for t in scheduled_talks:
        href = f"talks/{t['_file']}.html"
        talk_rows += f"""
        <a class="record-row" href="{href}">
          <div>
            <div class="record-title">{esc(t['title'])}</div>
            <div class="record-meta">{fmt_date(t.get('date'))} · {esc(t.get('speaker', ''))}</div>
          </div>
          <div class="record-aside">{badge(t.get('status', ''))}</div>
        </a>"""

    body = f"""
    <div class="page-header">
      <h1>Lab Operations</h1>
      <p>Browse people, projects, events, funding, outputs, and talks from the lab database.</p>
    </div>
    <div class="stats">{stat_cards}</div>
    <div class="grid-2">
      {section("Upcoming events", f'<div class="record-list">{upcoming_rows or "<p class=\\"muted\\">No upcoming events.</p>"}</div>')}
      {section("Scheduled talks", f'<div class="record-list">{talk_rows or "<p class=\\"muted\\">No scheduled talks.</p>"}</div>')}
    </div>
    {section("Active projects", f'<p class="muted">{len(active_projects)} active research projects · <a href="projects/index.html">View all</a></p>')}
    """
    write(SITE_DIR / "index.html", layout("Dashboard", "index.html", body, depth=0))


def generate_people(people: dict[str, dict], projects, events, funding, outputs, talks) -> None:
    by_status = {"active": [], "collaborator": [], "alumni": []}
    for p in people.values():
        status = p.get("status", "collaborator")
        by_status.setdefault(status, []).append(p)

    filters = ["all", "active", "collaborator", "alumni"]
    pills = "".join(
        f'<button class="filter-pill{" active" if f == "all" else ""}" data-filter="{f}">{f.replace("-", " ").title() if f != "all" else "All"}</button>'
        for f in filters
    )

    rows = []
    for status in ["active", "collaborator", "alumni"]:
        for p in sorted(by_status.get(status, []), key=lambda x: x.get("name", "")):
            slug = p["_slug"]
            meta_parts = [p.get("role", ""), p.get("institution", ""), p.get("email", "")]
            meta = " · ".join(x for x in meta_parts if x)
            rows.append(f"""
            <a class="record-row" href="{slug}.html" data-record-row data-status="{esc(status)}"
               data-search="{esc(p.get('name','') + ' ' + meta)}">
              <div>
                <div class="record-title">{esc(p['name'])}</div>
                <div class="record-meta">{esc(meta)}</div>
              </div>
              <div class="record-aside">{badge(status)}</div>
            </a>""")

    body = f"""
    <div class="page-header"><h1>People</h1><p>{len(people)} lab members, collaborators, and alumni.</p></div>
    <div class="toolbar">
      <input class="search-input" type="search" placeholder="Search people…" data-search-input/>
      <div class="filter-pills">{pills}</div>
    </div>
    <div class="record-list" data-record-list>{"".join(rows)}</div>
    """
    write(SITE_DIR / "people" / "index.html", layout("People", "people/index.html", body, depth=1))

    for slug, p in people.items():
        linked_projects = [r for r in projects if slug in members(r)]
        linked_events = [r for r in events if slug in members(r)]
        linked_funding = [r for r in funding if slug in members(r)]
        linked_outputs = [r for r in outputs if slug in members(r)]
        linked_talks = [r for r in talks if r.get("speaker_link") == slug]

        rel_sections = []
        if linked_projects:
            items = "".join(
                f'<a class="record-row" href="../projects/{r["_slug"]}.html"><div><div class="record-title">{esc(r["title"])}</div><div class="record-meta">{esc(r.get("status",""))}</div></div></a>'
                for r in linked_projects
            )
            rel_sections.append(section("Projects", f'<div class="record-list">{items}</div>'))
        if linked_events:
            items = "".join(
                f'<a class="record-row" href="../events/{r["_id"]}.html"><div><div class="record-title">{esc(r["title"])}</div><div class="record-meta">{fmt_date_range(r.get("date_start"), r.get("date_end"))}</div></div></a>'
                for r in linked_events
            )
            rel_sections.append(section("Events", f'<div class="record-list">{items}</div>'))

        fields = "".join([
            field_row("Email", f'<a href="mailto:{esc(p.get("email",""))}">{esc(p.get("email",""))}</a>'),
            field_row("Secondary email", esc(p.get("email_secondary", ""))),
            field_row("Role", esc(p.get("role", ""))),
            field_row("Status", badge(p.get("status", ""))),
            field_row("Institution", esc(p.get("institution", ""))),
            field_row("Department", esc(p.get("department", ""))),
            field_row("Timezone", esc(p.get("timezone", ""))),
            field_row("GitHub", f'<a href="https://github.com/{esc(p["github"])}" target="_blank" rel="noopener">{esc(p.get("github",""))}</a>' if p.get("github") else ""),
            field_row("ORCID", f'<a href="https://orcid.org/{esc(p["orcid"])}" target="_blank" rel="noopener">{esc(p.get("orcid",""))}</a>' if p.get("orcid") else ""),
            field_row("Bio", f'<div class="prose">{multiline(p.get("bio",""))}</div>'),
            field_row("Research interests", f'<div class="prose">{multiline(p.get("research_interests",""))}</div>'),
        ])

        skills = p.get("skills") or []
        skills_html = ", ".join(esc(s) for s in skills) if skills else ""

        body = f"""
        <div class="detail-header">
          {photo_html(slug, p, depth=1)}
          <div>
            <h1 class="detail-title">{esc(p['name'])}</h1>
            <p class="detail-subtitle">{esc(p.get('role',''))}{' · ' + esc(p.get('institution','')) if p.get('institution') else ''}</p>
            {badge(p.get('status',''))}
            {tags_html(skills) if skills else ''}
          </div>
        </div>
        {section("Profile", f'<dl class="fields">{fields}</dl>')}
        {field_row("Skills", skills_html) and section("Skills", f'<p>{skills_html}</p>') or ""}
        {"".join(rel_sections)}
        """
        write(SITE_DIR / "people" / f"{slug}.html", layout(p["name"], f"people/{slug}.html", body, depth=1))


def generate_projects(people, projects, events, funding, outputs) -> None:
    statuses = sorted({p.get("status", "") for p in projects if p.get("status")})
    pills = '<button class="filter-pill active" data-filter="all">All</button>' + "".join(
        f'<button class="filter-pill" data-filter="{esc(s)}">{esc(s)}</button>' for s in statuses
    )
    rows = []
    for p in sorted(projects, key=lambda x: x.get("title", "")):
        lead_links = ", ".join(link_person(s, people, "projects/index.html") for s in leads(p))
        rows.append(f"""
        <a class="record-row" href="{p['_slug']}.html" data-record-row data-status="{esc(p.get('status',''))}"
           data-search="{esc(p.get('title','') + ' ' + ' '.join(leads(p)))}">
          <div>
            <div class="record-title">{esc(p['title'])}</div>
            <div class="record-meta">Lead: {lead_links or '—'}</div>
          </div>
          <div class="record-aside">{badge(p.get('status',''))}</div>
        </a>""")

    body = f"""
    <div class="page-header"><h1>Projects</h1><p>{len(projects)} research projects.</p></div>
    <div class="toolbar">
      <input class="search-input" type="search" placeholder="Search projects…" data-search-input/>
      <div class="filter-pills">{pills}</div>
    </div>
    <div class="record-list" data-record-list>{"".join(rows)}</div>
    """
    write(SITE_DIR / "projects" / "index.html", layout("Projects", "projects/index.html", body, depth=1))

    for p in projects:
        slug = p["_slug"]
        fields = "".join([
            field_row("Status", badge(p.get("status", ""))),
            field_row("Lead", ", ".join(link_person(s, people, f"projects/{slug}.html") for s in leads(p))),
            field_row("Team", ", ".join(link_person(s, people, f"projects/{slug}.html") for s in (p.get("team") or []))),
            field_row("Dates", f"{fmt_date(p.get('start_date'))} – {fmt_date(p.get('end_date')) or 'ongoing'}"),
            field_row("GitHub", f'<a href="{esc(p["github_repo"])}" target="_blank" rel="noopener">{esc(p.get("github_repo",""))}</a>' if p.get("github_repo") else ""),
            field_row("Description", f'<div class="prose">{multiline(p.get("description",""))}</div>'),
        ])
        body = f"""
        <div class="page-header">
          <h1 class="detail-title">{esc(p['title'])}</h1>
          {badge(p.get('status',''))}
          {tags_html(p.get('tags'))}
        </div>
        {section("Details", f'<dl class="fields">{fields}</dl>')}
        """
        write(SITE_DIR / "projects" / f"{slug}.html", layout(p["title"], f"projects/{slug}.html", body, depth=1))


def generate_events(people, events) -> None:
    statuses = sorted({e.get("status", "") for e in events if e.get("status")})
    pills = '<button class="filter-pill active" data-filter="all">All</button>' + "".join(
        f'<button class="filter-pill" data-filter="{esc(s)}">{esc(s)}</button>' for s in statuses
    )

    by_year: dict[str, list] = {}
    for e in events:
        by_year.setdefault(e["_year"], []).append(e)

    list_html = []
    for year in sorted(by_year.keys(), reverse=True):
        group_rows = []
        for e in sorted(by_year[year], key=lambda x: parse_date(x.get("date_start")) or date.min):
            loc = ", ".join(x for x in [e.get("city"), e.get("country")] if x)
            group_rows.append(f"""
            <a class="record-row" href="{e['_id']}.html" data-record-row data-status="{esc(e.get('status',''))}"
               data-search="{esc(e.get('title','') + ' ' + loc)}">
              <div>
                <div class="record-title">{esc(e['title'])}</div>
                <div class="record-meta">{fmt_date_range(e.get('date_start'), e.get('date_end'))} · {esc(loc or 'TBD')}</div>
              </div>
              <div class="record-aside">{badge(e.get('status',''))}</div>
            </a>""")
        list_html.append(f'<div class="year-group"><h3>{esc(year)}</h3><div class="record-list">{"".join(group_rows)}</div></div>')

    body = f"""
    <div class="page-header"><h1>Events</h1><p>{len(events)} conferences, datathons, workshops, and visits.</p></div>
    <div class="toolbar">
      <input class="search-input" type="search" placeholder="Search events…" data-search-input/>
      <div class="filter-pills">{pills}</div>
    </div>
    <div data-record-list>{"".join(list_html)}</div>
    """
    write(SITE_DIR / "events" / "index.html", layout("Events", "events/index.html", body, depth=1))

    for e in events:
        eid = e["_id"]
        loc = ", ".join(x for x in [e.get("city"), e.get("country")] if x)
        virtual = e.get("virtual")
        if virtual is True:
            loc = f"{loc} (virtual)" if loc else "Virtual"
        elif virtual == "hybrid":
            loc = f"{loc} (hybrid)" if loc else "Hybrid"

        fields = "".join([
            field_row("Status", badge(e.get("status", ""))),
            field_row("Type", esc(e.get("type", ""))),
            field_row("Dates", fmt_date_range(e.get("date_start"), e.get("date_end"))),
            field_row("Location", esc(loc)),
            field_row("Lead", link_person(e.get("lead", ""), people, f"events/{eid}.html")),
            field_row("Team", ", ".join(link_person(s, people, f"events/{eid}.html") for s in (e.get("team") or []))),
            field_row("URL", f'<a href="{esc(e["url"])}" target="_blank" rel="noopener">{esc(e.get("url",""))}</a>' if e.get("url") else ""),
            field_row("Description", f'<div class="prose">{multiline(e.get("description",""))}</div>'),
        ])
        body = f"""
        <div class="page-header">
          <h1 class="detail-title">{esc(e['title'])}</h1>
          <p class="detail-subtitle">{fmt_date_range(e.get('date_start'), e.get('date_end'))} · {esc(loc or 'TBD')}</p>
          {badge(e.get('status',''))}
          {tags_html(e.get('tags'))}
        </div>
        {section("Details", f'<dl class="fields">{fields}</dl>')}
        """
        write(SITE_DIR / "events" / f"{eid}.html", layout(e["title"], f"events/{eid}.html", body, depth=1))


def generate_funding(people, funding) -> None:
    statuses = sorted({f.get("status", "") for f in funding if f.get("status")})
    pills = '<button class="filter-pill active" data-filter="all">All</button>' + "".join(
        f'<button class="filter-pill" data-filter="{esc(s)}">{esc(s.replace("-", " "))}</button>' for s in statuses
    )
    rows = []
    for f in sorted(funding, key=lambda x: x.get("title", "")):
        rows.append(f"""
        <a class="record-row" href="{f['_slug']}.html" data-record-row data-status="{esc(f.get('status',''))}"
           data-search="{esc(f.get('title','') + ' ' + (f.get('agency') or ''))}">
          <div>
            <div class="record-title">{esc(f['title'])}</div>
            <div class="record-meta">{esc(f.get('agency') or '')} · {esc(f.get('type') or '')}</div>
          </div>
          <div class="record-aside">{badge(f.get('status',''))}</div>
        </a>""")

    body = f"""
    <div class="page-header"><h1>Funding</h1><p>{len(funding)} grants and sponsored research records.</p></div>
    <div class="toolbar">
      <input class="search-input" type="search" placeholder="Search funding…" data-search-input/>
      <div class="filter-pills">{pills}</div>
    </div>
    <div class="record-list" data-record-list>{"".join(rows)}</div>
    """
    write(SITE_DIR / "funding" / "index.html", layout("Funding", "funding/index.html", body, depth=1))

    for f in funding:
        slug = f["_slug"]
        amount = ""
        if f.get("amount_awarded"):
            amount = f"{f.get('amount_awarded'):,} {f.get('currency', 'USD')} awarded"
        elif f.get("amount_requested"):
            amount = f"{f"{f.get('amount_requested'):,}"} {f.get('currency', 'USD')} requested"

        fields = "".join([
            field_row("Status", badge(f.get("status", ""))),
            field_row("Agency", esc(f.get("agency", ""))),
            field_row("Program", esc(f.get("program", ""))),
            field_row("Type", esc(f.get("type", ""))),
            field_row("Grant number", esc(f.get("grant_number", ""))),
            field_row("Lead", link_person(f.get("lead", ""), people, f"funding/{slug}.html")),
            field_row("Team", ", ".join(link_person(s, people, f"funding/{slug}.html") for s in (f.get("team") or []))),
            field_row("Amount", esc(amount)),
            field_row("Submission", fmt_date(f.get("date_submission"))),
            field_row("Period", f"{fmt_date(f.get('date_start'))} – {fmt_date(f.get('date_end')) or 'ongoing'}"),
            field_row("URL", f'<a href="{esc(f["url"])}" target="_blank" rel="noopener">{esc(f.get("url",""))}</a>' if f.get("url") else ""),
            field_row("Description", f'<div class="prose">{multiline(f.get("description",""))}</div>'),
        ])
        body = f"""
        <div class="page-header">
          <h1 class="detail-title">{esc(f['title'])}</h1>
          <p class="detail-subtitle">{esc(f.get('agency') or '')}</p>
          {badge(f.get('status',''))}
          {tags_html(f.get('tags'))}
        </div>
        {section("Details", f'<dl class="fields">{fields}</dl>')}
        """
        write(SITE_DIR / "funding" / f"{slug}.html", layout(f["title"], f"funding/{slug}.html", body, depth=1))


def generate_outputs(people, outputs) -> None:
    statuses = sorted({o.get("status", "") for o in outputs if o.get("status")})
    pills = '<button class="filter-pill active" data-filter="all">All</button>' + "".join(
        f'<button class="filter-pill" data-filter="{esc(s)}">{esc(s)}</button>' for s in statuses
    )
    rows = []
    for o in sorted(outputs, key=lambda x: x.get("title", "")):
        rows.append(f"""
        <a class="record-row" href="{o['_id']}.html" data-record-row data-status="{esc(o.get('status',''))}"
           data-search="{esc(o.get('title','') + ' ' + (o.get('type') or ''))}">
          <div>
            <div class="record-title">{esc(o['title'])}</div>
            <div class="record-meta">{esc(o.get('type') or '')} · {esc(o.get('venue') or '')}</div>
          </div>
          <div class="record-aside">{badge(o.get('status',''))}</div>
        </a>""")

    body = f"""
    <div class="page-header"><h1>Outputs</h1><p>{len(outputs)} papers, datasets, software, and reports.</p></div>
    <div class="toolbar">
      <input class="search-input" type="search" placeholder="Search outputs…" data-search-input/>
      <div class="filter-pills">{pills}</div>
    </div>
    <div class="record-list" data-record-list>{"".join(rows)}</div>
    """
    write(SITE_DIR / "outputs" / "index.html", layout("Outputs", "outputs/index.html", body, depth=1))

    for o in outputs:
        oid = o["_id"]
        fields = "".join([
            field_row("Status", badge(o.get("status", ""))),
            field_row("Type", esc(o.get("type", ""))),
            field_row("Lead", link_person(o.get("lead", ""), people, f"outputs/{oid}.html")),
            field_row("Team", ", ".join(link_person(s, people, f"outputs/{oid}.html") for s in (o.get("team") or []))),
            field_row("Venue", esc(o.get("venue", ""))),
            field_row("Submitted", fmt_date(o.get("date_submitted"))),
            field_row("Published", fmt_date(o.get("date_published"))),
            field_row("DOI", f'<a href="https://doi.org/{esc(o["doi"])}" target="_blank" rel="noopener">{esc(o.get("doi",""))}</a>' if o.get("doi") else ""),
            field_row("URL", f'<a href="{esc(o["url"])}" target="_blank" rel="noopener">{esc(o.get("url",""))}</a>' if o.get("url") else ""),
            field_row("GitHub", f'<a href="{esc(o["github_repo"])}" target="_blank" rel="noopener">{esc(o.get("github_repo",""))}</a>' if o.get("github_repo") else ""),
            field_row("Description", f'<div class="prose">{multiline(o.get("description",""))}</div>'),
        ])
        body = f"""
        <div class="page-header">
          <h1 class="detail-title">{esc(o['title'])}</h1>
          <p class="detail-subtitle">{esc(o.get('type') or '')}{' · ' + esc(o.get('venue')) if o.get('venue') else ''}</p>
          {badge(o.get('status',''))}
          {tags_html(o.get('tags'))}
        </div>
        {section("Details", f'<dl class="fields">{fields}</dl>')}
        """
        write(SITE_DIR / "outputs" / f"{oid}.html", layout(o["title"], f"outputs/{oid}.html", body, depth=1))


def generate_talks(people, talks) -> None:
    statuses = sorted({t.get("status", "") for t in talks if t.get("status")})
    pills = '<button class="filter-pill active" data-filter="all">All</button>' + "".join(
        f'<button class="filter-pill" data-filter="{esc(s)}">{esc(s)}</button>' for s in statuses
    )
    rows = []
    for t in sorted(talks, key=lambda x: parse_date(x.get("date")) or date.min, reverse=True):
        speaker = t.get("speaker", "")
        if t.get("speaker_link") and t["speaker_link"] in people:
            speaker = people[t["speaker_link"]]["name"]
        rows.append(f"""
        <a class="record-row" href="{t['_file']}.html" data-record-row data-status="{esc(t.get('status',''))}"
           data-search="{esc(t.get('title','') + ' ' + speaker)}">
          <div>
            <div class="record-title">{esc(t['title'])}</div>
            <div class="record-meta">{fmt_date(t.get('date'))} · {esc(speaker)}</div>
          </div>
          <div class="record-aside">{badge(t.get('status',''))}</div>
        </a>""")

    body = f"""
    <div class="page-header"><h1>Talks</h1><p>{len(talks)} lab presentations and invited talks.</p></div>
    <div class="toolbar">
      <input class="search-input" type="search" placeholder="Search talks…" data-search-input/>
      <div class="filter-pills">{pills}</div>
    </div>
    <div class="record-list" data-record-list>{"".join(rows)}</div>
    """
    write(SITE_DIR / "talks" / "index.html", layout("Talks", "talks/index.html", body, depth=1))

    for t in talks:
        fid = t["_file"]
        speaker = t.get("speaker", "")
        speaker_field = esc(speaker)
        if t.get("speaker_link"):
            speaker_field = link_person(t["speaker_link"], people, f"talks/{fid}.html")
            if t.get("speaker_affiliation"):
                speaker_field += f' <span class="muted">({esc(t["speaker_affiliation"])})</span>'

        fields = "".join([
            field_row("Date", fmt_date(t.get("date"))),
            field_row("Time", esc(t.get("time", ""))),
            field_row("Speaker", speaker_field),
            field_row("Type", esc(t.get("type", ""))),
            field_row("Status", badge(t.get("status", ""))),
            field_row("Abstract", f'<div class="prose">{multiline(t.get("abstract",""))}</div>'),
            field_row("Slides", f'<a href="{esc(t["slides_url"])}" target="_blank" rel="noopener">{esc(t.get("slides_url",""))}</a>' if t.get("slides_url") else ""),
            field_row("Recording", f'<a href="{esc(t["recording_url"])}" target="_blank" rel="noopener">{esc(t.get("recording_url",""))}</a>' if t.get("recording_url") else ""),
            field_row("Notes", f'<div class="prose">{multiline(t.get("notes",""))}</div>'),
        ])
        body = f"""
        <div class="page-header">
          <h1 class="detail-title">{esc(t['title'])}</h1>
          <p class="detail-subtitle">{fmt_date(t.get('date'))}{' · ' + esc(t.get('time','')) if t.get('time') else ''}</p>
          {badge(t.get('status',''))}
          {tags_html(t.get('tags'))}
        </div>
        {section("Details", f'<dl class="fields">{fields}</dl>')}
        """
        write(SITE_DIR / "talks" / f"{fid}.html", layout(t["title"], f"talks/{fid}.html", body, depth=1))


def clean_site_dir() -> None:
    """Remove old generated HTML while preserving nothing user-authored."""
    if SITE_DIR.exists():
        for sub in SITE_DIR.iterdir():
            if sub.name == "README.md":
                continue
            if sub.is_dir():
                shutil.rmtree(sub)
            else:
                sub.unlink()


def main() -> None:
    people = load_people()
    projects = load_projects()
    events = load_events()
    funding = load_funding()
    outputs = load_outputs()
    talks = load_talks()

    clean_site_dir()
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    write_css()
    write_js()
    copy_photos(people)

    generate_index(people, projects, events, funding, outputs, talks)
    generate_people(people, projects, events, funding, outputs, talks)
    generate_projects(people, projects, events, funding, outputs)
    generate_events(people, events)
    generate_funding(people, funding)
    generate_outputs(people, outputs)
    generate_talks(people, talks)

    total_pages = 1 + sum([
        1 + len(people),
        1 + len(projects),
        1 + len(events),
        1 + len(funding),
        1 + len(outputs),
        1 + len(talks),
    ])
    print(f"Generated {total_pages} pages in {SITE_DIR.relative_to(REPO_ROOT)}/")


if __name__ == "__main__":
    main()
