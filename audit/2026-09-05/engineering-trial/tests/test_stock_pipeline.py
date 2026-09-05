import json
from pathlib import Path
import tempfile
import unittest

from stock_parser import parse_stock
from stock_totals import total_stock


class StockPipelineTests(unittest.TestCase):
    def test_json_file_to_sorted_totals(self):
        with tempfile.TemporaryDirectory(prefix="stock-pipeline-") as directory:
            path = Path(directory) / "input.json"
            path.write_text(json.dumps([
                {"sku": " B ", "quantity": 3},
                {"sku": "A", "quantity": 2},
                {"sku": "B", "quantity": 4},
                {"sku": "A", "quantity": 0},
            ]), encoding="utf-8")
            with path.open(encoding="utf-8") as stream:
                records = json.load(stream)
            result = total_stock(iter(parse_stock(iter(records))))
            self.assertEqual(result, {"A": 2, "B": 7})
            self.assertEqual(list(result), ["A", "B"])
        self.assertFalse(Path(directory).exists())

    def test_invalid_file_fails_at_parse_boundary(self):
        with tempfile.TemporaryDirectory(prefix="stock-pipeline-") as directory:
            path = Path(directory) / "invalid.json"
            path.write_text(json.dumps([
                {"sku": "A", "quantity": 2},
                {"sku": "B", "quantity": True},
            ]), encoding="utf-8")
            with path.open(encoding="utf-8") as stream:
                records = json.load(stream)
            with self.assertRaisesRegex(ValueError, r"row 2:.*quantity"):
                total_stock(parse_stock(iter(records)))
        self.assertFalse(Path(directory).exists())


if __name__ == "__main__":
    unittest.main()
