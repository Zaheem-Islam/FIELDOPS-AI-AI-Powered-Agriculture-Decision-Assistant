from copy import deepcopy
from functools import lru_cache
import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen


UI_TEXT = {
    "en": {
        "app_title": "🌾 FIELDOPS AI",
        "subtitle": "Agriculture Decision Intelligence — Multimodal Multi-Agent Field Assistant",
        "field_assessment": "⚙️ Field Assessment",
        "crop": "Crop",
        "growth_stage": "Growth Stage",
        "field_area": "Field Area (acres)",
        "soil_moisture": "Soil Moisture",
        "recent_rainfall": "Recent Rainfall (mm)",
        "expected_rainfall": "Expected Rainfall Next 24h (mm)",
        "temperature": "Temperature (°C)",
        "field_notes": "Field Notes",
        "upload_image": "📷 Upload Crop Image",
        "analyze_button": "🔍 ANALYZE FIELD",
        "evidence_input": "📋 Evidence Input",
        "field_status": "Field Status",
        "irrigation": "Irrigation",
        "estimated_water": "Estimated Water",
        "method": "Method",
        "coordination_recommendation": "🧠 Coordinator Recommendation",
        "confidence": "Confidence",
        "human_review": "Human review: Required before consequential field action.",
        "specialist_findings": "🤖 Specialist Agent Findings",
        "rag_evidence": "📚 Evidence / RAG",
        "validation": "🛡️ Validation",
        "preliminary_image": "👁️ Preliminary Image Screening",
        "recommended_actions": "➡️ Recommended Next Actions",
        "download_report": "📄 Download Field Assessment Report",
        "disclaimer": "FIELDOPS AI is decision support, not autonomous farm control. Crop-health observations are preliminary and require field verification.",
        "status_running": "🤖 Running FIELDOPS AI agent workflow...",
        "task_router": "✓ Task Router — agriculture workflow selected",
        "farm_coordinator": "✓ Farm Coordinator — task plan created",
        "crop_health_agent": "✓ Crop Health Agent — preliminary image screening",
        "soil_agent": "✓ Soil Agent — soil condition assessment",
        "weather_agent": "✓ Weather Agent — rainfall/weather assessment",
        "irrigation_tool": "✓ Irrigation Tool — deterministic calculation",
        "knowledge_agent": "✓ Knowledge/RAG Agent — supporting guidance retrieved",
        "validator": "✓ Validator — missing-data and contradiction checks",
        "coordinator": "✓ Coordinator — final recommendation synthesized",
        "assessment_complete": "✅ Assessment complete",
        "enter_evidence": "Enter the field evidence in the sidebar and click **ANALYZE FIELD**.",
        "prototype_intro": "### What this prototype demonstrates",
        "prototype_text": "Specialist agents analyze crop health, soil, weather and irrigation; RAG supplies controlled agriculture guidance; a deterministic calculator handles the water estimate; a validator checks the evidence before the coordinator creates the action plan.",
        "language": "Language / زبان",
        "english": "English",
        "urdu": "اردو",
    },
    "ur": {
        "app_title": "🌾 فیلڈ آپس اے آئی",
        "subtitle": "زرعی فیصلہ سازی — ملٹی موڈل ملٹی ایجنٹ فیلڈ اسسٹنٹ",
        "field_assessment": "⚙️ فیلڈ اسسمنٹ",
        "crop": "فصل",
        "growth_stage": "نشوونما کا مرحلہ",
        "field_area": "میدان کا رقبہ (ایکڑ)",
        "soil_moisture": "مٹی کی نمی",
        "recent_rainfall": "حالیہ بارش (mm)",
        "expected_rainfall": "اگلے 24 گھنٹوں میں متوقع بارش (mm)",
        "temperature": "درجہ حرارت (°C)",
        "field_notes": "فیلڈ نوٹس",
        "upload_image": "📷 فصل کی تصویر اپ لوڈ کریں",
        "analyze_button": "🔍 فیلڈ کا تجزیہ کریں",
        "evidence_input": "📋 ثبوت/دستاویزات",
        "field_status": "میدان کی حالت",
        "irrigation": "سیراب کاری",
        "estimated_water": "تخمینہ شدہ پانی",
        "method": "طریقہ",
        "coordination_recommendation": "🧠 کوآرڈینیٹر سفارش",
        "confidence": "اعتماد",
        "human_review": "انسانی جائزہ: اہم فیلڈ فیصلے سے پہلے ضروری ہے۔",
        "specialist_findings": "🤖 اسپیشلسٹ ایجنٹ کے نتائج",
        "rag_evidence": "📚 ثبوت / RAG",
        "validation": "🛡️ توثیق",
        "preliminary_image": "👁️ ابتدائی تصویری جائزہ",
        "recommended_actions": "➡️ سفارش شدہ اگلی کارروائیاں",
        "download_report": "📄 فیلڈ اسسمنٹ رپورٹ ڈاؤن لوڈ کریں",
        "disclaimer": "فیلڈ آپس اے آئی فیصلہ سازی کا معاون ہے، خودکار فارم کنٹرول نہیں۔ فصل کی صحت کا جائزہ ابتدائی ہے اور فیلڈ چیک لازمی ہے۔",
        "status_running": "🤖 فیلڈ آپس اے آئی ایجنٹ ورک فلو چل رہا ہے...",
        "task_router": "✓ ٹاسک روٹر — زرعی ورک فلو منتخب",
        "farm_coordinator": "✓ فارم کوآرڈینیٹر — ٹاسک پلان بن چکا",
        "crop_health_agent": "✓ فصل کی صحت ایجنٹ — ابتدائی تصویری جائزہ",
        "soil_agent": "✓ مٹی ایجنٹ — مٹی کی حالت کا جائزہ",
        "weather_agent": "✓ موسمی ایجنٹ — بارش/موسم کا جائزہ",
        "irrigation_tool": "✓ سیراب کاری ٹول — فیصلہ کن حساب",
        "knowledge_agent": "✓ علم/RAG ایجنٹ — معاون رہنمائی حاصل",
        "validator": "✓ ویلیڈیٹر — معلومات کی کمی اور تضاد کی جانچ",
        "coordinator": "✓ کوآرڈینیٹر — حتمی سفارش تیار",
        "assessment_complete": "✅ اسسمنٹ مکمل",
        "enter_evidence": "سائیڈ بار میں فیلڈ ثبوت درج کریں اور **فیلڈ کا تجزیہ کریں** دبائیں۔",
        "prototype_intro": "### یہ پروٹو ٹائپ کیا دکھاتا ہے",
        "prototype_text": "اسپیشلسٹ ایجنٹ فصل کی صحت، مٹی، موسم اور سیراب کاری کا تجزیہ کرتے ہیں؛ RAG محدود زرعی رہنمائی فراہم کرتا ہے؛ ایک فیصلہ کن کیلکولیٹر پانی کے تخمینے کو سنبھالتا ہے؛ ویلیڈیٹر ثبوت کی جانچ کرتا ہے اور پھر کوآرڈینیٹر ایک معاون پلان بناتا ہے۔",
        "language": "زبان / Language",
        "english": "English",
        "urdu": "اردو",
    },
}

PHRASE_MAP = {
    "Water Stress Risk — HIGH": "پانی کی کمی کا خطرہ — بہت زیادہ",
    "Field Condition — MONITOR": "میدان کی حالت — نگرانی",
    "Low soil moisture": "مٹی میں پانی کم ہے",
    "low soil moisture": "مٹی میں پانی کم",
    "Adequate soil moisture": "مٹی میں پانی مناسب ہے",
    "High soil moisture": "مٹی میں پانی بہت زیادہ ہے",
    "Limited rainfall": "کم بارش",
    "limited rainfall": "کم بارش",
    "Rainfall may reduce immediate irrigation need": "بارش جلدی سیراب کاری کی ضرورت کو کم کر سکتی ہے",
    "Recommended": "تجویز شدہ",
    "No Immediate Irrigation": "فوری سیراب کاری نہیں",
    "Consider / Reassess": "غور کریں / دوبارہ جائزہ لیں",
    "Medium": "درمیانہ",
    "High": "زیادہ",
    "Low": "کم",
    "Required field information is missing.": "مطلوبہ معلومات موجود نہیں ہیں۔",
    "Review the irrigation recommendation with a field technician.": "فارم ٹیکنیشن سے سیراب کاری کی سفارش کا جائزہ لیں۔",
    "Review the irrigation recommendation.": "سیراب کاری کی سفارش کا دوبارہ جائزہ لیں۔",
    "Inspect crop leaves and soil condition within 24 hours.": "24 گھنٹوں کے اندر فصل کی پتیوں اور مٹی کی حالت کا جائزہ لیں۔",
    "Reassess soil moisture after irrigation or rainfall.": "سیراب کاری یا بارش کے بعد مٹی کی نمی کا دوبارہ جائزہ لیں۔",
    "Continue monitoring soil moisture.": "مٹی کی نمی کو جاری رکھیں۔",
    "Inspect visible crop symptoms.": "ظاہر ہونے والے فصل کے نشانات دیکھیں۔",
    "Reassess after significant rainfall or moisture change.": "کافی بارش یا نمی میں تبدیلی کے بعد دوبارہ جائزہ لیں۔",
    "No image was provided, so visual screening could not be performed.": "کوئی تصویر فراہم نہیں کی گئی، اس لیے بصری جائزہ نہیں کیا جا سکا۔",
    "Upload a crop image for preliminary visual screening.": "ابتدائی بصری جائزہ کے لیے فصل کی تصویر اپ لوڈ کریں۔",
    "Preliminary visual screening should be treated as a possible stress indicator, not a diagnosis.": "ابتدائی تصویری جائزے کو ممکنہ دباؤ کی علامت سمجھیں، حتمی تشخیص نہیں۔",
    "When recent and expected rainfall are limited, irrigation decisions should consider crop stage and current soil moisture together.": "جب حالیہ اور متوقع بارش کم ہو تو آبپاشی کا فیصلہ کرتے وقت فصل کے مرحلے اور موجودہ مٹی کی نمی دونوں کو مدِنظر رکھیں۔",
    "Wheat at flowering is a water-sensitive stage; low soil moisture during this stage warrants closer water-stress monitoring.": "پھول آنے کے مرحلے میں گندم پانی کی کمی سے متاثر ہو سکتی ہے؛ اس دوران مٹی کی کم نمی پر زیادہ توجہ دیں۔",
    "Soil moisture should be interpreted together with crop stage, recent rainfall and expected weather rather than as an isolated value.": "مٹی کی نمی کو اکیلا پیمانہ نہ سمجھیں؛ فصل کے مرحلے، حالیہ بارش اور متوقع موسم کے ساتھ دیکھیں۔",
    "Visible leaf symptoms are suitable for preliminary screening only; field inspection and validated diagnosis are required before treating a disease.": "پتوں کی ظاہری علامات صرف ابتدائی جائزے کے لیے ہیں؛ بیماری کا علاج کرنے سے پہلے کھیت کا معائنہ اور درست تشخیص ضروری ہے۔",
    "General guidance: interpret crop condition using multiple evidence sources and verify consequential actions in the field.": "عمومی رہنمائی: فصل کی حالت کو مختلف شواہد کی مدد سے سمجھیں اور اہم اقدامات کی کھیت میں تصدیق کریں۔",
    "Irrigation is recommended for the": "سیراب کاری کی سفارش کی جاتی ہے",
    "Immediate irrigation is not strongly indicated": "فوری سیراب کاری کی شدید ضرورت نہیں ہے",
    "Continue monitoring the": "میدان کو جاری رکھیں",
    "Evidence / RAG": "ثبوت / RAG",
    "Required inputs available. ✓ No major contradictions detected.": "مطلوبہ معلومات موجود ہیں۔ ✓ بڑے تضادات کا پتہ نہیں چلا۔",
    "low soil moisture + limited rainfall": "مٹی میں پانی کم + کم بارش",
    "Controlled demo rule: low soil moisture + limited rainfall": "کنٹرولڈ ڈیمو اصول: مٹی میں پانی کم + کم بارش",
    "Controlled demo rule: adequate moisture/rainfall": "کنٹرولڈ ڈیمو اصول: مناسب نمی/بارش",
    "Controlled demo rule: intermediate conditions": "کنٹرولڈ ڈیمو اصول: درمیانی حالات",
}


def translate_ui(key, language="en"):
    return UI_TEXT.get(language, UI_TEXT["en"]).get(key, key)


@lru_cache(maxsize=512)
def _translate_urdu_online(value):
    query = urlencode({"client": "gtx", "sl": "en", "tl": "ur", "dt": "t", "q": value})
    request = Request(
        f"https://translate.googleapis.com/translate_a/single?{query}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
        translated = "".join(
            segment[0]
            for segment in payload[0]
            if isinstance(segment, list) and segment and isinstance(segment[0], str)
        )
        return translated or None
    except (OSError, ValueError, IndexError, TypeError):
        return None


def _localize_fallback_recommendation(value):
    crop_names = {"wheat": "گندم", "rice": "چاول", "maize": "مکئی", "cotton": "کپاس", "other": "فصل"}
    stages = {
        "germination": "بیج کے اگنے کے مرحلے",
        "vegetative": "نشوونما کے مرحلے",
        "flowering": "پھول آنے کے مرحلے",
        "grain filling": "دانے بھرنے کے مرحلے",
        "maturity": "پختگی کے مرحلے",
    }
    recommended = re.fullmatch(
        r"Irrigation is recommended for the (.+?) field because soil moisture is low, "
        r"recent/expected rainfall is limited, and the crop is at the (.+?) stage\.",
        value,
        flags=re.IGNORECASE,
    )
    if recommended:
        crop = crop_names.get(recommended.group(1).lower())
        stage = stages.get(recommended.group(2).lower())
        if crop and stage:
            return f"{stage} میں {crop} کی فصل کے لیے آبپاشی کا مشورہ ہے کیونکہ مٹی میں نمی کم ہے اور حالیہ یا متوقع بارش محدود ہے۔"

    monitored = re.fullmatch(
        r"Immediate irrigation is not strongly indicated from the supplied evidence\. "
        r"Continue monitoring the (.+?) field and reassess after weather changes\.",
        value,
        flags=re.IGNORECASE,
    )
    if monitored:
        crop = crop_names.get(monitored.group(1).lower())
        if crop:
            return f"دی گئی معلومات سے فوری آبپاشی کی واضح ضرورت ظاہر نہیں ہوتی۔ موسم بدلنے پر {crop} کے کھیت کی نگرانی جاری رکھیں اور دوبارہ جائزہ لیں۔"

    return None


def translate_text(value, language="en"):
    if language != "ur" or not isinstance(value, str):
        return value

    fallback_translation = _localize_fallback_recommendation(value)
    if fallback_translation:
        return fallback_translation

    translated = value
    for source, target in sorted(PHRASE_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        translated = translated.replace(source, target)

    translated = translated.replace("Irrigation is recommended", "سیراب کاری کی سفارش کی جاتی ہے")
    translated = translated.replace("Review the irrigation recommendation.", "سیراب کاری کی سفارش کا دوبارہ جائزہ لیں۔")
    translated = translated.replace("Immediate irrigation is not strongly indicated", "فوری سیراب کاری کی شدید ضرورت نہیں ہے")
    translated = translated.replace("Continue monitoring the", "میدان کو جاری رکھیں")
    translated = translated.replace("Human review", "انسانی جائزہ")
    translated = translated.replace("Confidence", "اعتماد")
    translated = translated.replace("Recommended", "تجویز شدہ")
    translated = translated.replace("No Immediate Irrigation", "فوری سیراب کاری نہیں")
    translated = translated.replace("Consider / Reassess", "غور کریں / دوبارہ جائزہ لیں")
    translated = translated.replace("Required inputs available. ✓ No major contradictions detected.", "مطلوبہ معلومات موجود ہیں۔ ✓ بڑے تضادات کا پتہ نہیں چلا۔")

    def translate_fragment(match):
        return _translate_urdu_online(match.group(0)) or match.group(0)

    translated = re.sub(r"[A-Za-z][A-Za-z0-9 \t.,!?;:'\"()/_+\-]*", translate_fragment, translated)
    return translated


def localize_result(result, language="en"):
    if language != "ur":
        return result

    localized = deepcopy(result)
    for key in ["field_status", "recommendation", "confidence"]:
        localized[key] = translate_text(localized.get(key, ""), language)
    recommendation = localized["recommendation"]
    recommendation = recommendation.replace("سیراب کاری کی سفارش کی جاتی ہے", "سیراب کاری کا مشورہ دیا جاتا ہے")
    recommendation = recommendation.replace("آبپاشی کی سفارش کی جاتی ہے", "آبپاشی کا مشورہ دیا جاتا ہے")
    recommendation = recommendation.replace("سیراب کاری کی سفارش", "سیراب کاری کا مشورہ")
    recommendation = recommendation.replace("آبپاشی کی سفارش", "آبپاشی کا مشورہ")
    localized["recommendation"] = recommendation.replace("سفارش", "مشورہ")

    for agent_key in ["crop_health", "soil", "weather"]:
        agent_value = localized.get(agent_key, {})
        if not isinstance(agent_value, dict):
            continue
        agent_value["finding"] = translate_text(agent_value.get("finding", ""), language)
        agent_value["confidence"] = translate_text(agent_value.get("confidence", ""), language)

    vision = localized.get("vision", {})
    if isinstance(vision, dict):
        vision["observation"] = translate_text(vision.get("observation", ""), language)
        vision["limitation"] = translate_text(vision.get("limitation", ""), language)

    validation = localized.get("validation", {})
    if isinstance(validation, dict):
        validation["issues"] = [translate_text(issue, language) for issue in validation.get("issues", [])]

    next_actions = localized.get("next_actions", [])
    localized["next_actions"] = [translate_text(action, language) for action in next_actions]

    return localized


def localize_irrigation(irrigation, language="en"):
    if language != "ur":
        return irrigation

    localized = deepcopy(irrigation)
    localized["recommendation"] = translate_text(localized.get("recommendation", ""), language)
    localized["method"] = translate_text(localized.get("method", ""), language)
    return localized
