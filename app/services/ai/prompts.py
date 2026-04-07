from typing import Any, Dict
import json


SYSTEM_PROMPT = (
    "You are a technology news analyst. "
    "Return only valid JSON. "
    "Do not add explanations, markdown, or extra text."
)

def build_article_enrichment_prompt(article_payload: Dict[str, Any]) -> str:
    return f"""
    Analyze this technology news article and return JSON with exactly these fields:
    - category (string)
    - short_summary (string, max 2-3 sentences)
    - why_it_matters (string, max 2 sentences)
    - tags (array of strings, max 5)
    - importance_score (number from 0 to 10)
    - is_israeli_relevant (boolean)

    Rules:
    - Focus on technology, startup, business, AI, cyber, and product relevance.
    - Be concise and factual.
    - If the article is not related to Israel, set is_israeli_relevant to false.
    - Return only valid JSON.

    Article:
    {json.dumps(article_payload, ensure_ascii=False)}
    """.strip()