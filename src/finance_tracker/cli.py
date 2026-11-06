
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


from src.finance_tracker.models import Transaction, Budget
from src.finance_tracker.storage import (
    load_transactions,
    save_transactions,
    load_budgets,
    save_budgets,
)
from src.finance_tracker.summary import (
    calculate_summary,
    calculate_monthly_summary,
    calculate_expenses_by_category,
)


DEFAULT_DATA_FILE = Path.home() / ".personal-finance-tracker" / "transactions.csv"

DEFAULT_BUDGET_FILE = (
    Path.home() / ".personal-finance-tracker" / "budgets.csv"
)

def load_transactions_safely(data_file):
    """Load transactions and report expected file/data errors."""
    try:
        return load_transactions(data_file)
    except (ValueError, OSError, UnicodeError) as error:
        print(f"Error: {error}")
        return None

def load_budgets_safely(budget_file):
    """Load budgets and report expected file/data errors."""
    try:
        return load_budgets(budget_file)
    except (ValueError, OSError, UnicodeError) as error:
        print(f"Error: {error}")
        return None

def set_budget(args):
    """Create or update a monthly category budget."""

    budget_file = getattr(args, "budget_file", DEFAULT_BUDGET_FILE)

    try:
        selected_month = date.fromisoformat(f"{args.month}-01")
        amount = Decimal(args.amount)

        new_budget = Budget(
            year=selected_month.year,
            month=selected_month.month,
            category=args.category,
            amount=amount,
        )

    except (ValueError, InvalidOperation) as error:
        print(f"Error: {error}")
        return 1

    budgets = load_budgets_safely(budget_file)

    if budgets is None:
        return 1

    updated = False

    for index, budget in enumerate(budgets):
        if (
            budget.year == new_budget.year
            and budget.month == new_budget.month
            and budget.category.lower() == new_budget.category.lower()
        ):
            budgets[index] = new_budget
            updated = True
            break

    if not updated:
        budgets.append(new_budget)

    try:
        save_budgets(budgets, budget_file)
    except OSError as error:
        print(f"Error: Could not save budgets: {error}")
        return 1

    action = "Updated" if updated else "Created"

    print(
        f"{action} budget: {new_budget.category} "
        f"for {args.month} — ₹{new_budget.amount:.2f}"
    )

    return 0

def list_budgets(args):
    """Display budgets for a selected month."""

    budget_file = getattr(args, "budget_file", DEFAULT_BUDGET_FILE)

    try:
        selected_month = date.fromisoformat(f"{args.month}-01")
    except ValueError:
        print("Error: Month must use YYYY-MM format, e.g. 2026-11.")
        return 1

    budgets = load_budgets_safely(budget_file)

    if budgets is None:
        return 1

    monthly_budgets = [
        budget for budget in budgets
        if budget.year == selected_month.year
        and budget.month == selected_month.month
    ]

    if not monthly_budgets:
        print(f"No budgets found for {args.month}.")
        return 0

    print(f"Budgets for {args.month}:")

    for budget in sorted(monthly_budgets, key=lambda item: item.category.lower()):
        print(f"{budget.category}: ₹{budget.amount:.2f}")

    return 0

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


    data_file = getattr(args, "file", DEFAULT_DATA_FILE)
    transactions = load_transactions_safely(data_file)

    if transactions is None:
        return 1

    transactions.append(transaction)

    try:
        save_transactions(transactions, data_file)
    except OSError as error:
        print(f"Error: Could not save transactions: {error}")
        return 1

    print(f"Added {transaction.type}: {transaction.amount} ({transaction.category})")

    return 0


def list_transactions(args):
    """Display saved transactions."""

    data_file = getattr(args, "file", DEFAULT_DATA_FILE)
    transactions = load_transactions_safely(data_file)

    if transactions is None:
        return 1


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

    data_file = getattr(args, "file", DEFAULT_DATA_FILE)
    transactions = load_transactions_safely(data_file)

    if transactions is None:
        return 1

    summary = calculate_summary(transactions)

    print(f"Total income:   ₹{summary['total_income']:.2f}")
    print(f"Total expenses: ₹{summary['total_expenses']:.2f}")
    print(f"Balance:        ₹{summary['balance']:.2f}")

    return 0


def show_monthly_report(args):
    """Display financial totals for a selected month."""

    data_file = getattr(args, "file", DEFAULT_DATA_FILE)
    transactions = load_transactions_safely(data_file)

    if transactions is None:
        return 1

    try:
        selected_month = date.fromisoformat(f"{args.month}-01")
    except ValueError:
        print("Error: Month must use YYYY-MM format, e.g. 2026-10.")
        return 1

    year = selected_month.year
    month = selected_month.month

    summary = calculate_monthly_summary(
        transactions,
        year,
        month,
    )

    month_name = date(year, month, 1).strftime("%B")

    print(f"Monthly Report: {month_name} {year}")
    print(f"Total income:   ₹{summary['total_income']:.2f}")
    print(f"Total expenses: ₹{summary['total_expenses']:.2f}")
    print(f"Balance:        ₹{summary['balance']:.2f}")
    print(f"Savings rate:   {summary['savings_rate']:.2f}%")

    return 0

def show_category_report(args):
    """Display total expenses grouped by category."""

    data_file = getattr(args, "file", DEFAULT_DATA_FILE)
    transactions = load_transactions_safely(data_file)

    if transactions is None:
        return 1

    expenses = calculate_expenses_by_category(transactions)

    if not expenses:
        print("No expenses recorded yet.")
        return 0

    print("Expenses by Category:")

    for category, amount in sorted(expenses.items()):
        print(f"{category}: ₹{amount:.2f}")

    return 0

def build_parser():
    parser = argparse.ArgumentParser(
        prog="finance-tracker",
        description="Track personal income and expenses.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    budget_parser = subparsers.add_parser(
        "budget",
        help="Manage monthly category budgets",
    )

    budget_subparsers = budget_parser.add_subparsers(
        dest="budget_command",
        required=True,
    )

    set_budget_parser = budget_subparsers.add_parser(
        "set",
        help="Create or update a monthly category budget",
    )

    set_budget_parser.add_argument(
        "--month",
        required=True,
        help="Budget month in YYYY-MM format",
    )

    set_budget_parser.add_argument(
        "--category",
        required=True,
        help="Expense category",
    )

    set_budget_parser.add_argument(
        "--amount",
        required=True,
        help="Budget amount",
    )

    set_budget_parser.add_argument(
        "--budget-file",
        type=Path,
        default=DEFAULT_BUDGET_FILE,
        help="Path to the budgets CSV file",
    )

    set_budget_parser.set_defaults(func=set_budget)
    list_budget_parser = budget_subparsers.add_parser(
        "list",
        help="List budgets for a specific month",
    )

    list_budget_parser.add_argument(
        "--month",
        required=True,
        help="Month to display in YYYY-MM format",
    )

    list_budget_parser.add_argument(
        "--budget-file",
        type=Path,
        default=DEFAULT_BUDGET_FILE,
        help="Path to the budgets CSV file",
    )

    list_budget_parser.set_defaults(func=list_budgets)
    add_parser = subparsers.add_parser("add", help="Add an income or expense")
    add_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Path to the transactions CSV file",
    )
    add_parser.add_argument("--type", choices=["income", "expense"], required=True)
    add_parser.add_argument("--amount", required=True)
    add_parser.add_argument("--category", required=True)
    add_parser.add_argument("--description", required=True)
    add_parser.add_argument("--date", default=date.today().isoformat())
    add_parser.set_defaults(func=add_transaction)


    list_parser = subparsers.add_parser("list", help="List saved transactions")
    list_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Path to the transactions CSV file",
    )
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
    monthly_parser = subparsers.add_parser(
        "monthly",
        help="Show a financial report for a specific month",
    )

    monthly_parser.add_argument(
        "--month",
        required=True,
        help="Month to report in YYYY-MM format",
    )

    monthly_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Path to the transactions CSV file",
    )

    monthly_parser.set_defaults(func=show_monthly_report)
    categories_parser = subparsers.add_parser(
        "categories",
        help="Show expenses grouped by category",
    )

    categories_parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_DATA_FILE,
        help="Path to the transactions CSV file",
    )

    categories_parser.set_defaults(func=show_category_report)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
