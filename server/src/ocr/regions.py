"""게임 UI 스크린 영역 정의/크롭.

다크워 서바이벌 '상세' 다이얼로그 영역을 크롭한다.
해상도별로 다른 다이얼로그 위치를 사용한다.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image


@dataclass
class Region:
    """화면 내 사각형 영역."""
    x: int
    y: int
    width: int
    height: int

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        """PIL crop용 (left, upper, right, lower)."""
        return (self.x, self.y, self.x + self.width, self.y + self.height)


def crop_dialog(image: Image.Image) -> Image.Image:
    """'상세' 다이얼로그 영역만 크롭.

    해상도에 따라 다이얼로그 위치를 자동 감지한다.
    크롭에 실패하면 원본 이미지를 그대로 반환한다.
    """
    w, h = image.size
    aspect = h / w if w > 0 else 1

    if aspect > 1.5:
        # 세로 모바일 (1080x2340, 1080x1920 등)
        # 다이얼로그: x=55~700, y=280~930 (1080x2340 기준 비율)
        dx = int(w * 0.04)
        dy = int(h * 0.12)
        dw = int(w * 0.94)
        dh = int(h * 0.52)
        return image.crop((dx, dy, dx + dw, dy + dh))
    else:
        # 가로 PC/에뮬레이터
        # 다이얼로그가 화면 중앙~우측에 위치
        dx = int(w * 0.10)
        dy = int(h * 0.02)
        dw = int(w * 0.70)
        dh = int(h * 0.92)
        return image.crop((dx, dy, dx + dw, dy + dh))
