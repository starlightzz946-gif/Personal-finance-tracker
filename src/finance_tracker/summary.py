
from decimal import Decimal


def calculate_summary(transactions):
    """Calculate total income, expenses, and balance."""

    total_income = Decimal("0.00")
    total_expenses = Decimal("0.00")

    for transaction in transactions:
        if transaction.type == "income":
            total_income += transaction.amount
        elif transaction.type == "expense":
            total_expenses += transaction.amount

    balance = total_income - total_expenses

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
    }
