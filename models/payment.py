"""
Payment Models
==============

This module defines payment-related classes for the POS system.
"""

from enum import Enum
from typing import Optional
from dataclasses import dataclass
from datetime import datetime

class PaymentMethod(Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CARD = "card"
    MOBILE = "mobile"
    CHECK = "check"
    STORE_CREDIT = "store_credit"

class PaymentStatus(Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Payment:
    """Represents a payment transaction."""
    
    method: PaymentMethod
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING
    timestamp: Optional[datetime] = None
    transaction_id: Optional[str] = None
    reference_number: Optional[str] = None
    change_amount: float = 0.0
    notes: str = ""
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.amount < 0:
            raise ValueError("Payment amount cannot be negative")
    
    @property
    def is_cash_payment(self) -> bool:
        """Check if this is a cash payment."""
        return self.method == PaymentMethod.CASH
    
    @property
    def is_card_payment(self) -> bool:
        """Check if this is a card payment."""
        return self.method == PaymentMethod.CARD
    
    def mark_completed(self):
        """Mark payment as completed."""
        self.status = PaymentStatus.COMPLETED
    
    def mark_failed(self):
        """Mark payment as failed."""
        self.status = PaymentStatus.FAILED
    
    def calculate_change(self, total_due: float) -> float:
        """Calculate change amount."""
        if self.is_cash_payment and self.amount > total_due:
            self.change_amount = self.amount - total_due
        else:
            self.change_amount = 0.0
        return self.change_amount
    
    def to_dict(self) -> dict:
        """Convert payment to dictionary."""
        return {
            'method': self.method.value,
            'amount': self.amount,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'transaction_id': self.transaction_id,
            'reference_number': self.reference_number,
            'change_amount': self.change_amount,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Payment':
        """Create payment from dictionary."""
        return cls(
            method=PaymentMethod(data['method']),
            amount=float(data['amount']),
            status=PaymentStatus(data.get('status', 'pending')),
            timestamp=datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else None,
            transaction_id=data.get('transaction_id'),
            reference_number=data.get('reference_number'),
            change_amount=float(data.get('change_amount', 0.0)),
            notes=data.get('notes', '')
        )
