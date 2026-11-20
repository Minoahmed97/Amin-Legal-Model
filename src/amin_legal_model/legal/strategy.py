"""Transparent, rule-based litigation strategy triage.

This module does not predict judicial outcomes or replace verification of Egyptian
procedural law. It exposes the assumptions and rule triggers behind each suggestion.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def assess_strategy(facts: dict[str, Any]) -> dict[str, Any]:
    """Return a cautious first-pass response/timing recommendation.

    Expected keys are validated by the API schema; this function remains usable
    independently and treats absent/unsupported evidence conservatively.
    """
    today = facts.get("as_of_date") or date.today()
    if isinstance(today, str):
        today = date.fromisoformat(today)

    stage = str(facts.get("case_stage") or "").strip()
    role = str(facts.get("client_role") or "").strip()
    objective = str(facts.get("objective") or "").strip()
    deadline = facts.get("deadline_date")
    if isinstance(deadline, str):
        deadline = date.fromisoformat(deadline)

    opponent_points = facts.get("opponent_points") or []
    response_points = facts.get("response_points") or []
    missing_documents = facts.get("missing_documents") or []
    mandatory = bool(facts.get("mandatory_response"))
    silence_risk = bool(facts.get("silence_harm_possible"))
    curative_risk = bool(facts.get("risk_of_curative_reply"))
    verified_deadline = bool(facts.get("deadline_verified"))

    rule_triggers: list[str] = []
    warnings: list[str] = [
        "هذا فرز استراتيجي أولي قائم على البيانات المدخلة، وليس فتوى أو تحققًا من النصوص والمواعيد الإجرائية.",
        "لا يتنبأ النظام بما سيحكم به القاضي؛ يجب اختبار كل توصية على ملف الدعوى والقانون الساري.",
    ]
    if not role or not stage or not objective:
        return {
            "recommendation": "استكمال بيانات جوهرية قبل القرار",
            "response_scope": "غير محدد",
            "urgency": "غير قابل للتحديد",
            "confidence": "منخفضة",
            "reasons": ["يلزم تحديد صفة الموكل والمرحلة الإجرائية والهدف المطلوب."],
            "rule_triggers": ["missing_case_context"],
            "priority_points": [],
            "risks": ["أي قرار بشأن الرد أو الصمت قبل تحديد هذه البيانات قد يضر بالمركز الإجرائي."],
            "next_steps": ["استكمال صفة الموكل والمرحلة والهدف، والتحقق المستقل من أي ميعاد قائم."],
            "warnings": warnings,
        }

    urgency = "عادية"
    days_left: int | None = None
    if deadline is not None:
        days_left = (deadline - today).days
        if days_left < 0:
            urgency = "عاجلة جدًا"
            rule_triggers.append("entered_deadline_is_in_past")
            warnings.append("التاريخ المدخل مضى؛ لا يمكن الجزم بفوات الميعاد قبل التحقق من بدء سريانه ووقفه وانقطاعه وطريقة الإعلان.")
        elif days_left <= 3:
            urgency = "عاجلة جدًا"
            rule_triggers.append("deadline_within_three_days")
        elif days_left <= 7:
            urgency = "عاجلة"
            rule_triggers.append("deadline_within_seven_days")
        elif days_left <= 14:
            urgency = "قريبة"
            rule_triggers.append("deadline_within_fourteen_days")
        if not verified_deadline:
            warnings.append("الميـعاد المدخل غير مؤكد؛ راجع مصدر بدء الميعاد وطريقة الإعلان والعطلات والقواعد الخاصة قبل الإيداع.")

    must_act = mandatory or silence_risk or (deadline is not None and days_left is not None and 0 <= days_left <= 7)
    supported = [
        point for point in response_points
        if point.get("supported_by_record") is True
        and point.get("materiality", "medium") in {"critical", "high", "medium"}
    ]
    unsupported = [
        point for point in response_points
        if point.get("supported_by_record") is not True
    ]
    priority = [
        {
            "point": str(point.get("title") or "نقطة دون عنوان"),
            "materiality": point.get("materiality", "medium"),
            "evidence": "مدعومة بحسب البيانات المدخلة",
        }
        for point in sorted(
            supported,
            key=lambda item: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(
                item.get("materiality", "medium"), 2
            ),
        )
    ]
    risks: list[str] = []
    if unsupported:
        risks.append("توجد نقاط رد لا يثبتها الملف بحسب البيانات المدخلة؛ لا تعرضها كوقائع ثابتة.")
        rule_triggers.append("unsupported_response_points")
    if missing_documents:
        risks.append("المستندات الناقصة قد تغير التكييف أو عبء الإثبات أو جدوى الرد.")
        rule_triggers.append("missing_documents")
    if curative_risk:
        risks.append("الرد الموسع قد يمنح الخصم فرصة لتدارك نقص أو تعديل روايته؛ قصر الرد على اللازم ما لم يوجد واجب إجرائي.")
        rule_triggers.append("risk_of_curative_reply")

    reasons: list[str] = []
    next_steps: list[str] = []
    if must_act:
        recommendation = "اتخاذ إجراء حافظ للحق أو الرد الآن بعد التحقق العاجل"
        rule_triggers.append("mandatory_or_silence_risk_overrides_tactical_silence")
        reasons.append("وجود رد إلزامي أو ضرر إجرائي محتمل من الصمت أو ميعاد قريب يرجح عدم انتظار اكتمال التحليل.")
        if supported and (facts.get("request_full_brief") or len(supported) >= 3):
            scope = "مذكرة منظمة تتناول المسائل الجوهرية فقط"
        else:
            scope = "رد محدد ومقتصر على النقاط اللازمة لحفظ الحق"
        next_steps.append("تحقق فورًا من الإجراء الواجب والميعاد والجهة المختصة، ثم أودع ما يلزم لحفظ الحق.")
        if missing_documents:
            next_steps.append("اطلب أو قدم المستندات الناقصة وبيّن أثر تعذر الحصول عليها دون اختلاق مضمونها.")
    elif curative_risk and not supported:
        recommendation = "عدم تقديم رد موضوعي موسع الآن مع استكمال التحقق"
        scope = "لا رد موضوعي حاليًا؛ يراجع فقط ما إذا كان يلزم إجراء شكلي حافظ للحق"
        rule_triggers.append("silence_preferred_only_when_no_mandatory_risk_and_no_supported_answer")
        reasons.append("لا تظهر نقطة رد مدعومة، بينما يوجد خطر من كشف معالجة أو منح الخصم فرصة لتدارك نقصه.")
        next_steps.append("استكمل المستندات وافحص محضر الجلسة والإجراءات والميعاد قبل اتخاذ قرار الصمت.")
    elif missing_documents and not supported:
        recommendation = "استكمال المستندات والتحقق قبل الرد الموضوعي"
        scope = "تأجيل الرد الموضوعي فقط إذا لم يوجد ميعاد أو واجب إجرائي"
        reasons.append("الرد الحالي غير مسنود بما يكفي، والمستندات الناقصة قد تغير القرار.")
        next_steps.append("حدد كل مستند ناقص، وحائزه، ووسيلة الحصول عليه، وأثر غيابه على الإثبات.")
    elif supported:
        recommendation = "تقديم رد مركز على النقاط المنتجة"
        scope = (
            "مذكرة شاملة منضبطة" if facts.get("request_full_brief") or len(supported) >= 3
            else "رد محدد على النقاط المدعومة والمنتجة"
        )
        reasons.append("توجد نقاط رد مدعومة تستحق المعالجة دون تشتيت الملف في مسائل غير منتجة.")
        next_steps.append("اربط كل رد بمستنده وأثره القانوني، ثم اختبر أقوى جواب محتمل للخصم.")
    else:
        recommendation = "عدم التوسع في الرد قبل ظهور أساس واقعي أو قانوني"
        scope = "لا رد موسع؛ متابعة الملف والتحقق من النقاط المثارة"
        reasons.append("لم تُدخل بيانات تثبت وجود نقطة رد منتجة حتى الآن.")
        next_steps.append("راجع الأوراق ومصدر كل ادعاء وحدد ما إذا كان السكوت يترتب عليه أثر إجرائي.")

    if not verified_deadline:
        next_steps.append("وثق تاريخ الإعلان أو العلم والإجراء الذي يبدأ منه الميعاد؛ لا تعتمد على التاريخ التقديري وحده.")
    if opponent_points:
        reasons.append(f"تم إدخال {len(opponent_points)} نقطة للخصم؛ يلزم اختبار أقوى صياغة لها قبل اعتماد الرد.")
    return {
        "recommendation": recommendation,
        "response_scope": scope,
        "urgency": urgency,
        "confidence": "محدودة؛ توصية أولية مشروطة بصحة المدخلات",
        "reasons": reasons,
        "rule_triggers": rule_triggers,
        "priority_points": priority,
        "risks": risks,
        "next_steps": next_steps,
        "warnings": warnings,
    }
