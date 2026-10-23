
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


if __name__ == "__main__":
    unittest.main()
