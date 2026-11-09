"""Background generation worker: preprocessing -> generation -> post-processing -> quality -> storage -> credit settlement."""
import asyncio
import logging

from PIL import Image

from ai import compositing, imaging, prompts, quality
from ai.providers import ProviderError, get_provider
from core.config import CREDIT_COST, MAX_CONCURRENT_JOBS, MAX_PROVIDER_ATTEMPTS, MAX_QUALITY_RETRIES, QUALITY_RETRY_BELOW
from core.db import db
from core.models import GeneratedImage, GenerationJob, UploadedImage, new_id, now_iso
from services import credits, storage

logger = logging.getLogger(__name__)
_tasks: set[asyncio.Task] = set()
_sem = asyncio.Semaphore(MAX_CONCURRENT_JOBS)


def enqueue(job_id: str) -> None:
    task = asyncio.create_task(_run(job_id))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


async def _update(job_id: str, **fields) -> None:
    await db.generation_jobs.update_one({"_id": job_id}, {"$set": fields})


class JobContext:
    """Per-job cache: the full-resolution original, the model-ready copy and a lazily computed AI matte."""

    def __init__(self, job: GenerationJob, original_bytes: bytes):
        self.job = job
        self.original = imaging.flatten_rgb(imaging.open_image(original_bytes))
        self.original.thumbnail((3072, 3072), Image.LANCZOS)
        self.prepared = imaging.prepare_for_model(original_bytes, max_side=2048)
        self.edges: dict = {}
        self._matte = None
        self._matte_done = False

    async def matte(self):
        if not self._matte_done:
            self._matte_done = True
            try:
                small = self.original.copy()
                small.thumbnail((2048, 2048), Image.LANCZOS)
                square, box = compositing.pad_square(small)
                raw = await get_provider().segment_jewellery(imaging.encode(square, "JPEG"), self.job.category)
                m = await asyncio.to_thread(compositing.matte_from_render, raw, square.width, box)
                if m.size != self.original.size:
                    m = m.resize(self.original.size, Image.LANCZOS)
                if compositing.validate_matte(m):
                    self._matte, self.edges = m, compositing.touching_edges(m)
            except Exception as exc:
                logger.warning("job %s segmentation failed: %s", self.job.id, exc)
        return self._matte

    async def detail(self) -> bytes | None:
        m = await self.matte()
        return imaging.encode(compositing.detail_reference(self.original, m), "JPEG") if m is not None else None


def _plate(job: GenerationJob, raw: bytes) -> Image.Image:
    rw, rh = prompts.ASPECT_RATIOS[job.settings["aspect_ratio"]]
    img = imaging.flatten_rgb(imaging.open_image(raw))
    return imaging.resize_long_side(imaging.fit_aspect(img, rw, rh), int(job.settings["dimensions"]))


async def _render(ctx: JobContext, index: int) -> tuple[bytes, bool]:
    """Return (image bytes, pixel_exact)."""
    job, provider = ctx.job, get_provider()
    if job.mode == "bg_removal":
        m = await ctx.matte()
        if m is not None:
            return imaging.encode(compositing.cutout(ctx.original, m), "PNG"), True
        return await provider.remove_background(ctx.prepared, job.category), False
    if job.mode == "model":
        prompt = prompts.model_prompt(job.category, job.style, job.settings, index, job.output_count)
        return await provider.generate_model_photo(ctx.prepared, prompt, await ctx.detail()), False
    if job.settings.get("accuracy") == "exact":
        m = await ctx.matte()
        if m is None:
            raise ProviderError("Could not isolate the jewellery precisely. Try a photo on a plainer surface, or the AI re-shoot mode.")
        plate_raw = await provider.generate_background(prompts.plate_prompt(job.category, job.style, job.settings, index, job.output_count))
        plate = await asyncio.to_thread(_plate, job, plate_raw)
        piece = compositing.enhance(compositing.cutout(ctx.original, m))
        return imaging.encode(await asyncio.to_thread(compositing.compose, plate, piece, ctx.edges), "JPEG"), True
    prompt = prompts.product_prompt(job.category, job.style, job.settings, index, job.output_count)
    return await provider.edit_image_with_detail(ctx.prepared, await ctx.detail(), prompt), False


def _postprocess(job: GenerationJob, raw: bytes) -> tuple[bytes, str, int, int]:
    img = imaging.open_image(raw)
    if job.mode == "bg_removal":
        return raw, "image/png", img.width, img.height
    rw, rh = prompts.ASPECT_RATIOS[job.settings["aspect_ratio"]]
    img = imaging.resize_long_side(imaging.fit_aspect(imaging.flatten_rgb(img), rw, rh), int(job.settings["dimensions"]))
    return imaging.encode(img, "JPEG"), "image/jpeg", img.width, img.height


EXACT_NOTE = ("Pixel-exact: the jewellery is your original photo's own pixels with only a tone and clarity finish. "
              "Check the cut-out edges, especially thin chains.")


async def _generate_one(ctx: JobContext, index: int) -> tuple[bytes, str, int, int, dict]:
    """Retries provider errors; for AI re-shoots, regenerates while fidelity is below threshold and keeps the best."""
    job = ctx.job
    best, last_error, errors, q_retries = None, None, 0, 0
    while True:
        try:
            raw, exact = await _render(ctx, index)
            data, ctype, w, h = await asyncio.to_thread(_postprocess, job, raw)
        except Exception as exc:
            last_error, errors = exc, errors + 1
            logger.warning("job %s output %s attempt %s failed: %s", job.id, index, errors, exc)
            if errors >= MAX_PROVIDER_ATTEMPTS:
                break
            await asyncio.sleep(2 * errors)
            continue
        q = await quality.evaluate(ctx.prepared, data, job.mode)
        q["pixel_exact"] = exact
        if exact:
            q["note"] = EXACT_NOTE
            if not q["inspector_available"]:
                q.update(score=None, verdict="unverified", label="Original pixels - check cut-out edges")
        if best is None or (q["score"] or 0) > (best[4]["score"] or 0):
            best = (data, ctype, w, h, q)
        if exact or q["score"] is None or q["score"] >= QUALITY_RETRY_BELOW or q_retries >= MAX_QUALITY_RETRIES or get_provider().is_mock:
            break
        q_retries += 1
        await _update(job.id, stage=f"Fidelity {q['score']}/10 too low - regenerating image {index + 1} (attempt {q_retries + 1})")
    if best is None:
        raise last_error or RuntimeError("Generation failed")
    best[4]["attempts"] = errors + q_retries + 1
    return best


async def _run(job_id: str) -> None:
    async with _sem:
        job = GenerationJob.from_mongo(await db.generation_jobs.find_one({"_id": job_id}))
        if not job or job.status not in ("queued", "processing"):
            return
        try:
            await _update(job_id, status="processing", stage="Preparing your photo", progress=5)
            upload = UploadedImage.from_mongo(await db.uploads.find_one({"_id": job.upload_id}))
            ctx = await asyncio.to_thread(JobContext, job, await storage.get_object(upload.storage_path))
        except Exception as exc:
            logger.exception("job %s preprocessing failed", job_id)
            await _settle(job, [], [f"Could not read the uploaded photo: {exc}"])
            return
        if job.mode == "bg_removal" or job.settings.get("accuracy") == "exact":
            await _update(job_id, stage="Isolating the jewellery precisely", progress=8)
        outputs, failures = [], []
        for i in range(job.output_count):
            await _update(job_id, stage=f"Generating image {i + 1} of {job.output_count}",
                          progress=10 + int(80 * i / job.output_count))
            try:
                data, ctype, w, h, q = await _generate_one(ctx, i)
                ext = "png" if ctype == "image/png" else "jpg"
                path = await storage.put_object(storage.build_path("generated", job.user_id, f"{new_id()}.{ext}"), data, ctype)
                img = GeneratedImage(user_id=job.user_id, job_id=job.id, upload_id=job.upload_id, project_id=job.project_id,
                                     mode=job.mode, category=job.category, style=job.style, storage_path=path, content_type=ctype,
                                     width=w, height=h, quality=q, is_mock=get_provider().is_mock)
                await db.generated_images.insert_one(img.to_mongo())
                outputs.append(img.id)
                await db.generation_jobs.update_one({"_id": job_id}, {"$push": {"output_ids": img.id}})
            except Exception as exc:
                logger.exception("job %s output %s failed", job_id, i)
                failures.append(_friendly(exc))
        await _settle(job, outputs, failures)


def _friendly(exc: Exception) -> str:
    text = str(exc)
    if "Budget has been exceeded" in text or "RateLimitError" in text:
        return "The AI service balance is exhausted. The app owner needs to top up the AI key balance, then retry."
    return text[:200] or "Generation failed"


async def _settle(job: GenerationJob, outputs: list[str], failures: list[str]) -> None:
    failed = job.output_count - len(outputs)
    refund = failed * CREDIT_COST[job.mode]
    if refund:
        await credits.grant(job.user_id, refund, "refund", f"Refund for {failed} failed image(s)", job.id)
    if outputs:
        await db.users.update_one({"_id": job.user_id}, {"$inc": {"total_generated": len(outputs)}})
    status = "completed" if not failed else ("partial" if outputs else "failed")
    stage = {"completed": "Completed", "partial": "Partially completed", "failed": "Failed"}[status]
    await _update(job.id, status=status, stage=stage, progress=100, credits_refunded=refund, failures=failures,
                  error=failures[0] if failures and not outputs else None, finished_at=now_iso())


async def recover_interrupted_jobs() -> None:
    """On boot, resume queued jobs; jobs interrupted mid-run are settled (unfinished outputs refunded)."""
    async for doc in db.generation_jobs.find({"status": "processing"}):
        job = GenerationJob.from_mongo(doc)
        await _settle(job, job.output_ids, ["Interrupted by a server restart - please retry"])
    async for doc in db.generation_jobs.find({"status": "queued"}, {"_id": 1}):
        enqueue(doc["_id"])
