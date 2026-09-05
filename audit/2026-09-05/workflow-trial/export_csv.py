import csv
from io import StringIO
from typing import Iterable

from orders import Order


def export_orders_csv(orders: Iterable[Order]) -> str:
    """按输入顺序导出订单，保留取消状态并使用标准 CSV 转义。"""
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(("customer", "amount", "cancelled"))
    for order in orders:
        writer.writerow((
            order.customer,
            format(order.amount, ".2f"),
            "true" if order.cancelled else "false",
        ))
    return output.getvalue()
