"""players.json CRUD 스토리지."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ..models.player import Player


class PlayerStore:
    """플레이어 데이터 JSON 파일 관리."""

    def __init__(self, data_dir: Path):
        self.filepath = data_dir / "players.json"
        self._ensure_file()

    def _ensure_file(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self.filepath.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        text = self.filepath.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else []

    def _save(self, data: list[dict]) -> None:
        self.filepath.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def list_all(self) -> list[Player]:
        """모든 플레이어 목록 반환."""
        return [Player.from_dict(d) for d in self._load()]

    def get(self, player_id: str) -> Optional[Player]:
        """ID로 플레이어 조회."""
        for d in self._load():
            if d["id"] == player_id:
                return Player.from_dict(d)
        return None

    def add(self, player: Player) -> Player:
        """플레이어 추가. 이미 존재하면 ValueError."""
        data = self._load()
        if any(d["id"] == player.id for d in data):
            raise ValueError(f"플레이어 '{player.id}'가 이미 존재합니다")
        data.append(player.to_dict())
        self._save(data)
        return player

    def update(self, player: Player) -> Player:
        """플레이어 정보 업데이트."""
        data = self._load()
        for i, d in enumerate(data):
            if d["id"] == player.id:
                data[i] = player.to_dict()
                self._save(data)
                return player
        raise ValueError(f"플레이어 '{player.id}'를 찾을 수 없습니다")

    def delete(self, player_id: str) -> bool:
        """플레이어 삭제."""
        data = self._load()
        new_data = [d for d in data if d["id"] != player_id]
        if len(new_data) == len(data):
            return False
        self._save(new_data)
        return True
