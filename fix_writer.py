content = """import google.genai as genai
import json
from django.conf import settings


def generate_post(content_digest, source_urls):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    prompt = (
        "You are a senior technical writer for MLPulse, covering ML, AI, and data science. "
        "Write a comprehensive long-form article (1500-2500 words) based on the latest news provided. "
        "Respond with ONLY a valid JSON object, no markdown fences, in this format: "
        '{"title": "Specific engaging title", '
        '"excerpt": "2-3 sentence summary under 300 chars", '
        '"body": "Full HTML article with h2, h3, p, ul, li, strong, a href tags and 5-8 inline links", '
        '"tags": ["tag1", "tag2", "tag3", "tag4", "tag5"], '
        '"category_slug": "one of: machine-learning, deep-learning, data-science, ai-research, tools-libraries, industry-news", '
        '"meta_description": "SEO description max 155 chars"}'
        "\\n\\nLatest ML/AI/DS content:\\n" + content_digest
    )
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        data["source_urls"] = source_urls
        data["ai_model"] = "gemini-2.0-flash"
        return data
    except Exception as e:
        print(f"Gemini error: {e}")
        return None
"""

with open("automation/writer.py", "w") as f:
    f.write(content)

print("writer.py created successfully!")
