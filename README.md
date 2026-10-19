# ✨ Image Enhancer — Online (Streamlit version)

Photo ko bara aur saaf karo — **bilkul free, browser mein**. Koi install nahi, koi credits nahi.

- **2 upscale tareeqe:** 🤖 AI Super-Resolution (FSRCNN) 2x/3x/4x, ya 🔍 High-quality Lanczos (custom 1.5x–4x)
- **Enhance options:** Denoise, Sharpen, Auto-contrast
- **Download:** PNG ya JPG mein

## Deploy (free, ~5 minute)

1. GitHub par free account banao (github.com) — agar nahi hai
2. New repository banao, naam `image-enhancer`
3. Is folder ki **saari files aur folders** (`app.py`, `requirements.txt`, `README.md`, aur `models/` folder समेत) repo mein upload karo
4. **share.streamlit.io** kholo → GitHub se sign in → **"New app"** / **"Create app"**
5. Repository + branch (`main`) + `app.py` select karo → **Deploy**
6. 2-3 minute mein tumhara link taiyaar: `tumhara-naam-image-enhancer.streamlit.app` 🔖

**2 chhoti baatein:** free apps 12 ghante idle rehne par so jati hain (link kholo to khud jaag jati hai, ~30 sec), aur pehli enhance mein thoda time lag sakta hai.

## ⚠️ Imaandaar limits

- **Output max 8000px** (lambi side) — free hosting ki memory limit ki wajah se. Is se bari photo par app khud size cap kar dega aur bata dega.
- **AI super-resolution 2x–4x** par asal detail recover karta hai. Us se aage sirf smooth interpolation hai — **16K output is app se mumkin nahi**, aur jo aisa daawa kare woh jhoot bol raha hai.
- Bohat chhoti (misal 200px) ya bohat zyada blurry/shor wali photo se chamatkar ki umeed na rakhein — result behtar hoga, perfect nahi.
- Free server par bari photo (misal 4000px → 8000px) mein 30–60 second lag sakte hain. Sabar rakhein ☕
