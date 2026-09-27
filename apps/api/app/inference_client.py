import httpx

from .config import get_settings


class InferenceServiceError(RuntimeError):
    pass


def solve(question: str) -> dict:
    settings = get_settings()
    try:
        response = httpx.post(
            f"{settings.inference_service_url}/generate",
            json={"question": question},
            headers={"X-API-Key": settings.inference_api_key},
            timeout=120.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise InferenceServiceError(f"Inference service call failed: {exc}") from exc

    return response.json()
