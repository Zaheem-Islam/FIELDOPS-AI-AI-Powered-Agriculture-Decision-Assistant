import streamlit as st
from PIL import Image
from agents import analyze_field
from calculator import calculate_irrigation
from rag import retrieve_guidance
from report import build_report

st.set_page_config(page_title="FIELDOPS AI", page_icon="🌾", layout="wide")

st.markdown("""
<style>
.main-title {font-size:42px;font-weight:800;margin-bottom:0}
.subtitle {font-size:17px;color:#6b7280;margin-top:0}
.status-card {padding:18px;border-radius:14px;border:1px solid #e5e7eb;background:#ffffff}
.agent {padding:12px 15px;border-radius:10px;background:#f8fafc;border-left:4px solid #16a34a;margin:8px 0}
.small {color:#64748b;font-size:13px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌾 FIELDOPS AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Agriculture Decision Intelligence — Multimodal Multi-Agent Field Assistant</div>', unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("⚙️ Field Assessment")
    crop = st.selectbox("Crop", ["Wheat", "Rice", "Maize", "Cotton", "Other"])
    stage = st.selectbox("Growth Stage", ["Germination", "Vegetative", "Flowering", "Grain Filling", "Maturity"])
    area = st.number_input("Field Area (acres)", min_value=0.1, value=2.0, step=0.1)
    moisture = st.number_input("Soil Moisture", min_value=0.0, value=220.0, step=10.0)
    rainfall = st.number_input("Recent Rainfall (mm)", min_value=0.0, value=3.0, step=1.0)
    forecast = st.number_input("Expected Rainfall Next 24h (mm)", min_value=0.0, value=2.0, step=1.0)
    temperature = st.number_input("Temperature (°C)", min_value=-10.0, value=30.0, step=1.0)
    notes = st.text_area("Field Notes", value="Leaves look slightly stressed.")
    uploaded = st.file_uploader("📷 Upload Crop Image", type=["jpg","jpeg","png"])
    analyze = st.button("🔍 ANALYZE FIELD", type="primary", use_container_width=True)

st.subheader("📋 Evidence Input")
c1,c2,c3 = st.columns(3)
c1.metric("Soil Moisture", f"{moisture:g}")
c2.metric("Recent Rainfall", f"{rainfall:g} mm")
c3.metric("Field Area", f"{area:g} acres")

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded crop image", width=320)

if not analyze:
    st.info("Enter the field evidence in the sidebar and click **ANALYZE FIELD**.")
    st.markdown("### What this prototype demonstrates")
    st.write("Specialist agents analyze crop health, soil, weather and irrigation; RAG supplies controlled agriculture guidance; a deterministic calculator handles the water estimate; a validator checks the evidence before the coordinator creates the action plan.")
    st.stop()

image_bytes = uploaded.getvalue() if uploaded else None

with st.status("🤖 Running FIELDOPS AI agent workflow...", expanded=True) as status:
    st.write("✓ Task Router — agriculture workflow selected")
    st.write("✓ Farm Coordinator — task plan created")
    result = analyze_field(
        crop=crop, stage=stage, area=area, moisture=moisture,
        rainfall=rainfall, forecast=forecast, temperature=temperature,
        notes=notes, image_bytes=image_bytes
    )
    st.write("✓ Crop Health Agent — preliminary image screening")
    st.write("✓ Soil Agent — soil condition assessment")
    st.write("✓ Weather Agent — rainfall/weather assessment")

    irrigation = calculate_irrigation(
        crop=crop, stage=stage, area=area,
        moisture=moisture, rainfall=rainfall, forecast=forecast
    )
    st.write("✓ Irrigation Tool — deterministic calculation")

    evidence = retrieve_guidance(crop, stage, moisture, rainfall)
    st.write("✓ Knowledge/RAG Agent — supporting guidance retrieved")

    validation = result["validation"]
    st.write("✓ Validator — missing-data and contradiction checks")
    st.write("✓ Coordinator — final recommendation synthesized")
    status.update(label="✅ Assessment complete", state="complete")

st.divider()

st.subheader("🚨 Field Assessment")
a,b = st.columns([1,1])
with a:
    st.markdown('<div class="status-card">', unsafe_allow_html=True)
    st.metric("Field Status", result["field_status"])
    st.metric("Irrigation", irrigation["recommendation"])
    st.metric("Estimated Water", f'{irrigation["liters"]:,.0f} L')
    st.markdown(f'<div class="small">Method: {irrigation["method"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with b:
    st.markdown('<div class="status-card">', unsafe_allow_html=True)
    st.write("### 🧠 Coordinator Recommendation")
    st.write(result["recommendation"])
    st.write(f"**Confidence:** {result['confidence']}")
    st.write("**Human review:** Required before consequential field action.")
    st.markdown('</div>', unsafe_allow_html=True)

st.subheader("🤖 Specialist Agent Findings")
cols = st.columns(3)
agents = [
    ("🌱 Crop Health Agent", result["crop_health"]),
    ("💧 Soil Agent", result["soil"]),
    ("🌦️ Weather Agent", result["weather"]),
]
for col,(name,data) in zip(cols,agents):
    with col:
        st.markdown('<div class="agent">', unsafe_allow_html=True)
        st.write(f"**{name}**")
        st.write(data["finding"])
        st.caption(f"Confidence: {data['confidence']}")
        st.markdown('</div>', unsafe_allow_html=True)

st.subheader("📚 Evidence / RAG")
for item in evidence:
    st.info(item)

st.subheader("🛡️ Validation")
if validation["issues"]:
    for issue in validation["issues"]:
        st.warning(issue)
else:
    st.success("✓ Required inputs available. ✓ No major contradictions detected.")

st.subheader("👁️ Preliminary Image Screening")
st.write(result["vision"]["observation"])
st.caption(result["vision"]["limitation"])

st.subheader("➡️ Recommended Next Actions")
for action in result["next_actions"]:
    st.write(f"• {action}")

report = build_report(
    crop=crop, stage=stage, area=area, moisture=moisture,
    rainfall=rainfall, forecast=forecast, result=result,
    irrigation=irrigation, evidence=evidence, validation=validation
)
st.download_button(
    "📄 Download Field Assessment Report",
    data=report,
    file_name="fieldops_field_assessment.txt",
    mime="text/plain",
    use_container_width=True
)

st.caption("FIELDOPS AI is decision support, not autonomous farm control. Crop-health observations are preliminary and require field verification.")
