import json
from groq import Groq
from django.conf import settings

SYSTEM_PROMPT = """You are a senior technical writer for MLPulse, covering ML, AI, and data science.
Write a comprehensive long-form article (1500-2500 words) based on the latest news provided.
Respond with ONLY a valid JSON object, no markdown fences, exactly in this format:
{
  "title": "Specific engaging title",
  "excerpt": "2-3 sentence summary under 300 chars",
  "body": "Full HTML article with h2, h3, p, ul, li, strong, a href tags and 5-8 inline links",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "category_slug": "one of: machine-learning, deep-learning, data-science, ai-research, tools-libraries, industry-news",
  "meta_description": "SEO description max 155 chars"
}"""


def generate_post(content_digest, source_urls):
    client = Groq(api_key=settings.GROQ_API_KEY)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Latest ML/AI/DS content from the past 4 hours. Write a comprehensive article:\n\n{content_digest}"}
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        data["source_urls"] = source_urls
        data["ai_model"] = "llama-3.3-70b-versatile"
        return data
    except Exception as e:
        print(f"Groq error: {e}")
        return None