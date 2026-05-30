# MLPulse — Full Project Documentation

> The pulse of machine learning, AI & data science — auto-updated by AI.

**Live site:** https://salmanabbasi36.pythonanywhere.com
**GitHub:** https://github.com/salmanabbasi36/mlpulse

---

## Table of Contents

1. [What Is MLPulse?](#1-what-is-mlpulse)
2. [How It Works — The Full Picture](#2-how-it-works--the-full-picture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Apps & Modules](#5-apps--modules)
6. [Data Models](#6-data-models)
7. [URL Routes](#7-url-routes)
8. [AI Pipeline Deep Dive](#8-ai-pipeline-deep-dive)
9. [Admin Dashboard](#9-admin-dashboard)
10. [User Features](#10-user-features)
11. [Environment Variables](#11-environment-variables)
12. [Running Locally](#12-running-locally)
13. [Deployment (PythonAnywhere)](#13-deployment-pythonanywhere)
14. [How to Push Updates](#14-how-to-push-updates)
15. [Extending the Project](#15-extending-the-project)

---

## 1. What Is MLPulse?

MLPulse is a **full Django publication platform** modelled after Towards Data Science. It covers machine learning, AI, and data science.

What makes it different from a regular blog: **content is generated automatically by AI every time you click a button**. The system scrapes the latest news from RSS feeds, Reddit, and Hacker News, sends it to the Groq AI API (llama-3.3-70b), and gets back a fully written 1500–2500 word article with HTML formatting, tags, and an SEO description. The article lands in a draft queue. You review it in the dashboard and publish with one click.

Human writers can also submit articles through the public submission form, which go through the same review queue.

---

## 2. How It Works — The Full Picture

```
┌─────────────────────────────────────────────────────────┐
│                    PUBLIC INTERNET                       │
│                                                          │
│  ArXiv RSS  HuggingFace RSS  OpenAI RSS  DeepMind RSS   │
│  Reddit r/ML  r/datascience  r/learnML  r/artificial    │
│  Hacker News top AI/ML stories                          │
└───────────────────────┬─────────────────────────────────┘
                        │  scraper.py fetches & aggregates
                        ▼
              ┌─────────────────┐
              │  Content Digest  │  Plain text summary of
              │  (structured)    │  all recent ML/AI news
              └────────┬────────┘
                       │  writer.py sends to Groq API
                       ▼
              ┌─────────────────┐
              │  Groq API        │  llama-3.3-70b-versatile
              │  (LLM)           │  writes full HTML article
              └────────┬────────┘
                       │  returns JSON with title, body, tags
                       ▼
              ┌─────────────────┐
              │  Post saved as   │  status = 'draft'
              │  DRAFT in DB     │  source = 'auto'
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Admin Dashboard │  /dashboard/
              │  (staff only)    │  preview, publish, delete
              └────────┬────────┘
                       │  publish()
                       ▼
              ┌─────────────────┐
              │  LIVE POST       │  status = 'published'
              │  on the website  │  visible to all readers
              └─────────────────┘
```

### Triggering Generation

| Method | How |
|--------|-----|
| **Manual** | Click "Generate post now" in `/dashboard/` — synchronous, result in ~10s |
| **Scheduled** | Celery Beat task every 4 hours (requires Redis — works in production with Redis) |

---

## 3. Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 6.0.5 |
| Language | Python 3.12 |
| Database | SQLite (local + PythonAnywhere) |
| AI Model | Groq API — `llama-3.3-70b-versatile` |
| Task Queue | Celery 5.6.3 + django-celery-beat |
| Message Broker | Redis (for Celery scheduling) |
| Static Files | WhiteNoise (served directly by Django/gunicorn) |
| Rich Text Editor | django-summernote (Bootstrap 4 theme) |
| Tags | django-taggit |
| Read Time | readtime |
| Hosting | PythonAnywhere (free tier) |
| Web Server | PythonAnywhere WSGI (gunicorn for other platforms) |
| CSS/JS | Custom — `static/css/main.css`, `static/js/main.js` |

---

## 4. Project Structure

```
mlpulse/
│
├── mlpulse/                  # Django project package
│   ├── settings.py           # All configuration
│   ├── urls.py               # Root URL dispatcher
│   ├── celery.py             # Celery app setup
│   ├── wsgi.py               # WSGI entry point
│   └── __init__.py           # Imports Celery app
│
├── blog/                     # Core blog app
│   ├── models.py             # Post, Category, Comment, Newsletter
│   ├── views.py              # home, post_detail, search, archive, etc.
│   ├── urls.py               # Blog URL patterns
│   ├── forms.py              # CommentForm, NewsletterForm
│   ├── context_processors.py # Injects categories + recent posts globally
│   ├── sitemaps.py           # XML sitemap for SEO
│   └── management/
│       └── commands/
│           └── setup_site.py # Creates initial categories + AI author user
│
├── accounts/                 # Custom user & auth app
│   ├── models.py             # Extended User (bio, avatar, social links)
│   ├── views.py              # register, login, logout, profile, edit
│   ├── urls.py               # /accounts/* routes
│   └── forms.py              # RegisterForm, LoginForm, ProfileForm
│
├── submissions/              # Community article submission app
│   ├── models.py             # Submission (pending/approved/rejected)
│   ├── views.py              # submit_article view
│   ├── forms.py              # SubmissionForm
│   └── urls.py               # /submit/ route
│
├── automation/               # AI pipeline + admin dashboard app
│   ├── scraper.py            # Fetches RSS, Reddit, Hacker News
│   ├── writer.py             # Calls Groq API to generate article JSON
│   ├── tasks.py              # Celery task: auto_generate_post
│   ├── views.py              # Dashboard, trigger, publish, approve, reject
│   └── urls.py               # /dashboard/* routes
│
├── templates/                # All HTML templates
│   ├── base.html             # Navbar, footer, messages bar
│   ├── blog/
│   │   ├── home.html         # Hero post + post grid + newsletter
│   │   ├── post_detail.html  # Full article with comments
│   │   ├── archive.html      # All posts listed chronologically
│   │   ├── category.html     # Posts filtered by category
│   │   ├── tag.html          # Posts filtered by tag
│   │   └── search.html       # Search results
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html      # Author profile + their posts
│   ├── submissions/
│   │   └── submit.html       # Article submission form
│   └── admin_dashboard/
│       ├── dashboard.html    # Draft queue + submission queue
│       ├── preview.html      # Preview AI-generated draft
│       └── preview_submission.html  # Preview user submission
│
├── static/
│   ├── css/main.css          # Full site styling (~227 lines)
│   └── js/main.js            # Mobile nav toggle + UI helpers
│
├── .env                      # Local secrets (never committed)
├── .gitignore                # Excludes .env, __pycache__, db.sqlite3, etc.
├── requirements.txt          # Python dependencies
├── Procfile                  # web / worker / beat process definitions
├── runtime.txt               # Python 3.13 specification
├── railway.toml              # Railway deployment config
├── render.yaml               # Render.com one-click deploy config
└── manage.py                 # Django management entry point
```

---

## 5. Apps & Modules

### `blog` — Core Content

The heart of the site. Handles everything a reader sees.

- **`Post`** — the main content object. Has a `status` field (`draft`/`published`), a `source` field (`auto`/`user`), auto-calculated reading time via `readtime`, auto-generated unique slugs, and a `publish()` method that sets `published_at`.
- **`Category`** — 6 pre-seeded categories: Machine Learning, Deep Learning, Data Science, AI Research, Tools & Libraries, Industry News. Each has a hex colour used for badges in the UI.
- **`Comment`** — threaded comments (supports `parent` FK for replies). Anonymous comments allowed (name + email fields).
- **`Newsletter`** — simple email collection. `get_or_create` prevents duplicates.
- **`context_processors.site_context`** — runs on every request and injects `categories` and `recent_posts` into all templates, which is how the navbar category links and footer links are populated.

### `accounts` — Users & Profiles

Extends Django's `AbstractUser` with:
- `bio`, `avatar`, `twitter`, `github`, `linkedin`, `website`
- `is_author` flag (reserved for future author tier logic)
- `get_avatar()` — returns the uploaded avatar URL or falls back to a generated avatar from `ui-avatars.com` using their name/username

All authentication (register, login, logout) is handled by custom views, not Django's built-in auth views.

### `submissions` — Community Writing

Any visitor can submit an article via `/submit/`. Logged-in users get their name/email/bio pre-filled. Submissions enter a `pending` queue visible in the dashboard. Admin can preview, approve (instantly publishes as a `Post`), or reject.

### `automation` — AI Engine + Dashboard

This is the most unique part of the project.

**`scraper.py`** — fetches from three source types:
- **RSS**: Towards Data Science, ArXiv (cs.LG + cs.AI), OpenAI blog, HuggingFace blog, DeepMind blog, Google AI blog
- **Reddit**: r/MachineLearning, r/datascience, r/learnmachinelearning, r/artificial (filters by score > 100, skips self-posts)
- **Hacker News**: top 50 stories, filtered by AI/ML keywords, takes first 8 matches

**`writer.py`** — takes the aggregated digest and sends it to Groq's `llama-3.3-70b-versatile` model with a structured system prompt that demands a specific JSON response format (title, excerpt, body HTML, tags, category slug, meta description).

**`tasks.py`** — Celery task `auto_generate_post` that chains scraper → writer → DB save. Supports retries (max 3, 5 min delay). Reads `AUTO_PUBLISH` setting to decide whether to publish immediately or save as draft.

**`views.py`** — the staff-only dashboard with all management actions: trigger generation, preview/publish/delete drafts, preview/approve/reject user submissions.

---

## 6. Data Models

### Post

| Field | Type | Notes |
|-------|------|-------|
| `title` | CharField(300) | |
| `slug` | SlugField(350) | Auto-generated, unique, collision-safe |
| `author` | FK → User | SET_NULL on delete |
| `category` | FK → Category | SET_NULL on delete |
| `tags` | TaggableManager | django-taggit |
| `excerpt` | TextField(500) | Shown in listings |
| `body` | TextField | Full HTML content |
| `cover_image` | ImageField | Optional uploaded image |
| `cover_image_url` | URLField | For AI-generated posts using web images |
| `status` | CharField | `draft` or `published` |
| `source` | CharField | `auto` or `user` |
| `meta_description` | CharField(160) | SEO |
| `source_urls` | JSONField | List of URLs scraped to write this post |
| `ai_model` | CharField | Which model generated it |
| `views` | PositiveIntegerField | Incremented on each page view |
| `reading_time` | PositiveIntegerField | Minutes, auto-calculated from body |
| `published_at` | DateTimeField | Set on first publish |

### User (extends AbstractUser)

| Field | Type |
|-------|------|
| `bio` | TextField(500) |
| `avatar` | ImageField |
| `twitter` | CharField(100) |
| `github` | CharField(100) |
| `linkedin` | CharField(100) |
| `website` | URLField |
| `is_author` | BooleanField |

### Submission

| Field | Type | Notes |
|-------|------|-------|
| `author` | FK → User | Optional (anonymous allowed) |
| `author_name` | CharField(100) | |
| `author_email` | EmailField | |
| `author_bio` | TextField(500) | |
| `title` | CharField(300) | |
| `excerpt` | TextField(500) | |
| `body` | TextField | Full article content |
| `category` | FK → Category | |
| `tags` | CharField(255) | Comma-separated string |
| `cover_image` | ImageField | |
| `status` | CharField | `pending` / `approved` / `rejected` |
| `admin_notes` | TextField | Internal reviewer notes |
| `submitted_at` | DateTimeField | |
| `reviewed_at` | DateTimeField | |

### Comment

| Field | Type | Notes |
|-------|------|-------|
| `post` | FK → Post | CASCADE |
| `author` | FK → User | Optional (anonymous allowed) |
| `name` | CharField(100) | For anonymous comments |
| `email` | EmailField | For anonymous comments |
| `body` | TextField(2000) | |
| `parent` | FK → self | For threaded replies |
| `is_approved` | BooleanField | Default True |

---

## 7. URL Routes

| URL | View | Access |
|-----|------|--------|
| `/` | `blog:home` | Public |
| `/<slug>/` | `blog:post_detail` | Public |
| `/archive/` | `blog:archive` | Public |
| `/search/?q=...` | `blog:search` | Public |
| `/category/<slug>/` | `blog:category` | Public |
| `/tag/<slug>/` | `blog:tag` | Public |
| `/newsletter/subscribe/` | `blog:newsletter_subscribe` | Public (POST) |
| `/accounts/register/` | `accounts:register` | Public |
| `/accounts/login/` | `accounts:login` | Public |
| `/accounts/logout/` | `accounts:logout` | Authenticated |
| `/accounts/edit/` | `accounts:edit_profile` | Authenticated |
| `/accounts/<username>/` | `accounts:profile` | Public |
| `/submit/` | `submissions:submit` | Public |
| `/dashboard/` | `automation:dashboard` | Staff only |
| `/dashboard/trigger/` | `automation:trigger` | Staff only (POST) |
| `/dashboard/drafts/<pk>/` | `automation:preview_draft` | Staff only |
| `/dashboard/drafts/<pk>/publish/` | `automation:publish_post` | Staff only (POST) |
| `/dashboard/drafts/<pk>/delete/` | `automation:delete_draft` | Staff only (POST) |
| `/dashboard/submissions/<pk>/` | `automation:preview_submission` | Staff only |
| `/dashboard/submissions/<pk>/approve/` | `automation:approve_submission` | Staff only (POST) |
| `/dashboard/submissions/<pk>/reject/` | `automation:reject_submission` | Staff only (POST) |
| `/django-admin/` | Django Admin | Superuser |
| `/sitemap.xml` | Auto-generated sitemap | Public |

---

## 8. AI Pipeline Deep Dive

### Step 1 — Scraping (`automation/scraper.py`)

Three parallel scrapers run and return structured Python dicts:

**RSS** (`fetch_rss_items`):
- Parses 7 feeds using `feedparser`
- Takes up to 8 entries per feed
- Captures: title, link, summary (first 500 chars), published date, source name

**Reddit** (`fetch_reddit_posts`):
- Hits 4 subreddit JSON endpoints
- Filters: score > 100, not a self-post (links only)
- Returns top 15 by score across all subreddits

**Hacker News** (`fetch_hackernews`):
- Fetches top 50 story IDs
- For each, fetches full story JSON
- Matches title against keywords: `ai, ml, machine learning, llm, gpt, neural, model, data, deep learning, openai, anthropic`
- Stops after 8 matches

All three are combined into a single plain-text `content_digest` string and a flat list of `source_urls`.

### Step 2 — Writing (`automation/writer.py`)

The digest is sent to Groq with a system prompt that:
- Defines the writer as a "senior technical writer for MLPulse"
- Requests 1500–2500 words
- Demands a **strict JSON response** (no markdown fences) with exactly these keys: `title`, `excerpt`, `body`, `tags`, `category_slug`, `meta_description`
- The body must be valid HTML with `h2`, `h3`, `p`, `ul`, `li`, `strong`, `a href` tags and 5–8 inline links

Temperature is set to 0.7 for a balance of creativity and consistency. Max tokens: 4000.

If the model returns markdown-fenced JSON (```json ... ```), the code strips the fences before parsing.

### Step 3 — Saving (`automation/tasks.py` or `automation/views.py`)

The returned JSON is used to:
1. Look up the `Category` by `category_slug` (falls back to first category if slug not found)
2. Find the `mlpulse-ai` user (created by `setup_site` command)
3. Create a `Post` with `status='draft'` (or `'published'` if `AUTO_PUBLISH=True`)
4. Add tags via `post.tags.add(*tags)`

The `Post.save()` method auto-calculates:
- Unique slug from the title
- Reading time from the HTML body
- Sets `published_at` if status is `published`

---

## 9. Admin Dashboard

URL: `/dashboard/` — accessible only to staff users (`is_staff=True`).

### What You See

**Top row stats:**
- Drafts pending review
- User submissions pending review
- Posts published today
- Total published posts

**Draft queue (AI-generated):**
Each draft shows title, date created, AI model used, and two buttons: Preview | Publish. There is also a Delete button. Clicking Preview shows the full rendered article before it goes live.

**User submission queue:**
Each submission shows title, author name, submitted date, and Preview | Approve | Reject buttons. Approving instantly creates a published `Post` from the submission data.

**"Generate post now" button:**
Triggers `scraper.gather_all_content()` + `writer.generate_post()` synchronously in the web request. A new draft appears at the top of the queue within ~10 seconds (depending on Groq API response time).

### Creating a Superuser / Staff User

```bash
python manage.py createsuperuser
```

Any superuser has `is_staff=True` automatically and can access the dashboard.

---

## 10. User Features

### Reading
- Browse homepage (hero post + grid of latest 9 posts)
- Filter by category (navbar or footer links)
- Filter by tag (tag badges on post detail page)
- Full-text search across title, body, excerpt
- View archive (all posts, paginated by 20)
- Read post detail with reading time, view count, related posts

### Commenting
- Anonymous or logged-in comments on any post
- Threaded replies (click "Reply" under any comment)
- All comments approved by default

### Newsletter
- Email subscription form in homepage footer
- `get_or_create` prevents duplicate signups

### Accounts
- Register with username, email, password
- Login / logout
- Edit profile: bio, avatar image, Twitter/GitHub/LinkedIn/website links
- Public author profile page showing all their published posts
- Avatar auto-generated from name if no image uploaded (via ui-avatars.com)

### Writing
- Submit an article via `/submit/`
- Rich text editor (Summernote) for the body
- Cover image upload
- Category selection and comma-separated tags
- If logged in, name/email/bio pre-filled from profile
- Status tracked: pending → approved/rejected
- Published submissions appear as normal posts with the submitter as author

---

## 11. Environment Variables

All variables are read from `.env` in the project root via `python-decouple`. Create `.env` by copying the template below. **Never commit `.env` to git.**

```env
# Required
SECRET_KEY=your-random-secret-key-50-chars-minimum
GROQ_API_KEY=gsk_...              # From console.groq.com

# App behaviour
DEBUG=True                        # False in production
AUTO_PUBLISH=False                # True to skip draft review

# Hosts (comma-separated)
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# URLs
SITE_URL=http://localhost:8000

# Celery (only needed for scheduled auto-generation)
REDIS_URL=redis://localhost:6379/0

# Email (optional — for future newsletter sending)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@mlpulse.app
```

### Production values (PythonAnywhere)

```env
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=salmanabbasi36.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://salmanabbasi36.pythonanywhere.com
GROQ_API_KEY=gsk_...
AUTO_PUBLISH=False
SITE_URL=https://salmanabbasi36.pythonanywhere.com
```

---

## 12. Running Locally

### Prerequisites

- Python 3.12+
- Git

### Setup

```bash
# Clone
git clone https://github.com/salmanabbasi36/mlpulse.git
cd mlpulse

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env (fill in SECRET_KEY and GROQ_API_KEY at minimum)
copy .env.example .env         # Windows
cp .env.example .env           # Mac/Linux

# Set up database
python manage.py migrate
python manage.py setup_site    # Creates 6 categories + AI author
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run
python manage.py runserver
```

Visit:
- `http://localhost:8000` — the site
- `http://localhost:8000/dashboard/` — the admin dashboard (log in as superuser)

### Generating Posts Locally

No Redis/Celery required locally. Just:
1. Go to `http://localhost:8000/dashboard/`
2. Click **"Generate post now"**
3. Wait ~10 seconds
4. A new draft appears — click Preview, then Publish

### Optional: Run with Celery (auto-scheduling)

Requires Redis running locally (`redis-server`).

```bash
# Terminal 2
celery -A mlpulse worker --loglevel=info

# Terminal 3
celery -A mlpulse beat --loglevel=info -S django_celery_beat.schedulers:DatabaseScheduler
```

Posts will auto-generate every 4 hours. Frequency can be changed in `automation/apps.py`.

---

## 13. Deployment (PythonAnywhere)

The site is deployed on [PythonAnywhere](https://www.pythonanywhere.com) free tier.

| Detail | Value |
|--------|-------|
| Username | `salmanabbasi36` |
| Live URL | `https://salmanabbasi36.pythonanywhere.com` |
| Python version | 3.12 |
| Virtualenv | `~/venv` |
| Project path | `~/mlpulse` |
| Static files | `~/mlpulse/staticfiles` → served at `/static/` |
| Media files | `~/mlpulse/media` → served at `/media/` |
| WSGI file | `/var/www/salmanabbasi36_pythonanywhere_com_wsgi.py` |
| Database | `~/mlpulse/db.sqlite3` (persistent on PythonAnywhere filesystem) |

### WSGI File Content

```python
import sys
import os

path = '/home/salmanabbasi36/mlpulse'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'mlpulse.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### PythonAnywhere Limitations (Free Tier)

- **No Celery/Redis** — auto-scheduling every 4 hours does not run. Use the "Generate post now" button in the dashboard manually.
- **Outbound internet** — PythonAnywhere free tier uses a whitelist for outbound connections. The Groq API currently works. If it stops, request `api.groq.com` be whitelisted via their forums.
- **No custom domain** — URL is `salmanabbasi36.pythonanywhere.com`. Upgrade to Hacker plan ($5/month) for a custom domain.
- **CPU quota** — 100 CPU-seconds/day on free tier. Generating one article uses ~2–5 CPU-seconds.

---

## 14. How to Push Updates

### Workflow

```bash
# 1. Make code changes locally
# 2. Test locally: python manage.py runserver
# 3. Commit and push to GitHub main
git add <files>
git commit -m "your message"
git push origin master:main

# 4. Pull on PythonAnywhere (via their bash console)
cd ~/mlpulse && git pull

# 5. If you changed models:
~/venv/bin/python manage.py migrate

# 6. If you changed static files:
~/venv/bin/python manage.py collectstatic --no-input

# 7. Reload the web app
# → PythonAnywhere dashboard → Web → Reload button
# OR via API:
# curl -X POST -H "Authorization: Token <your-token>" \
#   https://www.pythonanywhere.com/api/v0/user/salmanabbasi36/webapps/salmanabbasi36.pythonanywhere.com/reload/
```

---

## 15. Extending the Project

### Add a New RSS Source

Edit `automation/scraper.py` → `SOURCES['rss']`:
```python
'rss': [
    ...
    'https://your-new-feed.com/rss.xml',  # Add here
]
```

### Change Post Generation Frequency

The Celery beat schedule is managed via `django-celery-beat` and stored in the database. Change it from the Django admin at `/django-admin/` → Periodic Tasks, or set it up with:

```python
# In automation/apps.py or a data migration
from django_celery_beat.models import PeriodicTask, IntervalSchedule
schedule, _ = IntervalSchedule.objects.get_or_create(every=4, period=IntervalSchedule.HOURS)
PeriodicTask.objects.get_or_create(
    name='Auto generate post',
    defaults={'interval': schedule, 'task': 'automation.tasks.auto_generate_post'}
)
```

### Change the AI Model

Edit `automation/writer.py`:
```python
model="llama-3.3-70b-versatile",  # Change to any Groq-supported model
```

Available Groq models: `llama-3.1-8b-instant` (faster), `mixtral-8x7b-32768` (alternative), `llama-3.3-70b-versatile` (current — best quality).

### Change the Writing Style / Tone

Edit the `SYSTEM_PROMPT` in `automation/writer.py`. The prompt controls article length, structure, HTML formatting requirements, and writing style.

### Add a New Category

Go to `/django-admin/` → Categories → Add, or:
```bash
python manage.py shell -c "
from blog.models import Category
Category.objects.create(name='Computer Vision', slug='computer-vision', color='#ec4899')
"
```

### Enable Auto-Publishing (Skip Review)

Set in `.env`:
```env
AUTO_PUBLISH=True
```

All AI-generated posts will publish immediately without appearing in the draft queue.

### Switch AI Provider

The writer is self-contained in `automation/writer.py`. To switch from Groq to OpenAI:

```python
from openai import OpenAI

def generate_post(content_digest, source_urls):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"...\n\n{content_digest}"}
        ],
        ...
    )
```

Then update `settings.py` to read `OPENAI_API_KEY` from `.env`.

---

*MLPulse — Built with Django 6, powered by Groq llama-3.3-70b.*
