import unittest
from decimal import Decimal
from orders import Order

class OrderTests(unittest.TestCase):
    def test_contract(self):
        self.assertEqual(Order("Ada", Decimal("1.20")).amount, Decimal("1.20"))
