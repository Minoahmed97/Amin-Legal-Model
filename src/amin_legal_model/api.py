from fastapi import FastAPI, HTTPException, status

from amin_legal_model import __version__
from amin_legal_model.providers.base import ModelNotConfiguredError, UnconfiguredProvider
from amin_legal_model.schemas import LegalRequest, LegalResponse

app = FastAPI(
    title="AMIN Legal AI Engine API",
    version=__version__,
    description="Reusable legal AI engine API. A model provider is not configured yet.",
)

_provider = UnconfiguredProvider()


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "amin-legal-model",
        "model_loaded": False,
        "message": "API is running; inference is unavailable until a model is configured.",
    }


@app.post("/v1/legal/respond", response_model=LegalResponse)
async def legal_respond(request: LegalRequest) -> LegalResponse:
    try:
        answer = await _provider.generate(
            system_prompt="",
            user_prompt=f"Task: {request.task}\nJurisdiction: {request.jurisdiction}\n{request.text}",
        )
    except ModelNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return LegalResponse(status="completed", answer=answer)
