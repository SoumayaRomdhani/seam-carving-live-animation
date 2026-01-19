import streamlit as st
import numpy as np
from PIL import Image
import io
import time
import cv2
import base64

from seam_carving import energy_map, carve_vertical_generator, carve_horizontal_generator

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Seam Carving Animation", layout="wide")


# ----------------------------
# FIXED DEFAULTS (hidden)
# ----------------------------
DEFAULT_MAX_SHOW_WIDTH = 500
DEFAULT_SPEED_MS = 55
DEFAULT_UPDATE_EVERY = 1
DEFAULT_SPEED_MODE = True
DEFAULT_MAX_INPUT_WIDTH = 600


# ----------------------------
# TEXTS (exactly as you wanted)
# ----------------------------
TITLE_CONTENT = "Content-aware resized image."
DESC_CONTENT = "This is the result of resizing the image using seam carving."

TITLE_ORIGINAL = "Original image."
DESC_ORIGINAL = "This is the original image, shown for comparison purposes."

TITLE_ENERGY = "Energy."
DESC_ENERGY = (
    "This is a measure of pixel importance; a pixel’s importance is determined by the contrast with its neighboring pixels. "
    "The white seam is a vertical path that traverses the least important pixels. On each iteration of the algorithm, this seam is removed."
)

TITLE_NAIVE = "Resized image."
DESC_NAIVE = (
    "This is the result of the browser resizing the image without regard to the image content. "
    "This is shown for comparison purposes."
)


# ----------------------------
# CRAZY PREMIUM LIGHT DESIGN (NO SIDEBAR)
# ----------------------------
st.markdown(
    """
<style>
/* Background */
.stApp{
    background: radial-gradient(1200px circle at 20% 10%, #eef4ff 0%, #ffffff 55%, #f8f1ff 100%);
}

/* remove menu/footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* spacing */
.block-container{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* ======= TOP TITLE (NO CARD) ======= */
.top-title{
    display:flex;
    align-items:center;
    gap:12px;
    margin: 4px 0 6px 0;
}
.top-title .icon{
    width:44px;height:44px;
    border-radius:16px;
    display:flex;
    align-items:center;
    justify-content:center;
    background: linear-gradient(135deg,#2563eb,#7c3aed,#ec4899);
    box-shadow: 0 14px 30px rgba(0,0,0,0.10);
    color:white;
    font-size:20px;
    font-weight:950;
}
.top-title h1{
    margin:0;
    font-weight: 990;
    font-size: 2.55rem;
    letter-spacing: 0.2px;
    background: linear-gradient(90deg,#2563eb,#7c3aed,#ec4899);
    -webkit-background-clip:text;
    color: transparent;
}
.subtitle{
    margin: 0 0 14px 56px;
    opacity: 0.90;
    font-size: 1.22rem;
    line-height:1.55rem;
    font-weight: 650;
    color: #111;
}
.divider-line{
    height: 1px;
    width: 100%;
    margin: 12px 0 14px 0;
    background: linear-gradient(90deg, rgba(37,99,235,0.0), rgba(37,99,235,0.25), rgba(236,72,153,0.25), rgba(236,72,153,0.0));
}

/* ======= CONTROLS WOW CARD ======= */
.controls-wrap{
    border-radius: 22px;
    padding: 14px 14px;
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(0,0,0,0.06);
    box-shadow: 0 16px 34px rgba(0,0,0,0.07);
    backdrop-filter: blur(12px);
    margin-bottom: 12px;
}
.controls-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom: 10px;
}
.controls-head .left{
    font-weight: 980;
    font-size: 1.25rem;
    color: #111;
    display:flex;
    align-items:center;
    gap:10px;
}
.pill{
    padding: 7px 12px;
    border-radius: 999px;
    border: 1px solid rgba(0,0,0,0.07);
    background: rgba(245,248,255,0.9);
    font-weight: 900;
    font-size: 1.00rem;
    color:#111;
}

/* labels under each widget */
.field-label{
    font-weight: 980;
    font-size: 1.08rem;
    color: #111;
    margin-bottom: 7px;
    opacity: 0.92;
}

/* make widgets look premium */
div[data-testid="stFileUploader"],
div[data-testid="stSelectbox"],
div[data-testid="stSlider"]{
    border-radius: 18px !important;
    background: rgba(255,255,255,0.88) !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
    padding: 10px 12px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
}

/* Bigger widget text */
div[data-testid="stSelectbox"] div,
div[data-testid="stSlider"]{
    font-size: 1.08rem !important;
    font-weight: 750 !important;
}

/* file uploader button */
div[data-testid="stFileUploader"] button{
    border-radius: 14px !important;
    font-weight: 950 !important;
    font-size: 1.05rem !important;
}

/* slider knob look */
div[data-testid="stSlider"] [role="slider"]{
    transform: scale(1.10);
}

/* ======= BUTTONS (WOW) ======= */
div.stButton > button{
    width: 100%;
    border-radius: 18px;
    border: 1px solid rgba(0,0,0,0.10);

    color: #ffffff !important;
    font-weight: 990 !important;
    font-size: 1.25rem !important;
    padding: 0.95rem 1.05rem;

    background: linear-gradient(135deg,#2563eb,#7c3aed,#ec4899);
    box-shadow: 0 16px 30px rgba(37,99,235,0.22);
    transition: 0.18s ease;
}
div.stButton > button:hover{
    transform: translateY(-2px);
    box-shadow: 0 22px 42px rgba(37,99,235,0.28);
    filter: brightness(1.06);
}
div.stButton > button:active{
    transform: translateY(0px) scale(0.99);
}

/* description box */
.desc-box{
    background:#f6f9ff;
    border:1px solid #cfd8ea;
    border-top:0px;
    padding:16px 16px;
    border-radius: 0 0 12px 12px;
    font-size:18px;
    line-height:1.70rem;
}
.desc-title{
    font-weight:990;
    color:#111;
}
.desc-text{
    color:#111;
    font-weight:650;
}

/* images rounded top */
img{
    border-radius: 12px 12px 0 0 !important;
}

/* status chip bigger */
.kchip{
    margin: 10px 0 16px 0;
    padding: 16px 18px;
    border-radius: 18px;
    background: rgba(255,255,255,0.96);
    border: 1px solid rgba(0,0,0,0.10);
    box-shadow: 0 12px 22px rgba(0,0,0,0.08);
    font-weight: 990;
    font-size: 1.45rem;
    color: #111;
}

/* ==========================================================
    FOCUS PANELS (Original + Naive)
   ========================================================== */
.panel-focus{
    border-radius: 18px;
    padding: 12px;
    backdrop-filter: blur(14px);
    background: rgba(255,255,255,0.55);
    box-shadow: 0 18px 45px rgba(0,0,0,0.08);
}

/* Original = blue focus */
.panel-focus.blue{
    border: 1px solid rgba(37,99,235,0.25);
    box-shadow: 0 18px 48px rgba(37,99,235,0.12);
}
.panel-focus.blue .focus-badge{
    background: rgba(37,99,235,0.12);
    border: 1px solid rgba(37,99,235,0.22);
    color: #2563eb;
}

/* Naive = pink focus */
.panel-focus.pink{
    border: 1px solid rgba(236,72,153,0.22);
    box-shadow: 0 18px 48px rgba(236,72,153,0.10);
}
.panel-focus.pink .focus-badge{
    background: rgba(236,72,153,0.10);
    border: 1px solid rgba(236,72,153,0.20);
    color: #ec4899;
}

.focus-badge{
    display:inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    font-weight: 950;
    font-size: 0.95rem;
    margin: 0 0 10px 0;
}

/* make focus title colored + stronger */
.panel-focus.blue .desc-title{ color:#2563eb; }
.panel-focus.pink .desc-title{ color:#ec4899; }

/* slightly tinted desc background inside focus */
.panel-focus.blue .desc-box{
    background: rgba(240,247,255,0.95);
    border-color: rgba(37,99,235,0.18);
}
.panel-focus.pink .desc-box{
    background: rgba(255,242,250,0.95);
    border-color: rgba(236,72,153,0.16);
}
</style>
""",
    unsafe_allow_html=True
)


# ----------------------------
# HELPERS
# ----------------------------
def normalize_energy(e: np.ndarray) -> np.ndarray:
    return (255 * e / (e.max() + 1e-9)).astype(np.uint8)


def overlay_white_seam_on_energy(e_gray_u8: np.ndarray, seam_img_rgb: np.ndarray) -> np.ndarray:
    energy_rgb = cv2.cvtColor(e_gray_u8, cv2.COLOR_GRAY2RGB)
    red_mask = (
        (seam_img_rgb[:, :, 0] == 255) &
        (seam_img_rgb[:, :, 1] == 0) &
        (seam_img_rgb[:, :, 2] == 0)
    )
    energy_rgb[red_mask] = [255, 255, 255]
    return energy_rgb


def to_base64_png(image_array: np.ndarray) -> str:
    """Convert numpy image to base64 PNG (for focus panels)."""
    pil_img = Image.fromarray(image_array)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def show_panel(placeholder, image_array, title, desc, width, focus=False, theme="blue", badge_text="KEY VIEW"):
    """
    focus=False -> normal panel
    focus=True  -> highlighted panel (glass + soft color + colored title)
    """
    placeholder.empty()
    with placeholder.container():
        if focus:
            b64 = to_base64_png(image_array)
            st.markdown(
                f"""
                <div class="panel-focus {theme}">
                    <div class="focus-badge">{badge_text}</div>
                    <img src="data:image/png;base64,{b64}"
                         style="width:{width}px; max-width:100%; display:block; border-radius:12px 12px 0 0;" />
                    <div class="desc-box">
                      <span class="desc-title">{title}</span>
                      <span class="desc-text"> {desc}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.image(image_array, width=width)
            st.markdown(
                f"""
                <div class="desc-box">
                  <span class="desc-title">{title}</span>
                  <span class="desc-text"> {desc}</span>
                </div>
                """,
                unsafe_allow_html=True
            )


# ----------------------------
# TOP TITLE (NO FRAME)
# ----------------------------
st.markdown(
    """
<div class="top-title">
  <div class="icon"></div>
  <h1>Live Seam Carving Animation</h1>
</div>
<div class="subtitle">
  Upload an image → choose direction → set <b>k seams</b> → press Play to watch seam carving step-by-step.
</div>
<div class="divider-line"></div>
""",
    unsafe_allow_html=True
)


# ----------------------------
# CONTROLS ON MAIN PAGE (WOW)
# ----------------------------
st.markdown('<div class="controls-wrap">', unsafe_allow_html=True)
st.markdown(
    """
<div class="controls-head">
  <div class="left"> Controls <span class="pill">Fast Mode </span></div>
  <div class="pill">Default: Horizontal • k=100</div>
</div>
""",
    unsafe_allow_html=True
)

c1, c2, c3, c4, c5 = st.columns([2.2, 1.3, 2.6, 1.0, 1.0])

with c1:
    st.markdown('<div class="field-label">Upload image</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

with c2:
    st.markdown('<div class="field-label">Direction</div>', unsafe_allow_html=True)
    direction = st.selectbox("", ["Vertical", "Horizontal"], index=1, label_visibility="collapsed")

play = False
reset = False
k = 50

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    img_np = np.array(img)

    H, W = img_np.shape[:2]
    if DEFAULT_SPEED_MODE and W > DEFAULT_MAX_INPUT_WIDTH:
        scale = DEFAULT_MAX_INPUT_WIDTH / W
        img_np = cv2.resize(img_np, (int(W * scale), int(H * scale)), interpolation=cv2.INTER_AREA)

    H, W = img_np.shape[:2]
    max_k = (W - 5) if direction == "Vertical" else (H - 5)
    max_k = max(1, max_k)

    default_k = min(100, min(300, max_k))

    with c3:
        st.markdown('<div class="field-label">k seams to remove</div>', unsafe_allow_html=True)
        k = st.slider("", 1, min(300, max_k), default_k, label_visibility="collapsed")

    with c4:
        st.markdown('<div class="field-label">&nbsp;</div>', unsafe_allow_html=True)
        play = st.button("▶ Play", use_container_width=True)

    with c5:
        st.markdown('<div class="field-label">&nbsp;</div>', unsafe_allow_html=True)
        reset = st.button("⟲ Reset", use_container_width=True)
else:
    with c3:
        st.markdown('<div class="field-label">k seams to remove</div>', unsafe_allow_html=True)
        st.slider("", 1, 10, 5, disabled=True, label_visibility="collapsed")
    with c4:
        st.markdown('<div class="field-label">&nbsp;</div>', unsafe_allow_html=True)
        st.button("▶ Play", disabled=True, use_container_width=True)
    with c5:
        st.markdown('<div class="field-label">&nbsp;</div>', unsafe_allow_html=True)
        st.button("⟲ Reset", disabled=True, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------
# MAIN ANIMATION (DIRECTLY)
# ----------------------------
if uploaded:
    if "cur_img" not in st.session_state or reset:
        st.session_state.cur_img = img_np.copy()

    original = img_np.copy()
    cur = st.session_state.cur_img.copy()

    max_show_width = DEFAULT_MAX_SHOW_WIDTH
    speed_ms = DEFAULT_SPEED_MS
    update_every = DEFAULT_UPDATE_EVERY

    vis_scale = max_show_width / original.shape[1]

    status = st.empty()

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    ph_original = row1_col1.empty()
    ph_naive = row1_col2.empty()
    ph_content = row2_col1.empty()
    ph_energy = row2_col2.empty()

    naive0 = cv2.resize(original, (cur.shape[1], cur.shape[0]), interpolation=cv2.INTER_AREA)
    e0 = normalize_energy(energy_map(cur))

    #  focus ONLY for Original + Naive
    show_panel(ph_original, original, TITLE_ORIGINAL, DESC_ORIGINAL, width=int(original.shape[1] * vis_scale),
               focus=True, theme="blue", badge_text="ORIGINAL (START)")

    show_panel(ph_naive, naive0, TITLE_NAIVE, DESC_NAIVE, width=int(cur.shape[1] * vis_scale),
               focus=True, theme="pink", badge_text="Resized (FINAL)")

    show_panel(ph_content, cur, TITLE_CONTENT, DESC_CONTENT, width=int(cur.shape[1] * vis_scale))
    show_panel(ph_energy, e0, TITLE_ENERGY, DESC_ENERGY, width=int(cur.shape[1] * vis_scale))

    if play:
        progress = st.progress(0)

        if direction == "Vertical":
            gen = carve_vertical_generator(cur, k)
        else:
            gen = carve_horizontal_generator(cur, k)

        final_img = cur.copy()

        for step, cur_img, e, seam_img in gen:
            if (step % update_every != 0) and (step != k):
                continue

            naive = cv2.resize(original, (cur_img.shape[1], cur_img.shape[0]), interpolation=cv2.INTER_AREA)

            e_norm = normalize_energy(e)
            e_with_seam = overlay_white_seam_on_energy(e_norm, seam_img)

            progress.progress(int(step / k * 100))
            status.markdown(
                f'<div class="kchip"> k = {step}/{k}  |  Current size = {cur_img.shape[1]} × {cur_img.shape[0]}</div>',
                unsafe_allow_html=True
            )

            #  focus ONLY for Original + Naive during animation too
            show_panel(ph_original, original, TITLE_ORIGINAL, DESC_ORIGINAL, width=int(original.shape[1] * vis_scale),
                       focus=True, theme="blue", badge_text="ORIGINAL (START)")

            show_panel(ph_naive, naive, TITLE_NAIVE, DESC_NAIVE, width=int(cur_img.shape[1] * vis_scale),
                       focus=True, theme="pink", badge_text="NAIVE (FINAL)")

            show_panel(ph_content, seam_img, TITLE_CONTENT, DESC_CONTENT, width=int(seam_img.shape[1] * vis_scale))
            show_panel(ph_energy, e_with_seam, TITLE_ENERGY, DESC_ENERGY, width=int(seam_img.shape[1] * vis_scale))

            if speed_ms > 0:
                time.sleep(speed_ms / 1000)

            final_img = cur_img

        st.session_state.cur_img = final_img.copy()
        st.success(" Animation finished!")

        out_pil = Image.fromarray(final_img)
        buf = io.BytesIO()
        out_pil.save(buf, format="PNG")

        st.download_button(
            "⬇ Download final image (PNG)",
            data=buf.getvalue(),
            file_name="resized_seam_carving.png",
            mime="image/png"
        )
