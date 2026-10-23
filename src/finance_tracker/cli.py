
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from src.finance_tracker.models import Transaction
from src.finance_tracker.storage import load_transactions, save_transactions
from src.finance_tracker.summary import calculate_summary


DEFAULT_DATA_FILE = Path.home() / ".personal-finance-tracker" / "transactions.csv"


def add_transaction(args):
    """Create and save a new income or expense."""
    try:
        amount = Decimal(args.amount)
        transaction = Transaction(
            date=date.fromisoformat(args.date),
            type=args.type,
            amount=amount,
            category=args.category,
            description=args.description,
        )
    except (ValueError, InvalidOperation) as error:
        print(f"Error: {error}")
        return 1

    transactions = load_transactions(DEFAULT_DATA_FILE)
    transactions.append(transaction)
    save_transactions(transactions, DEFAULT_DATA_FILE)

    print(f"Added {transaction.type}: {transaction.amount} ({transaction.category})")
    return 0


def list_transactions(args):
    """Display saved transactions."""
    transactions = load_transactions(DEFAULT_DATA_FILE)

    if not transactions:
        print("No transactions yet.")
        return 0

    for transaction in transactions:
        print(
            f"{transaction.date} | {transaction.type} | "
            f"{transaction.amount} | {transaction.category} | "
            f"{transaction.description}"
        )

    return 0


def show_summary(args):
    """Display totals for saved transactions."""
    transactions = load_transactions(args.file)
    summary = calculate_summary(transactions)

    print(f"Total income:   ₹{summary['total_income']:.2f}")
    print(f"Total expenses: ₹{summary['total_expenses']:.2f}")
    print(f"Balance:        ₹{summary['balance']:.2f}")

    return 0



def build_parser():
    parser = argparse.ArgumentParser(
        prog="finance-tracker",
        description="Track personal income and expenses.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add an income or expense")
    add_parser.add_argument("--type", choices=["income", "expense"], required=True)
    add_parser.add_argument("--amount", required=True)
    add_parser.add_argument("--category", required=True)
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument("--date", default=date.today().isoformat())
    add_parser.set_defaults(func=add_transaction)

    list_parser = subparsers.add_parser("list", help="List saved transactions")
    list_parser.set_defaults(func=list_transactions)

    summary_parser = subparsers.add_parser(
        "summary",
        help="Show total income, expenses, and balance",
    )
    summary_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Path to the transactions CSV file",
    )
    summary_parser.set_defaults(func=show_summary)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
