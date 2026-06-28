"""
AlgoPrep-MK2 | Nabamita Artisan Technology
Production-ready image processor for AlgoLaser MK2 / AlgoOS
Version: 2.0.0 — Smart Background Isolation Engine
"""

import streamlit as st
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import cv2
import io

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AlgoPrep-MK2 | Nabamita Artisan Technology",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  :root {
    --bg-primary:#0D0E14;--bg-card:#13141C;--bg-elevated:#1A1B26;
    --accent-laser:#FF6B00;--accent-glow:#FF9A40;--accent-teal:#00C9B1;
    --text-primary:#E8E9F3;--text-muted:#6E7191;--border:#2A2B3D;
  }
  .stApp{background-color:var(--bg-primary);}
  section[data-testid="stSidebar"]{background-color:var(--bg-card)!important;border-right:1px solid var(--border);}
  .stSlider>div>div>div{background:var(--accent-laser)!important;}
  .stDownloadButton>button{
    background:linear-gradient(135deg,#FF6B00,#FF9A40)!important;color:white!important;
    border:none!important;border-radius:8px!important;font-weight:700!important;
    letter-spacing:.05em!important;padding:.6rem 1.4rem!important;width:100%;
  }
  .header-banner{
    background:linear-gradient(135deg,#0D0E14 0%,#1A0A00 50%,#0D0E14 100%);
    border:1px solid var(--border);border-left:4px solid var(--accent-laser);
    border-radius:12px;padding:18px 24px;margin-bottom:24px;
    display:flex;align-items:center;gap:16px;
  }
  .header-title{
    font-family:'SF Mono','Fira Code',monospace;font-size:1.6rem;font-weight:800;
    color:var(--accent-laser);letter-spacing:.04em;margin:0;
    text-shadow:0 0 20px rgba(255,107,0,.4);
  }
  .header-sub{font-size:.78rem;color:var(--text-muted);letter-spacing:.12em;text-transform:uppercase;margin:0;}
  .stats-bar{display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;}
  .stat-chip{
    background:var(--bg-elevated);border:1px solid var(--border);border-radius:20px;
    padding:5px 14px;font-size:.74rem;color:var(--text-muted);font-family:'SF Mono',monospace;
  }
  .stat-chip span{color:var(--accent-teal);font-weight:700;}
  .panel-label{
    font-family:'SF Mono',monospace;font-size:.7rem;letter-spacing:.15em;
    text-transform:uppercase;color:var(--text-muted);border-bottom:1px solid var(--border);
    padding-bottom:8px;margin-bottom:12px;
  }
  .panel-label.laser{color:var(--accent-teal);}
  .sidebar-section{
    font-family:'SF Mono',monospace;font-size:.65rem;letter-spacing:.2em;
    text-transform:uppercase;color:var(--accent-laser);margin:18px 0 8px 0;
    border-top:1px solid var(--border);padding-top:14px;
  }
  .metric-card{
    background:var(--bg-elevated);border:1px solid var(--border);border-radius:10px;
    padding:12px 14px;text-align:center;
  }
  .metric-value{font-size:1.2rem;font-weight:800;color:var(--accent-glow);font-family:'SF Mono',monospace;}
  .metric-label{font-size:.65rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em;margin-top:2px;}
  .info-pill{
    background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.25);
    border-radius:8px;padding:10px 14px;font-size:.77rem;color:var(--accent-teal);
    margin-bottom:14px;line-height:1.5;
  }
  .warn-pill{
    background:rgba(255,107,0,.08);border:1px solid rgba(255,107,0,.25);
    border-radius:8px;padding:10px 14px;font-size:.77rem;color:var(--accent-glow);
    margin-bottom:14px;line-height:1.5;
  }
  .mode-card{
    background:var(--bg-elevated);border:1px solid var(--border);border-radius:10px;
    padding:12px;margin-bottom:8px;font-size:.75rem;color:var(--text-muted);line-height:1.6;
  }
  .mode-card b{color:var(--accent-glow);}
  #MainMenu,footer,header{visibility:hidden;}
  .block-container{padding-top:1.4rem;padding-bottom:2rem;}
</style>
""", unsafe_allow_html=True)


# ─── CORE PROCESSING ENGINE v2.0 ───────────────────────────────────────────────

def smart_bg_isolation(gray: np.ndarray, dark_threshold: int) -> np.ndarray:
    """
    Smart Background Isolation Engine.

    The root problem with a simple global threshold:
    When artwork is photographed against a textured background (brick, wood, fabric),
    mid-tone background pixels fall within the threshold range and get captured as
    "artwork" — producing the noisy blob output in the original screenshot.

    This engine separates artwork from background by targeting only TRUE-BLACK pixels
    (the actual laser-cut / painted artwork), then uses morphological ops to clean up
    compression artifacts.

    Returns: binary array where 255 = background (no burn), 0 = artwork (burn)
    """
    # Step 1: Light blur to kill JPEG compression block artifacts
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.5)

    # Step 2: Hard threshold — only pixels darker than dark_threshold survive
    # This is the KEY fix: artwork is 0-60, brick/wood bg is 80+
    _, binary = cv2.threshold(blurred, dark_threshold, 255, cv2.THRESH_BINARY_INV)
    # binary now: artwork = 255 (found), background = 0 (gone)

    # Step 3: Open (removes isolated noise pixels smaller than kernel)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN,  k, iterations=1)

    # Step 4: Close (fills micro-holes in strokes caused by reflections)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, k, iterations=1)

    # Invert to laser convention: BLACK = burn, WHITE = skip
    return cv2.bitwise_not(cleaned)


def standard_threshold(gray: np.ndarray, threshold: int) -> np.ndarray:
    """
    Standard global threshold — best for clean source images, AI art, logos on white bg.
    Returns laser-convention image: black = burn, white = skip.
    """
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.3)
    _, binary = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)
    return binary


def apply_clahe_enhance(gray: np.ndarray) -> np.ndarray:
    """CLAHE — for low-contrast source images before thresholding."""
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def apply_circular_mask(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    size = min(img.size)
    img = img.crop(((img.width - size) // 2, (img.height - size) // 2,
                    (img.width + size) // 2, (img.height + size) // 2))
    from PIL import ImageDraw
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    result = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    result.paste(img, mask=mask)
    return result


def resize_to_max_dimension(img: Image.Image, max_mm: float = 304.8, dpi: int = 300) -> Image.Image:
    max_px = int((max_mm / 25.4) * dpi)
    w, h = img.size
    if max(w, h) <= max_px:
        return img
    ratio = max_px / max(w, h)
    return img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)


def apply_denoising(arr: np.ndarray, strength: int) -> np.ndarray:
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (strength * 2 + 1, strength * 2 + 1))
    opened = cv2.morphologyEx(arr, cv2.MORPH_OPEN,  k)
    return    cv2.morphologyEx(opened, cv2.MORPH_CLOSE, k)


def get_stats(arr: np.ndarray, dpi: int) -> dict:
    total_rows = arr.shape[0]
    blank_rows = int(np.sum(np.all(arr == 255, axis=1)))
    fill_pct = round(np.sum(arr == 0) / arr.size * 100, 1)
    w_mm = (arr.shape[1] / dpi) * 25.4
    active_rows = total_rows - blank_rows
    row_time_sec = ((w_mm / 6000) * 60) + 0.1
    est_min = round(active_rows * row_time_sec / 60, 1)
    return {
        "total_rows": total_rows,
        "blank_rows": blank_rows,
        "pct_blank": round(blank_rows / total_rows * 100, 1) if total_rows else 0,
        "fill_pct": fill_pct,
        "est_min": est_min,
    }


def pil_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def flatten_for_display(img: Image.Image) -> Image.Image:
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert("RGB")


# ─── SIDEBAR ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 4px 0;'>
      <div style='font-family:"SF Mono",monospace;font-size:1.1rem;font-weight:800;
                  color:#FF6B00;letter-spacing:.06em;text-shadow:0 0 14px rgba(255,107,0,.5);'>
        ⬡ ALGOPREP-MK2
      </div>
      <div style='font-size:.62rem;color:#6E7191;letter-spacing:.18em;text-transform:uppercase;margin-top:2px;'>
        v2.0 · Smart Isolation Engine
      </div>
    </div>
    <hr style='border-color:#2A2B3D;margin:12px 0;'>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Source Image",
        type=["png", "jpg", "jpeg", "bmp", "webp", "tiff"],
    )

    # ── Processing Mode ──
    st.markdown("<div class='sidebar-section'>① Processing Mode</div>", unsafe_allow_html=True)

    mode = st.radio(
        "Select Mode",
        options=[
            "🎯 Smart Isolation  (photo on textured bg)",
            "⚡ Standard Threshold  (clean/digital art)",
        ],
        index=0,
        help="Smart Isolation = artwork photographed on a wall/table/fabric. "
             "Standard = logo/AI art already on white/solid background."
    )
    is_smart_mode = mode.startswith("🎯")

    if is_smart_mode:
        dark_threshold = st.slider(
            "Darkness Cutoff",
            min_value=30, max_value=120, value=65, step=1,
            help="Only pixels DARKER than this value are treated as artwork. "
                 "Lower = stricter (only very dark pixels). "
                 "Raise if fine strokes are missing. Lower if background noise appears."
        )
        st.markdown(f"""
        <div class='info-pill'>
          🎯 <b>Smart Mode active</b><br>
          Targeting pixels darker than <b>{dark_threshold}</b> as artwork.<br>
          Background texture is algorithmically suppressed.
        </div>""", unsafe_allow_html=True)
    else:
        std_threshold = st.slider(
            "Threshold",
            min_value=0, max_value=255, value=128, step=1,
            help="Pixels below threshold → Black (burn). Above → White (skip)."
        )
        clahe_boost = st.toggle("CLAHE Contrast Boost", value=False,
                                help="Adaptive histogram equalisation — helps low-contrast art.")

    # ── Transforms ──
    st.markdown("<div class='sidebar-section'>② Transforms</div>", unsafe_allow_html=True)
    circular_crop = st.toggle("⬤  Circular Crop (round blanks)", value=False)
    invert = st.toggle("Invert Black ↔ White", value=False,
                       help="ON = dark wood (burn background). OFF = light wood (burn artwork).")
    max_size_mm = st.selectbox(
        "Output Size",
        options=[304.8, 203.2, 152.4, 101.6],
        format_func=lambda x: f"{x:.1f} mm  ({x/25.4:.0f} in)",
        index=0,
    )
    dpi = st.selectbox("Output DPI", options=[300, 254, 200], index=0)

    # ── Denoise ──
    st.markdown("<div class='sidebar-section'>③ Final Denoise</div>", unsafe_allow_html=True)
    denoise_enabled = st.toggle("Enable Final Denoise", value=True)
    denoise_strength = st.select_slider(
        "Denoise Strength",
        options=["Light (1px)", "Medium (2px)", "Aggressive (3px)"],
        value="Light (1px)",
        disabled=not denoise_enabled,
    )
    denoise_map = {"Light (1px)": 1, "Medium (2px)": 2, "Aggressive (3px)": 3}

    st.markdown("<div class='sidebar-section'>④ Export</div>", unsafe_allow_html=True)


# ─── MAIN AREA ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class='header-banner'>
  <div style='font-size:2rem;'>🔥</div>
  <div>
    <p class='header-title'>ALGOPREP-MK2</p>
    <p class='header-sub'>Production Image Processor · Smart Isolation Engine v2.0 · Nabamita Artisan Technology</p>
  </div>
</div>
""", unsafe_allow_html=True)

if uploaded_file is None:
    st.markdown("""
    <div style='background:#13141C;border:2px dashed #2A2B3D;border-radius:16px;
                padding:60px 40px;text-align:center;margin-top:20px;'>
      <div style='font-size:3rem;margin-bottom:16px;'>📷</div>
      <div style='font-size:1.1rem;font-weight:700;color:#E8E9F3;margin-bottom:8px;'>
        Upload an image in the sidebar to begin
      </div>
      <div style='font-size:.82rem;color:#6E7191;line-height:1.8;'>
        <b style='color:#FF9A40;'>🎯 Smart Mode</b> — Photo of artwork on brick/wood/fabric wall<br>
        <b style='color:#00C9B1;'>⚡ Standard Mode</b> — Digital art, AI-generated, logo on white bg<br><br>
        Output: Pure B&W PNG · 300 DPI · AlgoOS skip-blank optimised
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── LOAD & PROCESS ────────────────────────────────────────────────────────────

original_img = Image.open(uploaded_file)
orig_w, orig_h = original_img.size

# Pipeline start
processed = original_img.copy()

# Step 1: Circular crop
if circular_crop:
    processed = apply_circular_mask(processed)

# Step 2: Resize
processed = resize_to_max_dimension(processed, max_mm=max_size_mm, dpi=dpi)

# Step 3: Convert to numpy for OpenCV processing
rgb_arr = np.array(processed.convert("RGB"))
gray_arr = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2GRAY)

# Step 4: Core processing — Smart or Standard
if is_smart_mode:
    result_arr = smart_bg_isolation(gray_arr, dark_threshold)
else:
    if clahe_boost:
        gray_arr = apply_clahe_enhance(gray_arr)
    result_arr = standard_threshold(gray_arr, std_threshold)

# Step 5: Invert
if invert:
    result_arr = cv2.bitwise_not(result_arr)

# Step 6: Final denoise
if denoise_enabled:
    result_arr = apply_denoising(result_arr, denoise_map[denoise_strength])

# Back to PIL
processed = Image.fromarray(result_arr, mode="L")

# ─── STATS ─────────────────────────────────────────────────────────────────────
stats = get_stats(result_arr, dpi)

st.markdown(f"""
<div class='stats-bar'>
  <div class='stat-chip'>Source: <span>{orig_w}×{orig_h}px</span></div>
  <div class='stat-chip'>Output: <span>{processed.width}×{processed.height}px</span></div>
  <div class='stat-chip'>Blank Lines: <span>{stats['pct_blank']}%</span></div>
  <div class='stat-chip'>Fill Density: <span>{stats['fill_pct']}%</span></div>
  <div class='stat-chip'>Est. Job Time: <span>~{stats['est_min']} min</span></div>
  <div class='stat-chip'>Mode: <span>{'Smart Isolation' if is_smart_mode else 'Standard'}</span></div>
</div>
""", unsafe_allow_html=True)

if stats['est_min'] > 25:
    st.markdown(f"""<div class='warn-pill'>
      ⚠️ Est. time <b>{stats['est_min']} min</b> — raise Darkness Cutoff or enable Aggressive denoise.
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""<div class='info-pill'>
      ✅ Est. time <b>{stats['est_min']} min</b> — AlgoOS will skip <b>{stats['blank_rows']:,}</b> rows
      ({stats['pct_blank']}%), maximising throughput via 'Skip Blank Lines'.
    </div>""", unsafe_allow_html=True)

# ─── PREVIEW ───────────────────────────────────────────────────────────────────
col_orig, col_proc = st.columns(2, gap="medium")
with col_orig:
    st.markdown("<div class='panel-label'>▸ ORIGINAL SOURCE</div>", unsafe_allow_html=True)
    st.image(flatten_for_display(original_img), use_container_width=True)
with col_proc:
    st.markdown("<div class='panel-label laser'>▸ LASER-READY OUTPUT</div>", unsafe_allow_html=True)
    st.image(processed, use_container_width=True, clamp=True)

# ─── METRICS ───────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4, gap="small")
for col, val, lbl in zip(
    [m1, m2, m3, m4],
    [f"{processed.width}px", f"{processed.height}px", f"{stats['pct_blank']}%", f"~{stats['est_min']}m"],
    ["Output Width", "Output Height", "Skip-able Rows", "Est. Job Time"]
):
    col.markdown(f"""<div class='metric-card'>
      <div class='metric-value'>{val}</div>
      <div class='metric-label'>{lbl}</div>
    </div>""", unsafe_allow_html=True)

# ─── DOWNLOAD ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
dl_col, info_col = st.columns([1, 2], gap="medium")
with dl_col:
    stem = uploaded_file.name.rsplit(".", 1)[0]
    st.download_button(
        label="⬇  Download Laser-Ready PNG",
        data=pil_to_bytes(processed),
        file_name=f"{stem}_AlgoPrep_MK2.png",
        mime="image/png",
    )
with info_col:
    st.markdown(f"""<div class='info-pill' style='margin:0;'>
      <b>AlgoOS Import Checklist:</b><br>
      1. Import PNG → Mode: <b>Image → Passthrough</b> (already processed)<br>
      2. Enable: <b>Skip Blank Lines</b> ✓<br>
      3. DPI: <b>{dpi}</b> · Speed: <b>6000–8000 mm/min</b> · Power: <b>75–85%</b>
    </div>""", unsafe_allow_html=True)

st.markdown("""
<div style='margin-top:40px;border-top:1px solid #2A2B3D;padding-top:16px;
            text-align:center;font-size:.68rem;color:#6E7191;letter-spacing:.08em;'>
  ALGOPREP-MK2 v2.0 · Nabamita Artisan Technology · Kolkata, West Bengal<br>
  Smart Isolation Engine · AlgoLaser MK2 / AlgoOS · TTS-55 Pro 5.5W compatible
</div>
""", unsafe_allow_html=True)
