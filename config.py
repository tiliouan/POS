"""
Configuration Settings
======================

Configuration settings for the POS system.
"""

# Application settings
APP_TITLE = "Point of Sale - Système de Caisse"
APP_VERSION = "1.0.0"

# Window settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# Colors
PRIMARY_COLOR = "#20B2AA"      # Teal
SECONDARY_COLOR = "#666"       # Gray
SUCCESS_COLOR = "#90EE90"      # Light green
WARNING_COLOR = "#FFA500"      # Orange
DANGER_COLOR = "#FF6B6B"       # Red
BACKGROUND_COLOR = "#f0f0f0"   # Light gray

# Currency
CURRENCY_SYMBOL = "د.م"
CURRENCY_CODE = "MAD"

# Database settings
DATABASE_FILE = "pos_database.db"
BACKUP_ENABLED = True
BACKUP_INTERVAL_HOURS = 24

# Receipt settings
RECEIPT_WIDTH = 40
STORE_NAME = "Point of Sale"
STORE_ADDRESS = ""
RECEIPT_FOOTER = "Merci de votre visite!"

# Tax settings
DEFAULT_TAX_RATE = 0.20  # 20% VAT
TAX_INCLUDED = False

# Inventory settings
LOW_STOCK_THRESHOLD = 10
ENABLE_STOCK_ALERTS = True

# Payment settings
CASH_ROUNDING = True
ROUNDING_PRECISION = 0.05  # Round to nearest 5 centimes

# Language settings
DEFAULT_LANGUAGE = "fr"  # French
SUPPORTED_LANGUAGES = ["fr", "en", "ar"]

# Printer settings
AUTO_PRINT_RECEIPT = True
RECEIPT_COPIES = 1

# Security settings
REQUIRE_LOGIN = False
SESSION_TIMEOUT_MINUTES = 60
ENABLE_AUDIT_LOG = True
