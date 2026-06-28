"""
AlgoPrep-MK2 Pro | Nabamita Artisan Technology
Version: 3.1.0 — Production Workflow & Pricing Engine
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
    initial_sidebar_state="expanded",  # Opened sidebar to host the business calculator
)

# ── CSS STYLING ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root{
  --bg:#0D0E14; --card:#13141C; --raised:#1E1F2E;
  --orange:#FF6B00; --glow:#FF9A40; --teal:#00C9B1;
  --txt:#E8E9F3; --muted:#6E7191; --border:#2A2B3D;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;}
.block-container{max-width:1100px;padding:1rem 1rem 3rem!important;}
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

/* Download Button */
.stDownloadButton>button{
  background:linear-gradient(135deg,#FF6B00,#FF9A40)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:700!important;font-size:.9rem!important;
  padding:.7rem 1.6rem!important;width:100%;letter-spacing:.04em!important;
}

/* Stat Chips */
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;}
.chip{background:var(--raised);border:1px solid var(--border);
      border-radius:16px;padding:5px 13px;font-size:.72rem;
      color:var(--muted);font-family:'SF Mono',monospace;}
.chip b{color:var(--teal);}

/* Info/Warn Pills */
.info{background:rgba(0,201,177,.08);border:1px solid rgba(0,201,177,.25);
      border-radius:9px;padding:10px 14px;font-size:.78rem;
      color:var(--teal);margin:8px 0;line-height:1.6;}
.warn{background:rgba(255,107,0,.09);border:1px solid rgba(255,107,0,.3);
      border-radius:9px;padding:10px 14px;font-size:.78rem;
      color:var(--glow);margin:8px 0;line-height:1.6;}

/* Metric Cards */
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
</style>
""", unsafe_allow_html=True)

# ── WORKSHOP DATABASES ────────────────────────────────────────────────────────
MATERIAL_DATABASE = {
    "🪵 Soft Wood (Pine Rounds)": {"speed": 8000, "power": 80, "passes": 1, "cost": 4.50},
    "🍁 Hard Wood (Oak/Cherry)": {"speed": 6000, "power": 90, "passes": 1, "cost": 7.00},
    "🪵 Birch Plywood (3mm)": {"speed": 10000, "power": 75, "passes": 1, "cost": 2.20},
    "🪨 Natural Slate Coasters": {"speed": 5000, "power": 80, "passes": 1, "cost": 1.10},
    "🎨 Cast Acrylic (Black/Dark)": {"speed": 4000, "power": 85, "passes": 1, "cost": 5.80},
}

# ══════════════════════════════════════════════════════════════════════════════
#  IMAGE PROCESSING FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

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

def mode_photo_dither(gray: np.ndarray, gamma: float, contrast: float) -> np.ndarray:
    clahe_obj = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
    enhanced = clahe_obj.apply(gray)
    blur = cv2.GaussianBlur(enhanced, (0, 0), 2)
    sharp = cv2.addWeighted(enhanced.astype(np.float32), 1.0 + contrast, blur.astype(np.float32), -contrast, 0)
    sharp = np.clip(sharp, 0, 255).astype(np.uint8)

    p1, p99 = np.percentile(sharp, [1, 99])
    if p99 > p1:
        stretched = np.clip((sharp.astype(np.float32) - p1) / (p99 - p1) * 255, 0, 255).astype(np.uint8)
    else:
        stretched = sharp

    lut = np.array([int((i / 255.0) ** gamma * 255) for i in range(256)], dtype=np.uint8)
    gamma_img = cv2.LUT(stretched, lut)
    pil = Image.fromarray(gamma_img)
    dither_method = getattr(Image, 'Dither', Image).FLOYDSTEINBERG
    dithered = pil.convert("1", dither=dither_method).convert("L")
    return np.array(ImageOps.invert(dithered))

def mode_standard_threshold(gray: np.ndarray, thresh: int, clahe: bool) -> np.ndarray:
    if clahe:
        c = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        gray = c.apply(gray)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.3)
    _, binary = cv2.threshold(blurred, thresh, 255, cv2.THRESH_BINARY)
    return binary

def mode_smart_isolation(gray: np.ndarray, dark_thresh: int) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (3, 3), 0.5)
    _, binary = cv2.threshold(blurred, dark_thresh, 255, cv2.THRESH_BINARY_INV)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, k, iterations=1)
    return cv2.bitwise_not(cleaned)

def mode_edge_engrave(gray: np.ndarray, lo: int, hi: int, thickness: int) -> np.ndarray:
    blurred = cv2.GaussianBlur(gray, (5, 5), 1)
    edges = cv2.Canny(blurred, lo, hi)
    if thickness > 1:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (thickness, thickness))
        edges = cv2.dilate(edges, k, iterations=1)
    return cv2.bitwise_not(edges)

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

def get_stats(arr: np.ndarray, dpi: int, target_speed: float) -> dict:
    rows = arr.shape[0]
    blank = int(np.sum(np.all(arr == 255, axis=1)))
    fill = round(float(np.sum(arr == 0)) / float(arr.size) * 100, 1)
    w_mm = (arr.shape[1] / dpi) * 25.4
    
    # Calculate time based on chosen speed
    t = round((rows - blank) * ((w_mm / target_speed) * 60 + 0.08) / 60, 1)
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
#  SIDEBAR: WORKSHOP MANAGEMENT ENGINE
# ══════════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("### 💼 Workshop Costing Engine")

# Material Selector
selected_material_name = st.sidebar.selectbox("Select Workshop Stock", list(MATERIAL_DATABASE.keys()))
stock_specs = MATERIAL_DATABASE[selected_material_name]

# Cost Variables
st.sidebar.markdown("---")
st.sidebar.markdown("#### 💰 Production Costs")
unit_blank_cost = st.sidebar.number_input("Wood Blank Cost ($)", min_value=0.0, value=stock_specs["cost"], step=0.50)
workshop_labor_rate = st.sidebar.number_input("Labor Rate ($/Hour)", min_value=0.0, value=25.0, step=5.0)
markup_factor = st.sidebar.slider("Target Profit Markup (Multiplier)", 1.5, 5.0, 2.5, 0.1, 
                                 help="2.5x Markup = 60% Profit Margin")

# Machine Settings (Derived from Stock selection but manually adjustable)
st.sidebar.markdown("---")
st.sidebar.markdown("#### ⚙️ Presets override")
production_speed = st.sidebar.number_input("Laser Speed (mm/min)", 1000, 20000, stock_specs["speed"], step=500)
production_power = st.sidebar.slider("Laser Power (%)", 10, 100, stock_specs["power"], step=5)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <div style="font-size:2rem;">🔥</div>
  <div>
    <p class="hero-title">ALGOPREP-MK2 PRO</p>
    <p class="hero-sub">Production Workshop Hub · Nabamita Artisan Technology</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ① UPLOAD
st.markdown('<div class="card"><div class="card-title">① Upload Source Image</div>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "Upload design file",
    type=["png","jpg","jpeg","bmp","webp"],
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded:
    # ② PROCESSING MODES
    st.markdown('<div class="card"><div class="card-title">② Processing Mode</div>', unsafe_allow_html=True)
    mode = st.radio(
        "Mode",
        options=["🎯 Smart Isolation", "⚡ Standard Threshold", "📷 Photo / Dither", "✏️ Edge / Line Art"],
        index=2,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ③ ADJUSTMENTS CARD
    st.markdown('<div class="card"><div class="card-title">③ Output & Image Adjustments</div>', unsafe_allow_html=True)
    
    col_adj1, col_adj2 = st.columns(2)
    with col_adj1:
        circ = st.toggle("⬤ Circular Crop (12\" Template)", True)
        denoise_on = st.toggle("Denoise Fine Output", True)
    with col_adj2:
        max_mm = st.selectbox("Final Dimension", [304.8, 203.2, 152.4], format_func=lambda x: f"{x/25.4:.0f}\" Diameter Product")
        dpi = st.selectbox("Resolution Setting", [254, 300, 200], index=0)

    # Mode Parameter Branches
    st.markdown("<br>", unsafe_allow_html=True)
    invert_out = False
    
    if mode == "📷 Photo / Dither":
        col_g, col_c = st.columns(2)
        with col_g:
            gamma_val = st.slider("Tone/Depth (Gamma)", 0.4, 1.4, 0.8, 0.05)
        with col_c:
            contrast_val = st.slider("Sharpness Boost", 0.5, 3.0, 1.2, 0.1)
        invert_out = st.toggle("Invert Output Image", False)
        
    elif mode == "⚡ Standard Threshold":
        std_thresh = st.slider("Threshold Level", 0, 255, 128)
        clahe_on = st.toggle("CLAHE Contrast Equalizer", False)
        invert_out = st.toggle("Invert Output Image", False)
        
    elif mode == "🎯 Smart Isolation":
        dark_thresh = st.slider("Darkness Limit", 30, 120, 65)
        invert_out = st.toggle("Invert Output Image", False)
        
    elif mode == "✏️ Edge / Line Art":
        col_lo, col_hi = st.columns(2)
        with col_lo:
            canny_lo = st.slider("Edge Sensitivity (Low)", 10, 150, 50)
        with col_hi:
            canny_hi = st.slider("Edge Threshold (High)", 50, 300, 150)
        edge_thick = st.select_slider("Outline Thickness", [1, 2, 3, 4], 2)
        invert_out = st.toggle("Invert Output Image", False)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # ── PIPELINE EXECUTION ────────────────────────────────────────────────────
    with st.spinner("Processing framework..."):
        orig = Image.open(uploaded)
        img = orig.copy()

        if circ:
            img = apply_circular_mask(img)

        img = resize_img(img, max_mm, dpi)
        rgb = np.array(img.convert("RGB"))
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

        # Core logic execution
        if mode == "📷 Photo / Dither":
            result = mode_photo_dither(gray, gamma_val, contrast_val)
        elif mode == "⚡ Standard Threshold":
            result = mode_standard_threshold(gray, std_thresh, clahe_on)
        elif mode == "🎯 Smart Isolation":
            result = mode_smart_isolation(gray, dark_thresh)
        elif mode == "✏️ Edge / Line Art":
            result = mode_edge_engrave(gray, canny_lo, canny_hi, edge_thick)

        if invert_out:
            result = cv2.bitwise_not(result)

        if denoise_on:
            result = final_denoise(result, 1)

        out_img = Image.fromarray(result, mode="L")

    # Stats Engine Update
    stats = get_stats(result, dpi, production_speed)

    # ── BUSINESS & PRICING METRICS ───────────────────────────────────────────
    # Labor calculation
    manufacturing_labor_cost = round((stats["est_min"] / 60) * workshop_labor_rate, 2)
    
    # Simple Machine Wear calculation ($1.50 per hour of diode use)
    machine_depreciation = round((stats["est_min"] / 60) * 1.50, 2)
    
    # Total Cost of Goods Sold (COGS)
    total_cogs = round(unit_blank_cost + manufacturing_labor_cost + machine_depreciation, 2)
    
    # Retail Pricing
    recommended_retail_price = round(total_cogs * markup_factor, 2)
    total_profit_per_piece = round(recommended_retail_price - total_cogs, 2)

    # Display Analytics Dashboard
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f'<div class="met"><div class="met-v">~{stats["est_min"]}m</div><div class="met-l">Run-time (20W)</div></div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown(f'<div class="met"><div class="met-v">${total_cogs:.2f}</div><div class="met-l">COGS per Unit</div></div>', unsafe_allow_html=True)
    with m_col3:
        st.markdown(f'<div class="met"><div class="met-v" style="color:var(--teal);">${recommended_retail_price:.2f}</div><div class="met-l">Rec. Retail Price</div></div>', unsafe_allow_html=True)
    with m_col4:
        st.markdown(f'<div class="met"><div class="met-v" style="color:var(--teal);">${total_profit_per_piece:.2f}</div><div class="met-l">Profit margin</div></div>', unsafe_allow_html=True)

    # Side-By-Side Visuals
    st.markdown("<br>", unsafe_allow_html=True)
    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        st.markdown('<div class="plabel">▸ Original Design</div>', unsafe_allow_html=True)
        st.image(flatten(orig), use_container_width=True)
    with col_prev2:
        st.markdown('<div class="plabel hi">▸ AlgoLaser Production Output</div>', unsafe_allow_html=True)
        st.image(out_img, use_container_width=True, clamp=True)

    # Final Execution Panel
    st.markdown("<br>", unsafe_allow_html=True)
    col_dl, col_os = st.columns([1, 2])
    with col_dl:
        stem_name = uploaded.name.rsplit(".", 1)[0]
        st.download_button(
            "⬇  Download Production Image",
            data=to_bytes(out_img),
            file_name=f"{stem_name}_AlgoPrep_Pro.png",
            mime="image/png"
        )
    with col_os:
        st.markdown(f"""<div class="info" style="margin:0;">
          <b>⚙️ Active Production Profile: {selected_material_name}</b><br>
          Import to AlgoOS → <b>Passthrough mode</b>. Speed: <b>{production_speed} mm/min</b> | Power: <b>{production_power}%</b> | DPI: <b>{dpi}</b>
        </div>""", unsafe_allow_html=True)

else:
    st.markdown("""
    <div style="background:var(--card);border:2px dashed var(--border);border-radius:14px;
                padding:40px;text-align:center;color:var(--muted);margin-top:8px;">
      <div style="font-size:2.2rem;">📷</div>
      <div style="margin-top:10px;font-size:.9rem;">Upload a design template to initiate the pipeline</div>
    </div>""", unsafe_allow_html=True)
