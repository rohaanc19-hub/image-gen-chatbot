import os
import io
import random
import streamlit as st
from dotenv import load_dotenv

from prompt_styles import list_styles, build_final_prompt, DEFAULT_NEGATIVE_PROMPT
from api_client import generate_image, ImageGenerationError

load_dotenv()

try:
    if "HF_API_TOKEN" in st.secrets:
        os.environ["HF_API_TOKEN"] = st.secrets["HF_API_TOKEN"]
except Exception:
    pass

st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c1d 0%, #1a1430 50%, #0f0c1d 100%);
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff6ec4, #7873f5, #4adede);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        color: #a9a4c0;
        font-size: 1.05rem;
        margin-bottom: 1.8rem;
    }
    .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid #3a3357 !important;
        background-color: #1c1832 !important;
        color: #f0eefa !important;
        padding: 0.7rem 1rem !important;
    }
    .stTextInput input:focus {
        border: 1px solid #7873f5 !important;
        box-shadow: 0 0 0 2px rgba(120,115,245,0.25) !important;
    }
    div[role="radiogroup"] label {
        background: #1c1832;
        border: 1px solid #3a3357;
        border-radius: 20px;
        padding: 6px 16px;
        margin-right: 6px;
        transition: all 0.15s ease;
    }
    div[role="radiogroup"] label:hover {
        border-color: #7873f5;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #ff6ec4, #7873f5);
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2.2rem;
        font-weight: 700;
        font-size: 1.05rem;
        box-shadow: 0 4px 18px rgba(120,115,245,0.35);
        transition: transform 0.12s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
    }
    div.stButton > button[kind="secondary"] {
        border-radius: 10px;
        border: 1px solid #3a3357;
        background-color: #1c1832;
        color: #d8d4ef;
    }
    div[data-testid="stImage"] img {
        border-radius: 16px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.45);
    }
    h3 {
        color: #f0eefa !important;
    }
    .stCaption, p.caption {
        color: #9d97bd !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #15112a;
        border-right: 1px solid #2a2447;
    }
    .streamlit-expanderHeader {
        background-color: #1c1832 !important;
        border-radius: 10px !important;
        color: #d8d4ef !important;
    }
    hr {
        border-color: #2a2447 !important;
    }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

RANDOM_PROMPTS = [
    "A futuristic Indian city at night",
    "A dragon reading a newspaper in a cafe",
    "An astronaut tending a rooftop garden on Mars",
    "A cozy library inside a giant tree",
    "A robot street vendor selling chai in Mumbai",
]

STYLE_EMOJIS = {
    "Realistic": "📷",
    "Anime": "🌸",
    "Cyberpunk": "🌆",
    "Watercolor": "🎨",
    "3D Render": "🧊",
    "Sketch": "✏️",
}


def image_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


st.markdown('<div class="hero-title">🎨 AI Image Generation Chatbot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Describe anything. Pick a vibe. Watch it come to life, powered by the Hugging Face Inference API.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Generation Settings")
    num_images = st.slider("Number of images", 1, 4, 1)
    negative_prompt = st.text_input("Negative prompt (optional)", value="", placeholder=DEFAULT_NEGATIVE_PROMPT)
    if st.button("Surprise me with a prompt", use_container_width=True):
        st.session_state["prompt_input"] = random.choice(RANDOM_PROMPTS)

    st.markdown("---")
    st.markdown("### Session stats")
    st.metric("Images generated", sum(len(h["images"]) for h in st.session_state.history))
    st.metric("Prompts tried", len(st.session_state.history))

col_input, col_style = st.columns([3, 2])

with col_input:
    prompt = st.text_input("Describe the image you want to generate", key="prompt_input", placeholder="e.g. A futuristic Indian city at night")

with col_style:
    style = st.radio("Choose a style", list_styles(), horizontal=True, label_visibility="visible")

generate_clicked = st.button("Generate", type="primary")

if generate_clicked:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        final_prompt = build_final_prompt(prompt, style)
        neg_prompt = negative_prompt.strip() or DEFAULT_NEGATIVE_PROMPT

        with st.spinner("Conjuring your image..."):
            try:
                images = generate_image(final_prompt, negative_prompt=neg_prompt, num_images=num_images)
                st.session_state.history.insert(0, {
                    "prompt": prompt,
                    "style": style,
                    "final_prompt": final_prompt,
                    "images": images,
                })
                st.toast("Image generated!", icon="🎉")
            except ImageGenerationError as e:
                st.error(str(e))

if st.session_state.history:
    latest = st.session_state.history[0]
    st.markdown("### Result")
    st.caption("Final prompt sent to API: " + latest["final_prompt"])

    cols = st.columns(len(latest["images"]))
    for i, img in enumerate(latest["images"]):
        with cols[i]:
            st.image(img, use_container_width=True)
            st.download_button("Download", data=image_to_bytes(img), file_name="generated_image_" + str(i) + ".png", mime="image/png", key="dl_" + str(i), use_container_width=True)

    st.markdown("---")
    st.markdown("### Prompt History")

    if len(st.session_state.history) <= 1:
        st.caption("Your past generations will show up here.")
    else:
        for idx, item in enumerate(st.session_state.history[1:]):
            emoji = STYLE_EMOJIS.get(item["style"], "🎨")
            with st.expander(emoji + "  " + item["style"] + " - " + item["prompt"]):
                st.caption("Final prompt: " + item["final_prompt"])
                hist_cols = st.columns(len(item["images"]))
                for j, img in enumerate(item["images"]):
                    with hist_cols[j]:
                        st.image(img, use_container_width=True)
