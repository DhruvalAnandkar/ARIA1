from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class VisionResult:
    text: str
    provider: str
    latency_ms: float
    severity: str = "clear"  # "clear", "caution", "danger"
    confidence: float | None = None


class VisionProvider(ABC):
    """Abstract base class for all vision/LLM providers."""

    name: str = "base"

    @abstractmethod
    async def detect_obstacle(self, image_b64: str) -> VisionResult:
        """Analyze image for obstacles. Return short warning text."""
        ...

    @abstractmethod
    async def build_sentence(self, partial_text: str, emotion: str) -> VisionResult:
        """Complete partial ASL text into a natural sentence."""
        ...

    @abstractmethod
    async def translate(self, text: str, target_lang: str) -> VisionResult:
        """Translate text to target language."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if this provider is currently available."""
        ...
