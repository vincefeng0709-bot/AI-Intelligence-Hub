# XinyMao AI Intelligence Hub — CLAUDE.md

## Project Overview

AI intelligence hub that auto-generates daily/weekly/monthly reports, research digests, and company trackers using Claude API + GitHub Pages.

## Architecture

```
run_daily.py / run_weekly.py / run_monthly.py   ← entry points
    ↓
src/collectors/     ← fetch raw data (RSS, arXiv, HN, GitHub)
    ↓
src/analyzers/      ← Claude API calls
    ↓
src/generators/     ← build prompts + call analyzers → Markdown reports
    ↓
src/trackers/       ← company-specific tracking (Claude, OpenAI, Google)
    ↓
src/publishers/     ← build static HTML site
    ↓
public/             ← GitHub Pages output
```

## Model Strategy

- **Default**: `claude-sonnet-4-6` — daily reports, research digest, trackers
- **Deep analysis**: `claude-opus-4-8` — weekly and monthly reports only

## Key Commands

```bash
# Run full daily pipeline
python run_daily.py

# Run specific component only
python run_daily.py --only daily
python run_daily.py --only research
python run_daily.py --only tracker
python run_daily.py --only site

# Backfill a specific date
python run_daily.py --date 2025-06-22

# Weekly and monthly
python run_weekly.py
python run_monthly.py

# Build site only (no API calls)
python run_daily.py --only site
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | Anthropic API key |
| `SITE_URL` | Optional | Public site URL (default: https://xinymao.com/ai) |
| `GITHUB_PAGES_URL` | Optional | GitHub Pages URL |

## File Structure

```
reports/daily/YYYY-MM-DD.md          ← daily reports
reports/daily/YYYY-MM-DD-research.md ← research digests
reports/weekly/YYYY-Wxx.md           ← weekly reviews
reports/monthly/YYYY-MM.md           ← monthly trends
trackers/claude/YYYY-MM-DD.md        ← Claude tracker updates
trackers/openai/YYYY-MM-DD.md        ← OpenAI tracker updates
trackers/google/YYYY-MM-DD.md        ← Google tracker updates
public/                               ← static site (GitHub Pages)
```

## Adding New Data Sources

1. Add collector in `src/collectors/`
2. Import in relevant generator (e.g., `daily_generator.py`)
3. Add to prompt construction function

## GitHub Actions Schedule

| Workflow | Cron (UTC) | Beijing Time |
|----------|-----------|--------------|
| daily-report.yml | `0 0 * * *` | Every day 08:00 |
| weekly-report.yml | `0 0 * * 0` | Every Sunday 08:00 |
| monthly-report.yml | `0 0 1 * *` | Every 1st 08:00 |
| deploy-pages.yml | on push to public/ | Automatic |

## GitHub Secrets Required

- `ANTHROPIC_API_KEY` — set in repo Settings → Secrets → Actions

## GitHub Variables (Optional)

- `SITE_URL` — your custom domain or GitHub Pages URL

## Design Principles

- KISS: no databases, no heavy frameworks — just Python + Markdown + JSON
- All data stored as flat files (Markdown + JSONL)
- Static site, zero server cost
- Graceful degradation: each step fails independently, others continue
