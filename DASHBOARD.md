# MIT Critical Data — Lab Dashboard

_Generated 2026-06-30 · 113 records (32 projects · 6 grants · 75 events) · [contributing guide](docs/contributing.md)_

[Active projects](data/projects/README.md) · [Submit new project](https://forms.gle/fsPGeudtrjyA6sw59) · [Upcoming events](data/events/README.md)

---

## 🔴 Urgent (0)

_No urgent items._

---

## 🟡 Blocked (0)

_No blocked items._

---

## 🟢 This week (16)

### `Project` [AI and Frailty](https://github.com/criticaldata/mit/tree/main/data/projects/ai-frailty)
_updated 7d ago_

# Update June 23

- Received comments & feedbacks from Dae Hyun Kim. Fixing on those comments

## Task

- Finalizing the manuscript
- Submit to Nature (perspective article)

### `Project` [CXR Vector Embedding Release](https://github.com/criticaldata/mit/tree/main/data/projects/cxr-vector-embedding-release)
_updated 7d ago_

Received approval to release on PhysioNet for all models.

Tasks:
- Add torchxrayvision CheXpert weights
- Investigate chexagent-2-3b

### `Project` [Leo OpenClaw](https://github.com/criticaldata/mit/tree/main/data/projects/leo-openclaw)
_updated 3d ago_

**Key Takeaways**

- Release Strategy Shift: The Mimic login feature is deprioritized. LLeoMe will launch as a private beta for trusted users to ensure controlled debugging and prevent misuse.
- A/B Testing Mandated: A formal A/B test against Claude is the top priority. It will use two methods: an automated Open Claude for asynchronous regression testing and a live, synchronous session for new tasks.
- New Research Spun Off: A new project was conceived to train agents to detect when other agents are "cheating" on benchmarks, a concept inspired by the need for more robust evaluation.

**Topics**

*Project Status & Release Strategy*

- Status: The critical bug causing incorrect JSON output is fixed. The CI3D pipeline is operational on AWS.
- Scope: WhatsApp integration is dropped. The MIMIC login feature is paused.
- Rationale: A public release is premature and risky. A private beta enables controlled debugging and prevents users from publishing papers without understanding the content.
- Blocker: Access to Milit's S3 bucket is needed to update the paper dataset.

*A/B Testing & Evaluation Plan*

- Goal: Systematically compare Leo.me's performance against Claude.
- Method 1: Asynchronous Regression Testing
  - Tool: An automated OpenClaw.
  - Process: Replay past Claude conversations (e.g., March–June 2026) to check for consistent outputs.
  - Rationale: Provides continuous, objective performance monitoring to detect decay over time.
- Method 2: Synchronous Live Testing
  - Process: The team will work together on new tasks (e.g., revising manuscripts, responding to peer reviews).
  - Rationale: Enables real-time, collaborative debugging and rapid iteration.
- System Prompt Refinement: Yasin noted the system prompt may need refinement based on A/B test feedback.

*New Research: Agent Self-Correction*

- Problem: LLMs often fail to identify methodological flaws in papers (e.g., a recent Nature paper noted LLMs praised retracted papers).
- Idea: Develop a "critique benchmark" to test LLeoMe's ability to find flaws, potentially by injecting errors into papers.
- Evolution: This led to a more ambitious concept: training agents to recognize when they are "cheating" or gaming a benchmark.
  - Challenge: A single agent cannot be trusted to self-report.
  - Potential Solution: A community of agents could monitor each other for shortcuts.
  - Inspiration: Yasin shared the "Strawberry" tool, which mathematically calculates hallucination probability.
- Outcome: The team will explore this concept with the Dojo community and consider a proposal to Anthropic.

**Next Steps**

- Shrey:
  - Deprioritize the MIMIC login feature.
  - Secure access to Milit's S3 bucket.
  - Share the Leo.me concept paper with the team.
- Team:
  - Build an automated OpenClaw for asynchronous A/B testing.
  - Prepare for the synchronous A/B testing session.
- All:
  - Attend the synchronous A/B testing session on Sunday, July 12, at the same time.

### `Project` [LLM Interrogation](https://github.com/criticaldata/mit/tree/main/data/projects/llm-interrogation)
_updated 7d ago_

Submitting paper to COLM 2026.

### `Project` [Vector Embedding Pipeline (v1)](https://github.com/criticaldata/mit/tree/main/data/projects/vector-embedding-pipeline)
_updated 7d ago_

Deliverables:
- Pipeline code (GitHub + PyPI)
- Pre-computed CXR embeddings (PhysioNet)
- Methods paper

Tasks:
- Discuss target journal (JAMIA, NPJ Digital Medicine, JMIR, or conference)

### `Grant` [NVIDIA Academic Grant Program 2026](https://github.com/criticaldata/mit/tree/main/data/funding/nvidia-2026)
_updated 7d ago_

Awarded: 8xA100 node, July 1 – December 31, 2026.

### `Grant` [Smith Family Awards Program for Excellence in Biomedical Research](https://github.com/criticaldata/mit/tree/main/data/funding/hria-smith-2026)
_updated 7d ago_

Withdrawing from the Smith Family Awards Program. Applicants must hold a tenure-track faculty position; we do not qualify.

### `Event` [📅 [2027-01-29] Bunker Hill Community College](https://github.com/criticaldata/mit/tree/main/data/events/2027/bunker-hill-community-college)
_updated 7d ago_

Automatically added during event reconciliation on 2026-06-23. @leo-celi please confirm dates, location, and status are correct.

### `Event` [📅 [2027-10-01] China](https://github.com/criticaldata/mit/tree/main/data/events/2027/china)
_updated 7d ago_

Automatically added during event reconciliation on 2026-06-23. @leo-celi please confirm dates, location, and status are correct.

### `Event` [📅 [2026-09-26] Dublin Hackathon](https://github.com/criticaldata/mit/tree/main/data/events/2026/dublin-hackathon)
_updated 7d ago_

Please confirm this event was cancelled.

### `Event` [📅 [2027-10-22] Greece](https://github.com/criticaldata/mit/tree/main/data/events/2027/greece)
_updated 7d ago_

Automatically added during event reconciliation on 2026-06-23. @leo-celi please confirm dates, location, and status are correct.

### `Event` [📅 [2027-06-01] Norway](https://github.com/criticaldata/mit/tree/main/data/events/2027/norway)
_updated 7d ago_

Automatically added during event reconciliation on 2026-06-23. @leo-celi please confirm dates, location, and status are correct.

### `Event` [📅 [2026-12-09] NYC](https://github.com/criticaldata/mit/tree/main/data/events/2026/nyc)
_updated 7d ago_

Automatically added during event reconciliation on 2026-06-23. @leo-celi please confirm dates, location, and status are correct.

### `Event` [📅 [2027-04-09] Ohio State University](https://github.com/criticaldata/mit/tree/main/data/events/2027/ohio-state-university)
_updated 7d ago_

Automatically added during event reconciliation on 2026-06-23. @leo-celi please confirm dates, location, and status are correct.

### `Event` [📅 [2027-04-20] Panama](https://github.com/criticaldata/mit/tree/main/data/events/2027/panama)
_updated 7d ago_

Automatically added during event reconciliation on 2026-06-23. @leo-celi please confirm dates, location, and status are correct.

### `Event` [📅 [2026-09-01] Toronto](https://github.com/criticaldata/mit/tree/main/data/events/2026/toronto)
_updated 7d ago_

Please confirm this event was cancelled.

---

## ⚪ Stale (52)

| Record | Last update |
|---|---|
| `Project` [MIMIC DEID Next](https://github.com/criticaldata/mit/tree/main/data/projects/mimic-deid-next) | ⚠️ **27d since last update** |
| `Project` [6 Tools Framework + Jan 15 Event Take-aways](https://github.com/criticaldata/mit/tree/main/data/projects/6-tools-framework-jan-15-event-take-aways) | no updates |
| `Project` [AGORA: Agentic Game of Research and Academia](https://github.com/criticaldata/mit/tree/main/data/projects/agora-agentic-game-of-research-and-academia) | no updates |
| `Project` [AI as a Catalyst (Jan 15, 2026 Event)](https://github.com/criticaldata/mit/tree/main/data/projects/ai-as-a-catalyst) | no updates |
| `Project` [Bias in Omics Data Beyond Non-Representativeness](https://github.com/criticaldata/mit/tree/main/data/projects/bias-in-omics-data-beyond-non-representativeness) | no updates |
| `Project` [BODHI: Medical AI as Epistemic Agent](https://github.com/criticaldata/mit/tree/main/data/projects/bodhi-medical-ai-as-epistemic-agent) | no updates |
| `Project` [Brown Mental Health LLM-athon (Feb 26-27, 2026)](https://github.com/criticaldata/mit/tree/main/data/projects/brown-mental-health-llm-athon) | no updates |
| `Project` [Combinators are Dead](https://github.com/criticaldata/mit/tree/main/data/projects/combinators-are-dead) | no updates |
| `Project` [Epidemiology of Sentiments in Clinical Notes](https://github.com/criticaldata/mit/tree/main/data/projects/epidemiology-of-sentiments-in-clinical-notes) | no updates |
| `Project` [Impact Analysis of Prediction Models (Causal Inference)](https://github.com/criticaldata/mit/tree/main/data/projects/impact-analysis-of-prediction-models) | no updates |
| `Project` [Lab-MAE: Foundation Model for Lab Data](https://github.com/criticaldata/mit/tree/main/data/projects/lab-mae-foundation-model-for-lab-data) | no updates |
| `Project` [LabTube: 3D Temporal Modeling of ICU Labs](https://github.com/criticaldata/mit/tree/main/data/projects/labtube-3d-temporal-modeling-of-icu-labs) | no updates |
| `Project` [M4: Clinical Research Agent (MCP)](https://github.com/criticaldata/mit/tree/main/data/projects/m4-clinical-research-agent) | no updates |
| `Project` [MedScope: Pain Documentation Bias](https://github.com/criticaldata/mit/tree/main/data/projects/medscope-pain-documentation-bias) | no updates |
| `Project` [MIT Critical Data Branding, Events & Comms](https://github.com/criticaldata/mit/tree/main/data/projects/mit-critical-data-branding-events-comms) | no updates |
| `Project` [MIT Critical Data Central America](https://github.com/criticaldata/mit/tree/main/data/projects/mit-critical-data-central-america) | no updates |
| `Project` [Model Drift in MIMIC](https://github.com/criticaldata/mit/tree/main/data/projects/model-drift-in-mimic) | no updates |
| `Project` [Multimodal Data Discordance](https://github.com/criticaldata/mit/tree/main/data/projects/multimodal-data-discordance) | no updates |
| `Project` [Multimodal VE for Cardiovascular Disease](https://github.com/criticaldata/mit/tree/main/data/projects/multimodal-ve-for-cardiovascular-disease) | no updates |
| `Project` [RecursiveJEPA](https://github.com/criticaldata/mit/tree/main/data/projects/recursive-jepa) | no updates |
| `Project` [SLICES: SSL Objectives for ICU Representation](https://github.com/criticaldata/mit/tree/main/data/projects/slices-ssl-objectives-for-icu-representation) | no updates |
| `Project` [Snapshot Embedding for EHR Data](https://github.com/criticaldata/mit/tree/main/data/projects/snapshot-embedding-for-ehr-data) | no updates |
| `Project` [Standard Model of Care](https://github.com/criticaldata/mit/tree/main/data/projects/standard-model-of-care) | no updates |
| `Project` [This is not a Webinar Series](https://github.com/criticaldata/mit/tree/main/data/projects/this-is-not-a-webinar-series) | no updates |
| `Project` [WorldmedQA: Cross-Cultural Pain Concepts](https://github.com/criticaldata/mit/tree/main/data/projects/worldmedqa-cross-cultural-pain-concepts) | no updates |
| `Project` [XAI Claims in ICU ML Models (Scoping Review)](https://github.com/criticaldata/mit/tree/main/data/projects/xai-claims-in-icu-ml-models) | no updates |
| `Grant` [DOJO](https://github.com/criticaldata/mit/tree/main/data/funding/dojo) | no updates |
| `Grant` [Accessible Mulimodal Vector Embeddings for Global Cardiovascular AI](https://github.com/criticaldata/mit/tree/main/data/funding/nhlbi-2026) | no updates |
| `Grant` [snuh1](https://github.com/criticaldata/mit/tree/main/data/funding/snuh1) | no updates |
| `Grant` [snuh2](https://github.com/criticaldata/mit/tree/main/data/funding/snuh2) | no updates |
| `Event` [📅 [2026-07-23] ACOG](https://github.com/criticaldata/mit/tree/main/data/events/2026/acog) | no updates |
| `Event` [📅 [2026-11-10] AIMed](https://github.com/criticaldata/mit/tree/main/data/events/2026/aimed) | no updates |
| `Event` [📅 [2026-07-22] Annual Intensive Review of Internal Medicine](https://github.com/criticaldata/mit/tree/main/data/events/2026/annual-intensive-review-of-internal-medicine) | no updates |
| `Event` [📅 [2026-07-27] Brazil](https://github.com/criticaldata/mit/tree/main/data/events/2026/brazil) | no updates |
| `Event` [📅 [2026-09-28] Chile](https://github.com/criticaldata/mit/tree/main/data/events/2026/chile) | no updates |
| `Event` [📅 [2026-09-24] Conv2x Symposium](https://github.com/criticaldata/mit/tree/main/data/events/2026/conv2x-symposium) | no updates |
| `Event` [📅 [2026-08-14] Denmark](https://github.com/criticaldata/mit/tree/main/data/events/2026/denmark) | no updates |
| `Event` [📅 [2026-12-03] France](https://github.com/criticaldata/mit/tree/main/data/events/2026/france) | no updates |
| `Event` [📅 [2026-09-18] Ireland](https://github.com/criticaldata/mit/tree/main/data/events/2026/ireland) | no updates |
| `Event` [📅 [2026-09-04] Italy](https://github.com/criticaldata/mit/tree/main/data/events/2026/italy) | no updates |
| `Event` [📅 [2026-10-15] Korea](https://github.com/criticaldata/mit/tree/main/data/events/2026/korea) | no updates |
| `Event` [📅 [2026-09-10] National Library of Medicine](https://github.com/criticaldata/mit/tree/main/data/events/2026/national-library-of-medicine) | no updates |
| `Event` [📅 [2026-10-20] Taiwan](https://github.com/criticaldata/mit/tree/main/data/events/2026/taiwan) | no updates |
| `Event` [📅 [2026-10-18] Thailand](https://github.com/criticaldata/mit/tree/main/data/events/2026/thailand) | no updates |
| `Event` [📅 [2026-10-30] Turkey](https://github.com/criticaldata/mit/tree/main/data/events/2026/turkey) | no updates |
| `Event` [📅 [2026-11-21] Vancouver](https://github.com/criticaldata/mit/tree/main/data/events/2026/vancouver) | no updates |
| `Event` [📅 [2027-02-01] India](https://github.com/criticaldata/mit/tree/main/data/events/2027/india) | no updates |
| `Event` [📅 [2027-04-02] Mayo Clinic Florida](https://github.com/criticaldata/mit/tree/main/data/events/2027/mayo-clinic-florida) | no updates |
| `Event` [📅 [2027-08-31] World Congress of Epidemiology](https://github.com/criticaldata/mit/tree/main/data/events/2027/world-congress-of-epidemiology) | no updates |
| `Event` [📅 [TBD] Care Innovation Challenge (Boston)](https://github.com/criticaldata/mit/tree/main/data/events/undated/care-innovation-challenge) | no updates |
| `Event` [📅 [TBD] TBD: Australia Health AI Event Series](https://github.com/criticaldata/mit/tree/main/data/events/undated/tbd-australia-health-ai-event-series) | no updates |
| `Event` [📅 [TBD] Vietnam Datathon: AI as a Catalyst](https://github.com/criticaldata/mit/tree/main/data/events/undated/vietnam-datathon-ai-as-a-catalyst) | no updates |

---

<details>
<summary>🗄️ Inactive (45)</summary>

- `Project` [Next Generation MIMIC](https://github.com/criticaldata/mit/tree/main/data/projects/mimic-next-generation) _on-hold_
- `Event` [📅 [2025-07-17] Thailand Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-thailand) _completed_
- `Event` [📅 [2025-08-18] MITHIC Workshop 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/workshop-mithic) _completed_
- `Event` [📅 [2025-08-19] AMA August 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/ama-aug) _completed_
- `Event` [📅 [2025-08-21] Emory University Symposium and Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/event-emory) _completed_
- `Event` [📅 [2025-08-25] Singapore Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-singapore) _completed_
- `Event` [📅 [2025-09-03] Milan Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-milan) _completed_
- `Event` [📅 [2025-09-16] UPMC Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-upmc) _completed_
- `Event` [📅 [2025-09-27] Poland Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-poland) _completed_
- `Event` [📅 [2025-10-10] China Datathon October 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-china-oct) _completed_
- `Event` [📅 [2025-10-16] Korea Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-korea) _completed_
- `Event` [📅 [2025-10-27] Mexico Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-mexico) _completed_
- `Event` [📅 [2025-11-15] Vancouver Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-vancouver) _completed_
- `Event` [📅 [2025-11-19] Philips excursion November 19, 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/philips-excursion-november-19-2025) _completed_
- `Event` [📅 [2025-12-04] AMA December 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/ama-dec) _completed_
- `Event` [📅 [2025-12-10] France Datathon 2025](https://github.com/criticaldata/mit/tree/main/data/events/2025/datathon-france) _completed_
- `Event` [📅 [2026-01-15] AI as a Catalyst](https://github.com/criticaldata/mit/tree/main/data/events/2026/ai-as-a-catalyst) _completed_
- `Event` [📅 [2026-01-23] Vietnam Datathon 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/datathon-vietnam) _completed_
- `Event` [📅 [2026-02-12] Montreal Datathon February 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/datathon-montreal-feb) _completed_
- `Event` [📅 [2026-02-24] Hopkins Seminar 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/seminar-hopkins) _completed_
- `Event` [📅 [2026-02-26] Brown 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/brown-2026) _planned_
- `Event` [📅 [2026-02-26] Brown datathon](https://github.com/criticaldata/mit/tree/main/data/events/2026/brown-datathon) _planned_
- `Event` [📅 [2026-03-16] ISICEM 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/event-isicem) _completed_
- `Event` [📅 [2026-03-19] Brown University DSAIY AI-a-Thon](https://github.com/criticaldata/mit/tree/main/data/events/2026/brown-university-dsaiy-ai-a-thon) _planned_
- `Event` [📅 [2026-03-23] AMA 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/ama-2026) _confirmed_
- `Event` [📅 [2026-03-27] Meeting with Rifat Atun and his lab](https://github.com/criticaldata/mit/tree/main/data/events/2026/meeting-with-rifat-atun-and-his-lab) _planned_
- `Event` [📅 [2026-03-27] Montreal Seminar March 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/seminar-montreal-mar) _completed_
- `Event` [📅 [2026-03-29] Quebec](https://github.com/criticaldata/mit/tree/main/data/events/2026/quebec) _prospect_
- `Event` [📅 [2026-04-09] Mayo Datathon 2026 MIT](https://github.com/criticaldata/mit/tree/main/data/events/2026/mayo-datathon-2026-mit) _planned_
- `Event` [📅 [2026-04-10] Mayo Clinic Florida](https://github.com/criticaldata/mit/tree/main/data/events/2026/mayo-clinic-florida) _prospect_
- `Event` [📅 [2026-04-10] Mayo Datathon](https://github.com/criticaldata/mit/tree/main/data/events/2026/mayo-datathon) _prospect_
- `Event` [📅 [2026-04-15] WCA 2026 â€” World Congress of Anaesthesiologists](https://github.com/criticaldata/mit/tree/main/data/events/2026/conference-wca-morocco) _completed_
- `Event` [📅 [2026-04-15] WCA 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/wca-2026) _prospect_
- `Event` [📅 [2026-04-23] Panama Datathon 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/datathon-panama) _completed_
- `Event` [📅 [2026-04-27] HMS](https://github.com/criticaldata/mit/tree/main/data/events/2026/hms) _prospect_
- `Event` [📅 [2026-04-29] CHOC](https://github.com/criticaldata/mit/tree/main/data/events/2026/choc) _prospect_
- `Event` [📅 [2026-05-01] China Datathon May 2026](https://github.com/criticaldata/mit/tree/main/data/events/2026/datathon-china-may) _planned_
- `Event` [📅 [2026-05-01] Stanford](https://github.com/criticaldata/mit/tree/main/data/events/2026/stanford) _prospect_
- `Event` [📅 [2026-05-04] MGB](https://github.com/criticaldata/mit/tree/main/data/events/2026/mgb) _prospect_
- `Event` [📅 [2026-05-05] Hartford](https://github.com/criticaldata/mit/tree/main/data/events/2026/hartford) _prospect_
- `Event` [📅 [2026-05-07] Cincinnati](https://github.com/criticaldata/mit/tree/main/data/events/2026/cincinnati) _prospect_
- `Event` [📅 [2026-05-11] Hong Kong](https://github.com/criticaldata/mit/tree/main/data/events/2026/hong-kong) _prospect_
- `Event` [📅 [2026-05-29] MeHI's AI Workshop for Primary Care Innovation Challenge](https://github.com/criticaldata/mit/tree/main/data/events/2026/mehis-ai-workshop-for-primary) _prospect_
- `Event` [📅 [2026-06-12] China/Tibet](https://github.com/criticaldata/mit/tree/main/data/events/2026/chinatibet) _prospect_
- `Event` [📅 [2026-06-26] Dominican Republic](https://github.com/criticaldata/mit/tree/main/data/events/2026/dominican-republic) _prospect_

</details>
