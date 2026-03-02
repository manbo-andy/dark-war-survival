"""power_history.csv 읽기/쓰기 스토리지."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from ..models.player import PowerReading


COLUMNS = [
    "date", "player_id", "total_power", "building_power", "tech_power",
    "troop_power", "hero_power", "vehicle_power", "kill_count", "source",
]


class HistoryStore:
    """전투력 시계열 CSV 파일 관리."""

    def __init__(self, data_dir: Path):
        self.filepath = data_dir / "power_history.csv"
        self._ensure_file()

    def _ensure_file(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(COLUMNS)

    def _load_all(self) -> list[PowerReading]:
        readings = []
        with open(self.filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                readings.append(PowerReading.from_dict(row))
        return readings

    def add(self, reading: PowerReading) -> PowerReading:
        """전투력 기록 추가."""
        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writerow(reading.to_dict())
        return reading

    def get_history(self, player_id: str) -> list[PowerReading]:
        """특정 플레이어의 전투력 이력 반환 (날짜순)."""
        readings = [r for r in self._load_all() if r.player_id == player_id]
        readings.sort(key=lambda r: r.date)
        return readings

    def get_latest(self, player_id: Optional[str] = None) -> list[PowerReading]:
        """각 플레이어별 최신 전투력 반환."""
        all_readings = self._load_all()
        if player_id:
            all_readings = [r for r in all_readings if r.player_id == player_id]

        latest: dict[str, PowerReading] = {}
        for r in all_readings:
            if r.player_id not in latest or r.date > latest[r.player_id].date:
                latest[r.player_id] = r

        return sorted(latest.values(), key=lambda r: r.total_power, reverse=True)

    def get_ranking(self) -> list[PowerReading]:
        """전투력 랭킹 (최신 기록 기준, 내림차순)."""
        return self.get_latest()
