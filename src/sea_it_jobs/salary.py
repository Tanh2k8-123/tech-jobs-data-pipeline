"""Conservative syntax parser. No guessed lower bounds, currency or pay period."""

import re
from decimal import Decimal, InvalidOperation

NUMBER = r"[0-9][0-9.,]*"
GRAMMAR = re.compile(
    rf"(?P<prefix>up to |tối đa |from |từ )?(?P<low>{NUMBER})"
    rf"(?:\s*-\s*(?P<high>{NUMBER}))?\Z"
)


def number(text: str) -> Decimal:
    if re.fullmatch(r"\d{1,3}(,\d{3})+(\.\d{1,2})?", text):
        text = text.replace(",", "")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d{1,2})?", text):
        text = text.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d+,\d{1,2}", text):
        text = text.replace(",", ".")
    elif not re.fullmatch(r"\d+(\.\d{1,2})?", text):
        raise ValueError("Ambiguous numeric salary")
    value = Decimal(text)
    if value < 0:
        raise ValueError("Negative salary")
    return value


def parse_salary(text: str | None, period: str | None, currency_hint: str | None = None):
    result = {
        "salary_min_native": None,
        "salary_max_native": None,
        "salary_currency": None,
        "salary_period": period,
        "salary_type": "undisclosed",
        "salary_parse_status": "undisclosed",
    }
    value = " ".join((text or "").lower().replace("–", "-").replace("—", "-").split())
    if not value or any(
        word in value
        for word in (
            "thỏa thuận",
            "thoả thuận",
            "negotiable",
            "sign in",
            "you'll love",
            "competitive",
        )
    ):
        return result
    usd = "$" in value or "usd" in value
    vnd = any(unit in value for unit in ("vnd", "vnđ", "₫", "triệu", "trieu"))
    currency = None if usd and vnd else "USD" if usd else "VND" if vnd else currency_hint
    result.update(
        salary_currency=currency, salary_type="unknown", salary_parse_status="unsupported"
    )
    multiplier = Decimal(1000000) if "triệu" in value or "trieu" in value else Decimal(1)
    for token in ("usd", "vnd", "vnđ", "triệu", "trieu", "$", "₫"):
        value = value.replace(token, "")
    value = " ".join(value.split())
    match = GRAMMAR.fullmatch(value)
    if not match or currency not in {"USD", "VND"}:
        return result
    prefix = match["prefix"]
    if prefix and match["high"]:
        return result
    try:
        low = number(match["low"]) * multiplier
        high = number(match["high"]) * multiplier if match["high"] else low
    except (InvalidOperation, ValueError):
        return result
    if low > high:
        return result
    salary_type = "range" if match["high"] else "fixed"
    if prefix in {"up to ", "tối đa "}:
        low, salary_type = None, "upper_bound"
    elif prefix in {"from ", "từ "}:
        high, salary_type = None, "lower_bound"
    result.update(
        salary_min_native=float(low) if low is not None else None,
        salary_max_native=float(high) if high is not None else None,
        salary_type=salary_type,
        salary_parse_status="parsed" if period == "month" else "unsupported_period",
    )
    return result
