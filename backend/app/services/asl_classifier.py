import numpy as np


FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_PIPS = [3, 7, 11, 15, 19]


def classify_asl(landmarks: list[list[float]]) -> str:
    """Rule-based ASL finger-spell classifier.

    Args:
        landmarks: List of 21 [x, y, z] hand landmark coordinates from MediaPipe.

    Returns:
        Single uppercase letter A-Z, or ' ' for space gesture.
    """
    if len(landmarks) != 21:
        return ""

    lm = np.array(landmarks)

    def finger_up(tip_idx: int, pip_idx: int) -> bool:
        return lm[tip_idx][1] < lm[pip_idx][1]  # y decreases upward

    thumb_out = lm[4][0] > lm[3][0]  # Thumb extends right (right hand)
    index_up = finger_up(8, 6)
    middle_up = finger_up(12, 10)
    ring_up = finger_up(16, 14)
    pinky_up = finger_up(20, 18)

    fingers = [index_up, middle_up, ring_up, pinky_up]
    count = sum(fingers)

    # --- Core ASL finger-spell rules ---

    # A: Fist with thumb to the side
    if not any(fingers) and thumb_out:
        return "A"

    # B: All four fingers up, thumb across palm
    if all(fingers) and not thumb_out:
        return "B"

    # C: Curved hand (all fingers partially up) — simplified: all up + thumb out
    if all(fingers) and thumb_out:
        # Differentiate from B by thumb position
        thumb_tip_y = lm[4][1]
        index_base_y = lm[5][1]
        if thumb_tip_y < index_base_y:
            return "C"
        return "B"

    # D: Index up, others closed
    if index_up and not middle_up and not ring_up and not pinky_up and not thumb_out:
        return "D"

    # E: All fingers curled into fist, no thumb
    if count == 0 and not thumb_out:
        return "E"

    # F: Index and thumb touching, other three up
    if not index_up and middle_up and ring_up and pinky_up:
        return "F"

    # H: Index and middle out sideways
    if index_up and middle_up and not ring_up and not pinky_up and thumb_out:
        return "H"

    # I: Pinky up only (thumb not out)
    if not index_up and not middle_up and not ring_up and pinky_up and not thumb_out:
        return "I"

    # K: Index up, middle up, thumb between them
    if index_up and middle_up and not ring_up and not pinky_up and not thumb_out:
        return "K"

    # L: Index up, thumb out (L-shape)
    if index_up and not middle_up and not ring_up and not pinky_up and thumb_out:
        return "L"

    # N: Index and middle curled over thumb
    if count == 0 and not thumb_out:
        return "N"

    # P: Similar to K but pointed down — simplified to K variant
    # R: Index and middle crossed
    if index_up and middle_up and not ring_up and not pinky_up:
        # Check if index and middle are close together (crossed)
        dist = abs(lm[8][0] - lm[12][0])
        if dist < 0.03:
            return "R"
        return "U"

    # S: Fist with thumb over fingers
    if count == 0:
        return "S"

    # U: Index and middle up, together
    if index_up and middle_up and not ring_up and not pinky_up:
        return "U"

    # V: Index and middle up, spread apart
    # (handled by U above — V requires wider spread, hard to distinguish)

    # W: Index, middle, ring up
    if index_up and middle_up and ring_up and not pinky_up:
        return "W"

    # Y: Thumb and pinky out
    if not index_up and not middle_up and not ring_up and pinky_up and thumb_out:
        return "Y"

    # Default: space (open palm gesture or unrecognized)
    return " "
