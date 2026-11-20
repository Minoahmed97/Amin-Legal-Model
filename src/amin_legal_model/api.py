from fastapi import FastAPI, HTTPException, status

from amin_legal_model import __version__
from amin_legal_model.legal.prompts import EGYPTIAN_LEGAL_SYSTEM_PROMPT
from amin_legal_model.legal.strategy import assess_strategy
from amin_legal_model.providers.factory import provider_from_environment
from amin_legal_model.providers.base import ModelNotConfiguredError, UnconfiguredProvider
from amin_legal_model.schemas import LegalRequest, LegalResponse, LegalStrategyRequest

app = FastAPI(
    title="AMIN Legal AI Engine API",
    version=__version__,
    description="Reusable Egyptian-law engine API. Configure a licensed inference model for generation.",
)

_provider = provider_from_environment()


@app.get("/health")
def health() -> dict[str, str | bool]:
    configured = not isinstance(_provider, UnconfiguredProvider)
    return {
        "status": "ok",
        "service": "amin-legal-model",
        "model_configured": configured,
        "model_loaded": bool(getattr(_provider, "model_loaded", False)),
        "message": (
            "API is running; inference availability depends on the configured provider and model."
            if configured else
            "API is running; inference is unavailable until a model is configured."
        ),
    }


@app.post("/v1/legal/strategy")
def legal_strategy(request: LegalStrategyRequest) -> dict:
    """Return a transparent first-pass strategy triage, not an AI legal opinion."""
    return assess_strategy(request.model_dump())


@app.post("/v1/legal/respond", response_model=LegalResponse)
async def legal_respond(request: LegalRequest) -> LegalResponse:
    try:
        answer = await _provider.generate(
            system_prompt=EGYPTIAN_LEGAL_SYSTEM_PROMPT,
            user_prompt=f"Task: {request.task}\nJurisdiction: {request.jurisdiction}\n{request.text}",
        )
    except ModelNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return LegalResponse(status="completed", answer=answer)
