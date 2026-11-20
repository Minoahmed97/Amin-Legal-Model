from datetime import date

from amin_legal_model.legal.strategy import assess_strategy


def _facts(**overrides):
    data = {
        "objective": "رفض طلب الخصم",
        "case_stage": "استئناف",
        "client_role": "مستأنف ضده",
        "as_of_date": date(2026, 11, 20),
        "deadline_date": None,
        "deadline_verified": False,
        "mandatory_response": False,
        "silence_harm_possible": False,
        "risk_of_curative_reply": False,
        "opponent_points": [{"title": "دفع الخصم"}],
        "response_points": [
            {"title": "مخالفة الثابت بالأوراق", "supported_by_record": True, "materiality": "high"}
        ],
        "missing_documents": [],
        "request_full_brief": False,
    }
    data.update(overrides)
    return data


def test_mandatory_response_overrides_tactical_silence():
    result = assess_strategy(_facts(
        mandatory_response=True,
        risk_of_curative_reply=True,
        response_points=[],
    ))
    assert "الآن" in result["recommendation"]
    assert "mandatory_or_silence_risk_overrides_tactical_silence" in result["rule_triggers"]


def test_targeted_response_when_few_supported_points():
    result = assess_strategy(_facts())
    assert result["recommendation"] == "تقديم رد مركز على النقاط المنتجة"
    assert "رد محدد" in result["response_scope"]


def test_no_expansive_reply_when_only_curative_risk_and_no_supported_point():
    result = assess_strategy(_facts(response_points=[], risk_of_curative_reply=True))
    assert "عدم تقديم رد" in result["recommendation"]
    assert result["priority_points"] == []


def test_missing_case_context_prevents_recommendation():
    result = assess_strategy(_facts(client_role=""))
    assert result["recommendation"] == "استكمال بيانات جوهرية قبل القرار"
    assert result["confidence"] == "منخفضة"


def test_near_deadline_is_flagged_even_without_mandatory_checkbox():
    result = assess_strategy(_facts(deadline_date=date(2026, 11, 22)))
    assert result["urgency"] == "عاجلة جدًا"
    assert "deadline_within_three_days" in result["rule_triggers"]



def test_past_entered_deadline_triggers_procedural_review_not_silence():
    result = assess_strategy(_facts(deadline_date=date(2026, 11, 19)))
    assert result["urgency"] == "عاجلة جدًا"
    assert "الآن" in result["recommendation"]
    assert "entered_deadline_in_past" in result["rule_triggers"]
