# MIT Critical Data — Lab Operations Repository

## What this repo is

MIT Critical Data — evolved from the Laboratory for Computational Physiology (LCP) — is an academic research lab at MIT working to democratize healthcare through open data, open software, and community-driven AI. We unite clinicians, data scientists, engineers, and researchers worldwide around a shared mission: revolutionizing healthcare in a way that is democratized, decentralized, and equitable.

We pursue this through three pillars:
- **Open data & software** — developing and publishing MIMIC, PhysioNet, and related tools
- **Community capacity building** — training local healthcare AI communities through datathons and collaborative research
- **Equity advocacy** — championing diversity and inclusion in AI research and development

This repository is the lab's operational database — plain-text YAML files tracked in Git, making our people, projects, events, funding, and outputs auditable, portable, and scriptable.

## Repository structure

    data/
      people/           # Lab members, alumni, collaborators
        alice-smith/
          person.yaml
          updates/
            2026-01-15.md
      projects/         # Research projects
        mimic-iv/
          project.yaml
          updates/
            2026-01-15.md
      events/           # Conferences, talks, workshops
        symposium-2026/
          event.yaml
          updates/
            2026-01-15.md
      funding/          # Grants, sponsored research, and other funding sources
        nih-r01-2023/
          funding.yaml
          updates/
            2026-01-15.md
      outputs/          # Papers, datasets, software, posters, talks
        paper-nejm-2025/
          output.yaml
          updates/
            2026-01-15.md
      talks/            # Lab presentation schedule — one file per talk
        2026-05-15-leo-celi.yaml
    scripts/            # Validation, automation, and utility scripts
    docs/               # Schema documentation, onboarding guides, conventions

## Data format
Records are stored as YAML files. One file per record, named in lowercase
kebab-case matching the person or project (e.g. alice-smith, mimic-iv).
Relations between records use the folder name without any extension.

## Relations map
- people    <- linked from projects, events, funding, outputs, talks
- funding   <- linked from projects, events
- projects  <- linked from outputs
- events    <- linked from outputs

## Update files
Each record subdirectory contains an updates/ folder for meeting notes,
transcripts, and progress updates. Files are named by date (YYYY-MM-DD.md).

Standard update frontmatter:

    ---
    date: 2026-01-15
    attendees: [alice-smith, bob-jones]
    type: meeting          # meeting, progress, decision, transcript
    ---

## Schemas

### people

    # Required: name, email, role, status
    name:                  # REQUIRED
    email:                 # REQUIRED
    email_secondary:       # personal or non-institutional email
    role:                  # REQUIRED — PI, Postdoc, PhD Student, Master's,
                           # Undergrad, Admin, Affiliate, Research Scientist,
                           # Research Engineer, Visiting Scientist, Visiting Scholar
    status:                # REQUIRED — active, alumni, collaborator
    institution:
    department:
    start_date:
    end_date:              # leave blank if active
    github:
    orcid:
    whatsapp:              # include country code, quoted e.g. "+16175551234"
    photo:                 # filename only, stored in data/people/<name>/
    timezone:              # IANA timezone — use scripts/lookup_timezone.py if unsure
    bio: |
    research_interests: |
    skills: []             # freeform lowercase list — validation script normalizes case

### projects

    # Required: title, status, lead
    title:                 # REQUIRED
    status:                # REQUIRED — active, completed, on-hold, archived
    lead:                  # REQUIRED — links to data/people/
    team: []               # links to data/people/
    funding: []            # links to data/funding/
    start_date:
    end_date:              # leave blank if active
    github_repo:
    description: |
    tags: []               # lowercase kebab-case, topic/theme

### events

    # Required: title, status, date_start, type
    title:                 # REQUIRED
    type:                  # REQUIRED — conference, workshop, seminar,
                           # webinar, lecture, hackathon, other
    status:                # REQUIRED — prospect, planned, confirmed,
                           # completed, cancelled
    date_start:
    date_end:              # leave blank if single day
    city:
    country:
    virtual:               # true, false, hybrid
    url:
    lead:                  # links to data/people/
    team: []               # links to data/people/
    funding: []            # links to data/funding/
    description: |
    tags: []               # lowercase kebab-case, topic/theme

### funding

    # Required: title, status, lead
    title:                 # REQUIRED
    agency:
    program:
    type:                  # grant, contract, sponsored-research,
                           # gift, fellowship, other
    status:                # REQUIRED — prospect, drafting, submitted,
                           # awarded, rejected, withdrawn
    lead:                  # REQUIRED — links to data/people/
    team: []               # links to data/people/
    amount_requested:
    amount_awarded:
    currency: USD
    date_submission:
    date_start:
    date_end:
    projects: []           # links to data/projects/
    events: []             # links to data/events/
    url:
    description: |
    tags: []               # lowercase kebab-case, topic/theme

### outputs

    # Required: title, type, status
    title:                 # REQUIRED
    type:                  # REQUIRED — paper, dataset, software,
                           # abstract, poster, talk, report, other
    status:                # REQUIRED — draft, submitted, in-review,
                           # accepted, published, archived
    lead:                  # REQUIRED — links to data/people/
    team: []               # links to data/people/
    projects: []           # links to data/projects/
    events: []             # links to data/events/
    date_submitted:
    date_published:
    venue:                 # freeform — journal, conference, repository name
    doi:
    url:
    github_repo:
    description: |
    tags: []               # lowercase kebab-case, topic/theme

### talks

Talks live as flat files in `data/talks/`, named `YYYY-MM-DD-speaker-slug.yaml`.
The date prefix keeps the directory self-sorted chronologically.

    # Required: title, speaker, date, status
    title:                 # REQUIRED
    speaker:               # REQUIRED — freeform name (guest or lab member)
    speaker_affiliation:   # optional — institution or company
    speaker_link:          # optional — links to data/people/ if lab member
    date:                  # REQUIRED — YYYY-MM-DD
    time:                  # HH:MM timezone, e.g. 11:00 ET
    type:                  # lab-meeting, journal-club, external, invited, other
    status:                # REQUIRED — scheduled, completed, cancelled
    abstract: |
    slides_url:
    recording_url:
    notes: |               # post-talk notes or discussion summary
    tags: []               # lowercase kebab-case

## Task tracking
Tasks are managed via GitHub Issues, not YAML files.
Labels are auto-generated from project and funding folder names via scripts/sync_labels.py:
- Projects -> label prefix proj- (e.g. proj-mimic-iv)
- Funding  -> label prefix fund- (e.g. fund-nih-r01-2023)
Reference related records informally in the issue body.

## Scripts backlog

    scripts/
      lookup_timezone.py    # given a city/country, returns IANA timezone name
      validate.py           # checks required fields, relation references, lowercase skills
      sync_labels.py        # syncs project/funding folder names to GitHub Issues labels

## Rules
- Never commit credentials, API keys, or secrets
- All relation fields must reference existing folder names
- Required fields must be present and non-empty before merging
- File and folder names: lowercase kebab-case only
- Skills and tags: lowercase only — validation script normalizes case
- Scripts live in scripts/, not alongside data files

## Scratchpad

Claude Code must maintain `docs/working-notes.md` as a running log across sessions. This file is local only and is excluded from Git via .gitignore.

Rules:
- Always read `docs/working-notes.md` at the start of each session for context
- Always append a new entry at the end of each session before closing — never rewrite existing entries
- Each entry must be prefixed with the date (YYYY-MM-DD)
- For large or focused tasks (e.g. data migration), maintain a separate dated log in `docs/` (e.g. `docs/migration-notes.md`)

Each entry should include:
- Tasks completed
- Decisions made and why
- Known issues or gotchas
- Suggested next steps

## Lab context
- GitHub org: criticaldata
- This repo: criticaldata/mit
- Related repos: MIT-LCP/mimic-code, MIT-LCP/physionet-build
- Primary tools: AWS, GitHub Actions, Python
- Team: internationally distributed, mixed technical levels