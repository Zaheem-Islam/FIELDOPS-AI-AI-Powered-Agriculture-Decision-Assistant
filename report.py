from datetime import datetime

from i18n import localize_irrigation, localize_result, translate_text


def build_report(crop, stage, area, moisture, rainfall, forecast, result, irrigation, evidence, validation, language="en"):
    localized_result = localize_result(result, language)
    localized_irrigation = localize_irrigation(irrigation, language)
    localized_evidence = [translate_text(item, language) for item in evidence]
    localized_issues = [translate_text(issue, language) for issue in validation["issues"]]
    localized_actions = [translate_text(action, language) for action in result["next_actions"]]

    if language == "ur":
        lines = [
            "FIELDOPS AI — فیلڈ اسسمنٹ رپورٹ",
            "=" * 45,
            f"تخلیق: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "فیلڈ ان پٹس",
            f"فصل: {crop}",
            f"نشوونما کا مرحلہ: {stage}",
            f"میدان کا رقبہ: {area} ایکڑ",
            f"مٹی کی نمی: {moisture}",
            f"حالیہ بارش: {rainfall} mm",
            f"متوقع بارش: {forecast} mm",
            "",
            "میدان کی حالت",
            localized_result["field_status"],
            "",
            "سیراب کاری",
            localized_result["recommendation"],
            f"تخمینہ شدہ پانی: {localized_irrigation['liters']:,.0f} L",
            f"حساب کا طریقہ: {localized_irrigation['method']}",
            "",
            "ایجنٹ کے نتائج",
            f"فصل کی صحت: {localized_result['crop_health']['finding']}",
            f"مٹی: {localized_result['soil']['finding']}",
            f"موسم: {localized_result['weather']['finding']}",
            f"ویژن: {localized_result['vision']['observation']}",
            "",
            "علمی ثبوت",
            *[f"- {x}" for x in localized_evidence],
            "",
            "توثیق",
            *(localized_issues or ["بڑے تضادات کا پتہ نہیں چلا۔"]),
            "",
            "اگلی کارروائیاں",
            *[f"- {x}" for x in localized_actions],
            "",
            "حد",
            "فیلڈ آپس اے آئی فیصلہ سازی کا معاون ہے۔ اہم فیلڈ اقدامات سے پہلے انسانی جائزہ ضروری ہے۔",
            "فصل کی صحت کا تصویری جائزہ ابتدائی ہے اور قطعی تشخیص نہیں ہے۔",
        ]
        return "\n".join(lines)

    lines = [
        "FIELDOPS AI — FIELD ASSESSMENT REPORT",
        "=" * 45,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "FIELD INPUTS",
        f"Crop: {crop}",
        f"Growth stage: {stage}",
        f"Field area: {area} acres",
        f"Soil moisture: {moisture}",
        f"Recent rainfall: {rainfall} mm",
        f"Expected rainfall: {forecast} mm",
        "",
        "FIELD STATUS",
        localized_result["field_status"],
        "",
        "IRRIGATION",
        localized_result["recommendation"],
        f"Estimated water: {localized_irrigation['liters']:,.0f} L",
        f"Calculation method: {localized_irrigation['method']}",
        "",
        "AGENT FINDINGS",
        f"Crop Health: {localized_result['crop_health']['finding']}",
        f"Soil: {localized_result['soil']['finding']}",
        f"Weather: {localized_result['weather']['finding']}",
        f"Vision: {localized_result['vision']['observation']}",
        "",
        "KNOWLEDGE EVIDENCE",
        *[f"- {x}" for x in localized_evidence],
        "",
        "VALIDATION",
        *(localized_issues or ["No major validation issues detected."]),
        "",
        "NEXT ACTIONS",
        *[f"- {x}" for x in localized_actions],
        "",
        "LIMITATION",
        "FIELDOPS AI is decision support. Consequential field actions require human review.",
        "Crop-health image analysis is preliminary and is not a definitive diagnosis."
    ]
    return "\n".join(lines)
