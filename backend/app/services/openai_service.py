"""The single gateway from NipunHire AI features to OpenAI."""

from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel, ValidationError

from app.core.ai_exceptions import AIServiceError
from app.core.config import settings

if TYPE_CHECKING:
    from openai import AsyncOpenAI


ResponseModel = TypeVar("ResponseModel", bound=BaseModel)
_PLACEHOLDER_KEY = "your_openai_api_key_here"


class OpenAIService:
    """Generates structured, Pydantic-validated AI responses."""

    def __init__(self, client: "AsyncOpenAI | None" = None) -> None:
        self._client = client

    def _get_client(self):
        if self._client is not None:
            return self._client

        api_key = settings.OPENAI_API_KEY.get_secret_value()
        if not api_key or api_key == _PLACEHOLDER_KEY:
            raise AIServiceError("OPENAI_API_KEY is not configured")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise AIServiceError("OpenAI SDK is not installed; run `uv sync`") from exc
        self._client = AsyncOpenAI(api_key=api_key)
        return self._client

    async def generate(self, prompt: str, response_model: type[ResponseModel]) -> ResponseModel:
        """Generate one JSON response and validate it before it reaches any feature or DB."""
        try:
            response = await self._get_client().responses.parse(
                model=settings.OPENAI_MODEL,
                input=prompt,
                text_format=response_model,
            )
            if response.output_parsed is None:
                raise AIServiceError("OpenAI returned no structured response")
            return response_model.model_validate(response.output_parsed)
        except AIServiceError:
            raise
        except ValidationError as exc:
            raise AIServiceError("OpenAI response did not match the required schema") from exc
        except Exception as exc:
            raise AIServiceError("OpenAI request failed") from exc


openai_service = OpenAIService()
