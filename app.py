"""
AlgoPrep-MK2 | Nabamita Artisan Technology
Version: 3.1.0 — Full 4-Mode Processing Engine + Production Costing Database
"""

import streamlit as st
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import cv2
import io

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AlgoPrep-MK2",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",   # Expanded to house the business tools
)

# ── CSS STYLING (100% PRESERVED FROM V3.0) ─────────────────────────────────────
st.markdown("""
<style>
:root{
  --bg:#0D0E14; --card:#13141C; --raised:#1E1F2E;
  --orange:#FF6B00; --glow:#FF9A40; --teal:#00C9B1;
  --txt:#E8E9F3; --muted:#6E7191; --border:#2A2B3D;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;}
[data-testid="stSidebar"]{background-color:var(--card)!important; border-right:1px solid var(--border);}
.block-container{max-width:960px;padding:1rem 1rem 3rem!important;}
#MainMenu,footer,header{visibility:hidden;}

/* ── typography ── */
h1,h2,h3{color:var(--txt);}

/* ── cards ── */
.card{background:var(--card);border:1px solid var(--border);
      border-radius:14px;padding:18px 20px;margin-bottom:14px;}
.card-title{font-family:'SF Mono',monospace;font-size:.7rem;letter-spacing:.18em;
            text-transform:uppercase;color:var(--orange);margin-bottom:14px;
            border-bottom:1px solid var(--border);padding-bottom:8px;}

/* ── header ── */
.hero{background:linear-gradient(135deg,#0D0E14 0%,#1A0A00 60%,#0D0E14 100%);
      border:1px solid var(--border);border-left:4px solid var(--orange);
      border-radius:14px;padding:16px 22px;margin-bottom:18px;
      display:flex;align-items:center;gap:14px;}
.hero-title{font-family:'SF Mono',monospace;font-size:1.45rem;font-weight:800;
            color:var(--orange);letter-spacing:.05em;margin:0;
            text-shadow:0 0 22px rgba(255,107,0,.45);}
.hero-sub{font-size:.72rem;color:var(--muted);letter-spacing:.12em;
          text-transform:uppercase;margin:2px 0 0;}

/* ── mode selector tabs ── */
.stRadio>div{display:flex;flex-wrap:wrap;gap:8px!important;flex-direction:row!important;}
.stRadio>div>label{
  background:var(--raised)!important;border:1px solid var(--border)!important;
  border-radius:24px!important;padding:8px 16px!important;
  font-size:.78rem!important;color:var(--muted)!important;cursor:pointer;
  transition:all .18s;flex:0 0 auto;
}
.stRadio>div>label:has(input:checked){
  background:linear-gradient(135deg,#FF6B00,#FF9A40)!important;
  border-color:transparent!important;color:#fff!important;font-weight:700!important;
}
.stRadio label span{font-size:.78rem!important;}
div[data-testid="stRadio"] p{margin:0;}

/* ── sliders ── */
.stSlider>div>div>div{background:var(--orange)!important;}
[data-testid="stSlider"] [data-testid="stThumbValue"]{color:var(--glow)!important;}

/* ── toggles ── */
.stToggle span{font-size:.83rem!important;color:var(--txt)!important;}

/* ── selectbox ── */
.stSelectbox>div>div{
  background:var(--raised)!important;border:1px solid var(--border)!important;
  border-radius:8px!important;color:var(--txt)!important;
}

/* ── file uploader ── */
[data-testid="stFileUploader"]{
  background:var(--raised);border:2px dashed var(--border);
  border-radius:12px;padding:8px;
}
[data-testid="stFileUploader"]:hover{border-color:var(--orange);}

/* ── download button ── */
.stDownloadButton>button{
  background:linear-gradient(135deg,#FF6B00,#FF9A40)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:700!important;font-size:.9rem!important;
  padding:.7rem 1.6rem!important;width:100%;letter-spacing:.04em!important;
}

/* ── stat chips ── */
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;}
.chip{background:var(--raised);border:1px solid var(--border);
      border-radius:16px;padding:5px 13px;font-size:.72rem;
      color:var(--muted);font-family:'SF Mono',monospace;}
.chip b{color:var(--teal);}

/* ── info/warn pills ── */
.info{background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.25);
      border-radius:9px;padding:10px 14px;font-size:.78rem;
      color:var(--teal);margin:8px 0;line-height:1.6;}
.warn{background:rgba(255,107,0,.09);border:1px solid rgba(255,107,0,.3);
      border-radius:9px;padding:10px 14px;font-size:.78rem;
      color:var(--glow);margin:8px 0;line-height:1.6;}

/* ── metric cards ── */
.met{background:var(--raised);border:1px solid var(--border);border-radius:10px;
     padding:12px;text-align:center;}
.met-v{font-size:1.15rem;font-weight:800;color:var(--glow);
       font-family:'SF Mono',monospace;}
.met-l{font-size:.62rem;color:var(--muted);text-transform:uppercase;
       letter-spacing:.09em;margin-top:3px;}

/* ── panel labels ── */
.plabel{font-family:'SF Mono',monospace;font-size:.68rem;letter-spacing:.16em;
        text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border);
        padding-bottom:7px;margin-bottom:11px;}
.plabel.hi{color:var(--teal);}

/* ── divider ── */
.divider{border:none;border-top:1px solid var(--border);margin:18px 0;}

/* ── mobile breakpoint ── */
@media(max-width:640px){
  .hero-title{font-size:1.1rem;}
  .hero-sub{font-size:.62rem;}
}
</style>
""", unsafe_allow_html=True)


# ── PRODUCTION DATABASES (SIDEBAR INTEGRATION) ──────────────────────────────────
MATERIAL_DATABASE = {
    "🪵 Soft Wood (Pine Rounds)": {"speed": 8000, "power": 80, "cost": 4.50},
    "🍁 Hard Wood (Oak/Teak/Cherry)": {"speed": 6000, "power": 90, "cost": 7.00},
    "🪵 Birch Plywood (3mm/6mm)": {"speed": 10000, "power": 75, "cost": 2.20},
    "🪨 Natural Slate Coasters": {"speed": 5000, "power": 80, "cost": 1.10},
    "🎨 Cast Acrylic (Dark/Opaque)": {"speed": 4000, "power": 85, "cost": 5.80},
}

st.sidebar.markdown("### 💼 Production Costing Hub")
st.sidebar.markdown("Configure materials and manufacturing metrics below to calculate instant costing values.")

selected_material = st.sidebar.selectbox("Active Workshop Stock", list(MATERIAL_DATABASE.keys()))
stock_defaults = MATERIAL_DATABASE[selected_material]

st.sidebar.markdown("---")
st.sidebar.markdown("#### 💰 Manufacturing Costs")
custom_blank_cost = st.sidebar.number_input("Material Blank Cost ($)", min_value=0.0, value=stock_defaults["cost"], step=0.10)
hourly_labor_rate = st.sidebar.number_input("Workshop Labor Rate ($/Hr)", min_value=0.0, value=25.0, step=1.00)
retail_markup = st.sidebar.slider("Pricing Markup Multiplier", 1.5, 5.0, 2.5, 0.1)

st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚙️ Override Machine Profile")
machine_speed_override = st.sidebar.number_input("Target Engraving Speed (mm/min)", 1000, 20000, stock_defaults["speed"], step=500)
machine_power_override = st.sidebar.slider("Target Laser Power (%)", 10, 100, stock_defaults["power"], step=5)


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESSING ENGINE v3.0 (100% PRESERVED & SECURED)
# ══════════════════════════════════════════════════════════════════════════════

def mode_smart_isolation(gray: np.ndarray, dark_thresh: int) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.5)
    _, binary = cv2.threshold(blurred, dark_thresh, 255, cv2.THRESH_BINARY_INV)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, k, iterations=1)
    return cv2.bitwise_not(cleaned)


def mode_standard_threshold(gray: np.ndarray, thresh: int, clahe: bool) -> np.ndarray:
    if clahe:
        c = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = c.apply(gray)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.3)
    _, binary = cv2.threshold(blurred, thresh, 255, cv2.THRESH_BINARY)
    return binary


def mode_photo_dither(gray: np.ndarray, gamma: float, contrast: float) -> np.ndarray:
    # Step 1: CLAHE
    clahe_obj = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    enhanced = clahe_obj.apply(gray)

    # Step 2: Unsharp mask (sharpen carved lines)
    blur = cv2.GaussianBlur(enhanced, (0, 0), 2)
    sharp = cv2.addWeighted(
        enhanced.astype(np.float32), 1.0 + contrast,
        blur.astype(np.float32), -contrast, 0
    )
    sharp = np.clip(sharp, 0, 255).astype(np.uint8)

    # Step 3: Contrast stretch to full range with safety division check
    p1 = float(np.percentile(sharp, 1))
    p99 = float(np.percentile(sharp, 99))
    if p99 > p1:
        stretched = np.clip((sharp.astype(np.float32) - p1) / (p99 - p1) * 255, 0, 255)
    else:
        stretched = sharp.astype(np.float32)
    stretched = stretched.astype(np.uint8)

    # Step 4: Gamma correction
    lut = np.array([int((i / 255.0) ** gamma * 255) for i in range(256)], dtype=np.uint8)
    gamma_img = cv2.LUT(stretched, lut)

    # Step 5: Floyd-Steinberg dither with backward safety fallback
    pil = Image.fromarray(gamma_img)
    dither_method = getattr(Image, 'Dither', Image).FLOYDSTEINBERG
    dithered = pil.convert("1", dither=dither_method).convert("L")
    return np.array(ImageOps.invert(dithered))


def mode_edge_engrave(gray: np.ndarray, lo: int, hi: int, thickness: int) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    edges = cv2.Canny(blurred, lo, hi)
    if thickness > 1:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thickness, thickness))
        edges = cv2.dilate(edges, k, iterations=1)
    return cv2.bitwise_not(edges)


def apply_circular_mask(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    size = min(img.size)
    img = img.crop(((img.width-size)//2, (img.height-size)//2,
                    (img.width+size)//2, (img.height+size)//2))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    out = Image.new("RGBA", (size, size), (255,255,255,0))
    out.paste(img, mask=mask)
    return out


def resize_img(img: Image.Image, max_mm: float, dpi: int) -> Image.Image:
    max_px = int((max_mm / 25.4) * dpi)
    w, h = img.size
    if max(w, h) <= max_px:
        return img
    r = max_px / max(w, h)
    return img.resize((int(w*r), int(h*r)), Image.LANCZOS)


def final_denoise(arr: np.ndarray, strength: int) -> np.ndarray:
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (strength*2+1, strength*2+1))
    return cv2.morphologyEx(cv2.morphologyEx(arr, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)


def get_stats(arr: np.ndarray, dpi: int, machine_speed: float) -> dict:
    rows = arr.shape[0]
    blank = int(np.sum(np.all(arr == 255, axis=1)))
    fill = round(float(np.sum(arr == 0)) / float(arr.size) * 100, 1)
    w_mm = (arr.shape[1] / dpi) * 25.4
    # Calculate time using the user's active/override speed
    t = round((rows - blank) * ((w_mm / machine_speed) * 60 + 0.1) / 60, 1)
    return {"rows": rows, "blank": blank,
            "pct_blank": round(blank/rows*100,1) if rows else 0,
            "fill": fill, "est_min": max(1.0, t)}


def to_bytes(img: Image.Image) -> bytes:
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


def flatten(img: Image.Image) -> Image.Image:
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255,255,255))
        bg.paste(img, mask=img.split()[3])
        return bg
    return img.convert("RGB")


# ══════════════════════════════════════════════════════════════════════════════
#  UI MAIN CONTENT DISPLAY
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <div style="font-size:2rem;">🔥</div>
  <div>
    <p class="hero-title">ALGOPREP-MK2</p>
    <p class="hero-sub">Production Image Processor · v3.1 · Nabamita Artisan Technology</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── ① UPLOAD SOURCE ──
st.markdown('<div class="card"><div class="card-title">① Upload Source Image</div>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "PNG · JPG · WEBP · BMP · TIFF accepted",
    type=["png","jpg","jpeg","bmp","webp","tiff"],
    label_visibility="visible"
)
st.markdown('</div>', unsafe_allow_html=True)

# ── ② PROCESSING MODE ──
st.markdown('<div class="card"><div class="card-title">② Processing Mode — Select the right mode for your image type</div>', unsafe_allow_html=True)

mode = st.radio(
    "Mode",
    options=[
        "🎯 Smart Isolation",
        "⚡ Standard Threshold",
        "📷 Photo / Dither",
        "✏️ Edge / Line Art",
    ],
    index=0,
    horizontal=True,
    label_visibility="collapsed",
)

MODE_DESCRIPTIONS = {
    "🎯 Smart Isolation":
        "📌 <b>Use for:</b> Painted or metal artwork photographed on brick/fabric/wood walls.<br>"
        "📌 <b>How:</b> Isolates only true-black pixels (artwork) and discards mid-gray background noise.",
    "⚡ Standard Threshold":
        "📌 <b>Use for:</b> Digital logos, AI-generated art, line drawings on a white or solid background.<br>"
        "📌 <b>How:</b> Global brightness cutoff — everything below threshold → black (burn).",
    "📷 Photo / Dither":
        "📌 <b>Use for:</b> Photographs, wood carvings, relief art, portraits, gradient-rich images.<br>"
        "📌 <b>How:</b> Floyd-Steinberg dithering converts gray tones into dot patterns that simulate shading when engraved at 300 DPI. Use AlgoOS Photo mode.",
    "✏️ Edge / Line Art":
        "📌 <b>Use for:</b> Converting a photo or 3D render into a crisp outline/line engraving.<br>"
        "📌 <b>How:</b> Canny edge detection — only the contour lines are burned. Maximum blank-line skipping.",
}
st.markdown(f'<div class="info">{MODE_DESCRIPTIONS[mode]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── ③ PROCESSING CONTROLS (100% PRESERVED CONTROLS AND SLIDERS) ──
st.markdown('<div class="card"><div class="card-title">③ Processing Controls</div>', unsafe_allow_html=True)

invert_out = False  # Global scope safety initializer

if mode == "🎯 Smart Isolation":
    dark_thresh = st.slider("Darkness Cutoff", 30, 120, 65, 1,
        help="Only pixels DARKER than this value = artwork. Raise if strokes missing. Lower if background bleeds in.")
    st.markdown(f'<div class="info">Targeting pixels darker than <b>{dark_thresh}</b>. '
                f'Background noise above this value is discarded.</div>', unsafe_allow_html=True)
    invert_out = st.toggle("Invert output", False, help="ON = dark wood (engrave background). OFF = light wood.")

elif mode == "⚡ Standard Threshold":
    std_thresh = st.slider("Threshold", 0, 255, 128, 1,
        help="Pixels below threshold → Black (burn). Above → White (skip).")
    clahe_on = st.toggle("CLAHE Contrast Boost", False, help="Adaptive histogram equalisation for low-contrast art.")
    invert_out = st.toggle("Invert output", False)

elif mode == "📷 Photo / Dither":
    col_g, col_c = st.columns(2)
    with col_g:
        gamma_val = st.slider("Gamma (midtone depth)", 0.4, 1.4, 0.8, 0.05,
            help="Lower = darker midtones = deeper perceived engraving. 0.8 is optimal for most photos.")
    with col_c:
        contrast_val = st.slider("Sharpness / Detail", 0.5, 3.0, 1.2, 0.1,
            help="Unsharp mask strength. Higher = crisper carved lines. 1.2 works for most.")
    invert_out = st.toggle("Invert output", False,
        help="OFF = dark areas engraved (correct for most materials). ON = light areas engraved.")
    st.markdown('<div class="info">⬡ <b>AlgoOS setting:</b> Import this PNG → Mode: <b>Image → Passthrough</b>. '
                'The dithering is baked in. Do NOT apply additional dithering in AlgoOS.</div>',
                unsafe_allow_html=True)

elif mode == "✏️ Edge / Line Art":
    col_lo, col_hi = st.columns(2)
    with col_lo:
        canny_lo = st.slider("Edge Sensitivity (Low)", 10, 150, 50, 5,
            help="Lower = more edges detected (noisier). Higher = only strong edges.")
    with col_hi:
        canny_hi = st.slider("Edge Threshold (High)", 50, 300, 150, 5,
            help="Must be ~2-3× the low value. Controls which edges are confirmed.")
    edge_thick = st.select_slider("Line Thickness", options=[1, 2, 3, 4], value=2,
        help="Pixel width of engraved lines. 2px is standard. 3-4px for bolder output.")
    invert_out = st.toggle("Invert output", False)

st.markdown('</div>', unsafe_allow_html=True)

# ── ④ OUTPUT SETTINGS ──
st.markdown('<div class="card"><div class="card-title">④ Output Settings</div>', unsafe_allow_html=True)
col_sz, col_dpi, col_crop = st.columns(3)
with col_sz:
    max_mm = st.selectbox("Max Size",
        options=[304.8, 203.2, 152.4, 101.6],
        format_func=lambda x: f"{x:.0f}mm ({x/25.4:.0f}\")",
        index=0)
with col_dpi:
    dpi = st.selectbox("DPI", options=[300, 254, 200], index=0)
with col_crop:
    circ = st.toggle("⬤ Circular Crop", False, help="For round blanks / coasters")

denoise_on = st.toggle("Final Denoise Pass", True, help="Morphological clean-up after processing. Recommended ON.")
if denoise_on:
    d_str = st.select_slider("Denoise Strength",
        options=["Light (1px)", "Medium (2px)", "Aggressive (3px)"], value="Light (1px)")
    d_map = {"Light (1px)": 1, "Medium (2px)": 2, "Aggressive (3px)": 3}

st.markdown('</div>', unsafe_allow_html=True)

# ── RUNTIME ENGINE ──
if uploaded is None:
    st.markdown("""
    <div style="background:var(--card);border:2px dashed var(--border);border-radius:14px;
                padding:40px;text-align:center;color:var(--muted);margin-top:8px;">
      <div style="font-size:2.2rem;">📷</div>
      <div style="margin-top:10px;font-size:.9rem;">Upload an image above to generate your laser-ready output</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

with st.spinner("Processing image…"):
    orig = Image.open(uploaded)
    img = orig.copy()

    # Apply Circular mask
    if circ:
        img = apply_circular_mask(img)

    # Resize image
    img = resize_img(img, max_mm, dpi)

    # Gray array conversion
    rgb = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Execute selected mode
    if mode == "🎯 Smart Isolation":
        result = mode_smart_isolation(gray, dark_thresh)
        if invert_out: result = cv2.bitwise_not(result)

    elif mode == "⚡ Standard Threshold":
        result = mode_standard_threshold(gray, std_thresh, clahe_on)
        if invert_out: result = cv2.bitwise_not(result)

    elif mode == "📷 Photo / Dither":
        result = mode_photo_dither(gray, gamma_val, contrast_val)
        if invert_out: result = cv2.bitwise_not(result)

    elif mode == "✏️ Edge / Line Art":
        result = mode_edge_engrave(gray, canny_lo, canny_hi, edge_thick)
        if invert_out: result = cv2.bitwise_not(result)

    # Morphological denoise clean-up
    if denoise_on:
        result = final_denoise(result, d_map[d_str])

    out_img = Image.fromarray(result, mode="L")

# ── CALCULATE STATS ──
stats = get_stats(result, dpi, machine_speed_override)

# ── RETAIL PRICING ENGINE ──
labor_cost = round((stats["est_min"] / 60) * hourly_labor_rate, 2)
depreciation_cost = round((stats["est_min"] / 60) * 1.50, 2)  # Tube wear tracking
total_cogs = round(custom_blank_cost + labor_cost + depreciation_cost, 2)
recommended_retail = round(total_cogs * retail_markup, 2)
unit_profit = round(recommended_retail - total_cogs, 2)

# Stat Chips Display
st.markdown(f"""
<div class="chips">
  <div class="chip">Source <b>{orig.width}×{orig.height}px</b></div>
  <div class="chip">Output <b>{out_img.width}×{out_img.height}px</b></div>
  <div class="chip">Fill <b>{stats['fill']}%</b></div>
  <div class="chip">Skip-able rows <b>{stats['pct_blank']}%</b></div>
  <div class="chip">Est. job <b>~{stats['est_min']} min</b></div>
  <div class="chip">Mode <b>{mode.split()[1]}</b></div>
</div>
""", unsafe_allow_html=True)

# Safety notifications
pill_cls = "warn" if stats['est_min'] > 25 else "info"
pill_msg = (f"⚠️ Estimated <b>{stats['est_min']} min</b> — consider Edge mode or increase thresholds."
            if stats['est_min'] > 25 else
            f"✅ <b>{stats['est_min']} min</b> estimated — AlgoOS will skip "
            f"<b>{stats['blank']:,}</b> rows ({stats['pct_blank']}%) via Skip Blank Lines.")
st.markdown(f'<div class="{pill_cls}">{pill_msg}</div>', unsafe_allow_html=True)

# ── COMPARISON DISPLAY PANEL ──
c1, c2 = st.columns(2, gap="medium")
with c1:
    st.markdown('<div class="plabel">▸ ORIGINAL SOURCE</div>', unsafe_allow_html=True)
    st.image(flatten(orig), use_container_width=True)
with c2:
    st.markdown('<div class="plabel hi">▸ LASER-READY OUTPUT</div>', unsafe_allow_html=True)
    st.image(out_img, use_container_width=True, clamp=True)

# ── METRIC CARDS (EXPANDED TO INCLUDE COSTING METRICS) ──
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
for col, v, l in zip(
    [m1, m2, m3, m4],
    [f"~{stats['est_min']}m", f"${total_cogs:.2f}", f"${recommended_retail:.2f}", f"${unit_profit:.2f}"],
    ["Est. Production Time", "Unit Cost (COGS)", "Recommended Retail Price", "Estimated Profit Margin"]
):
    col.markdown(f'<div class="met"><div class="met-v">{v}</div><div class="met-l">{l}</div></div>',
                 unsafe_allow_html=True)

# ── DOWNLOAD PANEL & SETTING SCHEMES ──
st.markdown("<br>", unsafe_allow_html=True)
dl_col, info_col = st.columns([1, 2], gap="medium")
with dl_col:
    stem = uploaded.name.rsplit(".", 1)[0]
    st.download_button(
        "⬇  Download Laser-Ready PNG",
        data=to_bytes(out_img),
        file_name=f"{stem}_AlgoPrep_MK2.png",
        mime="image/png",
    )
with info_col:
    algoos_note = {
        "🎯 Smart Isolation":  "AlgoOS Mode: <b>Image → Passthrough</b>. Enable Skip Blank Lines ✓",
        "⚡ Standard Threshold": "AlgoOS Mode: <b>Image → Passthrough</b>. Enable Skip Blank Lines ✓",
        "📷 Photo / Dither":  "AlgoOS Mode: <b>Image → Passthrough</b> (dither baked in). Do NOT re-dither. Enable Skip Blank Lines ✓",
        "✏️ Edge / Line Art": "AlgoOS Mode: <b>Image → Passthrough</b>. Skip Blank Lines gives maximum speedup here ✓",
    }
    st.markdown(f"""<div class="info" style="margin:0;">
      <b>AlgoOS Settings Guide:</b><br>
      {algoos_note[mode]}<br>
      Speed: <b>{machine_speed_override} mm/min</b> · Power: <b>{machine_power_override}%</b> · DPI: <b>{dpi}</b> · Material Preset: <b>{selected_material.split()[1]}</b>
    </div>""", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div style="margin-top:36px;border-top:1px solid var(--border);padding-top:14px;
            text-align:center;font-size:.66rem;color:var(--muted);letter-spacing:.07em;">
  ALGOPREP-MK2 v3.1 · Nabamita Artisan Technology · Kolkata, West Bengal<br>
  AlgoLaser MK2 / AlgoOS · TTS-55 Pro 5.5W compatible · 4-Mode Processing Engine
</div>
""", unsafe_allow_html=True)
