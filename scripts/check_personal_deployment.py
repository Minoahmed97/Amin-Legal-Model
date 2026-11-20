"""Smoke-test the live single-user AMIN server without printing secrets or case data."""
from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_json(url: str, *, api_key: str | None = None, payload: dict | None = None) -> dict:
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["X-Amin-Api-Key"] = api_key
    request = Request(url, data=data, headers=headers, method="POST" if data else "GET")
    with urlopen(request, timeout=900) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    base_url = os.getenv("AMIN_API_URL", "http://127.0.0.1:8000").rstrip("/")
    api_key = os.getenv("AMIN_API_KEY", "")
    if not api_key:
        print("FAIL: AMIN_API_KEY is not set.", file=sys.stderr)
        return 2

    try:
        health = request_json(f"{base_url}/health")
        if not health.get("model_configured") or not health.get("model_server_ready"):
            print("FAIL: API is reachable but the configured model server is not ready.")
            return 1
        print("PASS: private API and configured model server are ready.")

        response = request_json(
            f"{base_url}/v1/legal/respond",
            api_key=api_key,
            payload={
                "task": "analyze",
                "jurisdiction": "EG",
                "language": "ar",
                "text": (
                    "اختبار تقني فقط: اشرح بإيجاز منهج التحقق من مصدر القاعدة القانونية "
                    "ولا تذكر أرقام مواد أو أحكام غير مسترجعة من قاعدة البيانات."
                ),
            },
        )
        answer = response.get("answer")
        if response.get("status") != "completed" or not isinstance(answer, str) or not answer.strip():
            print("FAIL: model endpoint did not return a completed non-empty answer.")
            return 1
        print("PASS: real model inference returned a non-empty answer.")
        if response.get("warnings"):
            print("NOTICE: response warnings exist; legal source retrieval is not yet certified.")
        print("This smoke test verifies service operation only, not Egyptian-law accuracy.")
        return 0
    except HTTPError as exc:
        print(f"FAIL: HTTP {exc.code} from private service.", file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: private service check failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
