from collections.abc import Mapping
from typing import Iterable, List

from stock import Stock


def parse_stock(records: Iterable[Mapping]) -> List[Stock]:
    """校验记录并创建库存对象；错误信息中的行号从 1 开始。"""
    items: List[Stock] = []
    for row, record in enumerate(records, start=1):
        if not isinstance(record, Mapping):
            raise ValueError(f"row {row}: record must be a dictionary")
        sku = record.get("sku")
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(f"row {row}: sku must be a non-empty string")
        quantity = record.get("quantity")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
            raise ValueError(f"row {row}: quantity must be a non-negative integer")
        items.append(Stock(sku=sku.strip(), quantity=quantity))
    return items
