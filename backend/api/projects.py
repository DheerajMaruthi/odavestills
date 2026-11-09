import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ai.prompts import CATEGORIES
from core.db import db
from core.deps import current_user
from core.models import GeneratedImage, Project, User
from services.serializers import project_out

router = APIRouter(prefix="/api/projects")


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field("", max_length=400)
    category: Optional[str] = None


def _check_category(cat: Optional[str]):
    if cat and cat not in CATEGORIES:
        raise HTTPException(status_code=422, detail="Unknown jewellery category")


async def owned_project(project_id: str, user: User) -> Project:
    p = Project.from_mongo(await db.projects.find_one({"_id": project_id, "user_id": user.id, "is_deleted": False}))
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


async def _with_stats(p: Project) -> dict:
    live = {"project_id": p.id, "is_deleted": False}
    cover = GeneratedImage.from_mongo(await db.generated_images.find_one(live, sort=[("created_at", -1)]))
    return project_out(p, await db.generated_images.count_documents(live), cover)


@router.get("")
async def list_projects(q: str = "", category: Optional[str] = None, limit: int = Query(100, le=200),
                        user: User = Depends(current_user)):
    flt: dict = {"user_id": user.id, "is_deleted": False}
    if q.strip():
        flt["name"] = {"$regex": re.escape(q.strip()), "$options": "i"}
    if category:
        flt["category"] = category
    docs = db.projects.find(flt).sort("created_at", -1).limit(limit)
    return [await _with_stats(Project.from_mongo(d)) async for d in docs]


@router.post("", status_code=201)
async def create_project(body: ProjectIn, user: User = Depends(current_user)):
    _check_category(body.category)
    p = Project(user_id=user.id, **body.model_dump())
    await db.projects.insert_one(p.to_mongo())
    return project_out(p)


@router.get("/{project_id}")
async def get_project(project_id: str, user: User = Depends(current_user)):
    return await _with_stats(await owned_project(project_id, user))


@router.patch("/{project_id}")
async def update_project(project_id: str, body: ProjectIn, user: User = Depends(current_user)):
    _check_category(body.category)
    await owned_project(project_id, user)
    await db.projects.update_one({"_id": project_id}, {"$set": body.model_dump()})
    return await get_project(project_id, user)


@router.delete("/{project_id}")
async def delete_project(project_id: str, delete_images: bool = False, user: User = Depends(current_user)):
    await owned_project(project_id, user)
    change = {"is_deleted": True} if delete_images else {"project_id": None}
    await db.generated_images.update_many({"project_id": project_id, "user_id": user.id}, {"$set": change})
    await db.projects.update_one({"_id": project_id, "user_id": user.id}, {"$set": {"is_deleted": True}})
    return {"ok": True}
