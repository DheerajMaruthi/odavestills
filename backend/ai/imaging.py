"""Pre-processing, segmentation, mask generation and post-processing (Pillow + NumPy)."""
from io import BytesIO

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ALLOWED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
MIN_SIDE = 256


class InvalidImage(ValueError):
    pass


def open_image(data: bytes) -> Image.Image:
    return ImageOps.exif_transpose(Image.open(BytesIO(data)))


def validate_upload(data: bytes) -> tuple[str, int, int]:
    """Validate by decoding (not by extension). Returns (content_type, width, height)."""
    try:
        probe = Image.open(BytesIO(data))
        fmt = probe.format
        probe.verify()
        img = open_image(data)
    except Exception:
        raise InvalidImage("File is not a readable image")
    if fmt not in ALLOWED_FORMATS:
        raise InvalidImage("Only JPEG, PNG and WebP images are supported")
    w, h = img.size
    if min(w, h) < MIN_SIDE:
        raise InvalidImage(f"Image is too small ({w}×{h}). Use at least {MIN_SIDE}px on each side")
    return ALLOWED_FORMATS[fmt], w, h


def flatten_rgb(img: Image.Image, bg=(255, 255, 255)) -> Image.Image:
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        canvas = Image.new("RGB", img.size, bg)
        canvas.paste(img, mask=img.split()[-1])
        return canvas
    return img.convert("RGB")


def prepare_for_model(data: bytes, max_side: int = 1536) -> bytes:
    """Normalise orientation/colour, cap resolution, mild sharpening, JPEG encode."""
    img = flatten_rgb(open_image(data))
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=3))
    return encode(img, "JPEG")


def encode(img: Image.Image, fmt: str) -> bytes:
    buf = BytesIO()
    if fmt == "JPEG":
        flatten_rgb(img).save(buf, "JPEG", quality=94, optimize=True)
    else:
        img.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def estimate_mask(img: Image.Image, size: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Jewellery foreground estimate: pixels far from the border's dominant colour."""
    img = flatten_rgb(img)
    w, h = img.size
    small = img.resize((size, max(1, round(size * h / w))))
    a = np.asarray(small).astype(np.float32)
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    dist = np.sqrt(((a - bg) ** 2).sum(-1))
    border_dist = np.sqrt(((border - bg) ** 2).sum(-1))
    thr = max(28.0, float(np.percentile(border_dist, 90)) + 12)
    m = Image.fromarray(((dist > thr) * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
    return np.asarray(m) > 127, a


def full_res_alpha(img: Image.Image) -> Image.Image:
    mask, _ = estimate_mask(img, size=512)
    alpha = Image.fromarray((mask * 255).astype(np.uint8)).resize(img.size, Image.BILINEAR)
    return alpha.filter(ImageFilter.GaussianBlur(1.2))


def dominant_green_fraction(img: Image.Image) -> float:
    mask, a = estimate_mask(img)
    px = a[mask]
    if len(px) == 0:
        return 0.0
    r, g, b = px[:, 0], px[:, 1], px[:, 2]
    return float(((g - np.maximum(r, b)) > 25).mean())


def chroma_key(data: bytes, key: str = "green") -> bytes:
    """Turn a flat chroma background into transparency with edge despill. Returns RGBA PNG."""
    a = np.asarray(flatten_rgb(open_image(data))).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    spill = g - np.maximum(r, b) if key == "green" else np.minimum(r, b) - g
    alpha = np.clip(1 - (spill - 30) / 70, 0, 1)
    edge = alpha < 1
    if key == "green":
        a[..., 1] = np.where(edge, np.minimum(g, np.maximum(r, b)), g)
    else:
        cap = g + 10
        a[..., 0] = np.where(edge, np.minimum(r, cap), r)
        a[..., 2] = np.where(edge, np.minimum(b, cap), b)
    rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
    out = Image.fromarray(rgba, "RGBA")
    bbox = out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bbox:
        pad = 24
        out = out.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(out.width, bbox[2] + pad), min(out.height, bbox[3] + pad)))
    return encode(out, "PNG")


def fit_aspect(img: Image.Image, rw: int, rh: int) -> Image.Image:
    """Centre-crop to ratio when the loss is small, otherwise pad with the edge colour (never cut jewellery)."""
    w, h = img.size
    target, cur = rw / rh, w / h
    if abs(cur / target - 1) < 0.02:
        return img
    loss = 1 - min(cur, target) / max(cur, target)
    if loss <= 0.2:
        if cur > target:
            nw = round(h * target)
            x = (w - nw) // 2
            return img.crop((x, 0, x + nw, h))
        nh = round(w / target)
        y = (h - nh) // 2
        return img.crop((0, y, w, y + nh))
    rgb = flatten_rgb(img)
    a = np.asarray(rgb)
    edge = tuple(int(v) for v in np.median(np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]]), axis=0))
    nw, nh = (round(h * target), h) if cur < target else (w, round(w / target))
    canvas = Image.new("RGB", (nw, nh), edge)
    canvas.paste(rgb, ((nw - w) // 2, (nh - h) // 2))
    return canvas


def resize_long_side(img: Image.Image, long_side: int) -> Image.Image:
    w, h = img.size
    scale = long_side / max(w, h)
    if abs(scale - 1) < 0.01:
        return img
    return img.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
