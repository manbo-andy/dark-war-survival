"""Player and PowerReading data models."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Optional


@dataclass
class Player:
    """플레이어 등록 정보."""

    id: str
    name: str
    alliance: str = ""
    server: int = 510
    is_enemy: bool = False
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    active: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Player:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class PowerReading:
    """전투력 시계열 데이터 (게임 '상세' 화면 6개 항목 1:1 매핑)."""

    date: str  # ISO format YYYY-MM-DD
    player_id: str
    total_power: int = 0
    building_power: int = 0
    tech_power: int = 0
    troop_power: int = 0
    hero_power: int = 0
    vehicle_power: int = 0
    kill_count: int = 0
    source: str = "manual"  # manual | ocr

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> PowerReading:
        int_fields = {
            "total_power", "building_power", "tech_power", "troop_power",
            "hero_power", "vehicle_power", "kill_count",
        }
        cleaned = {}
        for k, v in data.items():
            if k not in cls.__dataclass_fields__:
                continue
            if k in int_fields:
                cleaned[k] = int(v) if v != "" else 0
            else:
                cleaned[k] = v
        return cls(**cleaned)

    @property
    def detail_sum(self) -> int:
        """세부 항목 합계 (총전투력과 비교 검증용)."""
        return (
            self.building_power
            + self.tech_power
            + self.troop_power
            + self.hero_power
            + self.vehicle_power
        )

    def validate(self) -> list[str]:
        """데이터 검증. 문제가 있으면 경고 메시지 리스트 반환."""
        warnings = []
        if self.total_power > 0 and self.detail_sum > 0:
            diff = abs(self.total_power - self.detail_sum)
            if diff > self.total_power * 0.05:
                warnings.append(
                    f"세부합계({self.detail_sum:,})와 총전투력({self.total_power:,}) 차이가 5% 초과"
                )
        if self.total_power < 0:
            warnings.append("총전투력이 음수입니다")
        return warnings
