import unittest
from decimal import Decimal

from orders import Order
from summary import summarize_orders


class SummaryTests(unittest.TestCase):
    def test_totals_are_sorted_and_cancelled_orders_are_excluded(self):
        result = summarize_orders([
            Order("Zoe", Decimal("2.30")),
            Order("Ada", Decimal("1.20")),
            Order("Zoe", Decimal("3.40")),
            Order("Ada", Decimal("99.00"), cancelled=True),
            Order("Cancelled only", Decimal("9.00"), cancelled=True),
        ])
        self.assertEqual(list(result), ["Ada", "Zoe"])
        self.assertEqual(result, {"Ada": Decimal("1.20"), "Zoe": Decimal("5.70")})

    def test_decimal_values_are_not_rounded_or_converted_to_float(self):
        result = summarize_orders([
            Order("Ada", Decimal("0.1001")),
            Order("Ada", Decimal("0.2002")),
        ])
        self.assertEqual(result["Ada"], Decimal("0.3003"))
        self.assertIsInstance(result["Ada"], Decimal)

    def test_accepts_one_shot_iterator(self):
        orders = (Order("Ada", Decimal(amount)) for amount in ("1.00", "2.00"))
        self.assertEqual(summarize_orders(orders), {"Ada": Decimal("3.00")})
        self.assertEqual(list(orders), [])

    def test_empty_input(self):
        self.assertEqual(summarize_orders(iter(())), {})


if __name__ == "__main__":
    unittest.main()
