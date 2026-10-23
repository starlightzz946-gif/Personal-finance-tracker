
import unittest
from datetime import date
from decimal import Decimal

from src.finance_tracker.models import Transaction
from src.finance_tracker.summary import calculate_summary


class TestCalculateSummary(unittest.TestCase):
    def test_calculates_income_expenses_and_balance(self):
        transactions = [
            Transaction(
                date=date.today(),
                type="income",
                amount=Decimal("5000.00"),
                category="Allowance",
                description="Monthly allowance",
            ),
            Transaction(
                date=date.today(),
                type="expense",
                amount=Decimal("800.00"),
                category="Food",
                description="Lunch",
            ),
        ]

        result = calculate_summary(transactions)

        self.assertEqual(result["total_income"], Decimal("5000.00"))
        self.assertEqual(result["total_expenses"], Decimal("800.00"))
        self.assertEqual(result["balance"], Decimal("4200.00"))

    def test_empty_transactions_return_zero_totals(self):
        result = calculate_summary([])

        self.assertEqual(result["total_income"], Decimal("0.00"))
        self.assertEqual(result["total_expenses"], Decimal("0.00"))
        self.assertEqual(result["balance"], Decimal("0.00"))

    def test_income_only(self):
        transactions = [
            Transaction(
                date=date.today(),
                type="income",
                amount=Decimal("1000.00"),
                category="Allowance",
                description="Money received",
            ),
        ]

        result = calculate_summary(transactions)

        self.assertEqual(result["total_income"], Decimal("1000.00"))
        self.assertEqual(result["total_expenses"], Decimal("0.00"))
        self.assertEqual(result["balance"], Decimal("1000.00"))


if __name__ == "__main__":
    unittest.main()
