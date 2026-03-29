"""Tests for the vision fallback system."""

import pytest

from app.services.vision.base import VisionProvider, VisionResult


class MockProvider(VisionProvider):
    """Mock vision provider for testing."""

    def __init__(self, name: str, should_fail: bool = False):
        self._name = name
        self._should_fail = should_fail
        self.call_count = 0

    @property
    def name(self) -> str:
        return self._name

    async def detect_obstacle(self, image_b64: str) -> VisionResult:
        self.call_count += 1
        if self._should_fail:
            raise Exception(f"{self._name} failed")
        return VisionResult(
            text="Clear path ahead",
            severity="clear",
            provider=self._name,
            latency_ms=100,
        )

    async def build_sentence(self, raw_letters: str, emotion: str) -> VisionResult:
        self.call_count += 1
        if self._should_fail:
            raise Exception(f"{self._name} failed")
        return VisionResult(
            text=f"Sentence from {raw_letters}",
            provider=self._name,
            latency_ms=50,
        )

    async def translate(self, text: str, target_lang: str) -> VisionResult:
        self.call_count += 1
        if self._should_fail:
            raise Exception(f"{self._name} failed")
        return VisionResult(
            text=f"Translated: {text}",
            provider=self._name,
            latency_ms=75,
        )

    async def health_check(self) -> bool:
        return not self._should_fail


class TestVisionResult:
    def test_vision_result_fields(self):
        result = VisionResult(
            text="Obstacle detected: chair",
            severity="caution",
            provider="gemini",
            latency_ms=150,
        )
        assert result.text == "Obstacle detected: chair"
        assert result.severity == "caution"
        assert result.provider == "gemini"
        assert result.latency_ms == 150

    def test_vision_result_defaults(self):
        result = VisionResult(text="test", provider="mock", latency_ms=10)
        assert result.severity == "clear"


class TestMockProvider:
    @pytest.mark.asyncio
    async def test_healthy_provider(self):
        provider = MockProvider("test")
        result = await provider.detect_obstacle("base64data")
        assert result.provider == "test"
        assert result.text == "Clear path ahead"
        assert provider.call_count == 1

    @pytest.mark.asyncio
    async def test_failing_provider(self):
        provider = MockProvider("broken", should_fail=True)
        with pytest.raises(Exception, match="broken failed"):
            await provider.detect_obstacle("base64data")

    @pytest.mark.asyncio
    async def test_health_check(self):
        healthy = MockProvider("ok")
        broken = MockProvider("fail", should_fail=True)
        assert await healthy.health_check() is True
        assert await broken.health_check() is False

    @pytest.mark.asyncio
    async def test_build_sentence(self):
        provider = MockProvider("test")
        result = await provider.build_sentence("HELLO", "happy")
        assert "HELLO" in result.text

    @pytest.mark.asyncio
    async def test_translate(self):
        provider = MockProvider("test")
        result = await provider.translate("Hello", "es")
        assert "Hello" in result.text
