
import csv
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.finance_tracker.models import Transaction
from src.finance_tracker.storage import save_transactions, load_transactions


class TestTransactionStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.csv_path = Path(self.temp_dir.name) / "transactions.csv"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_transaction(self):
        original = Transaction(
            date=date(2026, 10, 23),
            type="expense",
            amount=Decimal("120.00"),
            category="Food",
            description="Lunch",
        )

        save_transactions([original], self.csv_path)
        loaded = load_transactions(self.csv_path)

        self.assertEqual(loaded, [original])

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_transactions(self.csv_path), [])

    def test_empty_list_saves_csv_header(self):
        save_transactions([], self.csv_path)

        with self.csv_path.open(
            "r", newline="", encoding="utf-8"
        ) as file:
            reader = csv.reader(file)
            self.assertEqual(
                next(reader),
                ["date", "type", "amount", "category", "description"],
            )
            self.assertEqual(list(reader), [])

    def test_save_creates_parent_directories(self):
        nested_path = self.csv_path.parent / "data" / "transactions.csv"

        save_transactions([], nested_path)

        self.assertTrue(nested_path.exists())


    def test_load_rejects_invalid_amount(self):
        with self.csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                ["date", "type", "amount", "category", "description"]
            )
            writer.writerow(
                ["2026-10-23", "expense", "abc", "Food", "Lunch"]
            )
        with self.assertRaisesRegex(
            ValueError, "Invalid transaction on CSV row 2"
        ):
            load_transactions(self.csv_path)


    def test_load_rejects_invalid_date(self):
        with self.csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                ["date", "type", "amount", "category", "description"]
            )
            writer.writerow(
                ["not-a-date", "expense", "120.00", "Food", "Lunch"]
            )

        with self.assertRaisesRegex(
            ValueError, "Invalid transaction on CSV row 2"
        ):
            load_transactions(self.csv_path)


    def test_load_rejects_missing_description(self):
        with self.csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                ["date", "type", "amount", "category", "description"]
            )
            writer.writerow(
                ["2026-10-23", "expense", "120.00", "Food", ""]
            )

        with self.assertRaisesRegex(
            ValueError, "Invalid transaction on CSV row 2"
        ):
            load_transactions(self.csv_path)



if __name__ == "__main__":
    unittest.main()
