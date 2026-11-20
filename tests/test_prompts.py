from amin_legal_model.legal.prompts import EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_prohibits_fabricated_legal_authorities() -> None:
    assert "لا تختلق نصوص قوانين أو أحكامًا" in EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_requires_disclosing_missing_sources() -> None:
    assert "حدد النقص صراحة" in EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_requires_adversarial_analysis_and_counterargument() -> None:
    assert "ابنِ أقوى حجة للخصم أولاً" in EGYPTIAN_LEGAL_SYSTEM_PROMPT
    assert "كيف يمكن للقاضي رفضها" in EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_requires_timing_and_forfeiture_risk_analysis() -> None:
    assert "احتمال سقوط الحق فيه أو اعتباره تنازلاً" in EGYPTIAN_LEGAL_SYSTEM_PROMPT
    assert "خطر فوات ميعاد أو سقوط دفع" in EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_requires_deciding_whether_and_how_much_to_respond() -> None:
    assert "لا ترد على كل عبارة تلقائيًا" in EGYPTIAN_LEGAL_SYSTEM_PROMPT
    assert "رد محدود على نقطة محددة" in EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_requires_separating_hidden_intent_hypotheses_from_facts() -> None:
    assert "لا تنسب إليه نية خفية كحقيقة" in EGYPTIAN_LEGAL_SYSTEM_PROMPT
