
import unittest
from datetime import date
from decimal import Decimal

from src.finance_tracker.models import Transaction


class TestTransaction(unittest.TestCase):
    def test_valid_transaction(self):
        transaction = Transaction(
            date=date(2026, 10, 23),
            type="expense",
            amount=Decimal("120.00"),
            category="Food",
            description="Lunch",
        )

        self.assertEqual(transaction.amount, Decimal("120.00"))
        self.assertEqual(transaction.category, "Food")

    def test_rejects_zero_amount(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("0"),
                category="Food",
                description="Lunch",
            )

    def test_rejects_negative_amount(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("-10.00"),
                category="Food",
                description="Lunch",
            )

    def test_rejects_invalid_type(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="transfer",
                amount=Decimal("100.00"),
                category="Other",
                description="Transfer",
            )

    def test_rejects_empty_category(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("10.00"),
                category="   ",
                description="Lunch",
            )

    
    def test_rejects_empty_description(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("10.00"),
                category="Food",
                description="",
            )

    def test_rejects_whitespace_description(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("10.00"),
                category="Food",
                description="   ",
            )

    def test_rejects_nan_amount(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("NaN"),
                category="Food",
                description="Lunch",
            )

    def test_rejects_infinite_amount(self):
        with self.assertRaises(ValueError):
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("Infinity"),
                category="Food",
                description="Lunch",
            )



if __name__ == "__main__":
    unittest.main()
