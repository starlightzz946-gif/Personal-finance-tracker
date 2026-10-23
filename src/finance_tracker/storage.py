
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.finance_tracker.models import Transaction


CSV_FIELDS = [
    "date",
    "type",
    "amount",
    "category",
    "description",
]


def save_transactions(transactions, file_path):
    """Save transactions to a CSV file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for transaction in transactions:
            writer.writerow({
                "date": transaction.date.isoformat(),
                "type": transaction.type,
                "amount": str(transaction.amount),
                "category": transaction.category,
                "description": transaction.description,
            })


def load_transactions(file_path):
    """Load transactions from a CSV file."""
    path = Path(file_path)

    if not path.exists():
        return []

    transactions = []

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != CSV_FIELDS:
            raise ValueError("CSV file has an unexpected column structure.")

        for row in reader:
            transactions.append(
                Transaction(
                    date=date.fromisoformat(row["date"]),
                    type=row["type"],
                    amount=Decimal(row["amount"]),
                    category=row["category"],
                    description=row["description"],
                )
            )

    return transactions
