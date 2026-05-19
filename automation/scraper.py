import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.utils import timezone


SOURCES = {
    'rss': [
        'https://feeds.feedburner.com/towards-data-science',
        'http://export.arxiv.org/rss/cs.LG',
        'http://export.arxiv.org/rss/cs.AI',
        'https://openai.com/news/rss/',
        'https://huggingface.co/blog/feed.xml',
        'https://www.deepmind.com/blog/rss.xml',
        'https://ai.googleblog.com/feeds/posts/default',
    ],
    'reddit': [
        'https://www.reddit.com/r/MachineLearning/hot.json?limit=10',
        'https://www.reddit.com/r/datascience/hot.json?limit=10',
        'https://www.reddit.com/r/learnmachinelearning/hot.json?limit=10',
        'https://www.reddit.com/r/artificial/hot.json?limit=5',
    ],
    'hackernews': 'https://hacker-news.firebaseio.com/v0/topstories.json',
}

HEADERS = {'User-Agent': 'MLPulse/1.0 (mlpulse.app; content aggregator)'}


def fetch_rss_items(limit_hours=5):
    """Fetch recent items from all RSS feeds."""
    items = []
    cutoff = timezone.now() - timedelta(hours=limit_hours)
    for url in SOURCES['rss']:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                items.append({
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', '')[:500],
                    'published': published,
                    'source': feed.feed.get('title', url),
                })
        except Exception as e:
            print(f'RSS error {url}: {e}')
    return items


def fetch_reddit_posts():
    """Fetch hot posts from ML/DS subreddits."""
    items = []
    for url in SOURCES['reddit']:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            data = r.json()
            for post in data.get('data', {}).get('children', []):
                d = post['data']
                if d.get('score', 0) > 100 and not d.get('is_self', False):
                    items.append({
                        'title': d.get('title', ''),
                        'link': d.get('url', ''),
                        'score': d.get('score', 0),
                        'comments': d.get('num_comments', 0),
                        'subreddit': d.get('subreddit', ''),
                        'selftext': d.get('selftext', '')[:300],
                    })
        except Exception as e:
            print(f'Reddit error {url}: {e}')
    return sorted(items, key=lambda x: x['score'], reverse=True)[:15]


def fetch_hackernews():
    """Fetch top HN stories related to AI/ML."""
    items = []
    keywords = ['ai', 'ml', 'machine learning', 'llm', 'gpt', 'neural', 'model', 'data', 'deep learning', 'openai', 'anthropic']
    try:
        r = requests.get(SOURCES['hackernews'], timeout=10)
        story_ids = r.json()[:50]
        for sid in story_ids:
            try:
                sr = requests.get(f'https://hacker-news.firebaseio.com/v0/item/{sid}.json', timeout=5)
                story = sr.json()
                title = story.get('title', '').lower()
                if any(kw in title for kw in keywords):
                    items.append({
                        'title': story.get('title', ''),
                        'link': story.get('url', f'https://news.ycombinator.com/item?id={sid}'),
                        'score': story.get('score', 0),
                        'comments': story.get('descendants', 0),
                    })
                    if len(items) >= 8:
                        break
            except Exception:
                continue
    except Exception as e:
        print(f'HN error: {e}')
    return items


def gather_all_content():
    """Gather content from all sources and return structured data."""
    rss = fetch_rss_items()
    reddit = fetch_reddit_posts()
    hn = fetch_hackernews()

    # Build a summary string for Claude
    lines = ['=== RECENT RSS ARTICLES ===']
    for item in rss[:12]:
        lines.append(f"- [{item['source']}] {item['title']}")
        if item['summary']:
            lines.append(f"  Summary: {item['summary'][:200]}")
        lines.append(f"  URL: {item['link']}")

    lines.append('\n=== TRENDING ON REDDIT (ML/DS) ===')
    for item in reddit[:8]:
        lines.append(f"- r/{item['subreddit']}: {item['title']} (score: {item['score']}, comments: {item['comments']})")
        lines.append(f"  URL: {item['link']}")

    lines.append('\n=== HACKER NEWS AI/ML STORIES ===')
    for item in hn:
        lines.append(f"- {item['title']} (score: {item['score']})")
        lines.append(f"  URL: {item['link']}")

    # Collect all source URLs
    source_urls = (
        [i['link'] for i in rss[:12]] +
        [i['link'] for i in reddit[:8]] +
        [i['link'] for i in hn]
    )

    return '\n'.join(lines), source_urls
