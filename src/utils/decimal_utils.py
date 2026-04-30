from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal


def parse_brl_decimal(s: str | None) -> Decimal | None:
    if s is None or s == "":
        return None
    return Decimal(s.replace(",", "."))


def parse_sped_date(s: str) -> date:
    return date(int(s[4:8]), int(s[2:4]), int(s[0:2]))


def round_money(value: Decimal, places: int = 2) -> Decimal:
    quant = Decimal(10) ** -places
    return value.quantize(quant, rounding=ROUND_HALF_EVEN)
