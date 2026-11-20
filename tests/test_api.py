from fastapi.testclient import TestClient

from amin_legal_model.api import app

client = TestClient(app)


def test_health_endpoint_reports_no_model_loaded() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["model_configured"] is False
    assert payload["model_loaded"] is False


def test_inference_endpoint_does_not_fake_an_answer_without_model() -> None:
    response = client.post(
        "/v1/legal/respond",
        json={"task": "analyze", "text": "وقائع افتراضية للاختبار"},
    )
    assert response.status_code == 503
    assert "No model provider is configured" in response.json()["detail"]


def test_strategy_endpoint_returns_cautious_structured_assessment() -> None:
    response = client.post(
        "/v1/legal/strategy",
        json={
            "objective": "رفض طلب الخصم",
            "case_stage": "استئناف",
            "client_role": "مستأنف ضده",
            "risk_of_curative_reply": True,
            "response_points": [],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "recommendation" in payload
    assert payload["warnings"]


def test_legal_response_exposes_retrieval_unavailability_warning(monkeypatch, tmp_path):
    import amin_legal_model.api as api

    class FakeProvider:
        model_loaded = True
        async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
            assert "لا تختلق تشريعًا" in system_prompt
            assert "بحث المصادر" in user_prompt
            return "تحليل تجريبي"

    monkeypatch.setattr(api, "_provider", FakeProvider())
    monkeypatch.setenv("AMIN_LEGAL_INDEX_PATH", str(tmp_path / "missing.sqlite"))
    response = client.post(
        "/v1/legal/respond",
        json={
            "task": "analyze",
            "text": "وقائع افتراضية",
            "retrieval_query": "المادة المدنية",
        },
    )
    assert response.status_code == 200
    assert response.json()["answer"] == "تحليل تجريبي"
    assert response.json()["sources"] == []
    assert response.json()["warnings"]


def test_legal_response_uses_authorized_retrieval_results(monkeypatch, tmp_path):
    import amin_legal_model.api as api

    class FakeProvider:
        async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
            assert "[المصدر 1]" in user_prompt
            return "استناد إلى [المصدر 1]"

    monkeypatch.setattr(api, "_provider", FakeProvider())
    index = tmp_path / "index.sqlite"
    index.write_bytes(b"placeholder")
    monkeypatch.setenv("AMIN_LEGAL_INDEX_PATH", str(index))
    monkeypatch.setattr(api, "search_legal_index", lambda *args, **kwargs: [{
        "document_id": "doc-1",
        "chunk_number": 0,
        "title": "قانون تجريبي",
        "branch": "civil",
        "source_reference": "عدد رسمي",
        "source_url": "https://example.test/source",
        "effective_from": "2020-01-01",
        "effective_to": None,
        "chunk_text": "نص المادة المسترجعة",
    }])
    response = client.post(
        "/v1/legal/respond",
        json={
            "task": "analyze",
            "text": "وقائع افتراضية",
            "retrieval_query": "المادة المدنية",
            "as_of_date": "2024-01-01",
        },
    )
    assert response.status_code == 200
    assert response.json()["sources"][0]["title"] == "قانون تجريبي"
