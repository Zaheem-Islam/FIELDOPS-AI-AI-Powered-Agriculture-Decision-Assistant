import base64
import html
import io

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from agents import analyze_field
from calculator import calculate_irrigation
from rag import retrieve_guidance
from report import build_report
from i18n import localize_irrigation, localize_result, translate_text, translate_ui

try:
    from gtts import gTTS
except ImportError:  # pragma: no cover
    gTTS = None


def voice_button(label, text, language):
    button_index = st.session_state.get("_voice_button_index", 0)
    st.session_state["_voice_button_index"] = button_index + 1
    help_text = "یہ متن سنیں" if language == "ur" else "Read this aloud"
    if not st.button(label, key=f"voice_button_{button_index}", help=help_text):
        return

    if gTTS is None:
        st.toast("Urdu speech service is unavailable.")
        return

    if language == "ur":
        text = translate_text(text, language)

    audio_buffer = io.BytesIO()
    try:
        gTTS(text=text, lang="ur" if language == "ur" else "en").write_to_fp(audio_buffer)
    except Exception:
        st.toast("Could not create speech. Check the app server's internet connection.")
        return

    audio_data = base64.b64encode(audio_buffer.getvalue()).decode("ascii")
    components.html(
        f'<audio autoplay src="data:audio/mpeg;base64,{audio_data}"></audio>',
        height=0,
    )


st.set_page_config(page_title="FIELDOPS AI", page_icon="🌾", layout="wide")
st.session_state["_voice_button_index"] = 0

header_title, header_language = st.columns([4, 1])
with header_language:
    language = st.selectbox(
        "Language / زبان",
        ["en", "ur"],
        index=0,
        format_func=lambda code: {"en": "English", "ur": "اردو"}[code],
    )

st.markdown("""
<style>
:root {
    color-scheme: dark;
    --canvas: #0b100e;
    --panel: #111916;
    --panel-raised: #17211c;
    --line: #28352e;
    --text: #edf3ef;
    --muted: #9aa99f;
    --green: #73c58c;
    --green-strong: #9be0ad;
}
.stApp {background:var(--canvas);color:var(--text)}
[data-testid="stHeader"] {background:rgba(11,16,14,.88)}
[data-testid="stSidebar"] {background:#101713;border-right:1px solid var(--line)}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.55rem}
.block-container {max-width:1440px;padding-top:1.5rem;padding-bottom:3rem}
h1,h2,h3 {color:var(--text);letter-spacing:0;font-weight:650}
[data-testid="stMarkdownContainer"] p,[data-testid="stCaptionContainer"] {color:var(--muted)}
[data-testid="stVerticalBlockBorderWrapper"] {background:var(--panel);border-color:var(--line);border-radius:14px;transition:border-color .18s ease,background .18s ease}
[data-testid="stVerticalBlockBorderWrapper"]:hover {border-color:#3c5948;background:#131d18}
[data-testid="stMetric"] {background:transparent;padding:.25rem .1rem}
[data-testid="stMetricLabel"] {color:var(--muted)}
[data-testid="stMetricValue"] {color:var(--text);font-weight:650}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"] [role="combobox"] {background:#0c120f;color:var(--text);border-color:var(--line);border-radius:9px}
[data-testid="stFileUploader"] section {background:#0c120f;border:1px dashed #3b5143;border-radius:10px}
.stButton > button {min-height:2.65rem;border:1px solid #34443a;border-radius:9px;background:#17211c;color:var(--text);transition:background .18s ease,border-color .18s ease,transform .18s ease}
.stButton > button:hover {border-color:var(--green);background:#1d2b22;color:white;transform:translateY(-1px)}
[data-testid="stBaseButton-primary"] {background:#3e9b5a!important;border-color:#3e9b5a!important;color:#07120a!important;font-weight:700!important}
[data-testid="stBaseButton-primary"]:hover {background:#51b56e!important;border-color:#51b56e!important}
[data-testid="stAlert"],[data-testid="stStatusWidget"] {border-radius:10px}
[data-testid="stExpander"] {border-color:var(--line);border-radius:10px}
hr {border-color:var(--line)}
.brand-title {font-size:2rem;font-weight:750;line-height:1.3;color:var(--text);margin:.15rem 0}
.brand-subtitle {font-size:.98rem;line-height:1.65;color:var(--muted)}
.sidebar-brand {padding:.45rem 0 .7rem;border-bottom:1px solid var(--line);margin-bottom:.65rem}
.section-kicker {color:var(--green-strong);font-size:.82rem;font-weight:700;text-transform:uppercase}
.status-pill {display:inline-block;border:1px solid #435b49;background:#18241c;border-radius:999px;padding:.4rem .8rem;color:#c4e8ce;font-weight:650}
.status-pill.critical {border-color:#8f4942;background:#321d1b;color:#ffc0b6}
.status-pill.monitor {border-color:#8b7540;background:#302817;color:#f1dc9e}
@media (max-width: 760px) {
    .block-container {padding:1rem .8rem 2rem}
    .brand-title {font-size:1.6rem}
    [data-testid="stSidebar"] {min-width:0}
}
</style>
""", unsafe_allow_html=True)

if language == "ur":
    st.markdown("""
    <style>
    .stApp, .stApp button, .stApp input, .stApp textarea, .stApp label {
        font-family:'Noto Naskh Arabic','Noto Nastaliq Urdu','Segoe UI',Tahoma,sans-serif !important;
    }
    [data-testid="stMarkdownContainer"] {line-height:1.85}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {direction:rtl;text-align:right}
    [data-testid="stMetricLabel"] {direction:rtl;text-align:right}
    </style>
    """, unsafe_allow_html=True)

with header_title:
    title = "🌾 فیلڈ اسسٹنٹ" if language == "ur" else translate_ui("app_title", language)
    st.markdown(f'<div class="brand-title" dir="auto">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="brand-subtitle" dir="auto">{translate_ui("subtitle", language)}</div>', unsafe_allow_html=True)
st.divider()

with st.sidebar:
    brand_name = "فیلڈ اسسٹنٹ" if language == "ur" else "FIELDOPS AI"
    st.markdown(
        f'<div class="sidebar-brand"><div class="section-kicker">🌾 {brand_name}</div>'
        f'<div class="brand-subtitle">{translate_ui("subtitle", language)}</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("### 🌱 فیلڈ کی معلومات" if language == "ur" else "### 🌱 Field Information")

    crop_options = ["Wheat", "Rice", "Maize", "Cotton", "Other"]
    crop_labels = {"Wheat": "گندم", "Rice": "چاول", "Maize": "مکئی", "Cotton": "کپاس", "Other": "دیگر"}
    crop = st.selectbox(
        translate_ui("crop", language),
        crop_options,
        format_func=lambda value: crop_labels.get(value, value) if language == "ur" else value,
    )

    stage_options = ["Germination", "Vegetative", "Flowering", "Grain Filling", "Maturity"]
    stage_labels = {
        "Germination": "بیج کی اباد کاری", "Vegetative": "پودے کی نشوونما",
        "Flowering": "پھول آنا", "Grain Filling": "اناج بھرنا", "Maturity": "پختگی",
    }
    stage = st.selectbox(
        translate_ui("growth_stage", language),
        stage_options,
        format_func=lambda value: stage_labels.get(value, value) if language == "ur" else value,
    )

    area = st.number_input(translate_ui("field_area", language), min_value=0.1, value=2.0, step=0.1)
    moisture = st.number_input(translate_ui("soil_moisture", language), min_value=0.0, value=220.0, step=10.0)
    rainfall = st.number_input(translate_ui("recent_rainfall", language), min_value=0.0, value=3.0, step=1.0)
    forecast = st.number_input(translate_ui("expected_rainfall", language), min_value=0.0, value=2.0, step=1.0)
    temperature = st.number_input(translate_ui("temperature", language), min_value=-10.0, value=30.0, step=1.0)
    notes_default = "پتے کچھ مرجھائے ہوئے لگتے ہیں۔" if language == "ur" else "Leaves look slightly stressed."
    notes = st.text_area(translate_ui("field_notes", language), value=notes_default, key="field_notes")

    uploaded = st.file_uploader(translate_ui("upload_image", language), type=["jpg", "jpeg", "png"])

    if language == "ur":
        st.divider()
        st.caption("🔊 آواز")
        input_summary = (
            f"{translate_ui('crop', language)}: {crop_labels.get(crop, crop)}. "
            f"{translate_ui('growth_stage', language)}: {stage_labels.get(stage, stage)}. "
            f"{translate_ui('field_area', language)}: {area:g} ایکڑ. "
            f"{translate_ui('soil_moisture', language)}: {moisture:g} ملی میٹر. "
            f"{translate_ui('recent_rainfall', language)}: {rainfall:g} ملی میٹر. "
            f"{translate_ui('expected_rainfall', language)}: {forecast:g} ملی میٹر. "
            f"{translate_ui('temperature', language)}: {temperature:g} ڈگری سینٹی گریڈ. "
            f"{translate_ui('field_notes', language)}: {notes}"
        )
        voice_button("🔊 معلومات سنیں", input_summary, language)

st.subheader(translate_ui("evidence_input", language))
overview = st.columns(4)
overview_metrics = [
    ("🌾 " + translate_ui("field_area", language), f"{area:g} acres"),
    ("💧 " + translate_ui("soil_moisture", language), f"{moisture:g} mm"),
    ("🌧 " + translate_ui("recent_rainfall", language), f"{rainfall:g} mm"),
    ("🌡 " + translate_ui("temperature", language), f"{temperature:g} °C"),
]
for column, (label, value) in zip(overview, overview_metrics):
    with column:
        with st.container(border=True):
            st.metric(label, value)

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption=translate_text("Uploaded crop image", language), width=320)

analyze = st.button(translate_ui("analyze_button", language), type="primary", use_container_width=True)
if analyze:
    st.session_state["_analysis_requested"] = True

if not st.session_state.get("_analysis_requested", False):
    st.info(translate_ui("enter_evidence", language))
    with st.expander(translate_ui("prototype_intro", language)):
        st.write(translate_ui("prototype_text", language))
    st.stop()

image_bytes = uploaded.getvalue() if uploaded else None

with st.status(translate_ui("status_running", language), expanded=False) as status:
    st.write(translate_ui("task_router", language))
    st.write(translate_ui("farm_coordinator", language))
    result = analyze_field(
        crop=crop, stage=stage, area=area, moisture=moisture,
        rainfall=rainfall, forecast=forecast, temperature=temperature,
        notes=notes, image_bytes=image_bytes, language=language
    )
    result = localize_result(result, language)
    st.write(translate_ui("crop_health_agent", language))
    st.write(translate_ui("soil_agent", language))
    st.write(translate_ui("weather_agent", language))

    irrigation = localize_irrigation(
        calculate_irrigation(
            crop=crop, stage=stage, area=area,
            moisture=moisture, rainfall=rainfall, forecast=forecast
        ),
        language,
    )
    st.write(translate_ui("irrigation_tool", language))

    evidence = [translate_text(item, language) for item in retrieve_guidance(crop, stage, moisture, rainfall)]
    st.write(translate_ui("knowledge_agent", language))

    validation = result["validation"]
    st.write(translate_ui("validator", language))
    st.write(translate_ui("coordinator", language))
    status.update(label=translate_ui("assessment_complete", language), state="complete")

st.divider()

summary_title, summary_voice = st.columns([5, 1])
with summary_title:
    st.subheader(translate_ui("field_assessment", language))
with summary_voice:
    if language == "ur":
        summary_text = (
            f"{translate_ui('field_status', language)}: {result['field_status']}. "
            f"{translate_ui('irrigation', language)}: {irrigation['recommendation']}. "
            f"{translate_ui('estimated_water', language)}: {irrigation['liters']:,.0f} litres. "
            f"{translate_ui('confidence', language)}: {result['confidence']}"
        )
        voice_button("🔊 جائزہ سنیں", summary_text, language)

status_columns = st.columns(4)
field_status = str(result["field_status"])
status_class = "critical" if "HIGH" in field_status.upper() or "بہت زیادہ" in field_status else "monitor" if "MONITOR" in field_status.upper() or "نگرانی" in field_status else ""
status_metrics = [
    ("🧭 " + translate_ui("field_status", language), field_status),
    ("💧 " + translate_ui("irrigation", language), irrigation["recommendation"]),
    ("🚿 " + translate_ui("estimated_water", language), f'{irrigation["liters"]:,.0f} L'),
    ("✓ " + translate_ui("confidence", language), result["confidence"]),
]
for column, (label, value) in zip(status_columns, status_metrics):
    with column:
        with st.container(border=True):
            if label.startswith("🧭"):
                st.caption(label)
                st.markdown(
                    f'<span class="status-pill {status_class}">{html.escape(value)}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.metric(label, value)
            if label.startswith("🚿"):
                st.caption(f"{translate_ui('method', language)}: {irrigation['method']}")

with st.container(border=True):
    recommendation_title, recommendation_voice = st.columns([5, 1])
    with recommendation_title:
        heading = "🤖 AI زرعی مشورے" if language == "ur" else "🤖 AI Recommendation"
        st.markdown(f"### {heading}")
    with recommendation_voice:
        if language == "ur":
            voice_button("🔊 مشورہ سنیں", result["recommendation"], language)
    st.markdown(result["recommendation"])
    human_review = translate_ui("human_review", language)
    st.caption(human_review)

st.subheader(translate_ui("specialist_findings", language))
cols = st.columns(3)
agents = [
    (("🌱 فصل کی صحت" if language == "ur" else "🌱 Crop Health Agent"), result["crop_health"]),
    (("💧 مٹی" if language == "ur" else "💧 Soil Agent"), result["soil"]),
    (("🌦️ موسم" if language == "ur" else "🌦️ Weather Agent"), result["weather"]),
]
for col, (name, data) in zip(cols, agents):
    with col:
        with st.container(border=True):
            agent_title, agent_voice = st.columns([3, 1])
            with agent_title:
                st.markdown(f"**{name}**")
            with agent_voice:
                if language == "ur":
                    voice_button("🔊 سنیں", f"{name}. {data['finding']}. اعتماد: {data['confidence']}", language)
            st.write(data["finding"])
            st.caption(f"{translate_ui('confidence', language)}: {data['confidence']}")

evidence_title, evidence_voice = st.columns([5, 1])
with evidence_title:
    st.subheader(translate_ui("rag_evidence", language))
with evidence_voice:
    if language == "ur":
        voice_button("🔊 شواہد سنیں", "۔ ".join(evidence), language)
for item in evidence:
    st.info(item)

validation_text = "۔ ".join(validation["issues"]) if validation["issues"] else translate_text(
    "✓ Required inputs available. ✓ No major contradictions detected.", language
)
validation_title, validation_voice = st.columns([5, 1])
with validation_title:
    st.subheader(translate_ui("validation", language))
with validation_voice:
    if language == "ur":
        voice_button("🔊 توثیق سنیں", validation_text, language)
if validation["issues"]:
    for issue in validation["issues"]:
        st.warning(issue)
else:
    st.success(validation_text)

vision_title, vision_voice = st.columns([5, 1])
with vision_title:
    st.subheader(translate_ui("preliminary_image", language))
with vision_voice:
    if language == "ur":
        vision_text = f"{result['vision']['observation']} {result['vision']['limitation']}"
        voice_button("🔊 تصویری جائزہ سنیں", vision_text, language)
st.write(result["vision"]["observation"])
st.caption(result["vision"]["limitation"])

actions_title, actions_voice = st.columns([5, 1])
with actions_title:
    st.subheader(translate_ui("recommended_actions", language))
with actions_voice:
    if language == "ur":
        voice_button("🔊 اقدامات سنیں", "۔ ".join(result["next_actions"]), language)
for action in result["next_actions"]:
    st.write(f"• {action}")

report = build_report(
    crop=crop_labels.get(crop, crop) if language == "ur" else crop,
    stage=stage_labels.get(stage, stage) if language == "ur" else stage,
    area=area, moisture=moisture,
    rainfall=rainfall, forecast=forecast, result=result,
    irrigation=irrigation, evidence=evidence, validation=validation,
    language=language,
)
st.download_button(
    translate_ui("download_report", language),
    data=report,
    file_name="fieldops_field_assessment.txt",
    mime="text/plain",
    use_container_width=True,
)

st.caption(translate_ui("disclaimer", language))
