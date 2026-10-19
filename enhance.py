"""Core image-enhancement logic (no Streamlit dependency — unit testable).

app.py imports these functions, so tests here exercise the real code path.
"""
import cv2
import numpy as np
from PIL import Image

MAX_SIDE = 8000  # output longest-side cap (free-tier memory safety)
MODEL_DIR = "models"

FSRCNN_SCALES = (2, 3, 4)

_sr_cache = {}


def load_fsrcnn(scale: int):
    """Load an FSRCNN model once and reuse it."""
    if scale not in _sr_cache:
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel(f"{MODEL_DIR}/FSRCNN-small_x{scale}.pb")
        sr.setModel("fsrcnn", scale)
        _sr_cache[scale] = sr
    return _sr_cache[scale]


def load_image(fileobj) -> np.ndarray:
    """Decode upload to BGR numpy via Pillow (handles JPG/PNG/WebP)."""
    pil = Image.open(fileobj).convert("RGB")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def fit_to_cap(w: int, h: int, cap: int = MAX_SIDE):
    """Return (w, h, capped?) scaled so longest side <= cap."""
    longest = max(w, h)
    if longest <= cap:
        return w, h, False
    f = cap / longest
    return int(w * f), int(h * f), True


def upscale_fsrcnn(img: np.ndarray, scale: int, model_dir: str = MODEL_DIR):
    """AI super-resolution. Pre-shrinks input so output never exceeds the cap."""
    h, w = img.shape[:2]
    max_in = MAX_SIDE // scale
    pre_note = None
    if max(w, h) > max_in:
        w2, h2, _ = fit_to_cap(w, h, max_in)
        img = cv2.resize(img, (w2, h2), interpolation=cv2.INTER_AREA)
        pre_note = (f"Input {w}x{h} ko pehle {w2}x{h2} kiya "
                    f"(taake output {MAX_SIDE}px se zyada na ho).")
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(f"{model_dir}/FSRCNN-small_x{scale}.pb")
    sr.setModel("fsrcnn", scale)
    return sr.upsample(img), pre_note


def upscale_lanczos(img: np.ndarray, factor: float):
    """High-quality Lanczos resampling with an arbitrary factor."""
    h, w = img.shape[:2]
    tw, th = int(w * factor), int(h * factor)
    tw, th, capped = fit_to_cap(tw, th)
    out = cv2.resize(img, (tw, th), interpolation=cv2.INTER_LANCZOS4)
    note = None
    if capped:
        note = f"Output {MAX_SIDE}px par cap hua (free hosting ki memory limit)."
    return out, note


def denoise(img: np.ndarray) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(img, None, h=7, hColor=7,
                                           templateWindowSize=7, searchWindowSize=21)


def sharpen(img: np.ndarray, amount: float = 0.6) -> np.ndarray:
    blurred = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1 + amount, blurred, -amount, 0)


def auto_contrast(img: np.ndarray) -> np.ndarray:
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab = cv2.merge((clahe.apply(l), a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def enhance_pipeline(img: np.ndarray, method: str, scale: int = 2,
                     factor: float = 2.0, do_denoise: bool = True,
                     do_sharpen: bool = True, do_contrast: bool = False,
                     model_dir: str = MODEL_DIR):
    """Full pipeline: denoise -> upscale -> sharpen -> contrast. Returns (img, notes)."""
    notes = []
    if do_denoise:
        img = denoise(img)
    if method == "fsrcnn":
        img, n = upscale_fsrcnn(img, scale, model_dir)
    else:
        img, n = upscale_lanczos(img, factor)
    if n:
        notes.append(n)
    if do_sharpen:
        img = sharpen(img)
    if do_contrast:
        img = auto_contrast(img)
    return img, notes


def encode(img: np.ndarray, fmt: str) -> bytes:
    ext = ".png" if fmt == "PNG" else ".jpg"
    params = [cv2.IMWRITE_JPEG_QUALITY, 95] if fmt == "JPG" else []
    ok, buf = cv2.imencode(ext, img, params)
    if not ok:
        raise RuntimeError("Encoding failed")
    return buf.tobytes()
