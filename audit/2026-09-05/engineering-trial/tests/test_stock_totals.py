import unittest

from stock import Stock
from stock_totals import total_stock


class TotalStockTests(unittest.TestCase):
    def test_duplicate_skus_are_summed(self):
        items = [Stock("apple", 2), Stock("pear", 4), Stock("apple", 7)]

        self.assertEqual(total_stock(items), {"apple": 9, "pear": 4})

    def test_result_keys_are_sorted(self):
        items = [Stock("pear", 4), Stock("apple", 2), Stock("banana", 3)]

        self.assertEqual(
            list(total_stock(items).items()),
            [("apple", 2), ("banana", 3), ("pear", 4)],
        )

    def test_empty_input_returns_empty_dict(self):
        result = total_stock([])

        self.assertIsInstance(result, dict)
        self.assertEqual(result, {})

    def test_one_shot_iterator_is_consumed_once(self):
        class OneShotIterator:
            def __init__(self, records):
                self.records = iter(records)
                self.iterations = 0
                self.consumed = 0

            def __iter__(self):
                self.iterations += 1
                if self.iterations > 1:
                    raise AssertionError("The iterator was traversed twice")
                return self

            def __next__(self):
                record = next(self.records)
                self.consumed += 1
                return record

        items = OneShotIterator(
            [Stock("pear", 3), Stock("apple", 1), Stock("pear", 5)]
        )

        self.assertEqual(total_stock(items), {"apple": 1, "pear": 8})
        self.assertEqual(items.iterations, 1)
        self.assertEqual(items.consumed, 3)
        with self.assertRaises(StopIteration):
            next(items)

    def test_original_skus_and_quantities_are_preserved(self):
        items = [
            Stock(" apple ", 2),
            Stock("apple", 3),
            Stock("Apple", 4),
            Stock("", 0),
            Stock("apple", -1),
        ]

        self.assertEqual(
            total_stock(items),
            {"": 0, " apple ": 2, "Apple": 4, "apple": 2},
        )


if __name__ == "__main__":
    unittest.main()
