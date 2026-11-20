from amin_legal_model.legal.prompts import EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_prohibits_fabricated_legal_authorities() -> None:
    assert "لا تختلق نصوص قوانين أو أحكامًا" in EGYPTIAN_LEGAL_SYSTEM_PROMPT


def test_prompt_requires_disclosing_missing_sources() -> None:
    assert "فاذكر النقص صراحة ولا تخمّن" in EGYPTIAN_LEGAL_SYSTEM_PROMPT
