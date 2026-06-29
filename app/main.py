"""
DermAssist-AI — Streamlit entry point
Run: streamlit run app/main.py
"""
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.inference import predict_image
from utils.gradcam import generate_gradcam

CLASSES = ["Acne", "Eczema", "Melanoma", "Psoriasis"]

st.set_page_config(page_title="DermAssist-AI", page_icon="🔬", layout="centered")
st.title("🔬 DermAssist-AI")
st.subheader("Explainable Skin Condition Classifier")

uploaded = st.file_uploader("Upload a skin lesion image", type=["jpg", "jpeg", "png"])

if uploaded:
    st.image(uploaded, caption="Uploaded Image", use_container_width=True)
    with st.spinner("Analysing…"):
        label, confidence, probs = predict_image(uploaded)
        heatmap = generate_gradcam(uploaded)

    st.success(f"**Prediction:** {label}  —  {confidence:.1%} confidence")

    st.bar_chart({cls: float(p) for cls, p in zip(CLASSES, probs)})

    if heatmap is not None:
        st.subheader("Grad-CAM Heatmap (suspicious regions)")
        st.image(heatmap, use_container_width=True)

    st.info(
        "⚠️ This tool is for educational screening only. "
        "Always consult a certified dermatologist for diagnosis."
    )
