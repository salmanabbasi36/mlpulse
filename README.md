# MLPulse 🧠

> The pulse of machine learning, AI & data science — auto-updated every 4 hours.

## What this is

A full Django publication platform like Towards Data Science with:
- **Auto-generated posts** every 4 hours using Claude AI + web scraping
- **Admin dashboard** to review drafts and one-click publish
- **User article submissions** with a review queue
- **Comments** with threaded replies
- **Newsletter** subscription
- **Categories, tags, search, author profiles**

---

## Quick start (local)

### 1. Clone and set up Python env
```bash
git clone https://github.com/YOUR_USERNAME/mlpulse.git
cd mlpulse
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your values
```

Required values in `.env`:
```
SECRET_KEY=any-random-string-50-chars
DB_NAME=mlpulse
DB_USER=postgres
DB_PASSWORD=your-postgres-password
ANTHROPIC_API_KEY=sk-ant-...   # Get from console.anthropic.com
```

### 3. Create PostgreSQL database
```bash
# In psql:
CREATE DATABASE mlpulse;
```

### 4. Run migrations & setup
```bash
python manage.py migrate
python manage.py setup_site        # Creates categories + AI author
python manage.py createsuperuser   # Creates YOUR admin account
python manage.py collectstatic
```

### 5. Start services
You need 3 terminals:

**Terminal 1 — Django:**
```bash
python manage.py runserver
```

**Terminal 2 — Celery worker:**
```bash
celery -A mlpulse worker --loglevel=info
```

**Terminal 3 — Celery beat (scheduler):**
```bash
celery -A mlpulse beat --loglevel=info -S django_celery_beat.schedulers:DatabaseScheduler
```

Visit http://localhost:8000 — your site is live!
Visit http://localhost:8000/dashboard/ — your admin dashboard.

---

## Deploying to Render.com (free)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial MLPulse setup"
git remote add origin https://github.com/YOUR_USERNAME/mlpulse.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click **New** → **Blueprint**
3. Connect your GitHub repo
4. Render reads `render.yaml` and creates everything automatically

### Step 3: Set your API key
In the Render dashboard → your web service → **Environment**:
- Add `ANTHROPIC_API_KEY` = your key from console.anthropic.com

### Step 4: Run setup commands
In Render dashboard → your web service → **Shell**:
```bash
python manage.py setup_site
python manage.py createsuperuser
```

### Step 5: Connect your domain (mlpulse.app)
1. In Render: Settings → Custom Domain → Add `mlpulse.app` and `www.mlpulse.app`
2. In Namecheap: Advanced DNS → add the CNAME records Render gives you
3. Wait 10-30 mins for DNS propagation

---

## How the automation works

Every 4 hours, Celery Beat triggers `automation.tasks.auto_generate_post`:

1. **Scraper** fetches from: RSS feeds (ArXiv, HuggingFace, OpenAI, Google AI, TDS), Reddit (r/MachineLearning, r/datascience, r/learnmachinelearning), Hacker News (AI/ML stories)
2. **Writer** sends content digest to Claude API with a prompt to write a 1500-2500 word long-form article
3. **Post saved as DRAFT** — appears in your dashboard for review
4. **You click Publish** — one click, done

To skip review and auto-publish everything:
- Set `AUTO_PUBLISH=True` in your Render environment variables

To add your own RSS sources, edit `automation/scraper.py` → `SOURCES['rss']`.

---

## Dashboard

Go to `/dashboard/` (staff accounts only):
- See all pending AI drafts with preview
- One-click publish or delete
- See all user submissions with preview
- Approve (instantly publishes) or reject submissions
- Click "Generate post now" to trigger immediately

---

## Project structure

```
mlpulse/
├── mlpulse/          # Settings, URLs, Celery config
├── blog/             # Posts, categories, comments, newsletter
├── accounts/         # Custom user, auth, profiles
├── submissions/      # User article submissions
├── automation/       # Scraper, Claude API writer, Celery tasks, dashboard
├── templates/        # All HTML templates
├── static/           # CSS, JS
├── render.yaml       # One-click Render deployment
└── requirements.txt
```

---

## Customization

**Change post frequency:** In `automation/apps.py`, change `every=4` to any number of hours.

**Add news sources:** Edit `SOURCES` in `automation/scraper.py`.

**Change AI writing style:** Edit `SYSTEM_PROMPT` in `automation/writer.py`.

**Add categories:** Go to `/django-admin/` → Categories → Add.

**Change colors/design:** Edit `static/css/main.css`.
