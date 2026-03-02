"""FastAPI REST API 서버."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models.player import Player, PowerReading
from .storage.player_store import PlayerStore
from .storage.history_store import HistoryStore

app = FastAPI(title="DWS API", version="0.1.0", description="Dark War Survival 전략 관리 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _data_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "data"


def _screenshots_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "screenshots"


def _player_store() -> PlayerStore:
    return PlayerStore(_data_dir())


def _history_store() -> HistoryStore:
    return HistoryStore(_data_dir())


# ── Pydantic 요청/응답 모델 ───────────────────────────────────


class PlayerCreate(BaseModel):
    id: str
    name: str | None = None
    alliance: str = ""
    server: int = 510
    is_enemy: bool = False
    tags: list[str] = []
    notes: str = ""


class PlayerResponse(BaseModel):
    id: str
    name: str
    alliance: str
    server: int
    is_enemy: bool
    tags: list[str]
    notes: str
    active: bool


class PowerCreate(BaseModel):
    player_id: str
    total_power: int
    building_power: int = 0
    tech_power: int = 0
    troop_power: int = 0
    hero_power: int = 0
    vehicle_power: int = 0
    kill_count: int = 0
    date: str | None = None


class PowerResponse(BaseModel):
    date: str
    player_id: str
    total_power: int
    building_power: int
    tech_power: int
    troop_power: int
    hero_power: int
    vehicle_power: int
    kill_count: int
    source: str


# ── Player 엔드포인트 ─────────────────────────────────────────


@app.get("/api/players", response_model=list[PlayerResponse])
def list_players(alliance: Optional[str] = None, enemy: Optional[bool] = None):
    """플레이어 목록 조회."""
    players = _player_store().list_all()
    if alliance:
        players = [p for p in players if p.alliance == alliance]
    if enemy is not None:
        players = [p for p in players if p.is_enemy == enemy]
    return [p.to_dict() for p in players]


@app.post("/api/players", response_model=PlayerResponse, status_code=201)
def create_player(body: PlayerCreate):
    """플레이어 등록."""
    store = _player_store()
    player = Player(
        id=body.id,
        name=body.name or body.id,
        alliance=body.alliance,
        server=body.server,
        is_enemy=body.is_enemy,
        tags=body.tags,
        notes=body.notes,
    )
    try:
        store.add(player)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return player.to_dict()


@app.get("/api/players/{player_id}", response_model=PlayerResponse)
def get_player(player_id: str):
    """플레이어 상세 조회."""
    player = _player_store().get(player_id)
    if not player:
        raise HTTPException(status_code=404, detail=f"플레이어 '{player_id}'를 찾을 수 없습니다")
    return player.to_dict()


# ── Power 엔드포인트 ──────────────────────────────────────────


@app.get("/api/power/rank", response_model=list[PowerResponse])
def power_ranking(top: int = Query(20, ge=1, le=100)):
    """전투력 랭킹."""
    rankings = _history_store().get_ranking()[:top]
    return [r.to_dict() for r in rankings]


@app.get("/api/power/history/{player_id}", response_model=list[PowerResponse])
def power_history(player_id: str):
    """플레이어 전투력 이력."""
    history = _history_store().get_history(player_id)
    return [r.to_dict() for r in history]


@app.post("/api/power", response_model=PowerResponse, status_code=201)
def add_power(body: PowerCreate):
    """전투력 수동 입력."""
    if not _player_store().get(body.player_id):
        raise HTTPException(status_code=404, detail=f"플레이어 '{body.player_id}'가 등록되지 않았습니다")

    reading = PowerReading(
        date=body.date or date.today().isoformat(),
        player_id=body.player_id,
        total_power=body.total_power,
        building_power=body.building_power,
        tech_power=body.tech_power,
        troop_power=body.troop_power,
        hero_power=body.hero_power,
        vehicle_power=body.vehicle_power,
        kill_count=body.kill_count,
        source="manual",
    )
    _history_store().add(reading)
    return reading.to_dict()


# ── Scan 엔드포인트 ───────────────────────────────────────────


@app.post("/api/scan")
async def scan_screenshot(
    file: UploadFile = File(...),
    player_id: Optional[str] = Query(None, description="플레이어 ID 지정"),
):
    """스크린샷 OCR 처리 (multipart 업로드)."""
    from .ocr.parser import parse_detail_screenshot

    inbox = _screenshots_dir() / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)

    dest = inbox / file.filename
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        result = parse_detail_screenshot(dest, player_id=player_id)
        reading = result["reading"]

        if reading and result["confidence"].get("total_power", 0) >= 0.3:
            _history_store().add(reading)
            saved = True
        else:
            saved = False

        # inbox → processed 이동
        processed_dir = _screenshots_dir() / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.move(str(dest), str(processed_dir / file.filename))

        return {
            "status": "success" if saved else "low_confidence",
            "saved": saved,
            "filename": file.filename,
            "player_name_ocr": result["player_name_ocr"],
            "reading": reading.to_dict() if reading else None,
            "confidence": result["confidence"],
            "warnings": result["warnings"],
        }
    except Exception as e:
        return {
            "status": "error",
            "saved": False,
            "filename": file.filename,
            "error": str(e),
        }


# ── Events 엔드포인트 (Phase 5) ──────────────────────────────


@app.get("/api/events")
def list_events():
    """이벤트 목록 (Phase 5에서 구현)."""
    return []


# ── Reports 엔드포인트 (Phase 5) ─────────────────────────────


@app.post("/api/reports/generate")
def generate_report():
    """리포트 생성 (Phase 5에서 구현)."""
    return {"status": "not_implemented", "message": "Phase 5에서 구현 예정"}
