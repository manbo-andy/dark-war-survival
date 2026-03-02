"""matplotlib 차트 생성."""

from __future__ import annotations

import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # GUI 없이 렌더링
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

from ..models.player import PowerReading
from ..utils.korean import format_power


def _setup_korean_font():
    """한국어 폰트 자동 설정."""
    system = platform.system()
    if system == "Windows":
        font_name = "Malgun Gothic"
    elif system == "Darwin":
        font_name = "AppleGothic"
    else:
        font_name = "NanumGothic"

    try:
        fm.findfont(font_name)
        plt.rcParams["font.family"] = font_name
    except Exception:
        pass  # 폰트를 찾을 수 없으면 기본 폰트 사용

    plt.rcParams["axes.unicode_minus"] = False


_setup_korean_font()


def create_power_trend_chart(
    history: list[PowerReading],
    player_name: str,
    output_path: Path,
) -> Path:
    """전투력 추이 라인 차트 생성."""
    if not history:
        return output_path

    dates = [r.date for r in history]
    total = [r.total_power for r in history]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(dates, total, marker="o", linewidth=2, color="#4CAF50")
    ax.fill_between(dates, total, alpha=0.1, color="#4CAF50")

    ax.set_title(f"{player_name} 전투력 추이", fontsize=14, fontweight="bold")
    ax.set_xlabel("날짜")
    ax.set_ylabel("전투력")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_power(int(x))))

    plt.xticks(rotation=45)
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path


def create_power_breakdown_chart(
    reading: PowerReading,
    player_name: str,
    output_path: Path,
) -> Path:
    """전투력 구성 파이 차트 생성."""
    labels = ["건물", "기술", "병력", "영웅", "차량"]
    values = [
        reading.building_power,
        reading.tech_power,
        reading.troop_power,
        reading.hero_power,
        reading.vehicle_power,
    ]
    colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]

    # 0인 항목 제외
    filtered = [(l, v, c) for l, v, c in zip(labels, values, colors) if v > 0]
    if not filtered:
        return output_path

    labels, values, colors = zip(*filtered)

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors,
        autopct="%1.1f%%", startangle=90, pctdistance=0.85,
    )
    ax.set_title(f"{player_name} 전투력 구성", fontsize=14, fontweight="bold")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path


def create_ranking_bar_chart(
    rankings: list[tuple[str, int]],
    output_path: Path,
    title: str = "전투력 랭킹",
    top_n: int = 15,
) -> Path:
    """전투력 랭킹 가로 바 차트 생성."""
    rankings = rankings[:top_n]
    if not rankings:
        return output_path

    names = [r[0] for r in reversed(rankings)]
    powers = [r[1] for r in reversed(rankings)]

    fig, ax = plt.subplots(figsize=(10, max(4, len(rankings) * 0.5)))
    bars = ax.barh(names, powers, color="#36A2EB", edgecolor="white")

    for bar, power in zip(bars, powers):
        ax.text(
            bar.get_width() + max(powers) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            format_power(power),
            va="center", fontsize=9,
        )

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("전투력")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_power(int(x))))

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path
