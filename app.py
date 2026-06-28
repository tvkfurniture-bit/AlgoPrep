"""
AlgoPrep-MK2 | Nabamita Artisan Technology
Production-ready image processor for AlgoLaser MK2 / AlgoOS
Version: 1.0.0
"""

import streamlit as st
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import cv2
import io
import math

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AlgoPrep-MK2 | Nabamita Artisan Technology",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Core palette */
  :root {
    --bg-primary:   #0D0E14;
    --bg-card:      #13141C;
    --bg-elevated:  #1A1B26;
    --accent-laser: #FF6B00;
    --accent-glow:  #FF9A40;
    --accent-teal:  #00C9B1;
    --text-primary: #E8E9F3;
    --text-muted:   #6E7191;
    --border:       #2A2B3D;
  }

  /* Streamlit overrides */
  .stApp { background-color: var(--bg-primary); }
  section[data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border);
  }
  .stSlider > div > div > div { background: var(--accent-laser) !important; }
  .stDownloadButton > button {
    background: linear-gradient(135deg, #FF6B00, #FF9A40) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.4rem !important;
    width: 100%;
    transition: opacity 0.2s;
  }
  .stDownloadButton > button:hover { opacity: 0.88; }
  .stToggle label { color: var(--text-primary) !important; }
  
  /* Header banner */
  .header-banner {
    background: linear-gradient(135deg, #0D0E14 0%, #1A0A00 50%, #0D0E14 100%);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent-laser);
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .header-title {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--accent-laser);
    letter-spacing: 0.04em;
    margin: 0;
    text-shadow: 0 0 20px rgba(255,107,0,0.4);
  }
  .header-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0;
  }
  
  /* Stats bar */
  .stats-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }
  .stat-chip {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.74rem;
    color: var(--text-muted);
    font-family: 'SF Mono', monospace;
  }
  .stat-chip span { color: var(--accent-teal); font-weight: 700; }
  
  /* Panel labels */
  .panel-label {
    font-family: 'SF Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 12px;
  }
  .panel-label.laser { color: var(--accent-teal); }
  
  /* Sidebar section headers */
  .sidebar-section {
    font-family: 'SF Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent-laser);
    margin: 18px 0 8px 0;
    border-top: 1px solid var(--border);
    padding-top: 14px;
  }
  
  /* Metric cards */
  .metric-row {
    display: flex; gap: 10px; margin-bottom: 16px;
  }
  .metric-card {
    flex: 1;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
  }
  .metric-value {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--accent-glow);
    font-family: 'SF Mono', monospace;
  }
  .metric-label {
    font-size: 0.65rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 2px;
  }
  
  /* Warning/info pills */
  .info-pill {
    background: rgba(0, 201, 177, 0.08);
    border: 1px solid rgba(0, 201, 177, 0.25);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.77rem;
    color: var(--accent-teal);
    margin-bottom: 14px;
    line-height: 1.5;
  }
  .warn-pill {
    background: rgba(255, 107, 0, 0.08);
    border: 1px solid rgba(255, 107, 0, 0.25);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.77rem;
    color: var(--accent-glow);
    margin-bottom: 14px;
    line-height: 1.5;
  }
  
  /* Hide default Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)


# ─── Helper: Image Processing Functions ────────────────────────────────────────

def apply_circular_mask(img: Image.Image) -> Image.Image:
    """Crop image to a perfect circle with transparent background."""
    img = img.convert("RGBA")
    size = min(img.size)
    img = img.crop(((img.width - size) // 2,
                    (img.height - size) // 2,
                    (img.width + size) // 2,
                    (img.height + size) // 2))
    mask = Image.new("L", (size, size), 0)
    import PIL.ImageDraw as ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    result = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    result.paste(img, mask=mask)
    return result


def resize_to_max_dimension(img: Image.Image, max_mm: float = 304.8, dpi: int = 300) -> Image.Image:
    """Resize image so largest dimension = max_mm at the given DPI."""
    max_px = int((max_mm / 25.4) * dpi)
    w, h = img.size
    if max(w, h) <= max_px:
        return img
    if w >= h:
        new_w = max_px
        new_h = int(h * (max_px / w))
    else:
        new_h = max_px
        new_w = int(w * (max_px / h))
    return img.resize((new_w, new_h), Image.LANCZOS)


def apply_threshold(img: Image.Image, threshold: int) -> Image.Image:
    """Convert to pure B&W using threshold."""
    gray = img.convert("L")
    arr = np.array(gray)
    binary = np.where(arr >= threshold, 255, 0).astype(np.uint8)
    return Image.fromarray(binary, mode="L")


def apply_denoising(img: Image.Image, strength: int) -> Image.Image:
    """Remove stray pixels / AI dust using morphological ops."""
    arr = np.array(img.convert("L"))
    binary = (arr > 128).astype(np.uint8) * 255

    # Kernel size driven by strength (1=light, 2=medium, 3=aggressive)
    k = max(1, strength)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k * 2 + 1, k * 2 + 1))

    # Remove isolated noise pixels (open = erode then dilate)
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    # Fill tiny holes (close = dilate then erode)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)
    return Image.fromarray(closed, mode="L")


def count_blank_lines(img: Image.Image) -> dict:
    """Estimate % blank lines AlgoOS can skip."""
    arr = np.array(img.convert("L"))
    total_rows = arr.shape[0]
    blank_rows = np.sum(np.all(arr == 255, axis=1))
    pct = (blank_rows / total_rows) * 100 if total_rows else 0
    black_px = np.sum(arr == 0)
    total_px = arr.size
    return {
        "total_rows": total_rows,
        "blank_rows": int(blank_rows),
        "pct_blank": round(pct, 1),
        "fill_pct": round((black_px / total_px) * 100, 1),
    }


def estimate_engrave_time(img: Image.Image, speed_mm_min: int = 6000) -> float:
    """Rough time estimate in minutes for engraving at given speed."""
    stats = count_blank_lines(img)
    w_mm = (img.width / 300) * 25.4
    active_rows = stats["total_rows"] - stats["blank_rows"]
    # Each active row: travel width at speed + 0.1s overhead
    row_time_sec = ((w_mm / speed_mm_min) * 60) + 0.1
    total_sec = active_rows * row_time_sec
    return round(total_sec / 60, 1)


def pil_to_bytes(img: Image.Image, fmt="PNG") -> bytes:
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


def flatten_rgba_to_white(img: Image.Image) -> Image.Image:
    """Flatten any RGBA image onto a white background for display."""
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert("RGB")


# ─── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 4px 0;'>
      <div style='font-family:"SF Mono",monospace;font-size:1.1rem;
                  font-weight:800;color:#FF6B00;letter-spacing:0.06em;
                  text-shadow:0 0 14px rgba(255,107,0,0.5);'>
        ⬡ ALGOPREP-MK2
      </div>
      <div style='font-size:0.62rem;color:#6E7191;letter-spacing:0.18em;
                  text-transform:uppercase;margin-top:2px;'>
        Nabamita Artisan Technology
      </div>
    </div>
    <hr style='border-color:#2A2B3D;margin:12px 0;'>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Source Image",
        type=["png", "jpg", "jpeg", "bmp", "webp", "tiff"],
        help="Upload any raster image. JPG, PNG, WEBP all accepted."
    )

    # ── Pre-Process ──
    st.markdown("<div class='sidebar-section'>① Pre-Process</div>", unsafe_allow_html=True)

    circular_crop = st.toggle("⬤  Circular Crop (12-inch round blanks)", value=False)
    max_size_mm = st.selectbox(
        "Output Size (max dimension)",
        options=[304.8, 203.2, 152.4, 101.6],
        format_func=lambda x: f"{x} mm  ({x/25.4:.0f} inch)",
        index=0,
    )
    dpi = st.selectbox("Output DPI", options=[300, 254, 200], index=0)

    # ── Threshold ──
    st.markdown("<div class='sidebar-section'>② Threshold (B&W Conversion)</div>", unsafe_allow_html=True)
    threshold = st.slider(
        "Threshold",
        min_value=0, max_value=255, value=128, step=1,
        help="Pixels ≥ threshold → White (no burn). Pixels < threshold → Black (burn). "
             "Lower = more black. Higher = less black."
    )
    st.markdown(f"""
    <div class='info-pill'>
      🔥 Threshold: <b>{threshold}</b><br>
      {"◀ Dark — more area engraved" if threshold < 90 else ("▶ Light — less area engraved" if threshold > 180 else "⬤ Balanced")}
    </div>
    """, unsafe_allow_html=True)

    # ── Invert ──
    st.markdown("<div class='sidebar-section'>③ Invert</div>", unsafe_allow_html=True)
    invert = st.toggle(
        "Invert Black ↔ White",
        value=False,
        help="Toggle ON for dark woods (maple, cherry) where you engrave the background. "
             "Toggle OFF for light woods (birch, MDF)."
    )

    # ── Denoising ──
    st.markdown("<div class='sidebar-section'>④ Denoise (AI Dust Removal)</div>", unsafe_allow_html=True)
    denoise_enabled = st.toggle("Enable Denoising", value=True)
    denoise_strength = st.select_slider(
        "Denoise Strength",
        options=["Light (1px)", "Medium (2px)", "Aggressive (3px)"],
        value="Medium (2px)",
        disabled=not denoise_enabled,
    )
    denoise_map = {"Light (1px)": 1, "Medium (2px)": 2, "Aggressive (3px)": 3}

    # ── Export ──
    st.markdown("<div class='sidebar-section'>⑤ Export</div>", unsafe_allow_html=True)


# ─── Main Area ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class='header-banner'>
  <div style='font-size:2rem;'>🔥</div>
  <div>
    <p class='header-title'>ALGOPREP-MK2</p>
    <p class='header-sub'>Production Image Processor · AlgoLaser MK2 / AlgoOS · Nabamita Artisan Technology</p>
  </div>
</div>
""", unsafe_allow_html=True)

if uploaded_file is None:
    st.markdown("""
    <div style='
      background:#13141C;border:2px dashed #2A2B3D;border-radius:16px;
      padding:60px 40px;text-align:center;margin-top:20px;
    '>
      <div style='font-size:3rem;margin-bottom:16px;'>📷</div>
      <div style='font-size:1.1rem;font-weight:700;color:#E8E9F3;margin-bottom:8px;'>
        Upload an image in the sidebar to begin
      </div>
      <div style='font-size:0.82rem;color:#6E7191;line-height:1.7;'>
        Accepts PNG · JPG · WEBP · BMP · TIFF<br>
        Output: Pure B&W PNG · 300 DPI · AlgoOS skip-blank optimised<br>
        Target: 12-inch engraving in <b style='color:#FF9A40;'>under 20 minutes</b>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─── Load & Process ────────────────────────────────────────────────────────────

original_img = Image.open(uploaded_file)
orig_w, orig_h = original_img.size

# Pipeline
processed = original_img.copy()

# Step 1: Circular crop
if circular_crop:
    processed = apply_circular_mask(processed)

# Step 2: Resize
processed = resize_to_max_dimension(processed, max_mm=max_size_mm, dpi=dpi)

# Step 3: Threshold → pure B&W
processed = apply_threshold(processed, threshold)

# Step 4: Invert
if invert:
    processed = ImageOps.invert(processed.convert("L"))

# Step 5: Denoise
if denoise_enabled:
    processed = apply_denoising(processed, denoise_map[denoise_strength])

# Ensure final mode is "L"
processed = processed.convert("L")

# ─── Stats ─────────────────────────────────────────────────────────────────────
stats = count_blank_lines(processed)
est_time = estimate_engrave_time(processed, speed_mm_min=6000)

st.markdown(f"""
<div class='stats-bar'>
  <div class='stat-chip'>Source: <span>{orig_w}×{orig_h}px</span></div>
  <div class='stat-chip'>Output: <span>{processed.width}×{processed.height}px</span></div>
  <div class='stat-chip'>Blank Lines: <span>{stats['pct_blank']}%</span></div>
  <div class='stat-chip'>Fill Density: <span>{stats['fill_pct']}%</span></div>
  <div class='stat-chip'>Est. Engrave Time: <span>~{est_time} min</span></div>
</div>
""", unsafe_allow_html=True)

# Time warning
if est_time > 25:
    st.markdown(f"""
    <div class='warn-pill'>
      ⚠️ Estimated time <b>{est_time} min</b> — consider increasing threshold to reduce fill density,
      or enabling Aggressive denoising to remove stray pixels.
    </div>
    """, unsafe_allow_html=True)
elif est_time <= 20:
    st.markdown(f"""
    <div class='info-pill'>
      ✅ Estimated time <b>{est_time} min</b> — within target. 'Skip Blank Lines' in AlgoOS
      will skip <b>{stats['blank_rows']:,}</b> rows ({stats['pct_blank']}%), boosting throughput significantly.
    </div>
    """, unsafe_allow_html=True)

# ─── Side-by-side Preview ──────────────────────────────────────────────────────

col_orig, col_proc = st.columns(2, gap="medium")

with col_orig:
    st.markdown("<div class='panel-label'>▸ ORIGINAL SOURCE</div>", unsafe_allow_html=True)
    display_orig = flatten_rgba_to_white(original_img)
    st.image(display_orig, use_container_width=True)

with col_proc:
    st.markdown("<div class='panel-label laser'>▸ LASER-READY PREVIEW</div>", unsafe_allow_html=True)
    st.image(processed, use_container_width=True, clamp=True)

# ─── Metrics Row ───────────────────────────────────────────────────────────────

m1, m2, m3, m4 = st.columns(4, gap="small")
with m1:
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-value'>{processed.width}px</div>
      <div class='metric-label'>Output Width</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-value'>{processed.height}px</div>
      <div class='metric-label'>Output Height</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-value'>{stats['pct_blank']}%</div>
      <div class='metric-label'>Skip-able Rows</div>
    </div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class='metric-card'>
      <div class='metric-value'>~{est_time}m</div>
      <div class='metric-label'>Est. Job Time</div>
    </div>""", unsafe_allow_html=True)

# ─── Download ──────────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)
dl_col, info_col = st.columns([1, 2], gap="medium")

with dl_col:
    stem = uploaded_file.name.rsplit(".", 1)[0]
    fname = f"{stem}_AlgoPrep_MK2.png"
    img_bytes = pil_to_bytes(processed, "PNG")
    st.download_button(
        label="⬇  Download Laser-Ready PNG",
        data=img_bytes,
        file_name=fname,
        mime="image/png",
    )

with info_col:
    st.markdown(f"""
    <div class='info-pill' style='margin:0;'>
      <b>AlgoOS Import Checklist:</b><br>
      1. Import this PNG into AlgoOS → Mode: <b>Image</b><br>
      2. Engrave Mode: <b>Dither → Threshold</b> (already applied — use <i>Passthrough</i>)<br>
      3. Enable: <b>Skip Blank Lines</b> ✓<br>
      4. DPI in AlgoOS: <b>{dpi}</b> · Speed: <b>6000–8000 mm/min</b> · Power: <b>75–85%</b>
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style='margin-top:40px;border-top:1px solid #2A2B3D;padding-top:16px;
            text-align:center;font-size:0.68rem;color:#6E7191;letter-spacing:0.08em;'>
  ALGOPREP-MK2 · Nabamita Artisan Technology · Kolkata, West Bengal<br>
  Built for AlgoLaser MK2 / AlgoOS · TTS-55 Pro 5.5W compatible
</div>
""", unsafe_allow_html=True)
