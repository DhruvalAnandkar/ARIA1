import base64
import time

import google.generativeai as genai

from app.config import settings
from app.services.vision.base import VisionProvider, VisionResult

OBSTACLE_PROMPT = (
    "You are a navigation assistant for a blind person. "
    "Describe ONLY immediate obstacles or hazards visible. "
    "Use under 8 words. Examples: 'Step down ahead', "
    "'Person walking toward you', 'Door on your right', "
    "'Curb ahead, step up'. If safe: say 'Path is clear'. "
    "Also classify severity as one of: clear, caution, danger."
    "Format: SEVERITY|description"
)

SENTENCE_PROMPT_TEMPLATE = (
    "A deaf/mute person is signing. Detected letters: '{letters}'. "
    "Their facial expression shows: {emotion}. "
    "Complete this into ONE natural sentence they are trying to say. "
    "If emotion is 'fear' or 'sad', make it sound urgent. "
    "Return ONLY the sentence. No quotes. No explanation."
)

TRANSLATE_PROMPT_TEMPLATE = (
    "Translate this to {language}. Return ONLY the translation: '{text}'"
)


class GeminiProvider(VisionProvider):
    name = "gemini"

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    async def detect_obstacle(self, image_b64: str) -> VisionResult:
        start = time.monotonic()
        image_data = base64.b64decode(image_b64)
        response = self._model.generate_content([
            OBSTACLE_PROMPT,
            {"mime_type": "image/jpeg", "data": image_data},
        ])
        latency = (time.monotonic() - start) * 1000
        raw = response.text.strip()

        severity, text = self._parse_obstacle_response(raw)
        return VisionResult(
            text=text, provider=self.name, latency_ms=latency, severity=severity
        )

    async def build_sentence(self, partial_text: str, emotion: str) -> VisionResult:
        start = time.monotonic()
        prompt = SENTENCE_PROMPT_TEMPLATE.format(letters=partial_text, emotion=emotion)
        response = self._model.generate_content(prompt)
        latency = (time.monotonic() - start) * 1000
        return VisionResult(
            text=response.text.strip(), provider=self.name, latency_ms=latency
        )

    async def translate(self, text: str, target_lang: str) -> VisionResult:
        if target_lang == "en":
            return VisionResult(text=text, provider=self.name, latency_ms=0)
        start = time.monotonic()
        prompt = TRANSLATE_PROMPT_TEMPLATE.format(language=target_lang, text=text)
        response = self._model.generate_content(prompt)
        latency = (time.monotonic() - start) * 1000
        return VisionResult(
            text=response.text.strip(), provider=self.name, latency_ms=latency
        )

    async def health_check(self) -> bool:
        try:
            response = self._model.generate_content("Say 'ok'")
            return bool(response.text)
        except Exception:
            return False

    @staticmethod
    def _parse_obstacle_response(raw: str) -> tuple[str, str]:
        if "|" in raw:
            parts = raw.split("|", 1)
            severity = parts[0].strip().lower()
            text = parts[1].strip()
            if severity in ("clear", "caution", "danger"):
                return severity, text
        # Fallback: infer severity from keywords
        lower = raw.lower()
        if any(w in lower for w in ("danger", "stop", "careful", "watch out")):
            return "danger", raw
        if any(w in lower for w in ("caution", "ahead", "step", "curb", "person")):
            return "caution", raw
        return "clear", raw
