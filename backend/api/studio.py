import io
import zipfile
from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field

from ai import imaging, prompts
from ai.providers import get_provider
from api.projects import owned_project
from core.config import CREDIT_COST, MAX_OUTPUTS_PER_JOB, MAX_UPLOAD_BYTES
from core.db import db
from core.deps import current_user
from core.models import GeneratedImage, GenerationJob, GenerationSetting, UploadedImage, User, new_id
from core.security import job_limiter, upload_limiter, verify_signature
from services import credits, jobs, storage
from services.serializers import image_out, job_out, upload_out

router = APIRouter(prefix="/api")
MODE_LABEL = {"product": "Product photo", "model": "Model photo", "bg_removal": "Background removal"}


# ---------- uploads ----------
@router.post("/uploads", status_code=201)
async def upload_image(file: UploadFile = File(...), project_id: Optional[str] = Form(None), user: User = Depends(current_user)):
    upload_limiter.check(user.id)
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
    try:
        ctype, w, h = imaging.validate_upload(data)
    except imaging.InvalidImage as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if project_id:
        await owned_project(project_id, user)
    ext = ctype.split("/")[1].replace("jpeg", "jpg")
    path = await storage.put_object(storage.build_path("uploads", user.id, f"{new_id()}.{ext}"), data, ctype)
    up = UploadedImage(user_id=user.id, project_id=project_id, storage_path=path, filename=(file.filename or "photo")[:120],
                       content_type=ctype, width=w, height=h, size_bytes=len(data))
    await db.uploads.insert_one(up.to_mongo())
    return upload_out(up)


# ---------- jobs ----------
class JobIn(BaseModel):
    mode: Literal["product", "model", "bg_removal"]
    upload_id: str
    category: str
    style: Optional[str] = None
    settings: dict = Field(default_factory=dict)
    output_count: int = Field(1, ge=1, le=MAX_OUTPUTS_PER_JOB)
    project_id: Optional[str] = None


async def _job_images(job: GenerationJob) -> list[GeneratedImage]:
    return [GeneratedImage.from_mongo(d) async for d in db.generated_images.find({"job_id": job.id, "is_deleted": False}).sort("created_at", 1)]


async def _owned_job(job_id: str, user: User) -> GenerationJob:
    job = GenerationJob.from_mongo(await db.generation_jobs.find_one({"_id": job_id, "user_id": user.id}))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


async def _submit(user: User, body: JobIn, parent_job_id: Optional[str] = None) -> dict:
    job_limiter.check(user.id)
    if not await db.uploads.find_one({"_id": body.upload_id, "user_id": user.id, "is_deleted": False}):
        raise HTTPException(status_code=404, detail="Upload not found")
    if body.project_id:
        await owned_project(body.project_id, user)
    try:
        style, settings = prompts.validate_request(body.mode, body.category, body.style, body.settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    count = 1 if body.mode == "bg_removal" else body.output_count
    cost = CREDIT_COST[body.mode] * count
    provider = get_provider()
    job = GenerationJob(user_id=user.id, mode=body.mode, upload_id=body.upload_id, project_id=body.project_id, category=body.category,
                        style=style, settings=settings, output_count=count, credits_reserved=cost, provider=f"{provider.name}:{provider.model}",
                        is_mock=provider.is_mock, parent_job_id=parent_job_id)
    await credits.reserve(user.id, cost, f"{MODE_LABEL[body.mode]} × {count}", job.id)
    try:
        await db.generation_jobs.insert_one(job.to_mongo())
    except Exception:
        await credits.grant(user.id, cost, "refund", "Refund - job could not be created", job.id)
        raise
    await db.generation_settings.update_one({"user_id": user.id, "mode": body.mode},
                                            {"$set": {"settings": {**settings, "category": body.category, "style": style}},
                                             "$setOnInsert": GenerationSetting(user_id=user.id, mode=body.mode).model_dump(by_alias=True, exclude={"settings", "user_id", "mode"})},
                                            upsert=True)
    jobs.enqueue(job.id)
    return job_out(job, [])


@router.post("/jobs", status_code=202)
async def create_job(body: JobIn, user: User = Depends(current_user)):
    return await _submit(user, body)


@router.get("/jobs")
async def list_jobs(mode: Optional[str] = None, limit: int = Query(30, le=100), user: User = Depends(current_user)):
    flt = {"user_id": user.id, **({"mode": mode} if mode else {})}
    jobs_ = [GenerationJob.from_mongo(d) async for d in db.generation_jobs.find(flt).sort("created_at", -1).limit(limit)]
    by_job: dict[str, list[GeneratedImage]] = {}
    async for d in db.generated_images.find({"job_id": {"$in": [j.id for j in jobs_]}, "is_deleted": False}).sort("created_at", 1):
        by_job.setdefault(d["job_id"], []).append(GeneratedImage.from_mongo(d))
    return [job_out(j, by_job.get(j.id, [])) for j in jobs_]


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, user: User = Depends(current_user)):
    job = await _owned_job(job_id, user)
    return job_out(job, await _job_images(job))


class RerunIn(BaseModel):
    output_count: Optional[int] = Field(None, ge=1, le=MAX_OUTPUTS_PER_JOB)


@router.post("/jobs/{job_id}/rerun", status_code=202)
async def rerun_job(job_id: str, body: RerunIn, user: User = Depends(current_user)):
    """Retry a failed job or create new variations with identical settings."""
    job = await _owned_job(job_id, user)
    if job.status in ("queued", "processing"):
        raise HTTPException(status_code=409, detail="Job is still running")
    count = body.output_count or max(1, job.output_count - len(job.output_ids)) if job.status != "completed" else body.output_count or job.output_count
    return await _submit(user, JobIn(mode=job.mode, upload_id=job.upload_id, category=job.category, style=job.style,
                                     settings=job.settings, output_count=count, project_id=job.project_id), parent_job_id=job.id)


@router.get("/settings/{mode}")
async def last_settings(mode: str, user: User = Depends(current_user)):
    doc = await db.generation_settings.find_one({"user_id": user.id, "mode": mode})
    return (doc or {}).get("settings", {})


# ---------- generated images ----------
@router.get("/images")
async def list_images(project_id: Optional[str] = None, category: Optional[str] = None, mode: Optional[str] = None,
                      style: Optional[str] = None, skip: int = 0, limit: int = Query(60, le=200), user: User = Depends(current_user)):
    flt: dict = {"user_id": user.id, "is_deleted": False}
    for k, v in (("project_id", project_id), ("category", category), ("mode", mode), ("style", style)):
        if v:
            flt[k] = v
    total = await db.generated_images.count_documents(flt)
    items = [image_out(GeneratedImage.from_mongo(d)) async for d in db.generated_images.find(flt).sort("created_at", -1).skip(skip).limit(limit)]
    return {"items": items, "total": total}


class ImagePatch(BaseModel):
    project_id: Optional[str] = None


@router.patch("/images/{image_id}")
async def move_image(image_id: str, body: ImagePatch, user: User = Depends(current_user)):
    if body.project_id:
        await owned_project(body.project_id, user)
    res = await db.generated_images.update_one({"_id": image_id, "user_id": user.id, "is_deleted": False}, {"$set": {"project_id": body.project_id}})
    if not res.matched_count:
        raise HTTPException(status_code=404, detail="Image not found")
    return image_out(GeneratedImage.from_mongo(await db.generated_images.find_one({"_id": image_id})))


@router.delete("/images/{image_id}")
async def delete_image(image_id: str, user: User = Depends(current_user)):
    res = await db.generated_images.update_one({"_id": image_id, "user_id": user.id, "is_deleted": False}, {"$set": {"is_deleted": True}})
    if not res.matched_count:
        raise HTTPException(status_code=404, detail="Image not found")
    return {"ok": True}


# ---------- signed file delivery ----------
@router.get("/files/{kind}/{obj_id}")
async def serve_file(kind: Literal["upload", "gen", "zip"], obj_id: str, exp: int, sig: str, download: bool = Query(False)):
    verify_signature(kind, obj_id, exp, sig)
    headers = {"Cache-Control": "private, max-age=3600"}
    if kind == "zip":
        images = [GeneratedImage.from_mongo(d) async for d in db.generated_images.find({"job_id": obj_id, "is_deleted": False})]
        if not images:
            raise HTTPException(status_code=404, detail="Nothing to download")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_STORED) as zf:
            for n, img in enumerate(images, 1):
                zf.writestr(f"auragem-{img.category}-{n}.{img.storage_path.rsplit('.', 1)[-1]}", await storage.get_object(img.storage_path))
        headers["Content-Disposition"] = f'attachment; filename="auragem-{obj_id[:8]}.zip"'
        return Response(buf.getvalue(), media_type="application/zip", headers=headers)
    coll = db.uploads if kind == "upload" else db.generated_images
    doc = await coll.find_one({"_id": obj_id})
    if not doc or doc.get("is_deleted"):
        raise HTTPException(status_code=404, detail="File not found")
    if download:
        headers["Content-Disposition"] = f'attachment; filename="auragem-{obj_id[:8]}.{doc["storage_path"].rsplit(".", 1)[-1]}"'
    return Response(await storage.get_object(doc["storage_path"]), media_type=doc["content_type"], headers=headers)
