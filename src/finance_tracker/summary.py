
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


def calculate_monthly_summary(transactions, year, month):
    """Calculate income, expenses, and balance for a specific month."""

    total_income = Decimal("0.00")
    total_expenses = Decimal("0.00")

    for transaction in transactions:
        if transaction.date.year == year and transaction.date.month == month:
            if transaction.type == "income":
                total_income += transaction.amount
            elif transaction.type == "expense":
                total_expenses += transaction.amount

    balance = total_income - total_expenses

    if total_income > Decimal("0.00"):
        savings_rate = (balance / total_income) * Decimal("100")
    else:
        savings_rate = Decimal("0.00")

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "savings_rate": savings_rate.quantize(Decimal("0.01")),
    }

def calculate_expenses_by_category(transactions):
    """Calculate total expenses grouped by category."""

    expenses_by_category = {}

    for transaction in transactions:
        if transaction.type == "expense":
            category = transaction.category

            if category not in expenses_by_category:
                expenses_by_category[category] = Decimal("0.00")

            expenses_by_category[category] += transaction.amount

    return expenses_by_category