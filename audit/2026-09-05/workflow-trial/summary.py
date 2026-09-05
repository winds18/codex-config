from decimal import Decimal
from typing import Dict, Iterable

from orders import Order


def summarize_orders(orders: Iterable[Order]) -> Dict[str, Decimal]:
    """汇总有效订单，按客户名称排序返回金额。"""
    totals: Dict[str, Decimal] = {}
    for order in orders:
        if order.cancelled:
            continue
        totals[order.customer] = totals.get(order.customer, Decimal("0")) + order.amount
    return dict(sorted(totals.items()))
