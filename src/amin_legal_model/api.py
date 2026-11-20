from fastapi import FastAPI

from amin_legal_model import __version__

app = FastAPI(
    title="AMIN Legal Model API",
    version=__version__,
    description="Initial project scaffold. No language model is connected yet.",
)


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "amin-legal-model",
        "model_loaded": False,
        "message": "Foundation API is running; no inference model is configured.",
    }
