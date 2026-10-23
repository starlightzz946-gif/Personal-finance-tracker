
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
