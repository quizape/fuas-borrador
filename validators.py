import re


def clean_rut(value: str) -> str:
    return re.sub(r"[^0-9kK]", "", value or "").upper()


def valid_rut(value: str) -> bool:
    rut = clean_rut(value)

    if len(rut) < 2:
        return False

    body, dv = rut[:-1], rut[-1]

    if not body.isdigit():
        return False

    total = 0
    factor = 2

    for digit in reversed(body):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1

    result = 11 - total % 11
    expected = "0" if result == 11 else "K" if result == 10 else str(result)

    return dv == expected


def format_rut(value: str) -> str:
    rut = clean_rut(value)

    if len(rut) < 2:
        return value

    body, dv = rut[:-1], rut[-1]
    chunks = []

    while body:
        chunks.insert(0, body[-3:])
        body = body[:-3]

    return f"{'.'.join(chunks)}-{dv}"


def nonnegative_number(value) -> float:
    try:
        return max(float(value or 0), 0.0)
    except (TypeError, ValueError):
        return 0.0
