#!/usr/bin/env python3
import re
import csv
import argparse
from pathlib import Path

# 1) 이미 파싱된 라인: "YYYY.MM.DD amount product..."
parsed_line_pattern = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\s+(\d+)\s+(.+)$")

# 2) 원본 라인에 등장하는 날짜/금액 패턴
raw_date_pattern = re.compile(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.")
raw_amount_pattern = re.compile(r"₩([\d,]+)")

def norm_date(y: str, m: str, d: str) -> str:
    return f"{y}.{int(m):02d}.{int(d):02d}"

def norm_amount(s: str) -> int:
    return int(s.replace(",", ""))

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
    원본 형태:
      상품명
      상품명
      날짜(YYYY. M. D.)
      ₩금액
      문제 신고
    + 중간 예외 라인(예: '지불 금액: ...')이 끼거나, Hot Package가 아닌 상품 블록이 섞일 수 있음

    핵심:
    - 날짜를 만나면, 바로 위에서 '첫 의미 있는 줄'을 상품 후보로 확정
      (Hot Package가 아니면 그 레코드는 버림 -> 다른 블록의 Hot Package로 잘못 매칭 방지)
    - 날짜 아래로 내려가며 첫 ₩... 를 금액으로 사용
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
            # 가장 가까운 의미 있는 줄 1개만 후보로 사용
            return s
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
        date = norm_date(y, mo, da)

        product = nearest_meaningful_upwards(i)
        if not product or not product.startswith("Hot Package"):
            continue

        amount = find_amount_downwards(i)
        if amount is None:
            continue

        rows.append((date, amount, product))

    return rows

def main():
    parser = argparse.ArgumentParser(
        description="Parse billing history and export Hot Package* entries to CSV."
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

    # CSV 저장 (헤더 포함)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "amount", "product"])
        w.writerows(rows)

if __name__ == "__main__":
    main()