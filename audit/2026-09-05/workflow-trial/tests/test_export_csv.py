import csv
from decimal import Decimal
from io import StringIO
import unittest

from export_csv import export_orders_csv
from orders import Order


class ExportCsvTests(unittest.TestCase):
    def test_preserves_order_and_formats_amounts_and_booleans(self):
        result = export_orders_csv([
            Order("Zoe", Decimal("2"), cancelled=True),
            Order("Ada", Decimal("3.456")),
            Order("Zoe", Decimal("-1.2")),
        ])
        self.assertEqual(result, (
            "customer,amount,cancelled\r\n"
            "Zoe,2.00,true\r\n"
            "Ada,3.46,false\r\n"
            "Zoe,-1.20,false\r\n"
        ))

    def test_escapes_commas_quotes_and_newlines(self):
        customer = 'Ada, "A"\nsecond line\r\nthird line'
        result = export_orders_csv([Order(customer, Decimal("1.20"))])
        self.assertEqual(result, (
            'customer,amount,cancelled\r\n'
            '"Ada, ""A""\nsecond line\r\nthird line",1.20,false\r\n'
        ))
        self.assertEqual(list(csv.reader(StringIO(result, newline=""))), [
            ["customer", "amount", "cancelled"],
            [customer, "1.20", "false"],
        ])

    def test_accepts_one_shot_iterator(self):
        orders = (Order(name, Decimal("1")) for name in ("Zoe", "Ada"))
        self.assertEqual(export_orders_csv(orders), (
            "customer,amount,cancelled\r\n"
            "Zoe,1.00,false\r\n"
            "Ada,1.00,false\r\n"
        ))
        self.assertEqual(list(orders), [])

    def test_empty_input_is_only_header(self):
        self.assertEqual(export_orders_csv(iter(())), "customer,amount,cancelled\r\n")


if __name__ == "__main__":
    unittest.main()
