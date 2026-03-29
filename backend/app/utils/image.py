import base64

import cv2
import numpy as np


def decode_base64_image(b64_string: str) -> np.ndarray:
    """Decode a base64 JPEG string into an OpenCV BGR image."""
    img_data = base64.b64decode(b64_string)
    nparr = np.frombuffer(img_data, np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)


def encode_image_base64(image: np.ndarray, quality: int = 60) -> str:
    """Encode an OpenCV BGR image to a base64 JPEG string."""
    _, buffer = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buffer).decode("utf-8")


def resize_image(image: np.ndarray, max_dimension: int = 640) -> np.ndarray:
    """Resize image so its longest side is at most max_dimension pixels."""
    h, w = image.shape[:2]
    if max(h, w) <= max_dimension:
        return image
    scale = max_dimension / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
