"""Pixel-exact pipeline: AI segmentation matte -> cut out ORIGINAL pixels -> enhance -> composite onto an AI studio plate."""
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter

from ai import imaging

PAD_COLOUR = (128, 128, 128)


def pad_square(img: Image.Image) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Pad to a square so the model's (square) output maps back to the original pixel grid."""
    w, h = img.size
    side = max(w, h)
    canvas = Image.new("RGB", (side, side), PAD_COLOUR)
    box = ((side - w) // 2, (side - h) // 2, (side - w) // 2 + w, (side - h) // 2 + h)
    canvas.paste(imaging.flatten_rgb(img), box[:2])
    return canvas, box


def matte_from_render(raw: bytes, padded_side: int, box: tuple[int, int, int, int]) -> Image.Image:
    m = imaging.flatten_rgb(imaging.open_image(raw)).convert("L").resize((padded_side, padded_side), Image.LANCZOS)
    m = m.crop(box)
    m = m.point(lambda v: 0 if v < 70 else (255 if v > 185 else int((v - 70) * 255 / 115)))
    m = m.filter(ImageFilter.MedianFilter(3))
    k = 3 if max(m.size) < 2000 else 5
    return m.filter(ImageFilter.MinFilter(k))  # pull edges in to drop background halo


def touching_edges(matte: Image.Image, tol: int = 3) -> dict:
    bbox = matte.point(lambda v: 255 if v > 60 else 0).getbbox()
    if not bbox:
        return {}
    w, h = matte.size
    return {"left": bbox[0] <= tol, "top": bbox[1] <= tol, "right": bbox[2] >= w - tol, "bottom": bbox[3] >= h - tol}


def validate_matte(m: Image.Image) -> bool:
    a = np.asarray(m) > 128
    frac = a.mean()
    return 0.003 < frac < 0.92


def cutout(original: Image.Image, matte: Image.Image, pad: int = 6) -> Image.Image:
    rgba = imaging.flatten_rgb(original).convert("RGBA")
    rgba.putalpha(matte.filter(ImageFilter.GaussianBlur(0.6)))
    bbox = matte.point(lambda v: 255 if v > 20 else 0).getbbox()
    if not bbox:
        return rgba
    return rgba.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(rgba.width, bbox[2] + pad), min(rgba.height, bbox[3] + pad)))


def enhance(piece: Image.Image) -> Image.Image:
    """Gentle studio finish on the real pixels: no geometry changes, only tone, clarity and sparkle."""
    alpha = piece.getchannel("A")
    rgb = piece.convert("RGB")
    rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
    rgb = ImageEnhance.Color(rgb).enhance(1.06)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def detail_reference(original: Image.Image, matte: Image.Image, max_side: int = 1536) -> Image.Image:
    bbox = matte.point(lambda v: 255 if v > 20 else 0).getbbox() or (0, 0, *original.size)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    p = int(max(w, h) * 0.06)
    crop = imaging.flatten_rgb(original).crop((max(0, bbox[0] - p), max(0, bbox[1] - p), min(original.width, bbox[2] + p), min(original.height, bbox[3] + p)))
    crop.thumbnail((max_side, max_side), Image.LANCZOS)
    return crop


def _shadow(alpha: Image.Image, blur: float, opacity: float, offset: tuple[int, int], size) -> Image.Image:
    layer = Image.new("L", size, 0)
    layer.paste(alpha.point(lambda v: int(v * opacity)), offset)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def compose(plate: Image.Image, piece: Image.Image, edges: dict | None = None, fill: float = 0.64) -> Image.Image:
    """Place the real piece on the plate. Parts cut off by the original frame stay anchored to the frame edge."""
    edges = edges or {}
    W, H = plate.size
    if edges.get("top") or edges.get("bottom") or edges.get("left") or edges.get("right"):
        fill = 0.82
    scale = min(fill * W / piece.width, fill * H / piece.height)
    piece = piece.resize((max(1, round(piece.width * scale)), max(1, round(piece.height * scale))), Image.LANCZOS)
    x, y = (W - piece.width) // 2, (H - piece.height) // 2
    if edges.get("top") and not edges.get("bottom"):
        y = 0
    elif edges.get("bottom") and not edges.get("top"):
        y = H - piece.height
    if edges.get("left") and not edges.get("right"):
        x = 0
    elif edges.get("right") and not edges.get("left"):
        x = W - piece.width
    alpha = piece.getchannel("A")
    base = imaging.flatten_rgb(plate)
    darkness = 1 - np.asarray(base.convert("L")).mean() / 255
    soft_op = 0.30 - 0.15 * darkness
    s = max(W, H)
    shadow = ImageChops.lighter(
        _shadow(alpha, s * 0.018, soft_op, (x + round(s * 0.006), y + round(s * 0.016)), (W, H)),
        _shadow(alpha, s * 0.004, soft_op * 0.9, (x, y + round(s * 0.004)), (W, H)),
    )
    base = Image.composite(Image.new("RGB", (W, H), (20, 16, 12)), base, shadow)
    base.paste(piece, (x, y), alpha)
    return base
