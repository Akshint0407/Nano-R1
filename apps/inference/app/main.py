import logging

from fastapi import Depends, FastAPI, Header, HTTPException

from .config import get_settings
from .model import runner
from .schemas import GenerateRequest, GenerateResponse, HealthResponse

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Nano-R1 Inference Service", version="0.1.0")


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        model_loaded=runner.is_loaded,
        base_model_name=settings.base_model_name,
    )


@app.post("/generate", response_model=GenerateResponse, dependencies=[Depends(require_api_key)])
def generate(payload: GenerateRequest) -> GenerateResponse:
    if not payload.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")

    result = runner.generate(payload.question, payload.max_new_tokens)
    return GenerateResponse(
        reasoning=result.reasoning,
        answer=result.answer,
        raw_completion=result.raw_completion,
    )
