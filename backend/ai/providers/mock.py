import hashlib

from PIL import Image, ImageDraw

from ai import imaging
from ai.providers.base import ImageGenerationProvider

LABEL = "DEVELOPMENT MOCK - NOT AI GENERATED"


class MockImageProvider(ImageGenerationProvider):
    """Deterministic, clearly watermarked stand-in used when no AI key is configured."""

    name = "mock"
    model = "mock"
    is_mock = True

    def _stamp(self, img: Image.Image) -> Image.Image:
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, img.width, 34), fill=(28, 25, 23))
        draw.text((12, 10), LABEL, fill=(212, 175, 55))
        return img

    async def _render(self, prompt: str, images: list[bytes]) -> bytes:
        tone = hashlib.md5(prompt.encode()).digest()
        bg = (200 + tone[0] % 50, 190 + tone[1] % 50, 175 + tone[2] % 50)
        canvas = Image.new("RGB", (1024, 1024), bg)
        if images:
            src = imaging.open_image(images[0]).convert("RGBA")
            src.thumbnail((760, 760))
            canvas.paste(src, ((1024 - src.width) // 2, (1024 - src.height) // 2), imaging.full_res_alpha(src))
        return imaging.encode(self._stamp(canvas), "JPEG")

    async def segment_jewellery(self, padded_square: bytes, category: str) -> bytes:
        mask, _ = imaging.estimate_mask(imaging.open_image(padded_square), size=1024)
        return imaging.encode(Image.fromarray((mask * 255).astype("uint8")).convert("RGB"), "PNG")

    async def remove_background(self, image: bytes, category: str) -> bytes:
        img = imaging.open_image(image).convert("RGBA")
        img.putalpha(imaging.full_res_alpha(img))
        return imaging.encode(self._stamp(img), "PNG")
