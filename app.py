"""
AlgoPrep-MK2 Pro | Nabamita Artisan Technology
Version: 3.2.0 — Production Image Engine + Bed Visualizer + Job Ticket
"""

import streamlit as st
from PIL import Image, ImageOps, ImageDraw
import numpy as np
import cv2
import io

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AlgoPrep-MK2 Pro",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS STYLING (100% PRESERVED & EXPANDED FOR PRINT) ──────────────────────────
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

/* Typography */
h1,h2,h3{color:var(--txt);}

/* Cards */
.card{background:var(--card);border:1px solid var(--border);
      border-radius:14px;padding:18px 20px;margin-bottom:14px;}
.card-title{font-family:'SF Mono',monospace;font-size:.7rem;letter-spacing:.18em;
            text-transform:uppercase;color:var(--orange);margin-bottom:14px;
            border-bottom:1px solid var(--border);padding-bottom:8px;}

/* Header */
.hero{background:linear-gradient(135deg,#0D0E14 0%,#1A0A00 60%,#0D0E14 100%);
      border:1px solid var(--border);border-left:4px solid var(--orange);
      border-radius:14px;padding:16px 22px;margin-bottom:18px;
      display:flex;align-items:center;gap:14px;}
.hero-title{font-family:'SF Mono',monospace;font-size:1.45rem;font-weight:800;
            color:var(--orange);letter-spacing:.05em;margin:0;
            text-shadow:0 0 22px rgba(255,107,0,.45);}
.hero-sub{font-size:.72rem;color:var(--muted);letter-spacing:.12em;
          text-transform:uppercase;margin:2px 0 0;}

/* Radio tabs */
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

/* Sliders & Forms */
.stSlider>div>div>div{background:var(--orange)!important;}
[data-testid="stSlider"] [data-testid="stThumbValue"]{color:var(--glow)!important;}
.stToggle span{font-size:.83rem!important;color:var(--txt)!important;}
.stSelectbox>div>div{
  background:var(--raised)!important;border:1px solid var(--border)!important;
  border-radius:8px!important;color:var(--txt)!important;
}

/* File Uploader */
[data-testid="stFileUploader"]{
  background:var(--raised);border:2px dashed var(--border);
  border-radius:12px;padding:8px;
}
[data-testid="stFileUploader"]:hover{border-color:var(--orange);}

/* Buttons */
.stDownloadButton>button, .stButton>button{
  background:linear-gradient(135deg,#FF6B00,#FF9A40)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:700!important;font-size:.9rem!important;
  padding:.7rem 1.6rem!important;width:100%;letter-spacing:.04em!important;
}

/* Stats, Chips, Metrics */
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;}
.chip{background:var(--raised);border:1px solid var(--border);
      border-radius:16px;padding:5px 13px;font-size:.72rem;
      color:var(--muted);font-family:'SF Mono',monospace;}
.chip b{color:var(--teal);}
.info{background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.25);
      border-radius:9px;padding:10px 14px;font-size:.78rem;
      color:var(--teal);margin:8px 0;line-height:1.6;}
.warn{background:rgba(255,107,0,.09);border:1px solid rgba(255,107,0,.3);
      border-radius:9px;padding:10px 14px;font-size:.78rem;
      color:var(--glow);margin:8px 0;line-height:1.6;}
.met{background:var(--raised);border:1px solid var(--border);border-radius:10px;
     padding:12px;text-align:center;}
.met-v{font-size:1.15rem;font-weight:800;color:var(--glow);
       font-family:'SF Mono',monospace;}
.met-l{font-size:.62rem;color:var(--muted);text-transform:uppercase;
       letter-spacing:.09em;margin-top:3px;}
.plabel{font-family:'SF Mono',monospace;font-size:.68rem;letter-spacing:.16em;
        text-transform:uppercase;color:var(--muted);border-bottom:1px solid var(--border);
        padding-bottom:7px;margin-bottom:11px;}
.plabel.hi{color:var(--teal);}
.divider{border:none;border-top:1px solid var(--border);margin:18px 0;}

/* Print Media Stylesheet */
@media print {
  body, html, [data-testid="stAppViewContainer"] {
    background: #FFF !important;
    color: #000 !important;
  }
  .card, .met, .info, .chips {
    border: 1px solid #000 !important;
    background: #FFF !important;
    color: #000 !important;
  }
  [data-testid="stSidebar"], .hero, .stDownloadButton, [data-testid="stFileUploader"], .divider {
    display: none !important;
  }
}
</style>
""", unsafe_allow_html=True)


# ── WORKSHOP MATERIAL DATABASE ───────────────────────────────────────────────
MATERIAL_DATABASE = {
    "🪵 Soft Wood (Pine Rounds)": {"speed": 8000, "power": 80, "cost": 4.50},
    "🍁 Hard Wood (Oak/Teak/Cherry)": {"speed": 6000, "power": 90, "cost": 7.00},
    "🪵 Birch Plywood (3mm/6mm)": {"speed": 10000, "power": 75, "cost": 2.20},
    "🪨 Natural Slate Coasters": {"speed": 5000, "power": 80, "cost": 1.10},
    "🎨 Cast Acrylic (Dark/Opaque)": {"speed": 4000, "power": 85, "cost": 5.80},
}

st.sidebar.markdown("### 💼 Workshop Costing Hub")
selected_material = st.sidebar.selectbox("Active Stock Type", list(MATERIAL_DATABASE.keys()))
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
#  CORE IMAGE PROCESSING FUNCTIONS (100% RESTORED FROM V3.0)
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
    clahe_obj = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    enhanced = clahe_obj.apply(gray)
    blur = cv2.GaussianBlur(enhanced, (0, 0), 2)
    sharp = cv2.addWeighted(enhanced.astype(np.float32), 1.0 + contrast, blur.astype(np.float32), -contrast, 0)
    sharp = np.clip(sharp, 0, 255).astype(np.uint8)

    p1 = float(np.percentile(sharp, 1))
    p99 = float(np.percentile(sharp, 99))
    if p99 > p1:
        stretched = np.clip((sharp.astype(np.float32) - p1) / (p99 - p1) * 255, 0, 255)
    else:
        stretched = sharp.astype(np.float32)
    stretched = stretched.astype(np.uint8)

    lut = np.array([int((i / 255.0) ** gamma * 255) for i in range(256)], dtype=np.uint8)
    gamma_img = cv2.LUT(stretched, lut)

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
    t = round((rows - blank) * ((w_mm / machine_speed) * 60 + 0.1) / 60, 1)
    return {"rows": rows, "blank": blank, "pct_blank": round(blank/rows*100,1) if rows else 0, "fill": fill, "est_min": max(1.0, t)}

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
#  UI MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="card"><div class="card-title">① Upload Source Image</div>', unsafe_allow_html=True)
uploaded = st.file_uploader("PNG · JPG · WEBP · BMP · TIFF accepted", type=["png","jpg","jpeg","bmp","webp","tiff"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded:
    # ② PROCESSING MODE
    st.markdown('<div class="card"><div class="card-title">② Processing Mode</div>', unsafe_allow_html=True)
    mode = st.radio("Mode Selector", options=["🎯 Smart Isolation", "⚡ Standard Threshold", "📷 Photo / Dither", "✏️ Edge / Line Art"], index=2, horizontal=True, label_visibility="collapsed")
    st.markdown(f'<div class="info">{MODE_DESCRIPTIONS[mode]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ③ PROCESSING CONTROLS (100% original sliders intact)
    st.markdown('<div class="card"><div class="card-title">③ Processing Controls</div>', unsafe_allow_html=True)
    invert_out = False
    
    if mode == "🎯 Smart Isolation":
        dark_thresh = st.slider("Darkness Cutoff", 30, 120, 65, 1)
        invert_out = st.toggle("Invert output", False)
    elif mode == "⚡ Standard Threshold":
        std_thresh = st.slider("Threshold", 0, 255, 128, 1)
        clahe_on = st.toggle("CLAHE Contrast Boost", False)
        invert_out = st.toggle("Invert output", False)
    elif mode == "📷 Photo / Dither":
        col_g, col_c = st.columns(2)
        with col_g:
            gamma_val = st.slider("Gamma (midtone depth)", 0.4, 1.4, 0.8, 0.05)
        with col_c:
            contrast_val = st.slider("Sharpness / Detail", 0.5, 3.0, 1.2, 0.1)
        invert_out = st.toggle("Invert output", False)
    elif mode == "✏️ Edge / Line Art":
        col_lo, col_hi = st.columns(2)
        with col_lo:
            canny_lo = st.slider("Edge Sensitivity (Low)", 10, 150, 50, 5)
        with col_hi:
            canny_hi = st.slider("Edge Threshold (High)", 50, 300, 150, 5)
        edge_thick = st.select_slider("Line Thickness", options=[1, 2, 3, 4], value=2)
        invert_out = st.toggle("Invert output", False)
    st.markdown('</div>', unsafe_allow_html=True)

    # ④ OUTPUT SETTINGS
    st.markdown('<div class="card"><div class="card-title">④ Output Settings</div>', unsafe_allow_html=True)
    col_sz, col_dpi, col_crop = st.columns(3)
    with col_sz:
        max_mm = st.selectbox("Max Size", options=[304.8, 203.2, 152.4, 101.6], format_func=lambda x: f"{x:.0f}mm ({x/25.4:.0f}\")", index=0)
    with col_dpi:
        dpi = st.selectbox("DPI", options=[300, 254, 200], index=0)
    with col_crop:
        circ = st.toggle("⬤ Circular Crop", True)

    denoise_on = st.toggle("Final Denoise Pass", True)
    if denoise_on:
        d_str = st.select_slider("Denoise Strength", options=["Light (1px)", "Medium (2px)", "Aggressive (3px)"], value="Light (1px)")
        d_map = {"Light (1px)": 1, "Medium (2px)": 2, "Aggressive (3px)": 3}
    st.markdown('</div>', unsafe_allow_html=True)

    # ── IMAGE PROCESSING PIPELINE ──
    with st.spinner("Processing framework..."):
        orig = Image.open(uploaded)
        img = orig.copy()
        if circ:
            img = apply_circular_mask(img)
        img = resize_img(img, max_mm, dpi)
        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        if mode == "🎯 Smart Isolation":
            result = mode_smart_isolation(gray, dark_thresh)
        elif mode == "⚡ Standard Threshold":
            result = mode_standard_threshold(gray, std_thresh, clahe_on)
        elif mode == "📷 Photo / Dither":
            result = mode_photo_dither(gray, gamma_val, contrast_val)
        elif mode == "✏️ Edge / Line Art":
            result = mode_edge_engrave(gray, canny_lo, canny_hi, edge_thick)

        if invert_out:
            result = cv2.bitwise_not(result)
        if denoise_on:
            result = final_denoise(result, d_map[d_str])

        out_img = Image.fromarray(result, mode="L")

    # Stats Calculation
    stats = get_stats(result, dpi, machine_speed_override)

    # Production cost math
    labor_cost = round((stats["est_min"] / 60) * hourly_labor_rate, 2)
    depreciation = round((stats["est_min"] / 60) * 1.50, 2)
    total_cogs = round(custom_blank_cost + labor_cost + depreciation, 2)
    rec_price = round(total_cogs * retail_markup, 2)
    margin_profit = round(rec_price - total_cogs, 2)

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

    # 📐 ADVANCED FEATURE 1: INTERACTIVE BED & JIG VISUALIZER
    st.markdown('<div class="card"><div class="card-title">📐 Workshop Jig & Bed Alignment Visualizer</div>', unsafe_allow_html=True)
    
    # Calculate SVG positions
    bed_max_mm = 400.0  # AlgoLaser standard working field
    scale = 300 / bed_max_mm  # scale 400mm down to 300px viewport
    circle_radius = (max_mm / 2) * scale
    center_pos = 200 # center of 400x400 field
    
    col_vis_left, col_vis_right = st.columns([1, 1.2])
    with col_vis_left:
        # Render clean SVG bed view
        svg_visualizer = f"""
        <svg viewBox="0 0 300 300" width="100%" style="background:#13141C; border:1px solid var(--border); border-radius:8px;">
          <!-- Bed Grid lines (every 50mm) -->
          <line x1="0" y1="75" x2="300" y2="75" stroke="#2A2B3D" stroke-dasharray="2,2"/>
          <line x1="0" y1="150" x2="300" y2="150" stroke="#2A2B3D" stroke-dasharray="2,2"/>
          <line x1="0" y1="225" x2="300" y2="225" stroke="#2A2B3D" stroke-dasharray="2,2"/>
          <line x1="75" y1="0" x2="75" y2="300" stroke="#2A2B3D" stroke-dasharray="2,2"/>
          <line x1="150" y1="0" x2="150" y2="300" stroke="#2A2B3D" stroke-dasharray="2,2"/>
          <line x1="225" y1="0" x2="225" y2="300" stroke="#2A2B3D" stroke-dasharray="2,2"/>
          
          <!-- Bed Outer limits (400x400mm) -->
          <rect x="2" y="2" width="296" height="296" fill="none" stroke="#FF6B00" stroke-width="2" stroke-dasharray="4,4"/>
          
          <!-- Physical Blank representation (aligned center) -->
          <circle cx="150" cy="150" r="{circle_radius}" fill="rgba(0, 201, 177, 0.15)" stroke="#00C9B1" stroke-width="2"/>
          <circle cx="150" cy="150" r="3" fill="#00C9B1"/>
          
          <!-- Axis Indicators -->
          <text x="8" y="290" fill="#6E7191" font-family="monospace" font-size="10">0,0 (Home)</text>
          <text x="230" y="290" fill="#6E7191" font-family="monospace" font-size="10">X+ (400mm)</text>
          <text x="8" y="20" fill="#6E7191" font-family="monospace" font-size="10">Y+ (400mm)</text>
        </svg>
        """
        st.write(svg_visualizer, unsafe_allow_html=True)
    with col_vis_right:
        st.markdown(f"""
        <div style="font-size:0.83rem; line-height:1.7;">
          <b>Physical Jig Placement Metrics:</b><br>
          • <b>AlgoLaser Bed dimensions:</b> 400mm × 400mm working field.<br>
          • <b>Target piece size:</b> {max_mm:.1f}mm ({max_mm/25.4:.1f} inches).<br>
          • <b>Safety clearance margin:</b> {((bed_max_mm - max_mm) / 2):.1f}mm remaining on each edge.<br>
          • <b>Alignment Strategy:</b> Position your cardboard alignment frame centering around coordinate <b>(X: 200mm, Y: 200mm)</b> on your bed ruler. Use the AlgoOS "Frame" command to test physical travel paths prior to engraving.
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Side-by-Side preview structures
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown('<div class="plabel">▸ ORIGINAL SOURCE</div>', unsafe_allow_html=True)
        st.image(flatten(orig), use_container_width=True)
    with c2:
        st.markdown('<div class="plabel hi">▸ LASER-READY OUTPUT</div>', unsafe_allow_html=True)
        st.image(out_img, use_container_width=True, clamp=True)

    # Metric Panel Displays
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    for col, v, l in zip(
        [m1, m2, m3, m4],
        [f"~{stats['est_min']}m", f"${total_cogs:.2f}", f"${rec_price:.2f}", f"${margin_profit:.2f}"],
        ["Est. Production Time", "Unit Cost (COGS)", "Recommended Retail Price", "Estimated Profit Margin"]
    ):
        col.markdown(f'<div class="met"><div class="met-v">{v}</div><div class="met-l">{l}</div></div>', unsafe_allow_html=True)

    # 📋 ADVANCED FEATURE 2: PRINTABLE PRODUCTION JOB TICKET
    st.markdown('<div class="card"><div class="card-title">📋 Production Job Ticket</div>', unsafe_allow_html=True)
    st.markdown("""
    Use the browser print window (Ctrl+P / Cmd+P) to print this ticket to an physical paper label. 
    It is pre-formatted to strip the UI components and print cleanly on black-and-white thermal printer stock.
    """)
    
    # Render clean, flat Job Ticket card
    st.markdown(f"""
    <div style="background:#13141C; border:2px solid #2A2B3D; border-radius:8px; padding:18px; font-family:monospace; color:#E8E9F3;">
      <h3 style="margin:0 0 10px 0; color:#FF6B00; border-bottom:1px solid #2A2B3D; padding-bottom:5px;">PRODUCTION WORK ORDER</h3>
      <table style="width:100%; border-collapse:collapse; font-size:0.78rem;">
        <tr><td style="padding:4px 0; color:#6E7191;">Job Template:</td><td style="text-align:right; font-weight:bold;">{uploaded.name}</td></tr>
        <tr><td style="padding:4px 0; color:#6E7191;">Material Stock:</td><td style="text-align:right; font-weight:bold;">{selected_material}</td></tr>
        <tr><td style="padding:4px 0; color:#6E7191;">AlgoOS Target Mode:</td><td style="text-align:right; font-weight:bold;">Image (Passthrough)</td></tr>
        <tr><td style="padding:4px 0; color:#6E7191;">Speed / Power:</td><td style="text-align:right; font-weight:bold; color:#FF9A40;">{machine_speed_override} mm/min @ {machine_power_override}% Power</td></tr>
        <tr><td style="padding:4px 0; color:#6E7191;">Physical Size / DPI:</td><td style="text-align:right; font-weight:bold;">{max_mm:.1f}mm / {dpi} DPI</td></tr>
        <tr><td style="padding:4px 0; color:#6E7191;">Est. Engrave Duration:</td><td style="text-align:right; font-weight:bold; color:#00C9B1;">~{stats['est_min']} Minutes</td></tr>
      </table>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download & Instructions block
    st.markdown("<br>", unsafe_allow_html=True)
    dl_col, info_col = st.columns([1, 2], gap="medium")
    with dl_col:
        stem = uploaded.name.rsplit(".", 1)[0]
        st.download_button(
            "⬇  Download Production Image",
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
          Speed: <b>{machine_speed_override} mm/min</b> · Power: <b>{machine_power_override}%</b> · DPI: <b>{dpi}</b>
        </div>""", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown("""
<div style="margin-top:36px;border-top:1px solid var(--border);padding-top:14px;
            text-align:center;font-size:.66rem;color:var(--muted);letter-spacing:.07em;">
  ALGOPREP-MK2 v3.2 · Nabamita Artisan Technology · Kolkata, West Bengal<br>
  AlgoLaser MK2 / AlgoOS · TTS-55 Pro 5.5W compatible · 4-Mode Processing Engine
</div>
""", unsafe_allow_html=True)
