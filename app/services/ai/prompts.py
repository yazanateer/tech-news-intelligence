from typing import Any, Dict
import json


SYSTEM_PROMPT = (
    "You are a technology news analyst. "
    "Return only valid JSON. "
    "Do not add explanations, markdown, or extra text."
)

ENRICHMENT_SCHEMA_NAME = "article_enrichment"

# Strict JSON schema sent to the OpenAI Responses API (structured outputs).
ENRICHMENT_JSON_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "category": {"type": "string"},
        "short_summary": {"type": "string"},
        "why_it_matters": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "importance_score": {"type": "number"},
        "is_israeli_relevant": {"type": "boolean"},
    },
    "required": [
        "category",
        "short_summary",
        "why_it_matters",
        "tags",
        "importance_score",
        "is_israeli_relevant",
    ],
    "additionalProperties": False,
}


def build_article_enrichment_prompt(article_payload: Dict[str, Any]) -> str:
    return f"""
    Analyze this technology news article and return JSON with exactly these fields:
    - category (string, in Hebrew)
    - short_summary (string, in Hebrew, max 1 short sentence)
    - why_it_matters (string, in Hebrew, max 1 short sentence)
    - tags (array of strings, in Hebrew, max 3)
    - importance_score (number from 0 to 10)
    - is_israeli_relevant (boolean)

    Rules:
    - Keep the JSON field names in English exactly as listed above.
    - Write all text values (category, short_summary, why_it_matters, tags) in Hebrew.
    - Focus on technology, startup, business, AI, cyber, and product relevance.
    - Be concise and factual. Prefer short, direct sentences over long ones.
    - If the article is not related to Israel, set is_israeli_relevant to false.
    - Return only valid JSON.

    Article:
    {json.dumps(article_payload, ensure_ascii=False)}
    """.strip()
