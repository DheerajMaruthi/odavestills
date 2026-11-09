import os
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("FILE_SIGNING_SECRET", "test-secret")

from ai import imaging, prompts, quality  # noqa: E402
from core import security  # noqa: E402


def _png(img):
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _ring(bg=(240, 240, 240), size=(400, 400)):
    img = Image.new("RGB", size, bg)
    arr = np.asarray(img).copy()
    arr[150:250, 120:280] = (212, 175, 55)
    return Image.fromarray(arr)


def test_validate_upload_rejects_non_images_and_small():
    with pytest.raises(imaging.InvalidImage):
        imaging.validate_upload(b"not an image")
    with pytest.raises(imaging.InvalidImage):
        imaging.validate_upload(_png(Image.new("RGB", (100, 100))))
    assert imaging.validate_upload(_png(_ring())) == ("image/png", 400, 400)


def test_validate_request_defaults_and_errors():
    style, s = prompts.validate_request("product", "ring", "marble", {"instructions": "x" * 900})
    assert style == "marble" and s["aspect_ratio"] == "1:1" and len(s["instructions"]) == 500
    with pytest.raises(ValueError):
        prompts.validate_request("product", "crown", "marble", {})
    with pytest.raises(ValueError):
        prompts.validate_request("product", "ring", None, {})
    assert prompts.validate_request("bg_removal", "ring", None, {}) == (None, {})


def test_prompts_contain_preservation_rules():
    _, s = prompts.validate_request("model", "earrings", None, {"preset": "south_indian"})
    p = prompts.model_prompt("earrings", None, s)
    assert prompts.PRESERVATION_RULES in p and "earlobes" in p


def test_chroma_key_makes_background_transparent():
    img = _ring(bg=(0, 255, 0))
    out = Image.open(BytesIO(imaging.chroma_key(_png(img), "green")))
    assert out.mode == "RGBA"
    a = np.asarray(out.getchannel("A"))
    assert a.min() == 0 and a.max() == 255


def test_fit_aspect_crop_and_pad():
    assert imaging.fit_aspect(Image.new("RGB", (1000, 1100)), 1, 1).size == (1000, 1000)
    assert imaging.fit_aspect(Image.new("RGB", (1000, 1000)), 9, 16).size == (1000, 1778)


def test_signed_urls_verify_and_reject_tamper():
    url = security.signed_url("gen", "abc")
    q = dict(p.split("=") for p in url.split("?")[1].split("&"))
    security.verify_signature("gen", "abc", int(q["exp"]), q["sig"])
    with pytest.raises(Exception):
        security.verify_signature("gen", "other", int(q["exp"]), q["sig"])


def test_quality_local_metrics_identical_is_high():
    data = _png(_ring())
    q = quality.combine(quality.local_metrics(data, data, "product"), None, "product")
    assert q["score"] >= 9 and q["verdict"] == "high_fidelity" and not q["inspector_available"]


def test_quality_detects_colour_change():
    a = _png(_ring())
    arr = np.asarray(_ring()).copy()
    arr[150:250, 120:280] = (30, 60, 200)
    b = _png(Image.fromarray(arr))
    assert quality.local_metrics(a, b, "product")["colour_similarity"] < 0.5


def test_pixel_exact_compose_keeps_original_pixels():
    from ai import compositing
    orig = _ring(bg=(30, 30, 30))
    matte = Image.new("L", orig.size, 0)
    matte.paste(255, (120, 150, 280, 250))
    square, box = compositing.pad_square(orig)
    assert square.size == (400, 400) and box == (0, 0, 400, 400)
    piece = compositing.cutout(orig, matte)
    assert piece.mode == "RGBA" and compositing.validate_matte(matte)
    out = compositing.compose(Image.new("RGB", (800, 800), (240, 238, 232)), piece)
    centre = np.asarray(out)[400, 400]
    assert abs(int(centre[0]) - 212) < 6 and abs(int(centre[2]) - 55) < 6


def test_touching_edges_anchor():
    from ai import compositing
    m = Image.new("L", (100, 100), 0)
    m.paste(255, (30, 0, 70, 60))
    assert compositing.touching_edges(m) == {"left": False, "top": True, "right": False, "bottom": False}
