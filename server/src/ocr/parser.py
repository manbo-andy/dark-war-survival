"""게임 UI 텍스트 파싱.

스크린샷에서 OCR로 추출한 텍스트를 정규식으로 파싱하여 PowerReading으로 변환.
해상도에 관계없이 텍스트 패턴 기반으로 동작한다.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Optional

from PIL import Image

from ..models.player import PowerReading
from .engine import extract_all_text
from .regions import crop_dialog


def _extract_date_from_filename(filename: str) -> Optional[str]:
    """파일명에서 날짜를 추출.

    지원 패턴:
        Screenshot_20260302_034108_Dark War.jpg  → 2026-03-02
        스크린샷 2026-03-02 185633.png           → 2026-03-02
        써클비_2026-03-02 185227.png             → 2026-03-02
    """
    # YYYYMMDD 패턴 (Screenshot_20260302_...)
    m = re.search(r"(\d{4})(\d{2})(\d{2})_\d{6}", filename)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # YYYY-MM-DD 패턴
    m = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if m:
        return m.group(1)

    return None


def _parse_number(text: str) -> int:
    """쉼표 포함 숫자 문자열을 정수로 변환."""
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else 0


def parse_detail_screenshot(
    image_path: Path,
    player_id: Optional[str] = None,
    record_date: Optional[str] = None,
) -> dict:
    """'상세' 다이얼로그 스크린샷을 파싱.

    전체 다이얼로그를 OCR한 뒤 정규식으로 텍스트 패턴을 매칭한다.
    해상도(폰/PC)에 관계없이 동작한다.

    Returns:
        {
            "reading": PowerReading | None,
            "confidence": float,      # 평균 신뢰도
            "warnings": list[str],
            "player_name_ocr": str,
        }
    """
    image = Image.open(image_path)
    warnings = []

    # 다이얼로그 영역 크롭
    dialog = crop_dialog(image)

    # 전체 OCR 실행
    ocr_results = extract_all_text(dialog)

    if not ocr_results:
        return {
            "reading": None,
            "confidence": 0.0,
            "warnings": ["OCR 결과가 없습니다"],
            "player_name_ocr": "",
        }

    # 전체 텍스트 합치기 (디버깅 + 파싱용)
    all_texts = [text for text, _ in ocr_results]
    full_text = " ".join(all_texts)
    avg_confidence = sum(c for _, c in ocr_results) / len(ocr_results)

    # ── 텍스트 패턴 매칭 ──────────────────────────────────────

    player_name = ""
    total_power = 0
    kill_count = 0
    building_power = 0
    tech_power = 0
    troop_power = 0
    hero_power = 0
    vehicle_power = 0

    # 플레이어 이름: "상세"(OCR이 "상제" 등으로 오인식할 수 있음) 다음의 첫 비숫자 텍스트
    # 또는 "전투력XXX" 줄 바로 앞의 텍스트
    found_header = False
    for i, (text, _) in enumerate(ocr_results):
        # "상세" 또는 유사 텍스트 감지
        if any(c in text for c in ["상세", "상제", "상쎄"]):
            found_header = True
            continue
        if found_header and not player_name:
            candidate = text.strip()
            # "전투력", "처치", 순수 숫자, 버튼 텍스트 건너뜀
            if re.search(r"전투력|처치|전력|건축|과학|부대|영웅|개조", candidate):
                continue
            if re.match(r"^[\d,.\s:]+$", candidate):
                continue
            if candidate:
                player_name = candidate
                continue

    # 총전투력: "전투력" 바로 뒤에 붙은 숫자 또는 같은 줄의 숫자
    m = re.search(r"전투력\s*(\d[\d,.]*\d)", full_text)
    if m:
        total_power = _parse_number(m.group(1))

    # 적 처치: "적 처치:" 뒤의 숫자 (OCR이 앞/뒷자리를 누락할 수 있음)
    m = re.search(r"적?\s*처치\s*:?\s*,?([\d,.]+)", full_text)
    if m:
        kill_count = _parse_number(m.group(1))

    # 세부 전투력: 각 라벨 뒤의 숫자를 매칭
    detail_patterns = [
        ("building_power", r"건축물\s*전투력\s*(\d[\d,.]*\d)"),
        ("tech_power", r"과학기술\s*전투력\s*(\d[\d,.]*\d)"),
        ("troop_power", r"부대\s*전투력\s*(\d[\d,.]*\d)"),
        ("hero_power", r"영웅\s*전투력\s*(\d[\d,.]*\d)"),
        ("vehicle_power", r"개조차\s*전투력\s*(\d[\d,.]*\d)"),
    ]

    detail_values = {}
    for field, pattern in detail_patterns:
        m = re.search(pattern, full_text)
        if m:
            detail_values[field] = _parse_number(m.group(1))
        else:
            detail_values[field] = 0
            warnings.append(f"{field}: 패턴 매칭 실패")

    # 세부값이 총전투력을 초과하면 OCR 오류로 판단하여 0으로 리셋
    if total_power > 0:
        for field_name, value in list(detail_values.items()):
            if value > total_power:
                warnings.append(
                    f"{field_name}: 값({value:,})이 총전투력({total_power:,})을 초과 → OCR 오류로 0 처리"
                )
                detail_values[field_name] = 0

    building_power = detail_values.get("building_power", 0)
    tech_power = detail_values.get("tech_power", 0)
    troop_power = detail_values.get("troop_power", 0)
    hero_power = detail_values.get("hero_power", 0)
    vehicle_power = detail_values.get("vehicle_power", 0)

    # 날짜: 파라미터 > 파일명 > 오늘
    if not record_date:
        record_date = _extract_date_from_filename(image_path.name)
    if not record_date:
        record_date = date.today().isoformat()

    reading = PowerReading(
        date=record_date,
        player_id=player_id or player_name or "unknown",
        total_power=total_power,
        building_power=building_power,
        tech_power=tech_power,
        troop_power=troop_power,
        hero_power=hero_power,
        vehicle_power=vehicle_power,
        kill_count=kill_count,
        source="ocr",
    )

    # 검증
    warnings.extend(reading.validate())

    if total_power == 0:
        warnings.append("총전투력을 추출하지 못했습니다")

    return {
        "reading": reading,
        "confidence": avg_confidence,
        "warnings": warnings,
        "player_name_ocr": player_name,
        "ocr_raw": all_texts,  # 디버깅용
    }


def process_inbox(
    screenshots_dir: Path,
    data_dir: Path,
    player_id: Optional[str] = None,
) -> list[dict]:
    """inbox 폴더의 모든 스크린샷을 처리.

    Returns:
        처리 결과 리스트
    """
    from ..storage.player_store import PlayerStore
    from ..storage.history_store import HistoryStore

    inbox = screenshots_dir / "inbox"
    processed = screenshots_dir / "processed"
    processed.mkdir(parents=True, exist_ok=True)

    results = []
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    if not inbox.exists():
        return results

    player_store = PlayerStore(data_dir)
    history_store = HistoryStore(data_dir)

    for img_path in sorted(inbox.iterdir()):
        if img_path.suffix.lower() not in image_extensions:
            continue

        try:
            result = parse_detail_screenshot(img_path, player_id=player_id)
            reading = result["reading"]

            if reading and reading.total_power > 0:
                # 플레이어가 등록되어 있지 않으면 자동 등록
                if not player_store.get(reading.player_id):
                    from ..models.player import Player
                    player_store.add(Player(
                        id=reading.player_id,
                        name=reading.player_id,
                        alliance="GaNG",
                    ))

                history_store.add(reading)
                result["saved"] = True
            else:
                result["saved"] = False

            # inbox → processed 이동
            dest = processed / img_path.name
            if dest.exists():
                dest = processed / f"{img_path.stem}_{reading.date}{img_path.suffix}"
            shutil.move(str(img_path), str(dest))
            result["file"] = img_path.name
            results.append(result)

        except Exception as e:
            results.append({
                "file": img_path.name,
                "error": str(e),
                "saved": False,
            })

    # OCR 로그 저장
    _save_ocr_log(data_dir, results)

    return results


def _save_ocr_log(data_dir: Path, results: list[dict]) -> None:
    """OCR 처리 로그를 ocr_log.json에 저장."""
    log_path = data_dir / "ocr_log.json"

    existing = []
    if log_path.exists():
        text = log_path.read_text(encoding="utf-8")
        if text.strip():
            existing = json.loads(text)

    for r in results:
        log_entry = {
            "file": r.get("file", ""),
            "saved": r.get("saved", False),
            "warnings": r.get("warnings", []),
            "error": r.get("error"),
        }
        if "reading" in r and r["reading"]:
            log_entry["player_id"] = r["reading"].player_id
            log_entry["total_power"] = r["reading"].total_power
        if "ocr_raw" in r:
            log_entry["ocr_raw"] = r["ocr_raw"]
        existing.append(log_entry)

    log_path.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
