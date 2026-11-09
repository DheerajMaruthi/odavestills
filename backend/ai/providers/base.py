from abc import ABC, abstractmethod

from ai import imaging, prompts


class ProviderError(RuntimeError):
    pass


class ImageGenerationProvider(ABC):
    """Provider-agnostic contract. Implementations only need `_render`; the rest is shared."""

    name: str = "base"
    model: str = ""
    is_mock: bool = False

    @abstractmethod
    async def _render(self, prompt: str, images: list[bytes]) -> bytes:
        """Return encoded image bytes for a prompt + reference images."""

    async def generate_image(self, prompt: str, reference: bytes | None = None) -> bytes:
        return await self._render(prompt, [reference] if reference else [])

    async def edit_image(self, image: bytes, prompt: str) -> bytes:
        return await self._render(prompt, [image])

    async def generate_variations(self, image: bytes, prompt: str, count: int) -> list[bytes]:
        return [await self._render(f"{prompt} Variation {i + 1} of {count}.", [image]) for i in range(count)]

    async def replace_background(self, image: bytes, background_prompt: str) -> bytes:
        return await self._render(
            f"Keep the jewellery exactly as it is. {prompts.PRESERVATION_RULES} Replace only the background with {background_prompt}.", [image])

    async def generate_model_photo(self, image: bytes, prompt: str, detail: bytes | None = None) -> bytes:
        return await self._render(prompt, [image] + ([detail] if detail else []))

    async def edit_image_with_detail(self, image: bytes, detail: bytes | None, prompt: str) -> bytes:
        return await self._render(prompt, [image] + ([detail] if detail else []))

    async def segment_jewellery(self, padded_square: bytes, category: str) -> bytes:
        """Return a black/white matte image aligned to the (square-padded) input."""
        return await self._render(prompts.mask_prompt(category), [padded_square])

    async def generate_background(self, prompt: str) -> bytes:
        return await self._render(prompt, [])

    async def remove_background(self, image: bytes, category: str) -> bytes:
        """Segment jewellery onto a chroma colour chosen to avoid the piece's own colours, then key it out."""
        key = "magenta" if imaging.dominant_green_fraction(imaging.open_image(image)) > 0.03 else "green"
        raw = await self._render(prompts.background_removal_prompt(category, key), [image])
        return imaging.chroma_key(raw, key)
