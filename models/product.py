"""
Product Model
=============

This module defines the Product class for the POS system.
"""

from typing import Optional
from dataclasses import dataclass

@dataclass
class Product:
    """Represents a product in the POS system."""
    
    id: Optional[int]
    name: str
    description: str
    price: float  # Selling price
    barcode: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: int = 0
    is_active: bool = True
    supplier: Optional[str] = None
    cost_price: float = 0.0  # Cost price (without tax)
    
    def __post_init__(self):
        """Validate product data after initialization."""
        if self.price < 0:
            raise ValueError("Selling price cannot be negative")
        if self.cost_price < 0:
            raise ValueError("Cost price cannot be negative")
        if not self.name or not self.name.strip():
            raise ValueError("Product name cannot be empty")
    
    def __str__(self) -> str:
        return f"{self.name} - {self.price:.2f} د.م"
    
    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'barcode': self.barcode,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'is_active': self.is_active,
            'supplier': self.supplier,
            'cost_price': self.cost_price
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Create product from dictionary."""
        return cls(
            id=data.get('id'),
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            barcode=data.get('barcode'),
            category=data.get('category'),
            stock_quantity=data.get('stock_quantity', 0),
            is_active=data.get('is_active', True),
            supplier=data.get('supplier'),
            cost_price=float(data.get('cost_price', 0.0))
        )
