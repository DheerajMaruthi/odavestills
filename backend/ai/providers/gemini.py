import asyncio
import base64
import uuid

from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage

from ai.providers.base import ImageGenerationProvider, ProviderError

SYSTEM = ("You are an expert jewellery photography engine. You always return an image. "
          "Faithfully preserving the client's real jewellery design is your highest priority.")


class GeminiImageProvider(ImageGenerationProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str, timeout_s: int):
        if not api_key:
            raise ProviderError("EMERGENT_LLM_KEY is not configured")
        self.api_key, self.model, self.timeout_s = api_key, model, timeout_s

    async def _render(self, prompt: str, images: list[bytes]) -> bytes:
        chat = LlmChat(api_key=self.api_key, session_id=f"auragem-{uuid.uuid4().hex}", system_message=SYSTEM)
        chat.with_model("gemini", self.model).with_params(modalities=["image", "text"])
        msg = UserMessage(text=prompt, file_contents=[ImageContent(base64.b64encode(b).decode()) for b in images])
        try:
            text, out = await asyncio.wait_for(chat.send_message_multimodal_response(msg), timeout=self.timeout_s)
        except asyncio.TimeoutError:
            raise ProviderError("The AI provider timed out")
        if not out:
            raise ProviderError(f"The AI provider returned no image. {(text or '')[:160]}".strip())
        return base64.b64decode(out[0]["data"])
