from core.models import GeneratedImage, GenerationJob, Project, UploadedImage
from core.security import signed_url


def image_out(img: GeneratedImage) -> dict:
    return {
        **img.model_dump(exclude={"storage_path", "user_id", "is_deleted"}),
        "url": signed_url("gen", img.id),
        "download_url": signed_url("gen", img.id, download=True),
        "original_url": signed_url("upload", img.upload_id),
    }


def upload_out(up: UploadedImage) -> dict:
    return {**up.model_dump(exclude={"storage_path", "user_id", "is_deleted"}), "url": signed_url("upload", up.id)}


def job_out(job: GenerationJob, images: list[GeneratedImage]) -> dict:
    return {
        **job.model_dump(exclude={"user_id"}),
        "outputs": [image_out(i) for i in images],
        "original_url": signed_url("upload", job.upload_id),
        "zip_url": signed_url("zip", job.id, download=True) if images else None,
        "credits_charged": job.credits_reserved - job.credits_refunded if job.status not in ("queued", "processing") else None,
    }


def project_out(p: Project, image_count: int = 0, cover: GeneratedImage | None = None) -> dict:
    return {**p.model_dump(exclude={"user_id"}), "image_count": image_count,
            "cover_url": signed_url("gen", cover.id) if cover else None}
