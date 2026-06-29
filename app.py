"""
AlgoPrep-MK2 | Nabamita Artisan Technology
Version: 4.0.0 — Ultimate Edition
  • 6 Processing Modes (Smart Isolation / Standard Threshold / Photo Dither /
                        Edge Line Art / Halftone / Stencil Posterize)
  • Pre-Processing: Brightness, Contrast, Rotation, Flip, Border Pad,
                    Auto Background Removal
  • Light / Dark Theme Toggle (persistent session state)
  • Quick Presets (4 material/source presets)
  • Multi-format Export (PNG / JPEG / TIFF)
  • ₹ Cost Estimator
  • Session History (last 3 results)
  • Mobile-first full-page layout — no sidebar
"""

import streamlit as st
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw
import numpy as np
import cv2
import io
import base64
import math

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "history" not in st.session_state:
    st.session_state.history = []   # list of (thumb_bytes, label, stats_dict)

# ══════════════════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AlgoPrep-MK2 | Nabamita",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  THEME TOKENS
# ══════════════════════════════════════════════════════════════════════════════
DARK = {
    "bg":       "#0D0E14",
    "card":     "#13141C",
    "raised":   "#1E1F2E",
    "border":   "#2A2B3D",
    "txt":      "#E8E9F3",
    "muted":    "#6E7191",
    "orange":   "#FF6B00",
    "glow":     "#FF9A40",
    "teal":     "#00C9B1",
    "hero_grad":"linear-gradient(135deg,#0D0E14 0%,#1A0A00 60%,#0D0E14 100%)",
    "info_bg":  "rgba(0,201,177,.09)",
    "info_bdr": "rgba(0,201,177,.28)",
    "warn_bg":  "rgba(255,107,0,.09)",
    "warn_bdr": "rgba(255,107,0,.32)",
    "success_bg":"rgba(39,200,100,.09)",
    "success_bdr":"rgba(39,200,100,.32)",
    "success_txt":"#27C864",
    "shadow":   "0 4px 24px rgba(0,0,0,.5)",
    "img_border":"#2A2B3D",
}
LIGHT = {
    "bg":       "#F4F5F7",
    "card":     "#FFFFFF",
    "raised":   "#EEF0F5",
    "border":   "#D8DBE8",
    "txt":      "#1A1C2E",
    "muted":    "#7A7D99",
    "orange":   "#E55C00",
    "glow":     "#CC5200",
    "teal":     "#00897B",
    "hero_grad":"linear-gradient(135deg,#FFF3EC 0%,#FFE0CC 60%,#FFF3EC 100%)",
    "info_bg":  "rgba(0,137,123,.08)",
    "info_bdr": "rgba(0,137,123,.3)",
    "warn_bg":  "rgba(229,92,0,.08)",
    "warn_bdr": "rgba(229,92,0,.3)",
    "success_bg":"rgba(39,150,80,.08)",
    "success_bdr":"rgba(39,150,80,.3)",
    "success_txt":"#1B8040",
    "shadow":   "0 4px 24px rgba(0,0,0,.10)",
    "img_border":"#D8DBE8",
}

T = DARK if st.session_state.dark_mode else LIGHT

# ══════════════════════════════════════════════════════════════════════════════
#  CSS INJECTION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
/* ── tokens ── */
:root{{
  --bg:{T['bg']};--card:{T['card']};--raised:{T['raised']};--border:{T['border']};
  --txt:{T['txt']};--muted:{T['muted']};--orange:{T['orange']};--glow:{T['glow']};
  --teal:{T['teal']};--shadow:{T['shadow']};
}}

/* ── global ── */
html,body,.stApp,[data-testid="stAppViewContainer"],
[data-testid="stMain"]{{background:var(--bg)!important;color:var(--txt)!important;}}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{{display:none!important;}}
.block-container{{max-width:1040px!important;padding:0.8rem 1rem 3rem!important;}}
#MainMenu,footer,header{{visibility:hidden;}}
*{{box-sizing:border-box;}}

/* ── typography ── */
h1,h2,h3,h4,p,label,span,div{{color:var(--txt);}}
.stMarkdown p{{color:var(--txt)!important;}}

/* ── hero banner ── */
.hero{{
  background:{T['hero_grad']};
  border:1px solid var(--border);border-left:5px solid var(--orange);
  border-radius:16px;padding:18px 24px;margin-bottom:20px;
  display:flex;align-items:center;justify-content:space-between;gap:16px;
  box-shadow:var(--shadow);
}}
.hero-left{{display:flex;align-items:center;gap:16px;}}
.hero-title{{
  font-family:'SF Mono','Fira Code',monospace;font-size:1.5rem;font-weight:800;
  color:var(--orange);letter-spacing:.05em;margin:0;
  text-shadow:0 0 28px rgba(255,107,0,.35);
}}
.hero-sub{{font-size:.7rem;color:var(--muted);letter-spacing:.14em;
           text-transform:uppercase;margin:3px 0 0;}}
.hero-badge{{
  background:var(--raised);border:1px solid var(--border);border-radius:20px;
  padding:6px 14px;font-size:.68rem;color:var(--muted);
  font-family:'SF Mono',monospace;white-space:nowrap;
}}

/* ── cards ── */
.card{{
  background:var(--card);border:1px solid var(--border);border-radius:16px;
  padding:20px 22px;margin-bottom:16px;box-shadow:var(--shadow);
}}
.card-title{{
  font-family:'SF Mono',monospace;font-size:.68rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--orange);margin-bottom:16px;
  border-bottom:1px solid var(--border);padding-bottom:10px;
  display:flex;align-items:center;gap:8px;
}}

/* ── section step badge ── */
.step-badge{{
  display:inline-flex;align-items:center;justify-content:center;
  width:22px;height:22px;border-radius:50%;background:var(--orange);
  color:#fff;font-size:.65rem;font-weight:800;font-family:'SF Mono',monospace;
  flex-shrink:0;
}}

/* ── mode radio pills ── */
.stRadio>div{{display:flex;flex-wrap:wrap;gap:8px!important;flex-direction:row!important;}}
.stRadio>div>label{{
  background:var(--raised)!important;border:1px solid var(--border)!important;
  border-radius:28px!important;padding:9px 18px!important;
  font-size:.78rem!important;color:var(--muted)!important;
  cursor:pointer;transition:all .15s ease;flex:0 0 auto;
}}
.stRadio>div>label:has(input:checked){{
  background:linear-gradient(135deg,{T['orange']},{T['glow']})!important;
  border-color:transparent!important;color:#fff!important;font-weight:700!important;
  box-shadow:0 2px 12px rgba(255,107,0,.35)!important;
}}
.stRadio label span{{font-size:.78rem!important;color:inherit!important;}}
div[data-testid="stRadio"] p{{margin:0;}}

/* ── preset buttons ── */
.stButton>button{{
  background:var(--raised)!important;border:1px solid var(--border)!important;
  border-radius:10px!important;color:var(--txt)!important;
  font-size:.76rem!important;padding:.45rem .8rem!important;
  width:100%;transition:all .15s;
}}
.stButton>button:hover{{
  border-color:var(--orange)!important;color:var(--orange)!important;
  background:rgba(255,107,0,.06)!important;
}}

/* ── sliders ── */
.stSlider>div>div>div{{background:var(--orange)!important;}}
[data-testid="stSlider"] [data-testid="stThumbValue"]{{
  color:var(--glow)!important;font-family:'SF Mono',monospace!important;
}}
.stSlider label{{color:var(--txt)!important;font-size:.82rem!important;}}

/* ── select slider ── */
[data-testid="stSlider"] div[data-testid="stTickBar"]{{display:none;}}

/* ── toggle ── */
.stToggle span{{font-size:.82rem!important;color:var(--txt)!important;}}

/* ── selectbox ── */
.stSelectbox label{{color:var(--txt)!important;font-size:.82rem!important;}}
.stSelectbox>div>div{{
  background:var(--raised)!important;border:1px solid var(--border)!important;
  border-radius:10px!important;color:var(--txt)!important;
}}
[data-testid="stSelectboxVirtualDropdown"]{{
  background:var(--card)!important;border:1px solid var(--border)!important;
}}

/* ── number input ── */
.stNumberInput label{{color:var(--txt)!important;font-size:.82rem!important;}}
.stNumberInput input{{
  background:var(--raised)!important;border:1px solid var(--border)!important;
  color:var(--txt)!important;border-radius:8px!important;
}}

/* ── file uploader ── */
[data-testid="stFileUploader"]{{
  background:var(--raised);border:2px dashed var(--border);
  border-radius:14px;padding:10px;transition:border-color .2s;
}}
[data-testid="stFileUploader"]:hover{{border-color:var(--orange);}}
[data-testid="stFileUploader"] label{{color:var(--txt)!important;}}

/* ── download button ── */
.stDownloadButton>button{{
  background:linear-gradient(135deg,{T['orange']},{T['glow']})!important;
  color:#fff!important;border:none!important;border-radius:12px!important;
  font-weight:700!important;font-size:.88rem!important;
  padding:.75rem 1.6rem!important;width:100%;
  letter-spacing:.04em!important;box-shadow:0 4px 16px rgba(255,107,0,.3)!important;
  transition:opacity .2s!important;
}}
.stDownloadButton>button:hover{{opacity:.88!important;}}

/* ── info pills ── */
.pill-info{{
  background:{T['info_bg']};border:1px solid {T['info_bdr']};
  border-radius:10px;padding:10px 14px;font-size:.78rem;
  color:{T['teal']};margin:8px 0;line-height:1.65;
}}
.pill-warn{{
  background:{T['warn_bg']};border:1px solid {T['warn_bdr']};
  border-radius:10px;padding:10px 14px;font-size:.78rem;
  color:{T['glow']};margin:8px 0;line-height:1.65;
}}
.pill-success{{
  background:{T['success_bg']};border:1px solid {T['success_bdr']};
  border-radius:10px;padding:10px 14px;font-size:.78rem;
  color:{T['success_txt']};margin:8px 0;line-height:1.65;
}}

/* ── stat chips ── */
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 8px;}}
.chip{{
  background:var(--raised);border:1px solid var(--border);
  border-radius:20px;padding:5px 14px;font-size:.71rem;
  color:var(--muted);font-family:'SF Mono',monospace;
}}
.chip b{{color:{T['teal']};}}

/* ── metric cards ── */
.metrics-row{{display:flex;gap:10px;margin:14px 0;flex-wrap:wrap;}}
.met{{
  flex:1;min-width:90px;background:var(--raised);border:1px solid var(--border);
  border-radius:12px;padding:14px 12px;text-align:center;
}}
.met-v{{
  font-size:1.2rem;font-weight:800;color:{T['glow']};
  font-family:'SF Mono',monospace;line-height:1;
}}
.met-l{{
  font-size:.6rem;color:var(--muted);text-transform:uppercase;
  letter-spacing:.1em;margin-top:5px;
}}

/* ── panel labels ── */
.plabel{{
  font-family:'SF Mono',monospace;font-size:.67rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--muted);
  border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:12px;
}}
.plabel.hi{{color:{T['teal']};}}

/* ── preview image frame ── */
.img-frame{{
  background:var(--raised);border:1px solid {T['img_border']};
  border-radius:12px;padding:10px;overflow:hidden;
}}

/* ── history thumbs ── */
.hist-strip{{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px;}}
.hist-item{{
  background:var(--raised);border:1px solid var(--border);border-radius:10px;
  padding:8px;text-align:center;font-size:.65rem;color:var(--muted);flex:0 0 120px;
}}

/* ── cost table ── */
.cost-table{{width:100%;border-collapse:collapse;font-size:.8rem;}}
.cost-table td{{padding:7px 10px;border-bottom:1px solid var(--border);color:var(--txt);}}
.cost-table td:last-child{{text-align:right;font-family:'SF Mono',monospace;color:{T['glow']};font-weight:700;}}
.cost-table tr:last-child td{{border-bottom:none;font-weight:700;font-size:.88rem;}}

/* ── theme toggle custom ── */
.theme-btn{{
  background:var(--raised);border:1px solid var(--border);border-radius:20px;
  padding:6px 16px;font-size:.72rem;color:var(--muted);cursor:pointer;
  font-family:'SF Mono',monospace;
}}

/* ── divider ── */
hr.div{{border:none;border-top:1px solid var(--border);margin:20px 0;}}

/* ── comparison slider ── */
.compare-wrap{{position:relative;overflow:hidden;border-radius:12px;
               border:1px solid var(--border);background:var(--raised);}}

/* ── progress steps ── */
.prog-steps{{display:flex;gap:0;margin:10px 0 14px;}}
.prog-step{{
  flex:1;height:3px;background:var(--border);border-radius:2px;margin:0 2px;
  transition:background .3s;
}}
.prog-step.done{{background:linear-gradient(90deg,{T['orange']},{T['glow']});}}

/* ── mobile ── */
@media(max-width:640px){{
  .hero{{flex-direction:column;align-items:flex-start;gap:10px;}}
  .hero-title{{font-size:1.15rem;}}
  .metrics-row{{gap:6px;}}
  .met-v{{font-size:1rem;}}
  .hist-item{{flex:0 0 100px;}}
}}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESSING ENGINE v4.0
# ══════════════════════════════════════════════════════════════════════════════

def mode_smart_isolation(gray, dark_thresh):
    blurred = cv2.GaussianBlur(gray, (3,3), 0.5)
    _, binary = cv2.threshold(blurred, dark_thresh, 255, cv2.THRESH_BINARY_INV)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, k, iterations=1)
    return cv2.bitwise_not(cleaned)

def mode_standard_threshold(gray, thresh, use_clahe, use_otsu):
    if use_clahe:
        c = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = c.apply(gray)
    blurred = cv2.GaussianBlur(gray, (3,3), 0.3)
    if use_otsu:
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        _, binary = cv2.threshold(blurred, thresh, 255, cv2.THRESH_BINARY)
    return binary

def mode_photo_dither(gray, gamma, sharpness):
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    blur = cv2.GaussianBlur(enhanced, (0,0), 2)
    sharp = cv2.addWeighted(enhanced.astype(np.float32), 1.0+sharpness,
                            blur.astype(np.float32), -sharpness, 0)
    sharp = np.clip(sharp, 0, 255).astype(np.uint8)
    p1 = float(np.percentile(sharp, 1))
    p99 = float(np.percentile(sharp, 99))
    if p99 > p1:
        stretched = np.clip((sharp.astype(np.float32)-p1)/(p99-p1)*255, 0, 255)
    else:
        stretched = sharp.astype(np.float32)
    stretched = stretched.astype(np.uint8)
    lut = np.array([int((i/255.0)**gamma*255) for i in range(256)], dtype=np.uint8)
    gamma_img = cv2.LUT(stretched, lut)
    pil = Image.fromarray(gamma_img)
    dithered = pil.convert("1", dither=Image.Dither.FLOYDSTEINBERG).convert("L")
    return np.array(ImageOps.invert(dithered))

def mode_edge(gray, lo, hi, thickness):
    blurred = cv2.GaussianBlur(gray, (5,5), 1)
    edges = cv2.Canny(blurred, lo, hi)
    if thickness > 1:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(thickness,thickness))
        edges = cv2.dilate(edges, k, iterations=1)
    return cv2.bitwise_not(edges)

def mode_halftone(gray, cell_size, angle_deg=45):
    # Rotate for classic newspaper halftone angle
    h, w = gray.shape
    cx, cy = w//2, h//2
    M = cv2.getRotationMatrix2D((cx,cy), angle_deg, 1.0)
    rotated = cv2.warpAffine(gray, M, (w,h), borderValue=255)
    out = np.ones((h,w), dtype=np.uint8)*255
    for y in range(0, h - cell_size, cell_size):
        for x in range(0, w - cell_size, cell_size):
            cell = rotated[y:y+cell_size, x:x+cell_size]
            avg = float(cell.mean())
            darkness = 1.0 - (avg/255.0)
            max_r = (cell_size//2) - 1
            r = max(0, int(darkness * max_r * 1.3))
            if r > 0:
                cx2, cy2 = x+cell_size//2, y+cell_size//2
                cv2.circle(out, (cx2,cy2), r, 0, -1)
    # Rotate back
    M_inv = cv2.getRotationMatrix2D((w//2,h//2), -angle_deg, 1.0)
    out = cv2.warpAffine(out, M_inv, (w,h), borderValue=255)
    return out


def mode_color_illustration(rgb: np.ndarray,
                             bg_v_thresh: int = 235,
                             bg_s_thresh: int = 20,
                             detail_mode: str = "Detailed",
                             face_line_thresh: int = 100) -> np.ndarray:
    """
    Mode 7 — Color Illustration Extractor  (NEW)
    For: Full-color flat illustrations, clipart, vector-style artwork,
         religious icons, cartoon characters — ANY image with a plain
         white/solid background and multiple distinct fill colors.

    Root-cause this fixes:
      Grayscale conversion collapses color information. Yellow face (gray=168),
      dark blue headdress (gray=44), and white background (gray=244) exist in
      completely different hue channels — a single threshold destroys the structure.

    Pipeline:
      1. HSV background detection (high V, low S = pure white/off-white)
      2. Flood-fill from image border → solid artwork silhouette
      3. Morphological smoothing of silhouette edge
      4. Selective restoration of ornament white-detail (beads, gaps)
      5. Restoration of dark feature lines on colored face areas (eyes, lips)
      6. Final clean + laser-convention invert
    """
    hsv  = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    H, S, V = hsv[:,:,0], hsv[:,:,1], hsv[:,:,2]
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    h, w = gray.shape

    # Stage 1: background
    bg   = (V > bg_v_thresh) & (S < bg_s_thresh)
    art_raw = (~bg).astype(np.uint8) * 255

    # Stage 2: flood-fill solid silhouette
    flood = art_raw.copy()
    for x in range(0, w, max(1, w//20)):
        cv2.floodFill(flood, None, (x, 0),   255)
        cv2.floodFill(flood, None, (x, h-1), 255)
    for y in range(0, h, max(1, h//20)):
        cv2.floodFill(flood, None, (0,   y), 255)
        cv2.floodFill(flood, None, (w-1, y), 255)
    art_solid = art_raw.copy()
    art_solid[flood == 0] = 255

    # Stage 3: smooth silhouette edge
    k9 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    k3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    art_solid = cv2.morphologyEx(art_solid, cv2.MORPH_CLOSE, k9, iterations=2)
    art_solid = cv2.morphologyEx(art_solid, cv2.MORPH_OPEN,  k3, iterations=1)

    result = art_solid.copy()

    if detail_mode in ("Detailed", "Face Lines Only"):
        # Stage 4: restore ornament white detail (non-face white areas in artwork)
        yellow = (H >= 15) & (H <= 40) & (S > 80) & (V > 120)
        white_non_face = (art_raw == 0) & art_solid.astype(bool) & ~yellow
        k5e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        white_eroded = cv2.erode(white_non_face.astype(np.uint8)*255, k5e, iterations=1)
        result[white_eroded == 255] = 0

        # Stage 5: face feature lines (eyes, brows, lips, nose, bindi)
        dark_face = yellow & (gray < face_line_thresh)
        k5d = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        face_lines = cv2.dilate(dark_face.astype(np.uint8)*255, k5d, iterations=1)
        result[face_lines == 255] = 255

    if detail_mode == "Face Lines Only":
        # Only silhouette + face lines, no ornament gaps (cleaner for small blanks)
        yellow = (H >= 15) & (H <= 40) & (S > 80) & (V > 120)
        dark_face = yellow & (gray < face_line_thresh)
        k5d = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        face_lines = cv2.dilate(dark_face.astype(np.uint8)*255, k5d, iterations=1)
        result = art_solid.copy()
        result[face_lines == 255] = 255

    # Stage 6: final clean
    k5c = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, k5c, iterations=1)
    result = cv2.morphologyEx(result, cv2.MORPH_OPEN,  k3,  iterations=1)

    return cv2.bitwise_not(result)  # black=burn, white=skip

def mode_stencil(gray, levels):
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    p2, p98 = float(np.percentile(enhanced,2)), float(np.percentile(enhanced,98))
    if p98 > p2:
        stretched = np.clip((enhanced.astype(np.float32)-p2)/(p98-p2)*255,0,255).astype(np.uint8)
    else:
        stretched = enhanced
    step = 256 // levels
    quantized = (stretched.astype(np.float32)//step*step).astype(np.uint8)
    _, binary = cv2.threshold(quantized, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, k)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, k)
    return binary

# ── Pre-processing helpers ──────────────────────────────────────────────────

def auto_remove_bg(img_pil, tolerance=20):
    gray = np.array(img_pil.convert("L"))
    h, w = gray.shape
    mask = np.zeros((h+2, w+2), dtype=np.uint8)
    img_copy = gray.copy()
    for cx, cy in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]:
        cv2.floodFill(img_copy, mask, (cx,cy), 128,
                      loDiff=tolerance, upDiff=tolerance,
                      flags=cv2.FLOODFILL_MASK_ONLY|(255<<8))
    bg = mask[1:-1,1:-1] == 255
    rgb = np.array(img_pil.convert("RGBA"))
    rgb[bg] = [255,255,255,255]
    return Image.fromarray(rgb)

def apply_circular_mask(img):
    from PIL import ImageDraw
    img = img.convert("RGBA")
    size = min(img.size)
    img = img.crop(((img.width-size)//2,(img.height-size)//2,
                    (img.width+size)//2,(img.height+size)//2))
    mask = Image.new("L",(size,size),0)
    ImageDraw.Draw(mask).ellipse((0,0,size,size),fill=255)
    out = Image.new("RGBA",(size,size),(255,255,255,0))
    out.paste(img,mask=mask)
    return out

def add_border(img_pil, px):
    arr = np.array(img_pil.convert("L"))
    padded = np.pad(arr, px, mode='constant', constant_values=255)
    return Image.fromarray(padded, mode="L")

def resize_img(img, max_mm, dpi):
    max_px = int((max_mm/25.4)*dpi)
    w, h = img.size
    if max(w,h) <= max_px: return img
    r = max_px/max(w,h)
    return img.resize((int(w*r),int(h*r)),Image.LANCZOS)

def final_denoise(arr, strength):
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(strength*2+1,strength*2+1))
    return cv2.morphologyEx(cv2.morphologyEx(arr,cv2.MORPH_OPEN,k),cv2.MORPH_CLOSE,k)

def get_stats(arr, dpi):
    rows = arr.shape[0]
    blank = int(np.sum(np.all(arr==255,axis=1)))
    fill  = round(float(np.sum(arr==0))/float(arr.size)*100,1)
    w_mm  = (arr.shape[1]/dpi)*25.4
    t     = round((rows-blank)*((w_mm/6000)*60+0.1)/60,1)
    return {"rows":rows,"blank":blank,
            "pct_blank":round(blank/rows*100,1) if rows else 0,
            "fill":fill,"est_min":t,
            "w_px":arr.shape[1],"h_px":arr.shape[0]}

def to_bytes(img, fmt="PNG"):
    b = io.BytesIO()
    if fmt == "JPEG":
        img.convert("RGB").save(b,"JPEG",quality=95)
    elif fmt == "TIFF":
        img.save(b,"TIFF",compression="lzw")
    else:
        img.save(b,"PNG")
    return b.getvalue()

def thumb_bytes(img, size=120):
    t = img.copy(); t.thumbnail((size,size))
    b = io.BytesIO(); t.convert("RGB").save(b,"PNG"); return b.getvalue()

def flatten(img):
    if img.mode=="RGBA":
        bg=Image.new("RGB",img.size,(255,255,255))
        bg.paste(img,mask=img.split()[3]); return bg
    return img.convert("RGB")

def img_to_b64(img_pil):
    b = io.BytesIO()
    img_pil.convert("RGB").save(b,"PNG")
    return base64.b64encode(b.getvalue()).decode()


# ══════════════════════════════════════════════════════════════════════════════
#  PRESETS
# ══════════════════════════════════════════════════════════════════════════════
PRESETS = {
    "🖼 Logo on White": {
        "mode_idx": 1, "std_thresh": 128, "use_clahe": False, "use_otsu": True,
        "brightness": 1.0, "contrast": 1.0, "invert_out": False,
    },
    "📷 Photo Portrait": {
        "mode_idx": 2, "gamma_val": 0.8, "sharpness_val": 1.2,
        "brightness": 1.05, "contrast": 1.1, "invert_out": False,
    },
    "🪵 Wood Carving": {
        "mode_idx": 2, "gamma_val": 0.7, "sharpness_val": 1.5,
        "brightness": 1.0, "contrast": 1.2, "invert_out": False,
    },
    "🎨 Color Artwork": {
        "mode_idx": 6, "brightness": 1.0, "contrast": 1.0, "invert_out": False,
    },
    "⚫ Metal Cutout": {
        "mode_idx": 0, "dark_thresh": 65,
        "brightness": 1.0, "contrast": 1.0, "invert_out": False,
    },
    "🎨 Color Illustration":
        "📌 <b>Best for:</b> Full-color clipart, religious icons, flat illustrations, cartoons — any image with colored fills on a white background.<br>"
        "🔧 HSV-based color/background separation. Extracts complete artwork silhouette regardless of fill color. Restores face features and ornament detail.",
}
MODE_NAMES = [
    "🎯 Smart Isolation",
    "⚡ Standard Threshold",
    "📷 Photo / Dither",
    "✏️ Edge / Line Art",
    "⬤ Halftone",
    "🎭 Stencil / Posterize",
    "🎨 Color Illustration",
]
MODE_TIPS = {
    "🎯 Smart Isolation":
        "📌 <b>Best for:</b> Painted/metal/wood cutout artwork on a textured wall or fabric background.<br>"
        "🔧 Isolates only true-black pixels and discards mid-gray background noise.",
    "⚡ Standard Threshold":
        "📌 <b>Best for:</b> Digital logos, AI-generated art, clean illustrations on a white/solid background.<br>"
        "🔧 Global brightness cutoff — pixels below threshold → black (burn).",
    "📷 Photo / Dither":
        "📌 <b>Best for:</b> Photographs, wood carvings, 3D renders, portraits, gradients, relief art.<br>"
        "🔧 Floyd-Steinberg dithering converts gray tones to B&W dot patterns simulating shading at 300 DPI.",
    "✏️ Edge / Line Art":
        "📌 <b>Best for:</b> Converting photos/renders to crisp outline engravings — nameplates, architecture.<br>"
        "🔧 Canny edge detection — only contour lines are burned. Maximum blank-line skip efficiency.",
    "⬤ Halftone":
        "📌 <b>Best for:</b> Artistic/vintage look — circular dot grid simulates newspaper print style.<br>"
        "🔧 Dot size proportional to local darkness. Excellent for portraits on acrylic/dark anodized metal.",
    "🎭 Stencil / Posterize":
        "📌 <b>Best for:</b> High-contrast graphic art, multi-layer burns, pop-art style engraving.<br>"
        "🔧 Reduces image to N tonal levels then binary-splits. Great for bold statement pieces.",
}


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
th_icon = "🌙" if st.session_state.dark_mode else "☀️"
th_label = "Dark Mode" if st.session_state.dark_mode else "Light Mode"

header_cols = st.columns([6,1])
with header_cols[0]:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-left">
        <div style="font-size:2.2rem;">🔥</div>
        <div>
          <p class="hero-title">ALGOPREP-MK2</p>
          <p class="hero-sub">Production Image Processor · v4.0 Ultimate · Nabamita Artisan Technology</p>
        </div>
      </div>
      <div class="hero-badge">AlgoLaser MK2 · AlgoOS · TTS-55 Pro</div>
    </div>
    """, unsafe_allow_html=True)

with header_cols[1]:
    st.markdown("<div style='margin-top:18px;'>", unsafe_allow_html=True)
    if st.button(f"{th_icon} {th_label}", key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — UPLOAD + QUICK PRESETS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f'<div class="card"><div class="card-title"><span class="step-badge">1</span> Upload Image</div>', unsafe_allow_html=True)

up_col, preset_col = st.columns([2, 1], gap="large")
with up_col:
    uploaded = st.file_uploader(
        "PNG · JPG · WEBP · BMP · TIFF",
        type=["png","jpg","jpeg","bmp","webp","tiff"],
        label_visibility="visible",
    )
with preset_col:
    st.markdown(f"<div style='font-size:.68rem;letter-spacing:.15em;text-transform:uppercase;color:{T['muted']};margin-bottom:8px;'>⚡ Quick Presets</div>", unsafe_allow_html=True)
    active_preset = None
    for pname in PRESETS:
        if st.button(pname, key=f"preset_{pname}"):
            active_preset = pname
            st.session_state[f"preset_applied"] = pname

st.markdown('</div>', unsafe_allow_html=True)

# Read preset if applied
applied = st.session_state.get("preset_applied", None)
preset_data = PRESETS.get(applied, {}) if applied else {}


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — PROCESSING MODE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card"><div class="card-title"><span class="step-badge">2</span> Processing Mode</div>', unsafe_allow_html=True)

default_mode_idx = preset_data.get("mode_idx", 0)
mode = st.radio("Mode", options=MODE_NAMES, index=default_mode_idx,
                horizontal=True, label_visibility="collapsed")
st.markdown(f'<div class="pill-info">{MODE_TIPS[mode]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — PRE-PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card"><div class="card-title"><span class="step-badge">3</span> Pre-Processing Adjustments</div>', unsafe_allow_html=True)

pre_c1, pre_c2, pre_c3 = st.columns(3)
with pre_c1:
    brightness = st.slider("☀️ Brightness", 0.5, 2.0,
        float(preset_data.get("brightness", 1.0)), 0.05)
    contrast_pre = st.slider("🎚 Contrast", 0.5, 2.0,
        float(preset_data.get("contrast", 1.0)), 0.05)
with pre_c2:
    rotation = st.select_slider("↻ Rotation", options=[0,90,180,270], value=0)
    flip_h = st.toggle("↔ Flip Horizontal", False)
    flip_v = st.toggle("↕ Flip Vertical", False)
with pre_c3:
    auto_bg = st.toggle("🪄 Auto Remove Background", False,
        help="Flood-fills from image corners to remove uniform backgrounds. Works best on solid/gradient backgrounds.")
    bg_tolerance = st.slider("BG Tolerance", 5, 60, 20, 1,
        disabled=not auto_bg,
        help="Higher = removes more background variation. Lower = more conservative.")
    circ_crop = st.toggle("⬤ Circular Crop", False,
        help="For round blanks, coasters, and medals.")

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — MODE CONTROLS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card"><div class="card-title"><span class="step-badge">4</span> Processing Controls</div>', unsafe_allow_html=True)

invert_out = False

if mode == "🎯 Smart Isolation":
    c1, c2 = st.columns([2,1])
    with c1:
        dark_thresh = st.slider("Darkness Cutoff", 30, 120,
            int(preset_data.get("dark_thresh",65)), 1,
            help="Only pixels DARKER than this = artwork. Raise if strokes missing. Lower if background bleeds.")
    with c2:
        invert_out = st.toggle("Invert Output", bool(preset_data.get("invert_out",False)),
            help="ON = dark wood (burn background). OFF = light wood (burn artwork).")
    st.markdown(f'<div class="pill-info">Targeting pixels darker than <b>{dark_thresh}</b> as artwork. Background above discarded.</div>', unsafe_allow_html=True)

elif mode == "⚡ Standard Threshold":
    c1, c2, c3 = st.columns(3)
    with c1:
        use_otsu = st.toggle("Auto Threshold (Otsu)", False,
            help="Otsu's method automatically finds the optimal threshold. Overrides manual slider.")
    with c2:
        std_thresh = st.slider("Manual Threshold", 0, 255,
            int(preset_data.get("std_thresh",128)), 1,
            disabled=use_otsu,
            help="Pixels below → Black (burn). Above → White (skip).")
    with c3:
        use_clahe = st.toggle("CLAHE Boost", bool(preset_data.get("use_clahe",False)),
            help="Adaptive histogram equalisation for low-contrast images.")
        invert_out = st.toggle("Invert Output", False)

elif mode == "📷 Photo / Dither":
    c1, c2 = st.columns(2)
    with c1:
        gamma_val = st.slider("Gamma (Midtone Depth)", 0.4, 1.4,
            float(preset_data.get("gamma_val",0.8)), 0.05,
            help="Lower = darker midtones = deeper perceived engraving. 0.7–0.9 optimal.")
        invert_out = st.toggle("Invert Output", False)
    with c2:
        sharpness_val = st.slider("Sharpness / Detail", 0.5, 3.0,
            float(preset_data.get("sharpness_val",1.2)), 0.1,
            help="Unsharp mask strength. Higher = crisper carved lines.")
    st.markdown('<div class="pill-info">⬡ <b>AlgoOS:</b> Import PNG → Mode: <b>Image → Passthrough</b>. Dithering is baked in. Do NOT re-dither in AlgoOS.</div>', unsafe_allow_html=True)

elif mode == "✏️ Edge / Line Art":
    c1, c2, c3 = st.columns(3)
    with c1:
        canny_lo = st.slider("Edge Sensitivity (Low)", 10, 150, 50, 5)
    with c2:
        canny_hi = st.slider("Edge Threshold (High)", 50, 300, 150, 5)
    with c3:
        edge_thick = st.select_slider("Line Thickness", options=[1,2,3,4], value=2)
        invert_out = st.toggle("Invert Output", False)

elif mode == "⬤ Halftone":
    c1, c2 = st.columns(2)
    with c1:
        cell_size = st.slider("Dot Cell Size (px)", 4, 24, 10, 1,
            help="Smaller = finer dots = more detail. Larger = bolder look. 8–12 optimal for 300 DPI.")
        invert_out = st.toggle("Invert Output", False)
    with c2:
        ht_angle = st.slider("Halftone Angle (°)", 0, 90, 45, 5,
            help="Classic newspaper halftone uses 45°. 0° = square grid. 15° = subtle.")
    st.markdown('<div class="pill-info">⬡ Classic halftone dot grid. <b>AlgoOS:</b> Image → Passthrough. Recommended for dark anodized aluminium, acrylic, or slate.</div>', unsafe_allow_html=True)

elif mode == "🎨 Color Illustration":
    c1, c2, c3 = st.columns(3)
    with c1:
        detail_mode = st.radio("Detail Level", 
            options=["Solid Silhouette", "Detailed", "Face Lines Only"],
            index=1,
            help="Solid = clean wall-art cutout. Detailed = ornament gaps + face lines. Face Lines Only = silhouette + eyes/lips only.")
    with c2:
        bg_v_thresh = st.slider("Background Brightness Cutoff", 200, 255, 235, 1,
            help="Pixels brighter than this = background. Lower if background has cream/off-white tint.")
        bg_s_thresh = st.slider("Background Saturation Cutoff", 5, 60, 20, 1,
            help="Pixels less saturated than this = background. Raise if BG has a slight color cast.")
    with c3:
        face_line_thresh = st.slider("Face Line Sensitivity", 60, 160, 100, 5,
            help="Threshold for detecting dark features (eyes, lips, brows) on colored skin areas. Lower = only darkest lines. Higher = more detail.")
        invert_out = st.toggle("Invert Output", False)
    st.markdown('''<div class="pill-info">
      🎨 <b>Color Illustration mode active</b><br>
      This mode uses HSV color-space analysis — not grayscale. Yellow faces, blue headdresses,
      red accents all get captured correctly regardless of their gray value.<br>
      <b>AlgoOS:</b> Image → Passthrough · Skip Blank Lines ✓
    </div>''', unsafe_allow_html=True)

elif mode == "🎭 Stencil / Posterize":
    c1, c2 = st.columns(2)
    with c1:
        stencil_levels = st.select_slider("Tonal Levels", options=[2,3,4,5,6,8], value=4,
            help="2 = pure binary. 4 = balanced stencil. 6+ = more tonal nuance.")
        invert_out = st.toggle("Invert Output", False)
    with c2:
        st.markdown(f"""<div class="pill-info" style="margin-top:22px;">
          ⬡ <b>Level guide:</b><br>
          2 levels = bold graphic stencil<br>
          4 levels = balanced poster art<br>
          6+ levels = detailed layered burn
        </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5 — OUTPUT SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="card"><div class="card-title"><span class="step-badge">5</span> Output Settings</div>', unsafe_allow_html=True)

out_c1, out_c2, out_c3, out_c4 = st.columns(4)
with out_c1:
    max_mm = st.selectbox("Max Size",
        options=[304.8,203.2,152.4,101.6,76.2],
        format_func=lambda x:f"{x:.0f}mm ({x/25.4:.0f}\")", index=0)
with out_c2:
    dpi = st.selectbox("DPI", options=[300,254,200,150], index=0)
with out_c3:
    border_px = st.number_input("Border Pad (px)", 0, 100, 0, 5,
        help="White margin around the image so laser doesn't engrave to edge of blank.")
with out_c4:
    export_fmt = st.selectbox("Export Format", options=["PNG","JPEG","TIFF"], index=0)

denoise_on = st.toggle("Final Denoise Pass", True)
if denoise_on:
    d_str = st.select_slider("Denoise Strength",
        options=["Light (1px)","Medium (2px)","Aggressive (3px)"], value="Light (1px)")
d_map = {"Light (1px)":1,"Medium (2px)":2,"Aggressive (3px)":3}

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  EMPTY STATE
# ══════════════════════════════════════════════════════════════════════════════
if uploaded is None:
    st.markdown(f"""
    <div style="background:{T['card']};border:2px dashed {T['border']};border-radius:16px;
                padding:50px 30px;text-align:center;margin-top:8px;">
      <div style="font-size:3rem;">📷</div>
      <div style="font-size:1rem;font-weight:700;color:{T['txt']};margin:12px 0 6px;">
        Upload an image above to begin
      </div>
      <div style="font-size:.8rem;color:{T['muted']};line-height:1.8;">
        6 processing modes · Pre-processing adjustments · Light & Dark theme<br>
        PNG / JPEG / TIFF export · ₹ Cost estimator · Session history
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESSING PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

# Progress indicator
progress_steps = ["Load","Pre-Process","Core Algorithm","Post-Process","Stats"]
prog_html = '<div class="prog-steps">' + \
    ''.join(f'<div class="prog-step" id="ps{i}"></div>' for i in range(len(progress_steps))) + \
    '</div>'
prog_placeholder = st.empty()
prog_placeholder.markdown(prog_html, unsafe_allow_html=True)

def show_progress(n):
    html = '<div class="prog-steps">' + \
        ''.join(f'<div class="prog-step{"  done" if i<=n else ""}"></div>' for i in range(len(progress_steps))) + \
        '</div>'
    prog_placeholder.markdown(html, unsafe_allow_html=True)

with st.spinner("Processing…"):

    # ── Load ──
    show_progress(0)
    orig = Image.open(uploaded)
    img = orig.copy()

    # ── Pre-process ──
    show_progress(1)
    # Brightness / Contrast
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast_pre != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast_pre)
    # Flip
    if flip_h: img = ImageOps.mirror(img)
    if flip_v: img = ImageOps.flip(img)
    # Rotation
    if rotation != 0:
        img = img.rotate(-rotation, expand=True, fillcolor=(255,255,255))
    # Auto BG removal
    if auto_bg:
        img = auto_remove_bg(img, tolerance=bg_tolerance)
    # Circular crop
    if circ_crop:
        img = apply_circular_mask(img)
    # Resize
    img = resize_img(img, max_mm, dpi)

    # ── Core Algorithm ──
    show_progress(2)
    rgb = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    if mode == "🎯 Smart Isolation":
        result = mode_smart_isolation(gray, dark_thresh)
    elif mode == "⚡ Standard Threshold":
        result = mode_standard_threshold(gray, std_thresh, use_clahe, use_otsu)
    elif mode == "📷 Photo / Dither":
        result = mode_photo_dither(gray, gamma_val, sharpness_val)
    elif mode == "✏️ Edge / Line Art":
        result = mode_edge(gray, canny_lo, canny_hi, edge_thick)
    elif mode == "⬤ Halftone":
        result = mode_halftone(gray, cell_size, ht_angle)

    elif mode == "🎭 Stencil / Posterize":
        result = mode_stencil(gray, stencil_levels)
    elif mode == "🎨 Color Illustration":
        result = mode_color_illustration(rgb, bg_v_thresh, bg_s_thresh, detail_mode, face_line_thresh)

    if invert_out:
        result = cv2.bitwise_not(result)

    # ── Post-process ──
    show_progress(3)
    if denoise_on:
        result = final_denoise(result, d_map[d_str])
    if border_px > 0:
        out_img = add_border(Image.fromarray(result,"L"), border_px)
        result  = np.array(out_img)
    else:
        out_img = Image.fromarray(result, mode="L")

    # ── Stats ──
    show_progress(4)
    stats = get_stats(result, dpi)

show_progress(4)

# ── Save to history ──────────────────────────────────────────────────────────
hist_entry = (thumb_bytes(out_img), f"{mode.split()[1]} · {uploaded.name[:16]}", stats)
st.session_state.history = ([hist_entry] + st.session_state.history)[:3]


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS SECTION
# ══════════════════════════════════════════════════════════════════════════════

# ── Stat chips ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="chips">
  <div class="chip">Source <b>{orig.width}×{orig.height}px</b></div>
  <div class="chip">Output <b>{stats['w_px']}×{stats['h_px']}px</b></div>
  <div class="chip">Fill <b>{stats['fill']}%</b></div>
  <div class="chip">Blank rows <b>{stats['pct_blank']}%</b></div>
  <div class="chip">Est. job <b>~{stats['est_min']} min</b></div>
  <div class="chip">DPI <b>{dpi}</b></div>
  <div class="chip">Mode <b>{mode.split()[1]}</b></div>
</div>
""", unsafe_allow_html=True)

# Time pill
if stats['est_min'] > 25:
    st.markdown(f'<div class="pill-warn">⚠️ Estimated <b>{stats["est_min"]} min</b> — high fill density. Try Edge mode or raise threshold to reduce burn area.</div>', unsafe_allow_html=True)
elif stats['est_min'] > 12:
    st.markdown(f'<div class="pill-info">✅ <b>{stats["est_min"]} min</b> estimated — AlgoOS skips <b>{stats["blank"]:,}</b> rows ({stats["pct_blank"]}%) via Skip Blank Lines.</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="pill-success">🚀 <b>{stats["est_min"]} min</b> — Excellent! <b>{stats["pct_blank"]}%</b> skip ratio. AlgoOS will complete this rapidly.</div>', unsafe_allow_html=True)

# ── Before / After preview ───────────────────────────────────────────────────
prev_c1, prev_c2 = st.columns(2, gap="medium")
with prev_c1:
    st.markdown('<div class="plabel">▸ ORIGINAL SOURCE</div>', unsafe_allow_html=True)
    st.image(flatten(orig), use_container_width=True)
with prev_c2:
    st.markdown('<div class="plabel hi">▸ LASER-READY OUTPUT</div>', unsafe_allow_html=True)
    st.image(out_img, use_container_width=True, clamp=True)

# ── Interactive Before/After Slider ─────────────────────────────────────────
with st.expander("🔀 Interactive Before / After Comparison Slider", expanded=False):
    orig_b64 = img_to_b64(flatten(orig).resize(out_img.size, Image.LANCZOS))
    out_b64  = img_to_b64(out_img.convert("RGB"))
    st.components.v1.html(f"""
    <style>
    *{{margin:0;padding:0;box-sizing:border-box;}}
    .ba-wrap{{position:relative;width:100%;max-width:700px;margin:0 auto;
              user-select:none;border-radius:12px;overflow:hidden;
              box-shadow:0 4px 20px rgba(0,0,0,.3);}}
    .ba-before,.ba-after{{position:absolute;top:0;left:0;width:100%;height:100%;}}
    .ba-before img,.ba-after img{{width:100%;height:100%;object-fit:contain;
                                  display:block;background:#fff;}}
    .ba-after{{overflow:hidden;}}
    .ba-divider{{position:absolute;top:0;bottom:0;width:3px;
                 background:#FF6B00;cursor:ew-resize;z-index:10;
                 box-shadow:0 0 10px rgba(255,107,0,.8);}}
    .ba-handle{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                width:40px;height:40px;border-radius:50%;
                background:#FF6B00;display:flex;align-items:center;justify-content:center;
                color:#fff;font-size:1rem;font-weight:bold;box-shadow:0 2px 10px rgba(0,0,0,.4);}}
    .ba-label{{position:absolute;top:10px;background:rgba(0,0,0,.55);
               color:#fff;font-size:.7rem;padding:3px 10px;border-radius:12px;
               font-family:monospace;letter-spacing:.06em;}}
    .ba-label.orig{{left:10px;}}
    .ba-label.proc{{right:10px;}}
    </style>
    <div class="ba-wrap" id="baWrap">
      <div class="ba-before">
        <img src="data:image/png;base64,{orig_b64}" />
      </div>
      <div class="ba-after" id="baAfter" style="width:50%">
        <img src="data:image/png;base64,{out_b64}" style="min-width:calc(100vw / 1);" />
      </div>
      <div class="ba-divider" id="baDivider" style="left:50%">
        <div class="ba-handle">⇔</div>
      </div>
      <span class="ba-label orig">ORIGINAL</span>
      <span class="ba-label proc">LASER READY</span>
    </div>
    <script>
    const wrap=document.getElementById('baWrap'),
          after=document.getElementById('baAfter'),
          divider=document.getElementById('baDivider');
    let dragging=false;
    function setPos(x){{
      const r=wrap.getBoundingClientRect();
      let p=Math.max(0,Math.min(1,(x-r.left)/r.width));
      divider.style.left=(p*100)+'%';
      after.style.width=(p*100)+'%';
    }}
    divider.addEventListener('mousedown',()=>dragging=true);
    window.addEventListener('mouseup',()=>dragging=false);
    window.addEventListener('mousemove',e=>{{if(dragging)setPos(e.clientX);}});
    divider.addEventListener('touchstart',e=>{{dragging=true;e.preventDefault();}},{{passive:false}});
    window.addEventListener('touchend',()=>dragging=false);
    window.addEventListener('touchmove',e=>{{if(dragging)setPos(e.touches[0].clientX);}},{{passive:false}});
    // auto-size height
    const img=wrap.querySelector('.ba-before img');
    img.onload=()=>{{wrap.style.height=img.offsetHeight+'px';}};
    if(img.complete){{wrap.style.height=(wrap.offsetWidth*0.75)+'px';}}
    </script>
    """, height=520)

# ── Metrics row ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metrics-row">
  <div class="met"><div class="met-v">{stats['w_px']}px</div><div class="met-l">Width</div></div>
  <div class="met"><div class="met-v">{stats['h_px']}px</div><div class="met-l">Height</div></div>
  <div class="met"><div class="met-v">{stats['fill']}%</div><div class="met-l">Fill Density</div></div>
  <div class="met"><div class="met-v">{stats['pct_blank']}%</div><div class="met-l">Skip-able</div></div>
  <div class="met"><div class="met-v">~{stats['est_min']}m</div><div class="met-l">Est. Time</div></div>
  <div class="met"><div class="met-v">{dpi}</div><div class="met-l">DPI</div></div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ALGOOS CHECKLIST + DOWNLOAD
# ══════════════════════════════════════════════════════════════════════════════
dl_col, info_col = st.columns([1,2], gap="medium")

ALGOOS_NOTES = {
    "🎯 Smart Isolation":     "Mode: <b>Image → Passthrough</b> · Enable Skip Blank Lines ✓",
    "⚡ Standard Threshold":  "Mode: <b>Image → Passthrough</b> · Enable Skip Blank Lines ✓",
    "📷 Photo / Dither":      "Mode: <b>Image → Passthrough</b> · Do NOT re-dither · Skip Blank Lines ✓",
    "✏️ Edge / Line Art":     "Mode: <b>Image → Passthrough</b> · Skip Blank Lines gives max speedup ✓",
    "⬤ Halftone":             "Mode: <b>Image → Passthrough</b> · Skip Blank Lines ✓",
    "🎭 Stencil / Posterize": "Mode: <b>Image → Passthrough</b> · Skip Blank Lines ✓",
    "🎨 Color Illustration": "Mode: <b>Image → Passthrough</b> · HSV extraction baked in · Skip Blank Lines ✓",
}

with dl_col:
    stem = uploaded.name.rsplit(".",1)[0]
    ext_map = {"PNG":".png","JPEG":".jpg","TIFF":".tif"}
    st.download_button(
        f"⬇  Download {export_fmt}",
        data=to_bytes(out_img, export_fmt),
        file_name=f"{stem}_AlgoPrep_MK2{ext_map[export_fmt]}",
        mime=f"image/{'png' if export_fmt=='PNG' else 'jpeg' if export_fmt=='JPEG' else 'tiff'}",
    )

with info_col:
    st.markdown(f"""<div class="pill-info" style="margin:0;">
      <b>AlgoOS Import Checklist:</b><br>
      {ALGOOS_NOTES[mode]}<br>
      Speed: <b>6000–8000 mm/min</b> · Power: <b>75–85%</b> · DPI in AlgoOS: <b>{dpi}</b><br>
      ⚠️ <i>TTS-55 Pro (5.5W): use 85–95% power, 3000–4000 mm/min</i>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ₹ COST ESTIMATOR
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("₹ Job Cost Estimator", expanded=False):
    cost_c1, cost_c2 = st.columns(2)
    with cost_c1:
        material_cost = st.number_input("Material Cost (₹)", 0, 5000, 50, 10)
        power_watt    = st.number_input("Laser Wattage (W)", 1, 100, 10, 1)
        elec_rate     = st.number_input("Electricity Rate (₹/kWh)", 1.0, 20.0, 7.0, 0.5)
    with cost_c2:
        labour_rate   = st.number_input("Labour Rate (₹/hr)", 0, 1000, 150, 10)
        overhead_pct  = st.number_input("Overhead %", 0, 100, 20, 5)
        selling_price = st.number_input("Your Selling Price (₹)", 0, 50000, 499, 10)

    # Calculations
    job_hr       = stats['est_min'] / 60
    elec_cost    = round((power_watt / 1000) * job_hr * elec_rate, 2)
    labour_cost  = round(job_hr * labour_rate, 2)
    base_cost    = material_cost + elec_cost + labour_cost
    overhead_val = round(base_cost * overhead_pct / 100, 2)
    total_cost   = round(base_cost + overhead_val, 2)
    profit       = round(selling_price - total_cost, 2)
    margin       = round((profit / selling_price * 100) if selling_price > 0 else 0, 1)
    margin_color = T['success_txt'] if margin >= 60 else T['glow'] if margin >= 30 else "#e53935"

    st.markdown(f"""
    <table class="cost-table">
      <tr><td>🪵 Material</td><td>₹ {material_cost:.2f}</td></tr>
      <tr><td>⚡ Electricity ({stats['est_min']} min × {power_watt}W)</td><td>₹ {elec_cost}</td></tr>
      <tr><td>👷 Labour ({stats['est_min']} min)</td><td>₹ {labour_cost}</td></tr>
      <tr><td>📦 Overhead ({overhead_pct}%)</td><td>₹ {overhead_val}</td></tr>
      <tr><td><b>Total Job Cost</b></td><td>₹ {total_cost}</td></tr>
      <tr><td><b>Selling Price</b></td><td>₹ {selling_price}</td></tr>
      <tr><td><b>Profit</b></td><td style="color:{margin_color};">₹ {profit} &nbsp;(<b>{margin}% margin</b>)</td></tr>
    </table>
    """, unsafe_allow_html=True)
    if margin < 60:
        st.markdown(f'<div class="pill-warn" style="margin-top:8px;">⚠️ Margin is <b>{margin}%</b> — Nabamita target floor is 70%. Consider raising selling price to <b>₹ {round(total_cost/0.30)}</b>.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="pill-success" style="margin-top:8px;">✅ Margin <b>{margin}%</b> — above the 70% floor. Healthy job economics.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SESSION HISTORY
# ══════════════════════════════════════════════════════════════════════════════
if len(st.session_state.history) > 0:
    with st.expander(f"🕒 Session History ({len(st.session_state.history)} recent results)", expanded=False):
        hist_cols = st.columns(len(st.session_state.history))
        for i, (thumb, label, s) in enumerate(st.session_state.history):
            with hist_cols[i]:
                b64t = base64.b64encode(thumb).decode()
                st.markdown(f"""
                <div class="hist-item">
                  <img src="data:image/png;base64,{b64t}"
                       style="width:100%;border-radius:6px;margin-bottom:6px;">
                  <div style="color:{T['teal']};font-weight:700;">{label}</div>
                  <div style="margin-top:3px;">Fill: {s['fill']}% · ~{s['est_min']}m</div>
                </div>
                """, unsafe_allow_html=True)
        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<hr class="div">
<div style="text-align:center;font-size:.65rem;color:{T['muted']};letter-spacing:.07em;line-height:2;">
  ALGOPREP-MK2 v4.0 Ultimate Edition · Nabamita Artisan Technology · Kolkata, West Bengal<br>
  AlgoLaser MK2 / AlgoOS · TTS-55 Pro 5.5W · 6-Mode Processing Engine · ₹100 Cr Vision<br>
  <span style="color:{T['orange']};">🔥</span> Built for laser artisans scaling from maker to enterprise
</div>
""", unsafe_allow_html=True)
