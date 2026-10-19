"""Image Enhancer — free Streamlit Cloud version.

Upload an image, upscale it (AI super-resolution or high-quality Lanczos),
optionally denoise / sharpen / auto-contrast, then download the result.

HONEST LIMITS (also shown in the UI):
- Output longest side is capped at 8000px (memory safety on free hosting).
- AI super-resolution recovers real detail at 2x-4x. Beyond that is
  interpolation, not magic. 16K output is not possible here.
"""
import time

import cv2
import streamlit as st

from enhance import (
    FSRCNN_SCALES, MAX_SIDE, auto_contrast, denoise, encode,
    enhance_pipeline, load_image, sharpen,
)

# ---------------- UI ----------------
st.set_page_config(page_title="Image Enhancer", page_icon="✨")
st.title("✨ Image Enhancer")
st.caption("Photo ko bara aur saaf karo — bilkul free, browser mein")

with st.expander("⚠️ Imaandaar limits (zaroor parhein)"):
    st.write(
        "- **Output max 8000px** (lambi side) — free hosting ki memory limit.\n"
        "- **AI super-resolution 2x–4x** par asal detail wapas lata hai. "
        "Us se zyada sirf smooth interpolation hai — koi jadui 16K nahi.\n"
        "- Bohat chhoti ya bohat blurry photo se chamatkar ki umeed na rakhein 🙂"
    )

uploaded = st.file_uploader("📤 Image upload karo (JPG / PNG / WebP)",
                            type=["jpg", "jpeg", "png", "webp"])

st.subheader("⚙️ Settings")
method = st.radio("Upscale tareeqa / Method",
                  ["🤖 AI Super-Resolution (FSRCNN)", "🔍 High-quality Lanczos"])
if method.startswith("🤖"):
    scale = st.select_slider("Scale", options=list(FSRCNN_SCALES), value=2)
    lanczos_factor = 2.0
else:
    scale = 2
    lanczos_factor = st.slider("Custom scale", 1.5, 4.0, 2.0, 0.5)

col1, col2, col3 = st.columns(3)
with col1:
    do_denoise = st.checkbox("🧹 Denoise (shor hatana)", value=True)
with col2:
    do_sharpen = st.checkbox("🔪 Sharpen (tez karna)", value=True)
with col3:
    do_contrast = st.checkbox("💡 Auto-contrast", value=False)

fmt = st.radio("Download format", ["PNG", "JPG"], horizontal=True,
               help="PNG = behtar quality, bari file. JPG = chhoti file.")

if uploaded:
    orig = load_image(uploaded)
    oh, ow = orig.shape[:2]
    st.info(f"Original: **{ow}×{oh} px**")

    if st.button("✨ Enhance karo", type="primary"):
        t0 = time.time()
        use_method = "fsrcnn" if method.startswith("🤖") else "lanczos"
        with st.spinner("Enhance ho raha hai... (bari photo par thoda wait karo)"):
            img, notes = enhance_pipeline(
                orig.copy(), use_method, scale=scale, factor=lanczos_factor,
                do_denoise=do_denoise, do_sharpen=do_sharpen,
                do_contrast=do_contrast)
        dt = time.time() - t0
        eh, ew = img.shape[:2]
        data = encode(img, fmt)
        size_kb = len(data) / 1024

        for n in notes:
            st.warning("ℹ️ " + n)
        st.success(f"Ho gaya! ⏱️ {dt:.1f} second mein")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Original**")
            st.image(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB),
                     caption=f"{ow}×{oh} px", use_container_width=True)
        with c2:
            st.markdown("**Enhanced**")
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
                     caption=f"{ew}×{eh} px", use_container_width=True)

        size_txt = f"{size_kb/1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
        st.write(f"📐 Output: **{ew}×{eh} px** · 💾 File size: **{size_txt}** · "
                 f"⏱️ Time: **{dt:.1f}s**")
        st.download_button("⬇️ Download", data=data,
                           file_name=f"enhanced_{ew}x{eh}.{fmt.lower()}",
                           mime="image/png" if fmt == "PNG" else "image/jpeg")
else:
    st.write("👆 Pehle koi image upload karo.")
