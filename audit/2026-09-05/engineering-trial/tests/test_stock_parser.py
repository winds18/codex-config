from copy import deepcopy
import unittest

from stock import Stock
from stock_parser import parse_stock


class StockParserTests(unittest.TestCase):
    def test_normalizes_sku_and_preserves_input_records(self):
        records = [
            {"sku": "  B  ", "quantity": 3, "extra": ["untouched"]},
            {"sku": "\tA\n", "quantity": 0},
        ]
        original = deepcopy(records)
        self.assertEqual(parse_stock(records), [Stock("B", 3), Stock("A", 0)])
        self.assertEqual(records, original)

    def test_accepts_one_shot_iterator(self):
        records = ({"sku": name, "quantity": 1} for name in ("B", "A"))
        self.assertEqual(parse_stock(records), [Stock("B", 1), Stock("A", 1)])
        self.assertEqual(list(records), [])

    def test_empty_input(self):
        self.assertEqual(parse_stock(iter(())), [])

    def test_invalid_sku_includes_one_based_row(self):
        for sku in ("", " \t\n", None, 7, True):
            with self.subTest(sku=sku):
                with self.assertRaisesRegex(ValueError, r"row 2:.*sku"):
                    parse_stock([
                        {"sku": "valid", "quantity": 1},
                        {"sku": sku, "quantity": 2},
                    ])

    def test_invalid_quantity_includes_one_based_row(self):
        for quantity in (-1, 1.0, "1", None, True, False):
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(ValueError, r"row 2:.*quantity"):
                    parse_stock([
                        {"sku": "valid", "quantity": 1},
                        {"sku": "invalid", "quantity": quantity},
                    ])

    def test_missing_fields_and_non_mapping_records(self):
        for record in ({}, {"sku": "A"}, {"quantity": 1}, None, [], "A"):
            with self.subTest(record=record):
                with self.assertRaisesRegex(ValueError, r"row 1:"):
                    parse_stock([record])

    def test_failed_parse_does_not_modify_earlier_records(self):
        records = [{"sku": " A ", "quantity": 1}, {"sku": "B", "quantity": -1}]
        original = deepcopy(records)
        with self.assertRaises(ValueError):
            parse_stock(records)
        self.assertEqual(records, original)


if __name__ == "__main__":
    unittest.main()
