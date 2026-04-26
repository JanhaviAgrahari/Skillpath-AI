import asyncio
import json
from typing import TypeVar

from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import LLMOutputError
from app.core.logging import get_logger

T = TypeVar("T", bound=BaseModel)
logger = get_logger(__name__)


class LLMService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _get_client(self):
        if not self.settings.gemini_api_key:
            raise LLMOutputError("Gemini API key is not configured.")
        try:
            from google import genai
        except ImportError as exc:
            raise LLMOutputError("google-genai is not installed.") from exc
        return genai.Client(api_key=self.settings.gemini_api_key)

    async def generate_structured_output(
        self,
        prompt_name: str,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """Single-turn structured JSON output (used by skill extraction, learning plan, etc.)."""
        client = self._get_client()
        from google.genai import types

        # Append the JSON schema to the prompt so the model knows the expected format
        schema_hint = json.dumps(response_model.model_json_schema(), indent=2)
        full_prompt = f"{prompt}\n\nRespond ONLY with valid JSON matching this schema:\n{schema_hint}"

        last_error: Exception | None = None
        attempts = max(1, self.settings.llm_max_retries + 1)

        for attempt in range(1, attempts + 1):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=self.settings.gemini_model,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        ),
                    ),
                    timeout=self.settings.llm_timeout_seconds,
                )
                return response_model.model_validate_json(response.text)
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "llm_call_failed",
                    extra={"prompt_name": prompt_name, "attempt": attempt, "max_attempts": attempts, "error": str(exc)[:200]},
                )
                if attempt < attempts:
                    await asyncio.sleep(0.6 * attempt)

        raise LLMOutputError(f"Gemini request failed for prompt '{prompt_name}'.") from last_error

    async def chat(
        self,
        system_instruction: str,
        conversation_history: list[dict],
        response_model: type[T],
    ) -> T:
        """Multi-turn conversational call with structured JSON output.
        
        conversation_history is a list of dicts: [{"role": "user", "text": "..."}, {"role": "model", "text": "..."}]
        """
        client = self._get_client()
        from google.genai import types

        # Build contents list for the Gemini API
        contents = []
        for turn in conversation_history:
            contents.append(
                types.Content(
                    role=turn["role"],
                    parts=[types.Part.from_text(text=turn["text"])],
                )
            )

        last_error: Exception | None = None
        attempts = max(1, self.settings.llm_max_retries + 1)

        for attempt in range(1, attempts + 1):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=self.settings.gemini_model,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            response_mime_type="application/json",
                        ),
                    ),
                    timeout=self.settings.llm_timeout_seconds,
                )
                return response_model.model_validate_json(response.text)
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "llm_chat_failed",
                    extra={"attempt": attempt, "max_attempts": attempts, "error": str(exc)[:200]},
                )
                if attempt < attempts:
                    await asyncio.sleep(0.6 * attempt)

        raise LLMOutputError("Gemini chat request failed.") from last_error
