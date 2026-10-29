
import unittest
from argparse import Namespace
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from io import StringIO
from contextlib import redirect_stdout

from src.finance_tracker import cli
from src.finance_tracker.models import Transaction


class TestFinanceCLI(unittest.TestCase):
    def test_add_transaction_saves_income(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "transactions.csv"

            args = Namespace(
                type="income",
                amount="5000.00",
                category="Allowance",
                description="Monthly allowance",
                date=date.today().isoformat(),
            )

            transaction = Transaction(
                date=date.today(),
                type="income",
                amount=Decimal("5000.00"),
                category="Allowance",
                description="Monthly allowance",
            )

            with (
                patch.object(cli, "DEFAULT_DATA_FILE", data_file),
                redirect_stdout(StringIO()),
            ):
                result = cli.add_transaction(args)

            self.assertEqual(result, 0)
            saved = cli.load_transactions(data_file)
            self.assertEqual(saved, [transaction])


    def test_add_transaction_uses_custom_file(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "custom_transactions.csv"

            args = Namespace(
                type="income",
                amount="2500.00",
                category="Freelance",
                description="Website project",
                date=date.today().isoformat(),
                file=data_file,
            )

            with redirect_stdout(StringIO()):
                result = cli.add_transaction(args)

            self.assertEqual(result, 0)
            self.assertTrue(data_file.exists())

            saved = cli.load_transactions(data_file)
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0].amount, Decimal("2500.00"))
            self.assertEqual(saved[0].category, "Freelance")


    def test_show_summary_uses_custom_file(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "custom_transactions.csv"

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
                    amount=Decimal("120.00"),
                    category="Food",
                    description="Lunch",
                ),
            ]

            cli.save_transactions(transactions, data_file)
            args = Namespace(file=data_file)

            with redirect_stdout(StringIO()) as output:
                result = cli.show_summary(args)

            self.assertEqual(result, 0)
            self.assertIn("5000.00", output.getvalue())
            self.assertIn("120.00", output.getvalue())
            self.assertIn("4880.00", output.getvalue())


    def test_show_summary_displays_totals(self):
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
                amount=Decimal("120.00"),
                category="Food",
                description="Lunch",
            ),
        ]

        with (
            patch.object(cli, "load_transactions", return_value=transactions),
            patch.object(cli, "DEFAULT_DATA_FILE", Path("unused.csv")),
            redirect_stdout(StringIO()) as output,
        ):
            args = Namespace(file=Path("unused.csv"))
            result = cli.show_summary(args)

        self.assertEqual(result, 0)
        self.assertIn("5000.00", output.getvalue())
        self.assertIn("120.00", output.getvalue())
        self.assertIn("4880.00", output.getvalue())


    def test_list_transactions_uses_custom_file(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "custom_transactions.csv"

            transaction = Transaction(
                date=date.today(),
                type="income",
                amount=Decimal("2500.00"),
                category="Freelance",
                description="Website project",
            )

            cli.save_transactions([transaction], data_file)

            args = Namespace(file=data_file)

            with redirect_stdout(StringIO()) as output:
                result = cli.list_transactions(args)

            self.assertEqual(result, 0)
            self.assertIn("2500.00", output.getvalue())
            self.assertIn("Freelance", output.getvalue())
            self.assertIn("Website project", output.getvalue())


    def test_list_reports_invalid_csv_without_traceback(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "invalid.csv"
            data_file.write_text(
                "date,type,amount,category,description\n"
                "2026-10-23,expense,abc,Food,Lunch\n",
                encoding="utf-8",
            )

            args = Namespace(file=data_file)

            with redirect_stdout(StringIO()) as output:
                result = cli.list_transactions(args)

            self.assertEqual(result, 1)
            self.assertIn("Error:", output.getvalue())
            self.assertIn("CSV row 2", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())


    def test_summary_reports_invalid_csv_without_traceback(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "invalid.csv"
            data_file.write_text(
                "date,type,amount,category,description\n"
                "2026-10-23,expense,abc,Food,Lunch\n",
                encoding="utf-8",
            )

            args = Namespace(file=data_file)

            with redirect_stdout(StringIO()) as output:
                result = cli.show_summary(args)

            self.assertEqual(result, 1)
            self.assertIn("Error:", output.getvalue())
            self.assertIn("CSV row 2", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())


    def test_add_reports_invalid_csv_without_traceback(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "invalid.csv"
            invalid_content = (
                "date,type,amount,category,description\n"
                "2026-10-23,expense,abc,Food,Lunch\n"
            )
            data_file.write_text(invalid_content, encoding="utf-8")

            args = Namespace(
                type="income",
                amount="500.00",
                category="Allowance",
                description="Weekly allowance",
                date=date.today().isoformat(),
                file=data_file,
            )

            with redirect_stdout(StringIO()) as output:
                result = cli.add_transaction(args)

            self.assertEqual(result, 1)
            self.assertIn("Error:", output.getvalue())
            self.assertIn("CSV row 2", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())
            self.assertEqual(
                data_file.read_text(encoding="utf-8"),
                invalid_content,
            )


    def test_add_reports_save_error_without_traceback(self):
        with TemporaryDirectory() as temp_dir:
            data_file = Path(temp_dir) / "transactions.csv"

            args = Namespace(
                type="income",
                amount="500.00",
                category="Allowance",
                description="Weekly allowance",
                date=date.today().isoformat(),
                file=data_file,
            )

            with (
                patch.object(
                    cli, "save_transactions",
                    side_effect=PermissionError("Permission denied"),
                ),
                redirect_stdout(StringIO()) as output,
            ):
                result = cli.add_transaction(args)

            self.assertEqual(result, 1)
            self.assertIn("Error:", output.getvalue())
            self.assertNotIn("Traceback", output.getvalue())


if __name__ == "__main__":
    unittest.main()
