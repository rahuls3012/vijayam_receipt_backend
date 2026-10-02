from decimal import Decimal
from num2words import num2words


def amount_to_words(amount) -> str:
    amount = Decimal(amount)
    rupees = int(amount)
    paise = int((amount - rupees) * 100)
    words = num2words(rupees, lang="en_IN").replace(",", "").replace("-", " ").replace(" and ", " ").title()
    out = f"{words} Rupees"
    if paise:
        out += f" and {num2words(paise, lang='en_IN').replace('-', ' ').title()} Paise"
    return out + " Only"


def inr(value) -> str:
    """Indian digit grouping: 1234567.5 -> 12,34,567.50"""
    whole, frac = f"{Decimal(value):.2f}".split(".")
    if len(whole) > 3:
        head, tail, parts = whole[:-3], whole[-3:], []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts) + "," + tail
    return whole if frac == "00" else f"{whole}.{frac}"
