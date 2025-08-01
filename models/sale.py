"""
Sale Models
===========

This module defines the Sale and SaleItem classes for the POS system.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from .product import Product
from .payment import Payment

@dataclass
class SaleItem:
    """Represents an item in a sale."""
    
    product: Product
    quantity: int
    unit_price: Optional[float] = None
    discount: float = 0.0
    
    def __post_init__(self):
        """Set unit price if not provided."""
        if self.unit_price is None:
            self.unit_price = self.product.price
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this item."""
        return self.unit_price * self.quantity
    
    @property
    def total(self) -> float:
        """Calculate total after discount."""
        return self.subtotal - self.discount
    
    def to_dict(self) -> dict:
        """Convert sale item to dictionary."""
        return {
            'product_id': self.product.id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'discount': self.discount,
            'subtotal': self.subtotal,
            'total': self.total
        }

@dataclass
class Sale:
    """Represents a complete sale transaction."""
    
    id: Optional[int] = None
    items: List[SaleItem] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    payment: Optional[Payment] = None
    tax_rate: float = 0.0
    discount: float = 0.0
    notes: str = ""
    cashier_id: Optional[str] = None
    customer_id: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal of all items."""
        return sum(item.subtotal for item in self.items)
    
    @property
    def tax_amount(self) -> float:
        """Calculate tax amount."""
        return self.subtotal * self.tax_rate
    
    @property
    def total(self) -> float:
        """Calculate total amount."""
        return self.subtotal + self.tax_amount - self.discount
    
    @property
    def item_count(self) -> int:
        """Get total number of items."""
        return sum(item.quantity for item in self.items)
    
    def add_item(self, product: Product, quantity: int = 1):
        """Add an item to the sale."""
        # Check if product already exists in sale
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return
        
        # Add new item
        self.items.append(SaleItem(product, quantity))
    
    def remove_item(self, product_id: int):
        """Remove an item from the sale."""
        self.items = [item for item in self.items if item.product.id != product_id]
    
    def update_item_quantity(self, product_id: int, quantity: int):
        """Update quantity of an item."""
        for item in self.items:
            if item.product.id == product_id:
                if quantity <= 0:
                    self.remove_item(product_id)
                else:
                    item.quantity = quantity
                break
    
    def clear_items(self):
        """Clear all items from the sale."""
        self.items.clear()
    
    def to_dict(self) -> dict:
        """Convert sale to dictionary."""
        return {
            'id': self.id,
            'items': [item.to_dict() for item in self.items],
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'payment': self.payment.to_dict() if self.payment else None,
            'subtotal': self.subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'discount': self.discount,
            'total': self.total,
            'item_count': self.item_count,
            'notes': self.notes,
            'cashier_id': self.cashier_id,
            'customer_id': self.customer_id
        }
