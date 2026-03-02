"""마크다운 리포트 생성 (Obsidian 호환)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from ..models.player import PowerReading
from ..storage.player_store import PlayerStore
from ..storage.history_store import HistoryStore
from ..utils.korean import format_power
from .charts import (
    create_power_trend_chart,
    create_ranking_bar_chart,
)


def generate_daily_report(
    data_dir: Path,
    reports_dir: Path,
    report_date: str | None = None,
) -> Path:
    """일일 리포트 마크다운 생성.

    Returns:
        생성된 리포트 파일 경로
    """
    report_date = report_date or date.today().isoformat()
    ps = PlayerStore(data_dir)
    hs = HistoryStore(data_dir)

    players = {p.id: p for p in ps.list_all()}
    rankings = hs.get_ranking()

    # 차트 생성
    assets_dir = reports_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    if rankings:
        ranking_data = [
            (players[r.player_id].name if r.player_id in players else r.player_id, r.total_power)
            for r in rankings
        ]
        create_ranking_bar_chart(
            ranking_data,
            assets_dir / f"ranking_{report_date}.png",
        )

    # 마크다운 생성
    lines = [
        f"# 일일 리포트 - {report_date}",
        "",
        f"> 자동 생성: {report_date}",
        "",
    ]

    # 요약
    if rankings:
        lines.extend([
            "## 요약",
            "",
            f"- 등록 플레이어: {len(players)}명",
            f"- 전투력 기록: {len(rankings)}건",
            f"- 최고 전투력: {format_power(rankings[0].total_power)} ({players.get(rankings[0].player_id, rankings[0]).player_id if rankings[0].player_id not in players else players[rankings[0].player_id].name})",
            "",
        ])

    # 랭킹 테이블
    if rankings:
        lines.extend([
            "## 전투력 랭킹",
            "",
            f"![[assets/ranking_{report_date}.png]]",
            "",
            "| 순위 | 이름 | 연맹 | 전투력 | 적처치 |",
            "|---:|------|------|-------:|-------:|",
        ])
        for i, r in enumerate(rankings, 1):
            p = players.get(r.player_id)
            name = p.name if p else r.player_id
            alliance = p.alliance if p else "?"
            lines.append(
                f"| {i} | {name} | {alliance} | {format_power(r.total_power)} | {r.kill_count:,} |"
            )
        lines.append("")

    # 파일 저장
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"daily_{report_date}.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return output_path
