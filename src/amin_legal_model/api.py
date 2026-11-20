import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, status

from amin_legal_model import __version__
from amin_legal_model.legal.prompts import EGYPTIAN_LEGAL_SYSTEM_PROMPT
from amin_legal_model.legal.strategy import assess_strategy
from amin_legal_model.legal_index import search_legal_index
from amin_legal_model.providers.factory import provider_from_environment
from amin_legal_model.providers.base import ModelNotConfiguredError, UnconfiguredProvider
from amin_legal_model.schemas import LegalRequest, LegalResponse, LegalStrategyRequest

app = FastAPI(
    title="AMIN Legal AI Engine API",
    version=__version__,
    description="Reusable Egyptian-law engine API. Configure a licensed model and authorized corpus for production.",
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
    warnings: list[str] = []
    sources: list[dict[str, str]] = []
    retrieval_context = (
        "لم يُطلب بحث في قاعدة المصادر المعتمدة. لا تختلق أرقام مواد أو أحكام أو مراجع، "
        "وصرّح بأن السند القانوني يحتاج إلى تحقق من مصدر رسمي."
    )

    if request.retrieval_query:
        index_path = Path(os.getenv("AMIN_LEGAL_INDEX_PATH", "data/index/legal.sqlite"))
        if not index_path.is_file():
            warnings.append("قاعدة الفهرس القانوني غير موجودة أو لم تُحدد؛ لم يتم التحقق من مصدر قانوني داخل المحرك.")
        else:
            try:
                retrieved = search_legal_index(
                    index_path,
                    request.retrieval_query,
                    limit=6,
                    as_of_date=request.as_of_date,
                )
                if not retrieved:
                    warnings.append("لم يعثر الفهرس المعتمد على نتائج مطابقة؛ لا تعتبر ذلك دليلًا على عدم وجود نص أو حكم.")
                source_parts: list[str] = []
                for position, item in enumerate(retrieved, start=1):
                    source = {
                        "source_number": str(position),
                        "title": str(item.get("title") or ""),
                        "branch": str(item.get("branch") or ""),
                        "source_reference": str(item.get("source_reference") or ""),
                        "source_url": str(item.get("source_url") or ""),
                        "effective_from": str(item.get("effective_from") or ""),
                        "effective_to": str(item.get("effective_to") or ""),
                        "document_id": str(item.get("document_id") or ""),
                        "chunk_number": str(item.get("chunk_number") or ""),
                    }
                    if item.get("temporal_status"):
                        source["temporal_status"] = str(item["temporal_status"])
                    sources.append(source)
                    source_parts.append(
                        f"[المصدر {position}]\n"
                        f"العنوان: {source['title']}\n"
                        f"الفرع: {source['branch']}\n"
                        f"المرجع: {source['source_reference']}\n"
                        f"تاريخ السريان المسجل: {source['effective_from'] or 'غير محدد'}\n"
                        f"المقتطف: {item.get('chunk_text', '')}"
                    )
                    if item.get("temporal_warning"):
                        warnings.append(str(item["temporal_warning"]))
                if source_parts:
                    retrieval_context = (
                        "المصادر المسترجعة من الفهرس المعتمد. لا تتجاوز ما يثبته المقتطف، "
                        "واربط كل استناد برقم المصدر بين أقواس مربعة:\n\n"
                        + "\n\n".join(source_parts)
                    )
            except Exception:
                warnings.append(
                    "تعذر تنفيذ البحث في الفهرس بسبب خطأ أو رفض صلاحية؛ لم تُستخدم أي نتيجة غير متحقق منها."
                )

    system_prompt = (
        EGYPTIAN_LEGAL_SYSTEM_PROMPT
        + "\n\nقاعدة إلزامية للمصادر: لا تختلق تشريعًا أو حكمًا أو رقم طعن. "
        "عند إرفاق مقتطفات، اذكر رقم المصدر [المصدر N] بجوار كل استناد. "
        "إذا لم توجد مقتطفات، صرّح بأن السند يحتاج إلى تحقق ولا تعرض الذاكرة العامة كمرجع موثق."
    )
    user_prompt = (
        f"المهمة: {request.task}\nالاختصاص: {request.jurisdiction}\n"
        f"اللغة: {request.language}\nتاريخ القانون المطلوب تطبيقه: "
        f"{request.as_of_date.isoformat() if request.as_of_date else 'غير محدد'}\n\n"
        f"وقائع/مستندات وطلب المستخدم:\n{request.text}\n\n"
        f"بحث المصادر:\n{retrieval_context}"
    )
    try:
        answer = await _provider.generate(system_prompt=system_prompt, user_prompt=user_prompt)
    except ModelNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return LegalResponse(status="completed", answer=answer, sources=sources, warnings=warnings)
