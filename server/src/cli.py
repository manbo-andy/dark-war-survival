"""DWS CLI - Dark War Survival 전략 관리 도구."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import click

from .models.player import Player, PowerReading
from .storage.player_store import PlayerStore
from .storage.history_store import HistoryStore
from .utils.korean import format_power


def get_data_dir() -> Path:
    """프로젝트 루트의 data/ 디렉토리 경로."""
    return Path(__file__).resolve().parent.parent.parent / "data"


def get_player_store() -> PlayerStore:
    return PlayerStore(get_data_dir())


def get_history_store() -> HistoryStore:
    return HistoryStore(get_data_dir())


@click.group()
def cli():
    """DWS - Dark War Survival 전략 관리 도구"""
    pass


# ── Player 명령어 ──────────────────────────────────────────────


@cli.group()
def player():
    """플레이어 관리"""
    pass


@player.command("add")
@click.argument("player_id")
@click.option("--name", default=None, help="표시 이름 (기본: ID와 동일)")
@click.option("--alliance", "-a", default="", help="연맹 태그")
@click.option("--server", "-s", default=510, type=int, help="서버 번호")
@click.option("--enemy", is_flag=True, help="적군 여부")
@click.option("--tag", "-t", multiple=True, help="태그 (여러 개 가능)")
@click.option("--notes", default="", help="메모")
def player_add(player_id, name, alliance, server, enemy, tag, notes):
    """플레이어 등록"""
    store = get_player_store()
    p = Player(
        id=player_id,
        name=name or player_id,
        alliance=alliance,
        server=server,
        is_enemy=enemy,
        tags=list(tag),
        notes=notes,
    )
    try:
        store.add(p)
        click.echo(f"✓ 플레이어 '{p.name}' (ID: {p.id}) 등록 완료")
    except ValueError as e:
        click.echo(f"✗ {e}", err=True)
        raise SystemExit(1)


@player.command("list")
@click.option("--alliance", "-a", default=None, help="연맹 필터")
@click.option("--enemy", is_flag=True, default=False, help="적군만 표시")
def player_list(alliance, enemy):
    """플레이어 목록 조회"""
    store = get_player_store()
    players = store.list_all()

    if alliance:
        players = [p for p in players if p.alliance == alliance]
    if enemy:
        players = [p for p in players if p.is_enemy]

    if not players:
        click.echo("등록된 플레이어가 없습니다.")
        return

    click.echo(f"{'ID':<20} {'이름':<15} {'연맹':<8} {'서버':<6} {'태그'}")
    click.echo("─" * 70)
    for p in players:
        tags = ", ".join(p.tags) if p.tags else ""
        enemy_mark = " [적]" if p.is_enemy else ""
        click.echo(f"{p.id:<20} {p.name:<15} {p.alliance:<8} {p.server:<6} {tags}{enemy_mark}")


@player.command("info")
@click.argument("player_id")
def player_info(player_id):
    """플레이어 상세 정보"""
    ps = get_player_store()
    hs = get_history_store()

    p = ps.get(player_id)
    if not p:
        click.echo(f"✗ 플레이어 '{player_id}'를 찾을 수 없습니다", err=True)
        raise SystemExit(1)

    click.echo(f"ID:     {p.id}")
    click.echo(f"이름:   {p.name}")
    click.echo(f"연맹:   {p.alliance}")
    click.echo(f"서버:   {p.server}")
    click.echo(f"적군:   {'예' if p.is_enemy else '아니오'}")
    click.echo(f"태그:   {', '.join(p.tags) if p.tags else '-'}")
    click.echo(f"메모:   {p.notes or '-'}")

    history = hs.get_history(player_id)
    if history:
        latest = history[-1]
        click.echo(f"\n최근 전투력: {format_power(latest.total_power)} ({latest.date})")
        click.echo(f"  건물: {format_power(latest.building_power)}")
        click.echo(f"  기술: {format_power(latest.tech_power)}")
        click.echo(f"  병력: {format_power(latest.troop_power)}")
        click.echo(f"  영웅: {format_power(latest.hero_power)}")
        click.echo(f"  차량: {format_power(latest.vehicle_power)}")
        click.echo(f"  적처치: {latest.kill_count:,}")
        if len(history) > 1:
            prev = history[-2]
            diff = latest.total_power - prev.total_power
            sign = "+" if diff >= 0 else ""
            click.echo(f"  변화: {sign}{format_power(diff)} (vs {prev.date})")


# ── Power 명령어 ──────────────────────────────────────────────


@cli.group()
def power():
    """전투력 관리"""
    pass


@power.command("add")
@click.argument("player_id")
@click.argument("total_power", type=int)
@click.option("--building", default=0, type=int, help="건물 전투력")
@click.option("--tech", default=0, type=int, help="기술 전투력")
@click.option("--troop", default=0, type=int, help="병력 전투력")
@click.option("--hero", default=0, type=int, help="영웅 전투력")
@click.option("--vehicle", default=0, type=int, help="차량 전투력")
@click.option("--kills", default=0, type=int, help="적 처치 수")
@click.option("--date", "record_date", default=None, help="기록 날짜 (YYYY-MM-DD, 기본: 오늘)")
def power_add(player_id, total_power, building, tech, troop, hero, vehicle, kills, record_date):
    """전투력 수동 입력"""
    ps = get_player_store()
    if not ps.get(player_id):
        click.echo(f"✗ 플레이어 '{player_id}'가 등록되지 않았습니다. 먼저 'dws player add'를 실행하세요.", err=True)
        raise SystemExit(1)

    hs = get_history_store()
    reading = PowerReading(
        date=record_date or date.today().isoformat(),
        player_id=player_id,
        total_power=total_power,
        building_power=building,
        tech_power=tech,
        troop_power=troop,
        hero_power=hero,
        vehicle_power=vehicle,
        kill_count=kills,
        source="manual",
    )

    warnings = reading.validate()
    for w in warnings:
        click.echo(f"⚠ {w}")

    hs.add(reading)
    click.echo(f"✓ {player_id} 전투력 {format_power(total_power)} 기록 완료 ({reading.date})")


@power.command("rank")
@click.option("--top", default=20, type=int, help="표시할 순위 수")
def power_rank(top):
    """전투력 랭킹"""
    hs = get_history_store()
    ps = get_player_store()
    rankings = hs.get_ranking()[:top]

    if not rankings:
        click.echo("전투력 데이터가 없습니다.")
        return

    players = {p.id: p for p in ps.list_all()}

    click.echo(f"{'순위':<5} {'이름':<15} {'연맹':<8} {'전투력':<15} {'날짜'}")
    click.echo("─" * 60)
    for i, r in enumerate(rankings, 1):
        p = players.get(r.player_id)
        name = p.name if p else r.player_id
        alliance = p.alliance if p else "?"
        click.echo(f"{i:<5} {name:<15} {alliance:<8} {format_power(r.total_power):<15} {r.date}")


@power.command("history")
@click.argument("player_id")
def power_history(player_id):
    """특정 플레이어의 전투력 이력"""
    hs = get_history_store()
    history = hs.get_history(player_id)

    if not history:
        click.echo(f"'{player_id}'의 전투력 기록이 없습니다.")
        return

    click.echo(f"{'날짜':<12} {'총전투력':<15} {'건물':<12} {'기술':<12} {'병력':<12} {'영웅':<12} {'차량':<12} {'처치'}")
    click.echo("─" * 100)
    for r in history:
        click.echo(
            f"{r.date:<12} {format_power(r.total_power):<15} "
            f"{format_power(r.building_power):<12} {format_power(r.tech_power):<12} "
            f"{format_power(r.troop_power):<12} {format_power(r.hero_power):<12} "
            f"{format_power(r.vehicle_power):<12} {r.kill_count:,}"
        )


# ── Scan 명령어 (Phase 2에서 구현) ────────────────────────────


@cli.command()
@click.argument("path", required=False)
@click.option("--all", "scan_all", is_flag=True, help="inbox 폴더 전체 스캔")
@click.option("--player", "-p", default=None, help="플레이어 ID 지정")
def scan(path, scan_all, player):
    """스크린샷 OCR 처리"""
    from .ocr.parser import parse_detail_screenshot, process_inbox

    screenshots_dir = Path(__file__).resolve().parent.parent.parent / "screenshots"
    data_dir = get_data_dir()

    if scan_all:
        results = process_inbox(screenshots_dir, data_dir, player_id=player)
        if not results:
            click.echo("inbox에 처리할 스크린샷이 없습니다.")
            return
        for r in results:
            status = "✓" if r.get("saved") else "✗"
            reading = r.get("reading")
            name = r.get("player_name_ocr", "?")
            power_str = format_power(reading.total_power) if reading and reading.total_power else "?"
            click.echo(f"  {status} {r.get('file', '?')} → {name} ({power_str})")
            if r.get("error"):
                click.echo(f"    에러: {r['error']}")
            for w in r.get("warnings", []):
                click.echo(f"    ⚠ {w}")
        saved = sum(1 for r in results if r.get("saved"))
        click.echo(f"\n총 {len(results)}건 처리, {saved}건 저장")

    elif path:
        img_path = Path(path)
        if not img_path.exists():
            click.echo(f"✗ 파일을 찾을 수 없습니다: {path}", err=True)
            raise SystemExit(1)
        result = parse_detail_screenshot(img_path, player_id=player)
        reading = result["reading"]
        if reading:
            click.echo(f"플레이어: {result['player_name_ocr']}")
            click.echo(f"날짜:     {reading.date}")
            click.echo(f"총전투력: {format_power(reading.total_power)}")
            click.echo(f"  건물: {format_power(reading.building_power)}")
            click.echo(f"  기술: {format_power(reading.tech_power)}")
            click.echo(f"  병력: {format_power(reading.troop_power)}")
            click.echo(f"  영웅: {format_power(reading.hero_power)}")
            click.echo(f"  차량: {format_power(reading.vehicle_power)}")
            click.echo(f"  처치: {reading.kill_count:,}")
            click.echo(f"신뢰도: {result['confidence']:.2f}")
        else:
            click.echo("✗ 데이터를 추출하지 못했습니다")
        for w in result.get("warnings", []):
            click.echo(f"  ⚠ {w}")
    else:
        click.echo("경로 또는 --all 옵션을 지정하세요. 예: dws scan image.png / dws scan --all")


# ── Report 명령어 (Phase 5에서 구현) ──────────────────────────


@cli.group()
def report():
    """리포트 관리"""
    pass


@report.command("generate")
@click.option("--date", "report_date", default=None, help="리포트 날짜 (YYYY-MM-DD, 기본: 오늘)")
def report_generate(report_date):
    """일일 리포트 생성"""
    from .reports.markdown_gen import generate_daily_report

    data_dir = get_data_dir()
    reports_dir = Path(__file__).resolve().parent.parent.parent / "docs" / "reports"

    output = generate_daily_report(data_dir, reports_dir, report_date)
    click.echo(f"✓ 리포트 생성 완료: {output}")


# ── Serve 명령어 ──────────────────────────────────────────────


@cli.command()
@click.option("--host", default="0.0.0.0", help="바인드 호스트")
@click.option("--port", default=8000, type=int, help="포트 번호")
def serve(host, port):
    """API 서버 실행"""
    import uvicorn
    from .api import app

    click.echo(f"DWS API 서버 시작: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
