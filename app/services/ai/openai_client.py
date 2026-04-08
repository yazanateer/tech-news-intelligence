import json
from typing import Any, Dict

from openai import OpenAI

from app.core.config import settings
from app.services.ai.prompts import SYSTEM_PROMPT, build_article_enrichment_prompt

class OpenAIClient:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def enrich_article(self, article_payload: Dict[str, Any]) -> Dict[str, Any]:
        user_prompt = build_article_enrichment_prompt(article_payload)

        response = self.client.responses.create(
            model = self.model,
            temperature=0.2,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
        )

        output_text = response.output_text
        return json.loads(output_text)