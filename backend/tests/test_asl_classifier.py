"""Tests for the rule-based ASL finger-spell classifier."""

import numpy as np
import pytest

from app.services.asl_classifier import classify_asl


def _make_landmarks(overrides: dict[int, list[float]] | None = None) -> list[list[float]]:
    """Create a default 21-landmark set (all fingers closed, fist) with optional overrides."""
    # Default: all landmarks roughly in a closed-fist position
    base = [[0.5, 0.5, 0.0] for _ in range(21)]

    # Set wrist lower (higher y)
    base[0] = [0.5, 0.8, 0.0]

    # Finger PIP joints at mid-height
    for pip in [6, 10, 14, 18]:
        base[pip] = [0.5, 0.5, 0.0]

    # Finger tips below PIPs (fingers closed — higher y = lower on screen)
    for tip in [8, 12, 16, 20]:
        base[tip] = [0.5, 0.6, 0.0]

    # Thumb: tip close to palm (not extended)
    base[3] = [0.45, 0.5, 0.0]
    base[4] = [0.40, 0.5, 0.0]  # Thumb tip left of MCP = not extended right

    if overrides:
        for idx, coords in overrides.items():
            base[idx] = coords

    return base


def _fingers_up_landmarks(
    index: bool = False,
    middle: bool = False,
    ring: bool = False,
    pinky: bool = False,
    thumb_out: bool = False,
) -> list[list[float]]:
    """Helper to build landmarks with specific fingers up/down."""
    lm = _make_landmarks()

    # Fingers up: tip y < pip y (lower value = higher on screen)
    if index:
        lm[8] = [0.5, 0.3, 0.0]
    if middle:
        lm[12] = [0.5, 0.3, 0.0]
    if ring:
        lm[16] = [0.5, 0.3, 0.0]
    if pinky:
        lm[20] = [0.5, 0.3, 0.0]

    # Thumb out: tip x > mcp x
    if thumb_out:
        lm[3] = [0.45, 0.5, 0.0]
        lm[4] = [0.55, 0.5, 0.0]
    else:
        lm[3] = [0.45, 0.5, 0.0]
        lm[4] = [0.40, 0.5, 0.0]

    return lm


class TestClassifyASL:
    def test_empty_landmarks(self):
        assert classify_asl([]) == ""

    def test_wrong_landmark_count(self):
        assert classify_asl([[0, 0, 0]] * 10) == ""
        assert classify_asl([[0, 0, 0]] * 22) == ""

    def test_letter_a(self):
        """A: fist with thumb to the side (thumb out, no fingers up)."""
        lm = _fingers_up_landmarks(thumb_out=True)
        assert classify_asl(lm) == "A"

    def test_letter_e(self):
        """E: all fingers curled, no thumb out."""
        lm = _fingers_up_landmarks()  # all closed, thumb not out
        assert classify_asl(lm) == "E"

    def test_letter_d(self):
        """D: index up, others closed, thumb not out."""
        lm = _fingers_up_landmarks(index=True)
        assert classify_asl(lm) == "D"

    def test_letter_i(self):
        """I: pinky up only."""
        lm = _fingers_up_landmarks(pinky=True)
        assert classify_asl(lm) == "I"

    def test_letter_l(self):
        """L: index up + thumb out (L-shape)."""
        lm = _fingers_up_landmarks(index=True, thumb_out=True)
        assert classify_asl(lm) == "L"

    def test_letter_f(self):
        """F: index down, middle+ring+pinky up."""
        lm = _fingers_up_landmarks(middle=True, ring=True, pinky=True)
        assert classify_asl(lm) == "F"

    def test_letter_w(self):
        """W: index + middle + ring up, pinky down."""
        lm = _fingers_up_landmarks(index=True, middle=True, ring=True)
        assert classify_asl(lm) == "W"

    def test_letter_y(self):
        """Y: thumb and pinky out, others closed."""
        lm = _fingers_up_landmarks(pinky=True, thumb_out=True)
        assert classify_asl(lm) == "Y"

    def test_letter_k(self):
        """K: index + middle up, thumb not out."""
        lm = _fingers_up_landmarks(index=True, middle=True)
        # Need tips spread apart (not crossed) for K vs R
        lm[8] = [0.45, 0.3, 0.0]
        lm[12] = [0.55, 0.3, 0.0]
        assert classify_asl(lm) == "K"

    def test_21_landmarks_required(self):
        """Classifier requires exactly 21 landmarks."""
        assert classify_asl([[0.5, 0.5, 0.0]] * 20) == ""
        assert classify_asl([[0.5, 0.5, 0.0]] * 21) != ""
