from fastapi.testclient import TestClient

from amin_legal_model.api import app

client = TestClient(app)


def test_health_endpoint_reports_no_model_loaded() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["model_loaded"] is False


def test_inference_endpoint_does_not_fake_an_answer_without_model() -> None:
    response = client.post(
        "/v1/legal/respond",
        json={"task": "analyze", "text": "وقائع افتراضية للاختبار"},
    )
    assert response.status_code == 503
    assert "No model provider is configured" in response.json()["detail"]
