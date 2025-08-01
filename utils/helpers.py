"""
Utility Functions
=================

Common utility functions for the POS system.
"""

import re
from typing import Union
from datetime import datetime

def format_currency(amount: float, currency: str = "د.م") -> str:
    """Format amount as currency string."""
    return f"{amount:.2f} {currency}"

def parse_currency(amount_str: str) -> float:
    """Parse currency string to float."""
    # Remove currency symbols and spaces
    cleaned = re.sub(r'[^\d.,\-]', '', amount_str)
    # Replace comma with dot for decimal separator
    cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def validate_barcode(barcode: str) -> bool:
    """Validate barcode format."""
    if not barcode:
        return True  # Optional field
    
    # Basic validation - alphanumeric, 6-20 characters
    return bool(re.match(r'^[A-Z0-9]{6,20}$', barcode.upper()))

def generate_barcode() -> str:
    """Generate a simple barcode."""
    from random import randint
    return f"POS{randint(100000, 999999)}"

def format_datetime(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str) if dt else ""

def truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def calculate_change(amount_paid: float, total_due: float) -> float:
    """Calculate change amount."""
    change = amount_paid - total_due
    return max(0.0, change)

def round_currency(amount: float, precision: float = 0.05) -> float:
    """Round amount to specified precision."""
    return round(amount / precision) * precision

def is_valid_price(price: Union[str, float]) -> bool:
    """Validate if price is valid."""
    try:
        price_float = float(price) if isinstance(price, str) else price
        return price_float > 0
    except (ValueError, TypeError):
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for saving files."""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and dots
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized[:255]  # Limit filename length
