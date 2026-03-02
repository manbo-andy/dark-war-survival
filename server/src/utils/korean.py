"""한국어 숫자 포맷 유틸리티."""


def format_power(value: int) -> str:
    """전투력을 한국어 포맷으로 변환.

    Examples:
        206_589_465 -> "2억 658만"
        1_234_567 -> "123만"
        45_678 -> "4만"
        1_234 -> "1,234"
    """
    if value >= 100_000_000:
        eok = value // 100_000_000
        remainder = (value % 100_000_000) // 10_000
        if remainder > 0:
            return f"{eok}억 {remainder:,}만"
        return f"{eok}억"
    elif value >= 10_000:
        man = value // 10_000
        return f"{man:,}만"
    else:
        return f"{value:,}"


def parse_power_string(text: str) -> int:
    """한국어 전투력 문자열을 정수로 변환.

    Examples:
        "2억 658만" -> 206_580_000
        "123만" -> 1_230_000
        "1,234" -> 1234
    """
    text = text.strip().replace(",", "").replace(" ", "")

    total = 0
    if "억" in text:
        parts = text.split("억")
        total += int(parts[0]) * 100_000_000
        text = parts[1]

    if "만" in text:
        parts = text.split("만")
        if parts[0]:
            total += int(parts[0]) * 10_000
        text = parts[1] if len(parts) > 1 else ""

    if text:
        total += int(text)

    return total
