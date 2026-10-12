import json
import logging
from typing import Any, Dict, Optional

from openai import OpenAI, OpenAIError

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIClientError(Exception):
    """Raised when the LLM request fails or returns unusable output."""


class OpenAIClient:
    def __init__(self, client: Optional[OpenAI] = None, model: Optional[str] = None) -> None:
        self.client = client or OpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.openai_model

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        try:
            response = self.client.responses.create(
                model=self.model,
                temperature=0.2,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": schema,
                        "strict": True,
                    }
                },
            )
        except OpenAIError as exc:
            logger.error("OpenAI request failed: %s", exc)
            raise AIClientError(f"OpenAI request failed: {exc}") from exc

        try:
            return json.loads(response.output_text)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.error("OpenAI returned invalid JSON: %s", exc)
            raise AIClientError("OpenAI returned invalid JSON") from exc
