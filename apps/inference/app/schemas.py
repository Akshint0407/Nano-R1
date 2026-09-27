from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    question: str = Field(..., description="The math word problem to solve.")
    max_new_tokens: int | None = Field(default=None, ge=16, le=2048)


class GenerateResponse(BaseModel):
    reasoning: str
    answer: str
    raw_completion: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    base_model_name: str
