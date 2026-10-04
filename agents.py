import os
import json
import re


def _fallback(crop, stage, moisture, rainfall, forecast, notes, area):
    soil_status = (
        "Low soil moisture"
        if moisture < 250
        else ("Adequate soil moisture" if moisture < 350 else "High soil moisture")
    )

    weather_status = (
        "Limited rainfall"
        if rainfall < 10 and forecast < 10
        else "Rainfall may reduce immediate irrigation need"
    )

    if moisture < 250 and rainfall < 10 and forecast < 10:
        field_status = "Water Stress Risk — HIGH"

        recommendation = (
            f"Irrigation is recommended for the {crop} field because soil moisture is low, "
            f"recent/expected rainfall is limited, and the crop is at the "
            f"{stage.lower()} stage."
        )

        actions = [
            "Review the irrigation recommendation with a field technician.",
            "Inspect crop leaves and soil condition within 24 hours.",
            "Reassess soil moisture after irrigation or rainfall."
        ]

    else:
        field_status = "Field Condition — MONITOR"

        recommendation = (
            f"Immediate irrigation is not strongly indicated from the supplied evidence. "
            f"Continue monitoring the {crop} field and reassess after weather changes."
        )

        actions = [
            "Continue monitoring soil moisture.",
            "Inspect visible crop symptoms.",
            "Reassess after significant rainfall or moisture change."
        ]

    return {
        "field_status": field_status,
        "recommendation": recommendation,
        "confidence": "Medium",
        "crop_health": {
            "finding": "Preliminary visual screening should be treated as a possible stress indicator, not a diagnosis.",
            "confidence": "Medium"
        },
        "soil": {
            "finding": soil_status,
            "confidence": "High"
        },
        "weather": {
            "finding": weather_status,
            "confidence": "High"
        },
        "vision": {
            "observation": "No image was provided, so visual screening could not be performed.",
            "limitation": "Upload a crop image for preliminary visual screening."
        },
        "validation": {
            "issues": []
            if crop and stage and area > 0
            else ["Required field information is missing."]
        },
        "next_actions": actions
    }


def _gemini_client():
    try:
        from google import genai

        key = os.getenv("GEMINI_API_KEY")

        if not key:
            return None

        return genai.Client(api_key=key)

    except Exception as e:
        print("Gemini client error:", e)
        return None


def _parse_json(text):
    # Remove markdown code fences if Gemini adds them
    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text).strip()

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object returned")

    json_text = text[start:end + 1]

    return json.loads(json_text)


def analyze_field(
    crop,
    stage,
    area,
    moisture,
    rainfall,
    forecast,
    temperature,
    notes,
    image_bytes=None,
    language="en",
):
    fallback = _fallback(
        crop,
        stage,
        moisture,
        rainfall,
        forecast,
        notes,
        area
    )

    client = _gemini_client()

    if not client:
        return fallback

    output_language = "Urdu in Urdu script" if language == "ur" else "English"
    prompt = f"""
You are the Coordinator for FIELDOPS AI,
an agriculture decision-support prototype.

Analyze this controlled field assessment and return ONLY valid JSON.
Write every user-facing string value in {output_language}. Keep JSON keys in English.

Inputs:

crop={crop}

growth_stage={stage}

field_area_acres={area}

soil_moisture={moisture}

recent_rainfall_mm={rainfall}

next_24h_rainfall_mm={forecast}

temperature_c={temperature}

notes={notes}

Rules:

- This is decision support, not autonomous control.
- Crop image findings are preliminary, never a definitive disease diagnosis.
- Do not invent missing evidence.
- Be transparent about uncertainty.
- Irrigation quantity is calculated separately by Python;
  do not invent a water quantity.

Required JSON:

{{
    "field_status": "...",
    "recommendation": "...",
    "confidence": "High|Medium|Low",

    "crop_health": {{
        "finding": "...",
        "confidence": "..."
    }},

    "soil": {{
        "finding": "...",
        "confidence": "..."
    }},

    "weather": {{
        "finding": "...",
        "confidence": "..."
    }},

    "vision": {{
        "observation": "...",
        "limitation": "..."
    }},

    "validation": {{
        "issues": []
    }},

    "next_actions": [
        "...",
        "...",
        "..."
    ]
}}
"""

    try:

        response = client.models.generate_content(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            ),
            contents=prompt
        )

        data = _parse_json(response.text)

        required_keys = [
            "field_status",
            "recommendation",
            "confidence",
            "crop_health",
            "soil",
            "weather",
            "vision",
            "validation",
            "next_actions"
        ]

        for key in required_keys:
            if key not in data:
                return fallback

        return data

    except Exception as e:
        print("Gemini analysis error:", e)
        return fallback