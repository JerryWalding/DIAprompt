# OSINT Pipeline — Python Application
## Automated DIA-Style Intelligence Brief Generator

**Framework Version:** v12.2 (Methodological Transparency Update)  
**Branch:** `feature/python-osint-pipeline`  
**Status:** 🚧 In Development

---

## Overview

This repository contains a Python application that automates the OSINT analytical pipeline defined in the v12.2 framework. It replaces the token-limited chat-based workflow with a persistent, automated system that holds full session state, scrapes live sources, applies all four analytical protocols as automated filters, and generates DIA-style briefs on demand.

The framework document (v12.2) is the specification this application implements. The old prompt-based framework (v8.0) is archived at [`framework/v8.0.md`](framework/v8.0.md).

---

## What This Application Does

| Feature | Description |
|---------|-------------|
| **Source Scraping** | Automated RSS/web scraping from Rybar, DeepState, ISW, Reuters, AP, BBC |
| **Reliability Weighting** | All v12.2 source tiers and reliability weights applied at ingest |
| **Protocol Filters** | Denial, Silence, Distraction, and Advocacy-Laundering protocols as automated filters |
| **Projection Tracking** | SQLite database tracks all projections with timestamps and outcome logging |
| **Brief Generation** | DIA-style brief engine outputs Morning, Evening, or Flash briefs |
| **Session Persistence** | Full context held in local state — no token cliff |
| **CLI Interface** | Command-line interface for brief generation and session management |

---

## Project Structure

```
osint_pipeline/
├── main.py                   # CLI entry point
├── config.py                 # Source URLs, tier weights, protocol thresholds
├── scraper/
│   ├── __init__.py
│   ├── rss_scraper.py        # RSS feed ingestion (Reuters, AP, BBC)
│   └── web_scraper.py        # Web scraping (Rybar, DeepState, ISW)
├── protocols/
│   ├── __init__.py
│   ├── denial_protocol.py    # Denial Protocol filter
│   ├── silence_protocol.py   # Silence Protocol filter
│   ├── distraction_protocol.py  # Distraction Protocol filter
│   └── advocacy_laundering.py   # Advocacy-Laundering Protocol filter
├── analysis/
│   ├── __init__.py
│   ├── source_evaluator.py   # Tier weighting and claim evaluation
│   ├── indicator_engine.py   # Validated analytical indicators (14 indicators)
│   └── confidence_scorer.py  # CONFIRMED/PROBABLE/UNVERIFIED/SPECULATIVE labeler
├── database/
│   ├── __init__.py
│   ├── models.py             # SQLite schema (articles, claims, projections, sessions)
│   └── db.py                 # Database interface
├── brief/
│   ├── __init__.py
│   ├── generator.py          # DIA-style brief generation engine
│   └── templates/
│       ├── morning.txt       # Morning brief template
│       ├── evening.txt       # Evening brief template
│       └── flash.txt         # Flash brief template
├── session/
│   ├── __init__.py
│   └── state.py              # Session state persistence (replaces token context)
├── requirements.txt
└── README.md                 # This file
```

---

## Installation

### Prerequisites

- Python 3.11+
- pip
- SQLite3 (bundled with Python)

### Setup

```bash
# Clone the repository
git clone https://github.com/JerryWalding/DIAprompt.git
cd DIAprompt

# Checkout the feature branch
git checkout feature/python-osint-pipeline

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python main.py --init-db
```

---

## Usage

### Generate a Morning Brief

```bash
python main.py brief --type morning
```

### Generate an Evening Update

```bash
python main.py brief --type evening
```

### Generate a Flash Brief (breaking development)

```bash
python main.py brief --type flash --theater MIDDLE_EAST
```

### Run Source Scrape (manual trigger)

```bash
python main.py scrape --sources all
python main.py scrape --sources rybar,deepstate,isw
```

### Log a User Intelligence Contribution

```bash
python main.py intel --add "Iraqi militia full activation confirmed" --source "user" --id 113
```

### Query Projection Tracking Database

```bash
python main.py projections --status pending
python main.py projections --status all --since 2026-03-01
```

### View Session State

```bash
python main.py session --show
python main.py session --reset
```

---

## Source Tiers (v12.2)

| Tier | Range | Sources |
|------|-------|---------|
| 1 | 85–100% | Geolocated video/imagery; Reuters/AP factual wire; Official press releases (factual claims only) |
| 2 | 75–90% | DeepState map; BBC/NYT/CNN (political/diplomatic); Rybar (ground-level tactical) |
| 3 | 40–65% | ISW (tactical mapping usable; strategic assessments require corroboration); Ukrainian General Staff; Russian MoD |
| 4 | 30–50% | TASS, RIA Novosti; Al Jazeera |
| 5 | <30% | Unverified social media (leads only) |

---

## Automated Protocol Filters

### Denial Protocol
- **Trigger:** Ukrainian official denial of Russian territorial claim
- **Action:** Cross-reference geolocated video, DeepState, Rybar, ISW
- **Outputs:** `CONFIRMED_UA` / `CONFIRMED_RU` / `GREY_ZONE` / `UNVERIFIED`

### Silence Protocol
- **Trigger:** Active sector shows sustained coverage reduction
- **Action:** Investigate genuine quiet vs. reporting suppression
- **Outputs:** `GENUINE_QUIET` / `COVERAGE_GAP` / `NEGATIVE_DEVELOPMENT`

### Distraction Protocol
- **Trigger:** High-profile non-kinetic story during active strategic crisis
- **Action:** Identify displaced story; assess timing coordination
- **Outputs:** `COINCIDENTAL` / `PROBABLE_COORDINATION` / `CONFIRMED_COORDINATION`

### Advocacy-Laundering Protocol
- **Trigger:** Institutional source presents interested-party claim as independent analysis
- **Action:** Trace original source; check independent corroboration
- **Outputs:** `CORROBORATED` / `INTERESTED_PARTY_UNVERIFIED` / `CONTRADICTED`
- **Scope:** Universal — ISW, RUSI, Atlantic Council, Carnegie, Russian think tanks, Iranian state analysis

---

## Analytical Indicators Engine

The application encodes all 14 validated analytical indicators from the v12.2 framework:

1. Grey Zone language → collapse 1–10 days
2. Relief kilometers away → failed relief
3. Indicators 1+2 combined → imminent collapse
4. Armored vehicles openly visible → area secured
5. OPSEC violations → desperation indicator
6. Consolidation 3–5 days between advances
7. DeepState vs. UA officials → DeepState wins
8. UA denial without video → inverse indicator
9. Mass civilian evacuation → fall 3–7 days
10. Russian combined arms → serious offensive
11. Multi-axis pressure → force allocation crisis
12. Energy infrastructure strikes → C2 degradation
13. Noose flanking → supply interdiction
14. Institutional source + interested-party claim → verify independently

---

## Session Persistence

The session state module replaces the token-cliff problem of chat-based analysis. All context is stored locally in SQLite and survives between CLI invocations:

- Active verification items and their status
- Projection database with timestamps
- User intelligence contribution log (IDs #1–112+)
- Source tier evidence log
- Current baseline facts by theater
- Protocol trigger history

---

## Claim Labeling

All claims in generated briefs are labeled per v12.2 standards:

| Label | Meaning |
|-------|---------|
| `[CONFIRMED]` | Two or more independent credible sources |
| `[PROBABLE]` | Single credible source + corroborating circumstantial evidence |
| `[UNVERIFIED]` | Single source; not yet cross-referenced |
| `[SPECULATIVE]` | Analytical inference; no direct sourcing |
| `[CONTRADICTED]` | Claim conflicts with available evidence |
| `[INTERESTED PARTY — UNVERIFIED]` | Claim from source with direct stake; requires corroboration |

---

## Framework Reference

The full v12.2 analytical framework (source tiers, protocols, indicators, quality control checklist) is the specification this application implements. It is maintained separately as the system prompt document and is not reproduced here.

The archived v8.0 prompt-based framework is at [`framework/v8.0.md`](framework/v8.0.md).

---

## Development Status

| Module | Status |
|--------|--------|
| `scraper/rss_scraper.py` | 🚧 Scaffold pushed |
| `scraper/web_scraper.py` | 🚧 Scaffold pushed |
| `protocols/denial_protocol.py` | 🚧 Scaffold pushed |
| `protocols/silence_protocol.py` | 🚧 Scaffold pushed |
| `protocols/distraction_protocol.py` | 🚧 Scaffold pushed |
| `protocols/advocacy_laundering.py` | 🚧 Scaffold pushed |
| `analysis/source_evaluator.py` | 🚧 Scaffold pushed |
| `analysis/indicator_engine.py` | 🚧 Scaffold pushed |
| `analysis/confidence_scorer.py` | 🚧 Scaffold pushed |
| `database/models.py` | 🚧 Scaffold pushed |
| `database/db.py` | 🚧 Scaffold pushed |
| `brief/generator.py` | 🚧 Scaffold pushed |
| `session/state.py` | 🚧 Scaffold pushed |
| `main.py` | 🚧 Scaffold pushed |

---

## Classification Note

**UNCLASSIFIED // OPEN SOURCE INTELLIGENCE — INDEPENDENT ANALYSIS**

This application processes exclusively publicly available information. DIA-style output format is an organizational presentation preference only. This is not a government product and does not represent any official body.

---

*Framework v12.2 — Methodological Transparency Update — March 5, 2026*