import asyncio
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from src.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMExtractionError(Exception):
    pass


async def extract_pdf(
    pdf_path: Path,
    schema: type[T],
    prompt: str,
    max_retries: int = 2,
) -> T:
    """Extract structured data from a PDF using Gemini with Pydantic schema enforcement.

    Falls back to OpenRouter if Gemini fails after retries.
    """
    if not settings.gemini_api_key:
        raise LLMExtractionError("GEMINI_API_KEY não configurada")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    pdf_bytes = pdf_path.read_bytes()
    last_err: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            response = await client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=[
                    types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.0,
                ),
            )
            return schema.model_validate_json(response.text)
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                await asyncio.sleep(2**attempt)

    if settings.openrouter_api_key:
        return await _extract_via_openrouter(pdf_path, schema, prompt)

    raise LLMExtractionError(
        f"Falha após {max_retries + 1} tentativas: {last_err}"
    ) from last_err


async def _extract_via_openrouter(pdf_path: Path, schema: type[T], prompt: str) -> T:
    """Fallback simplificado via OpenRouter — placeholder; implementar quando necessário."""
    raise LLMExtractionError("Fallback OpenRouter ainda não implementado")
