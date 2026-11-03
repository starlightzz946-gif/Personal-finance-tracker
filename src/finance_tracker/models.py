
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


TransactionType = Literal["income", "expense"]


@dataclass
class Transaction:
    date: date
    type: TransactionType
    amount: Decimal
    category: str
    description: str

    def __post_init__(self):
        if self.type not in ("income", "expense"):
            raise ValueError("Type must be 'income' or 'expense'.")

        if not self.amount.is_finite() or self.amount <= 0:
            raise ValueError("Amount must be a positive, finite number.")

        if not self.category.strip():
            raise ValueError("Category cannot be empty.")

        if not self.description.strip():
            raise ValueError("Description cannot be empty.")


@dataclass
class Budget:
    year: int
    month: int
    category: str
    amount: Decimal

    def __post_init__(self):
        if self.year < 1:
            raise ValueError("Year must be a positive number.")

        if not 1 <= self.month <= 12:
            raise ValueError("Month must be between 1 and 12.")

        if not self.category.strip():
            raise ValueError("Category cannot be empty.")

        if not self.amount.is_finite() or self.amount <= 0:
            raise ValueError("Budget amount must be a positive, finite number.")