import unittest
from dataclasses import FrozenInstanceError
from stock import Stock

class StockTests(unittest.TestCase):
    def test_public_contract(self):
        self.assertEqual(Stock("A", 3).quantity, 3)
    def test_contract_is_frozen(self):
        with self.assertRaises(FrozenInstanceError):
            Stock("A", 3).quantity = 4
