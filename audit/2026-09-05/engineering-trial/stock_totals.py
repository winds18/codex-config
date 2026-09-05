"""Aggregate parsed stock records by their original SKU."""

from typing import Dict, Iterable

from stock import Stock


def total_stock(items: Iterable[Stock]) -> Dict[str, int]:
    """Consume items once and return quantity totals in SKU order."""
    totals: Dict[str, int] = {}
    for item in items:
        totals[item.sku] = totals.get(item.sku, 0) + item.quantity
    return dict(sorted(totals.items()))
