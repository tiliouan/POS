"""
Receipt Settings Manager
========================

This module handles receipt printing settings and configuration.
"""

import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ReceiptSettings:
    """Receipt printing settings."""
    # Store Information
    store_name: str = "Nom du magasin"
    store_address_line1: str = "Calle Rue del Percebe, 13"
    store_address_line2: str = "28000 - Madrid"
    store_phone: str = ""
    store_email: str = ""
    store_website: str = ""
    
    # Logo Settings
    logo_enabled: bool = True
    logo_path: str = ""
    logo_text: str = "your LOGO here"
    
    # Receipt Settings
    receipt_width: int = 40  # Characters for 80mm
    paper_size: str = "80mm"  # 80mm, 58mm, A4
    
    # Printer Settings
    default_printer: str = ""
    auto_print: bool = True
    print_copies: int = 1
    
    # Footer Settings
    footer_message: str = "Thanks for your purchase"
    show_footer: bool = True
    
    # Tax Settings
    tax_number: str = ""
    show_tax_number: bool = False

class ReceiptSettingsManager:
    """Manages receipt printing settings."""
    
    def __init__(self, settings_file: str = "config/receipt_settings.json"):
        self.settings_file = settings_file
        self.settings = ReceiptSettings()
        self.load_settings()
    
    def load_settings(self) -> None:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Update settings with saved values
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
        except Exception as e:
            print(f"Error loading receipt settings: {e}")
    
    def save_settings(self) -> None:
        """Save settings to file."""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving receipt settings: {e}")
    
    def get_settings(self) -> ReceiptSettings:
        """Get current settings."""
        return self.settings
    
    def update_settings(self, **kwargs) -> None:
        """Update settings."""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save_settings()
    
    def reset_to_defaults(self) -> None:
        """Reset settings to defaults."""
        self.settings = ReceiptSettings()
        self.save_settings()
    
    def get_paper_width(self) -> int:
        """Get paper width in characters based on paper size."""
        width_map = {
            "58mm": 32,
            "80mm": 40,
            "A4": 80
        }
        return width_map.get(self.settings.paper_size, 40)

def get_available_printers() -> List[str]:
    """Get list of available printers on the system."""
    printers = []
    try:
        # Try to use win32print for Windows
        import win32print
        
        # Get all printers
        printer_list = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for printer in printer_list:
            printers.append(printer[2])  # Printer name
        
    except ImportError:
        # Fallback if win32print is not available
        print("win32print not available, using fallback printer list")
        printers = ["Default Printer"]
    except Exception as e:
        print(f"Error getting printers: {e}")
        printers = ["Default Printer"]
    
    # Always add virtual PDF printer
    printers.append("Save as PDF")
    
    return printers
