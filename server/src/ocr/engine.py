"""EasyOCR 래퍼.

게임 스크린샷에서 텍스트를 추출하기 위한 OCR 엔진.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


# EasyOCR는 무거우므로 lazy import
_reader = None


def _get_reader():
    """EasyOCR Reader를 lazy로 생성."""
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["ko", "en"], gpu=False)
    return _reader


def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    """OCR 전처리: 그레이스케일 + 대비 강화 + 샤프닝."""
    gray = image.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(2.0)
    sharpened = enhanced.filter(ImageFilter.SHARPEN)
    return sharpened


def extract_all_text(image: Image.Image) -> list[tuple[str, float]]:
    """이미지에서 모든 텍스트를 추출.

    Returns:
        [(텍스트, 신뢰도), ...] 리스트 (위에서 아래 순서)
    """
    reader = _get_reader()
    processed = preprocess_for_ocr(image)
    img_array = np.array(processed)

    results = reader.readtext(img_array, detail=1, paragraph=False)

    if not results:
        return []

    # y좌표 기준 정렬 (위에서 아래로)
    results.sort(key=lambda r: r[0][0][1])

    return [(r[1], r[2]) for r in results]
