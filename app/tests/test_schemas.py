from datetime import date
from decimal import Decimal
import pytest 
from pydantic import ValidationError

from app.src.schemas import EntryCreate


def test_valid_income_entry():
    entry = EntryCreate(
        amount=5000,
        type="income",
        description="Monthly salary",
        date=date(2026, 11, 9),
    )

    assert entry.amount == Decimal("5000")
    assert entry.type == "income"
    assert entry.description == "Monthly salary"

def test_valid_expense_entry():
    entry = EntryCreate(
        amount=Decimal("2500.50"),
        type="expense",
        description="Groceries",
        date=date(2026, 11, 9),
    )

    assert entry.amount == Decimal("2500.50")
    assert entry.type == "expense"
    assert entry.description == "Groceries"

def test_reject_zero_amount():
    with pytest.raises(ValidationError):
        EntryCreate(
            amount=Decimal("0"),
            type="income",
            description="Zero amount test",
            date=date(2026, 11, 9),
        )

def test_reject_negative_amount():
    with pytest.raises(ValidationError):
        EntryCreate(
            amount=Decimal("-500"),
            type="expense",
            description="Negative amount test",
            date=date(2026, 11, 9),
        )

def test_reject_invalid_transaction_type():
    with pytest.raises(ValidationError):
        EntryCreate(
            amount=Decimal("500"),
            type="transfer",
            description="Invalid transaction type test",
            date=date(2026, 11, 9),
        )

def test_reject_empty_description():
    with pytest.raises(ValidationError):
        EntryCreate(
            amount=Decimal("500"),
            type="expense",
            description="",
            date=date(2026, 11, 9),
        )

def test_reject_long_description():
    with pytest.raises(ValidationError):
        EntryCreate(
            amount=Decimal("500"),
            type="income",
            description="a" * 501,
            date=date(2026, 11, 9),
        )

def test_reject_missing_fields():
    with pytest.raises(ValidationError):
        EntryCreate(
            amount=Decimal("500"),
            type="income",
            description="Missing date test",
        )

def test_reject_whitespace_description():
    with pytest.raises(ValidationError):
        EntryCreate(
            amount=Decimal("500"),
            type="expense",
            description="   ",
            date=date(2026, 11, 9),
        )