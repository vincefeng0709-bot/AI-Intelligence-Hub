# XinyMao AI Intelligence Hub

> Daily AI Intelligence for Developers, Researchers and Builders.

A self-running AI intelligence center that automatically collects, analyzes, and publishes daily AI industry reports — powered by Claude API and deployed on GitHub Pages.

---

## What it does

Every day at **08:00 Beijing Time**, the system automatically:

1. **Collects** — RSS feeds from Anthropic, OpenAI, Google, Meta, arXiv, HackerNews, GitHub Trending
2. **Analyzes** — Claude synthesizes insights, trends, and implications
3. **Generates** — Professional reports in structured Markdown
4. **Publishes** — Static site deployed to GitHub Pages

---

## Report Types

| Report | Frequency | Model | Path |
|--------|-----------|-------|------|
| AI Intelligence Daily | Every day 08:00 | Sonnet 4.6 | `reports/daily/YYYY-MM-DD.md` |
| Research Digest | Every day 08:00 | Sonnet 4.6 | `reports/daily/YYYY-MM-DD-research.md` |
| AI Intelligence Weekly | Every Sunday 08:00 | Opus 4.8 | `reports/weekly/YYYY-Wxx.md` |
| AI Intelligence Monthly | Every 1st 08:00 | Opus 4.8 | `reports/monthly/YYYY-MM.md` |

---

## Trackers

- **Claude Tracker** — Anthropic news, API updates, system status, model releases
- **OpenAI Tracker** — ChatGPT updates, API changes, status events
- **Google Tracker** — Gemini, DeepMind blog, Google AI announcements

---

## Quick Start

### Prerequisites

- Python 3.12+
- Anthropic API key ([get one here](https://console.anthropic.com))
- Git

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/ai-intelligence-hub
cd ai-intelligence-hub

pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...

# Run today's full pipeline
python run_daily.py
```

### Run individual components

```bash
# Daily report only
python run_daily.py --only daily

# Research digest only
python run_daily.py --only research

# Trackers only
python run_daily.py --only tracker

# Build site only (no API calls)
python run_daily.py --only site

# Weekly report (uses Opus 4.8)
python run_weekly.py

# Monthly report (uses Opus 4.8)
python run_monthly.py
```

---

## GitHub Pages Deployment

### Step 1: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/ai-intelligence-hub
git push -u origin main
```

### Step 2: Add API Key Secret

GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- Name: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key

### Step 3: Enable GitHub Pages

GitHub repo → **Settings** → **Pages** → Source: **GitHub Actions**

### Step 4: Enable Workflows

Go to **Actions** tab → Enable workflows if prompted.

That's it. The system will run automatically every day at 08:00 Beijing time.

---

## Ubuntu VPS Deployment

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/ai-intelligence-hub /opt/ai-hub
cd /opt/ai-hub

# Install Python dependencies
pip3 install -r requirements.txt

# Set up environment
echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.bashrc
source ~/.bashrc

# Set up cron jobs (Beijing time = UTC+8, so UTC 00:00 = Beijing 08:00)
crontab -e
# Add these lines:
# 0 0 * * *   cd /opt/ai-hub && python3 run_daily.py >> /var/log/ai-hub-daily.log 2>&1
# 0 0 * * 0   cd /opt/ai-hub && python3 run_weekly.py >> /var/log/ai-hub-weekly.log 2>&1
# 0 0 1 * *   cd /opt/ai-hub && python3 run_monthly.py >> /var/log/ai-hub-monthly.log 2>&1
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name xinymao.com www.xinymao.com;
    root /opt/ai-hub/public;
    index index.html;

    location / {
        try_files $uri $uri/ $uri.html =404;
    }

    gzip on;
    gzip_types text/html text/css application/javascript;
}
```

### HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d xinymao.com -d www.xinymao.com
```

---

## Custom Domain (GitHub Pages)

1. Add a `CNAME` file in `public/` with your domain:
   ```
   xinymao.com
   ```
2. Configure DNS: `CNAME xinymao.com → YOUR_USERNAME.github.io`
3. Enable HTTPS in GitHub Pages settings

---

## Data Sources

| Source | Type | Coverage |
|--------|------|----------|
| Anthropic RSS | RSS | Official Anthropic news |
| OpenAI News RSS | RSS | OpenAI announcements |
| Google AI Blog | RSS | Google AI / DeepMind |
| Meta AI Blog | RSS | Meta AI research |
| HuggingFace Blog | RSS | Open-source AI |
| arXiv cs.AI/CL/LG | RSS | Academic papers |
| Hacker News | API | Community discussion |
| GitHub Trending | Web | Open-source projects |
| Status APIs | JSON | System uptime |

---

## SEO Features

- `sitemap.xml` — auto-generated
- `robots.txt` — auto-generated
- `feed.xml` — RSS feed
- Open Graph meta tags on every page
- Twitter Card meta tags

---

## Project Structure

```
ai-intelligence-hub/
├── src/
│   ├── collectors/      # Data fetching
│   ├── analyzers/       # Claude API wrapper
│   ├── generators/      # Report generation
│   ├── publishers/      # Static site builder
│   ├── trackers/        # Company trackers
│   └── utils/           # HTTP, storage, dates
├── reports/
│   ├── daily/
│   ├── weekly/
│   └── monthly/
├── trackers/
│   ├── claude/
│   ├── openai/
│   └── google/
├── public/              # GitHub Pages output
├── config/settings.py
├── run_daily.py
├── run_weekly.py
├── run_monthly.py
├── requirements.txt
├── CLAUDE.md
└── .github/workflows/
```

---

## Brand

**XinyMao AI Intelligence Hub**
*Daily AI Intelligence for Developers, Researchers and Builders.*

---

*Powered by [Claude](https://claude.ai) · Deployed on GitHub Pages*
