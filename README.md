# MIT Critical Data — Lab Operations

## Quick links

| 📋 Resources | 📊 Directory |
|---|---|
| 🚀 [Onboarding](docs/onboarding/) | 👥 [People](data/people/README.md) |
| 📅 [Presentation schedule](data/talks/) | 📁 [Active projects](data/projects/README.md) / [Submit new project](https://forms.gle/fsPGeudtrjyA6sw59) |
| 📊 [Lab Dashboard](DASHBOARD.md) | 🗓️ [Upcoming events](data/events/README.md) |
| 🏢 [IMES Room Reservations](https://imes.skedda.com/booking) | |

---

This repository is the operational database for MIT Critical Data. It tracks our people, projects, events, funding, and outputs as plain-text YAML files, organized in Git for auditability and transparency.

**This database is only as useful as the data in it.** Keeping records accurate and up to date is a shared responsibility — everyone in the lab is expected to contribute updates when things change.

## What's in here

- **people/** — lab members, alumni, and collaborators
- **projects/** — active and past research projects
- **events/** — conferences, workshops, datathons, and talks
- **funding/** — grants, sponsored research, and other funding sources
- **outputs/** — papers, datasets, software, and other lab products
- **talks/** — lab presentation schedule, one YAML file per talk
- **scripts/** — automation and validation utilities
- **docs/** — schema documentation and contribution guides

## 📝 Adding updates & meeting notes

The most common task in this repo is adding notes from meetings, calls, or project check-ins. To do this:

1. Navigate to the relevant record folder (e.g. `data/projects/mimic-iv/updates/`)
2. Create a new file prefixed with today's date: `YYYY-MM-DD-description.ext`

Examples:
- `2026-01-15-meeting-notes.md` — written notes
- `2026-01-15-fathom-transcript.pdf` — raw transcript export
- `2026-01-15-decisions.md` — key decisions recorded

3. Commit and push using your preferred Git tool (e.g. GitHub Desktop, command line, or the GitHub web editor for quick edits)

The date prefix is the only required convention — it keeps updates sorted chronologically and findable. No reformatting of raw transcript exports is needed; upload them as-is.

To update a project's core details (status, team, funding links), edit `project.yaml` directly in the same folder.

---

## 📅 Scheduling a presentation

Lab meetings are held **every Tuesday**. Each talk is a single YAML file in `data/talks/`.

**File naming:** `YYYY-MM-DD-speaker-slug.yaml` (e.g. `2026-06-10-jane-smith.yaml`)

**Minimal example:**

```yaml
title: My Research Talk
speaker: Jane Smith
speaker_affiliation: Stanford Medicine
date: 2026-06-10
time: "11:00 ET"
type: invited
status: scheduled
```

**Full fields:**

| Field | Required | Notes |
|---|---|---|
| `title` | ✅ | Talk title |
| `speaker` | ✅ | Freeform name — guest or lab member |
| `speaker_affiliation` | | Institution or company |
| `speaker_link` | | Folder name in `data/people/` if the speaker is a lab member |
| `date` | ✅ | `YYYY-MM-DD` |
| `time` | | e.g. `"11:00 ET"` |
| `type` | | `lab-meeting`, `journal-club`, `external`, `invited`, `other` |
| `status` | ✅ | `scheduled`, `completed`, `cancelled` |
| `abstract` | | Free text |
| `slides_url` | | Link to slides — title becomes clickable |
| `recording_url` | | Link to recording — title becomes clickable |
| `notes` | | Post-talk discussion summary |
| `tags` | | Lowercase kebab-case list |

**Generate the schedule:**

```bash
py scripts/generate_schedule.py
```

This prints a Markdown table of every Tuesday for the next 4 months, with booked slots filled in and empty slots shown as blank rows.

---

## How to contribute

Each data type lives in its own subdirectory as a YAML file. To add or update a record:

1. Create a folder named in lowercase kebab-case (e.g. `data/people/alice-smith/`)
2. Add a `person.yaml` (or `project.yaml`, etc.) using the schema in `CLAUDE.md`
3. Commit and open a pull request for review

If your project doesn't exist in this repository yet, [submit it here](https://forms.gle/fsPGeudtrjyA6sw59) and it will be added.

## Tasks and issues

Day-to-day tasks are tracked in [GitHub Issues](../../issues). Labels are automatically generated from project and funding records.

## Questions

See `CLAUDE.md` for full schema documentation, or reach out to Ken at kepaik@mit.edu.