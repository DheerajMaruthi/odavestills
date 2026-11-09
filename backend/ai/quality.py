"""Jewellery fidelity evaluation: local pixel metrics + an AI vision inspector comparing original vs generated."""
import asyncio
import base64
import json
import logging
import re
import uuid

import numpy as np
from PIL import Image

from ai import imaging
from core.config import AI_PROVIDER, EMERGENT_LLM_KEY, QUALITY_JUDGE_MODEL

logger = logging.getLogger(__name__)

JUDGE_PROMPT = (
    "You are a meticulous jewellery quality inspector. IMAGE 1 is the ORIGINAL product photo. IMAGE 2 is an AI-generated "
    "photo that must show the SAME physical piece ({mode}). Ignore background, lighting, props and model; compare ONLY the jewellery. "
    "Check silhouette/shape, number and arrangement of stones, stone colours, metal colour, motifs/engravings and chain/links. "
    "Be strict: an attractive image with a changed design must score low. Reply with ONLY minified JSON: "
    '{{"shape":0-10,"stones":0-10,"metal_colour":0-10,"details":0-10,"overall":0-10,"verdict":"faithful|minor_deviation|significant_deviation","issues":["short issue", "..."]}}'
)


def _hist(a: np.ndarray, mask: np.ndarray) -> np.ndarray | None:
    px = a[mask]
    if len(px) < 50:
        return None
    hsv = np.asarray(Image.fromarray(px.reshape(-1, 1, 3).astype(np.uint8)).convert("HSV")).reshape(-1, 3).astype(np.int32)
    h, s = hsv[:, 0] * 18 // 256, hsv[:, 1] * 4 // 256
    hist = np.bincount(h * 4 + s, minlength=72).astype(np.float64)
    return hist / hist.sum()


def _aspect(mask: np.ndarray) -> float | None:
    ys, xs = np.nonzero(mask)
    if len(xs) < 50:
        return None
    return (xs.max() - xs.min() + 1) / (ys.max() - ys.min() + 1)


def local_metrics(original: bytes, generated: bytes, mode: str) -> dict:
    o_img, g_img = imaging.open_image(original), imaging.open_image(generated)
    om, oa = imaging.estimate_mask(o_img)
    if mode == "bg_removal" and g_img.mode == "RGBA":
        small = g_img.resize((256, max(1, round(256 * g_img.height / g_img.width))))
        gm = np.asarray(small.getchannel("A")) > 128
        ga = np.asarray(imaging.flatten_rgb(small)).astype(np.float32)
    else:
        gm, ga = imaging.estimate_mask(g_img)
    out: dict = {}
    ho, hg = _hist(oa, om), _hist(ga, gm)
    if ho is not None and hg is not None:
        out["colour_similarity"] = round(float(np.sqrt(ho * hg).sum()), 3)
    ao, ag = _aspect(om), _aspect(gm)
    if mode != "model" and ao and ag:
        out["shape_ratio_similarity"] = round(min(ao, ag) / max(ao, ag), 3)
    return out


def _parse_json(text: str) -> dict | None:
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        return None
    try:
        data = json.loads(match.group(0))
        data["overall"] = float(data["overall"])
        return data
    except (ValueError, KeyError, TypeError):
        return None


async def ai_inspect(original: bytes, generated: bytes, mode: str) -> dict | None:
    if AI_PROVIDER == "mock" or not EMERGENT_LLM_KEY:
        return None
    from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"qa-{uuid.uuid4().hex}",
                       system_message="You are a strict jewellery QA inspector that answers in JSON only.")
        chat.with_model("gemini", QUALITY_JUDGE_MODEL)
        jpeg = imaging.encode(imaging.flatten_rgb(imaging.open_image(generated)), "JPEG")
        msg = UserMessage(text=JUDGE_PROMPT.format(mode={"model": "worn by a model", "bg_removal": "background removed"}.get(mode, "product shot")),
                          file_contents=[ImageContent(base64.b64encode(original).decode()), ImageContent(base64.b64encode(jpeg).decode())])
        return _parse_json(await asyncio.wait_for(chat.send_message(msg), timeout=90))
    except Exception as exc:
        logger.warning("AI inspection unavailable: %s", exc)
        return None


def combine(local: dict, judge: dict | None, mode: str) -> dict:
    local_vals = [v for v in local.values() if v is not None]
    local_score = round(10 * sum(local_vals) / len(local_vals), 1) if local_vals else None
    if judge and local_score is not None and mode != "model":
        score = round(0.75 * judge["overall"] + 0.25 * local_score, 1)
    elif judge:
        score = round(judge["overall"], 1)
    else:
        score = local_score
    if score is None:
        verdict, label = "unverified", "Not verified - inspect manually"
    elif score >= 8:
        verdict, label = "high_fidelity", "High design fidelity"
    elif score >= 6:
        verdict, label = "review", "Review stones & details"
    else:
        verdict, label = "altered", "Design likely altered"
    return {
        "score": score, "verdict": verdict, "label": label, "local": local,
        "inspector": judge, "inspector_available": judge is not None,
        "issues": (judge or {}).get("issues", [])[:5],
        "note": "Automated check. Always verify stones, engravings and dimensions before publishing.",
    }


async def evaluate(original: bytes, generated: bytes, mode: str) -> dict:
    local = await asyncio.to_thread(local_metrics, original, generated, mode)
    judge = await ai_inspect(original, generated, mode)
    return combine(local, judge, mode)
