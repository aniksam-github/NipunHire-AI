"""Generic, retrying OpenAI service used by all AI features."""

import asyncio
import logging
import random
from typing import TypeVar

from openai import APIConnectionError, APITimeoutError, AsyncOpenAI, AuthenticationError, BadRequestError, RateLimitError
from pydantic import BaseModel, ValidationError

from app.ai.utils.json_utils import JSONExtractionError, extract_json
from app.core.ai_exceptions import AINonRetryableError, AIResponseValidationError, AIRetryExhaustedError, AIServiceError
from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
_RETRYABLE_EXCEPTIONS = (APIConnectionError, APITimeoutError, RateLimitError)
_NON_RETRYABLE_EXCEPTIONS = (AuthenticationError, BadRequestError)


class AIService:
    """Centralized, feature-agnostic OpenAI client wrapper."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            timeout=settings.OPENAI_REQUEST_TIMEOUT_SECONDS,
        )
        self._model = settings.OPENAI_MODEL
        self._max_retries = settings.OPENAI_MAX_RETRIES

    async def get_structured_response(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
        temperature: float = 0.3,
    ) -> T:
        raw_content = await self._call_with_retry(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )
        return self._validate_response(raw_content, response_model)

    async def _call_with_retry(self, *, system_prompt: str, user_prompt: str, temperature: float) -> str:
        last_exception: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=self._model,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                usage = response.usage
                logger.info(
                    "AI call succeeded (attempt=%d, prompt_tokens=%s, completion_tokens=%s)",
                    attempt,
                    usage.prompt_tokens if usage else None,
                    usage.completion_tokens if usage else None,
                )
                content = response.choices[0].message.content
                if content is None:
                    raise AIServiceError("OpenAI returned an empty response body")
                return content
            except _NON_RETRYABLE_EXCEPTIONS as exc:
                logger.error("Non-retryable AI error: %s", exc)
                raise AINonRetryableError(str(exc)) from exc
            except _RETRYABLE_EXCEPTIONS as exc:
                last_exception = exc
                if attempt < self._max_retries:
                    backoff_seconds = self._compute_backoff(attempt)
                    logger.warning(
                        "Retryable AI error on attempt %d/%d: %s; retrying in %.2fs",
                        attempt,
                        self._max_retries,
                        exc,
                        backoff_seconds,
                    )
                    await asyncio.sleep(backoff_seconds)

        logger.error("All %d AI retry attempts exhausted", self._max_retries)
        raise AIRetryExhaustedError(f"OpenAI call failed after {self._max_retries} attempts") from last_exception

    @staticmethod
    def _compute_backoff(attempt: int) -> float:
        return 2 ** (attempt - 1) + random.uniform(0, 0.5)

    @staticmethod
    def _validate_response(raw_content: str, response_model: type[T]) -> T:
        try:
            data = extract_json(raw_content)
        except JSONExtractionError as exc:
            logger.error("AI response was not valid JSON: %s", raw_content[:500])
            raise AIResponseValidationError("AI response was not valid JSON") from exc
        try:
            return response_model.model_validate_json(data)
        except ValidationError as exc:
            logger.error("AI response failed schema validation: %s", exc)
            raise AIResponseValidationError(str(exc)) from exc
