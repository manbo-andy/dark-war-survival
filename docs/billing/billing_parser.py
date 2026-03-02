#!/usr/bin/env python3
import re
import csv
import argparse
from pathlib import Path
from datetime import date

# 1) 이미 파싱된 라인: "YYYY.MM.DD amount product..."
parsed_line_pattern = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\s+(\d+)\s+(.+)$")

# 2) 원본 라인에 등장하는 날짜/금액 패턴
raw_date_pattern = re.compile(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.")
raw_amount_pattern = re.compile(r"₩([\d,]+)")

def norm_date(y: str, m: str, d: str) -> str:
    return f"{y}.{int(m):02d}.{int(d):02d}"

def norm_amount(s: str) -> int:
    return int(s.replace(",", ""))

def parse_date_ymd(datestr: str) -> date:
    # datestr: YYYY.MM.DD
    y, m, d = datestr.split(".")
    return date(int(y), int(m), int(d))

def add_month_totals(rows):
    """
    rows: List[(YYYY.MM.DD, amount:int, product:str)]
    반환: 월 끝에
      - 합계 라인: (YYYY.MM, monthly_sum, MONTH_TOTAL)
      - 빈 줄: ("", "", "")
    를 삽입한 rows
    """
    if not rows:
        return rows

    # 입력 순서가 뒤죽박죽이어도 월별 "끝나는 시점"이 정의되려면 정렬이 안전함
    # 같은 날짜 내 순서는 원본 순서를 유지하도록 idx를 함께 둠
    indexed = []
    for idx, (dstr, amt, prod) in enumerate(rows):
        indexed.append((parse_date_ymd(dstr), idx, dstr, amt, prod))
    indexed.sort(key=lambda x: (x[0], x[1]))

    out = []
    current_ym = None
    month_sum = 0

    for dt, _, dstr, amt, prod in indexed:
        ym = (dt.year, dt.month)
        if current_ym is None:
            current_ym = ym

        # 월이 바뀌는 순간: 이전 월의 합계/빈줄 추가
        if ym != current_ym:
            y, m = current_ym
            out.append((f"{y}.{m:02d}", month_sum, "MONTH_TOTAL"))
            out.append(("", "", ""))  # 월 구분 빈줄

            current_ym = ym
            month_sum = 0

        out.append((dstr, amt, prod))
        month_sum += amt

    # 마지막 월 처리
    y, m = current_ym
    out.append((f"{y}.{m:02d}", month_sum, "MONTH_TOTAL"))
    out.append(("", "", ""))

    return out

def parse_from_already_parsed(lines):
    """lines: 'YYYY.MM.DD amount product...' 형태"""
    rows = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = parsed_line_pattern.match(line)
        if not m:
            continue
        y, mo, da, amount_str, product = m.groups()
        product = product.strip()
        if not product.startswith("Hot Package"):
            continue
        rows.append((f"{y}.{mo}.{da}", int(amount_str), product))
    return rows

def parse_from_raw(lines):
    """
    원본 형태 + 중간 예외 라인 가능.
    날짜 기준:
      - 위쪽으로 '가장 가까운 의미 있는 줄' 1개만 상품명 후보로 확정 (다른 블록으로 올라가는 오매칭 방지)
      - 아래쪽으로 첫 ₩... 줄을 금액으로 사용
    """
    rows = []
    lines = [ln.rstrip("\n") for ln in lines]

    def nearest_meaningful_upwards(idx: int):
        j = idx - 1
        while j >= 0:
            s = lines[j].strip()
            if not s:
                j -= 1
                continue
            if s == "문제 신고":
                j -= 1
                continue
            if s.startswith("지불 금액:"):
                j -= 1
                continue
            return s  # 가장 가까운 의미 있는 줄 1개만
        return None

    def find_amount_downwards(idx: int):
        j = idx + 1
        while j < len(lines):
            s = lines[j].strip()
            if not s:
                j += 1
                continue
            if s == "문제 신고":
                j += 1
                continue
            m = raw_amount_pattern.match(s)
            if m:
                return norm_amount(m.group(1))
            j += 1
        return None

    for i, line in enumerate(lines):
        line_s = line.strip()
        dm = raw_date_pattern.match(line_s)
        if not dm:
            continue

        y, mo, da = dm.groups()
        dstr = norm_date(y, mo, da)

        product = nearest_meaningful_upwards(i)
        if not product or not product.startswith("Hot Package"):
            continue

        amount = find_amount_downwards(i)
        if amount is None:
            continue

        rows.append((dstr, amount, product))

    return rows

def main():
    parser = argparse.ArgumentParser(
        description="Parse billing history and export Hot Package* entries to CSV (with monthly totals)."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="billing_history.txt",
        help="Input file path (default: billing_history.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="billing_summary.csv",
        help="Output CSV file path (default: billing_summary.csv)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    with input_path.open("r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    # 입력이 "이미 파싱된 형태"인지 자동 판별
    has_parsed_style = any(parsed_line_pattern.match(ln.strip()) for ln in raw_lines if ln.strip())

    if has_parsed_style:
        rows = parse_from_already_parsed(raw_lines)
    else:
        rows = parse_from_raw(raw_lines)

    # 월별 합계/빈줄 삽입
    rows = add_month_totals(rows)

    # CSV 저장 (헤더 포함)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "amount", "product"])
        w.writerows(rows)

if __name__ == "__main__":
    main()