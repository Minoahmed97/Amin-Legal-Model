from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_personal_compose_keeps_model_server_unpublished_and_api_loopback_only():
    config = yaml.safe_load((ROOT / "docker-compose.personal.yml").read_text())
    model = config["services"]["model"]
    api = config["services"]["api"]

    assert "ports" not in model
    assert model["expose"] == ["8001"]
    assert api["ports"] == ["127.0.0.1:${AMIN_API_PORT:-8000}:8000"]
    assert api["environment"]["AMIN_ENV"] == "production"
    assert api["environment"]["AMIN_PROVIDER"] == "vllm"
    assert config["networks"]["amin-private"].get("internal", False) is False


def test_personal_deployment_has_a_non_secret_env_template():
    env_template = (ROOT / ".env.personal.example").read_text()
    gitignore = (ROOT / ".gitignore").read_text()

    assert "google/gemma-4-31B-it-qat-w4a16-ct" in env_template
    assert "AMIN_API_KEY=REPLACE_" in env_template
    assert "AMIN_MODEL_SERVER_KEY=REPLACE_" in env_template
    assert ".env" in gitignore
    assert "!.env.personal.example" in gitignore
