#!/usr/bin/env python3
"""
Test GUI barcode scanner dialog
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config.language_settings import get_text, language_manager
    from database.db_manager import DatabaseManager
    
    class TestBarcodeScannerDialog:
        """Test version of barcode scanner dialog."""
        
        def __init__(self, parent, callback):
            self.callback = callback
            self.window = tk.Toplevel(parent)
            self.window.title(get_text("barcode_scanner"))
            self.window.geometry("400x200")
            self.window.transient(parent)
            self.window.grab_set()
            
            # Center the window
            self.window.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
            
            self.create_widgets()
            
            # Focus on entry and bind Enter key
            self.barcode_entry.focus_set()
            self.window.bind('<Return>', lambda e: self.scan_barcode())
            
        def create_widgets(self):
            """Create dialog widgets."""
            main_frame = ttk.Frame(self.window, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text=get_text("scan_barcode"), 
                                   font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Barcode entry
            ttk.Label(main_frame, text=get_text("enter_barcode"), 
                     font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
            
            self.barcode_var = tk.StringVar()
            self.barcode_entry = ttk.Entry(main_frame, textvariable=self.barcode_var,
                                          font=("Arial", 12), width=30)
            self.barcode_entry.pack(fill="x", pady=(0, 20))
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x")
            
            scan_btn = ttk.Button(button_frame, text=get_text("scan_button"), 
                                 command=self.scan_barcode)
            scan_btn.pack(side="right", padx=(10, 0))
            
            cancel_btn = ttk.Button(button_frame, text=get_text("cancel"), 
                                   command=self.window.destroy)
            cancel_btn.pack(side="right")
            
        def scan_barcode(self):
            """Process the scanned barcode."""
            barcode = self.barcode_var.get().strip()
            if barcode:
                self.callback(barcode)
                self.window.destroy()
            else:
                messagebox.showwarning(get_text("warning"), get_text("enter_barcode"))

    class TestApp:
        def __init__(self):
            self.root = tk.Tk()
            self.root.title("Barcode Scanner Test")
            self.root.geometry("300x200")
            
            # Load database
            self.db = DatabaseManager()
            self.products = self.db.get_all_products()
            
            # Create test interface
            frame = ttk.Frame(self.root, padding="20")
            frame.pack(fill="both", expand=True)
            
            ttk.Label(frame, text="Barcode Scanner Test", font=("Arial", 16, "bold")).pack(pady=(0, 20))
            
            ttk.Button(frame, text="Open Barcode Scanner", 
                      command=self.open_scanner).pack(pady=10)
            
            self.result_label = ttk.Label(frame, text="Scan a barcode to test...", 
                                         font=("Arial", 12))
            self.result_label.pack(pady=20)
            
            # Sample barcodes
            ttk.Label(frame, text="Sample barcodes to test:", font=("Arial", 10, "bold")).pack(pady=(20, 5))
            sample_frame = ttk.Frame(frame)
            sample_frame.pack()
            
            samples = ["CAFE001", "CROI001", "EAU001"]
            for barcode in samples:
                ttk.Button(sample_frame, text=barcode, 
                          command=lambda b=barcode: self.test_barcode(b)).pack(side="left", padx=5)
        
        def open_scanner(self):
            """Open the barcode scanner dialog."""
            scanner_dialog = TestBarcodeScannerDialog(self.root, self.add_product_by_barcode)
        
        def test_barcode(self, barcode):
            """Test a barcode directly."""
            self.add_product_by_barcode(barcode)
        
        def add_product_by_barcode(self, barcode):
            """Add product to cart by barcode."""
            if not barcode.strip():
                return
                
            # Find product by barcode
            for product in self.products:
                if product.barcode and product.barcode.strip().lower() == barcode.strip().lower():
                    self.result_label.config(text=f"✓ Found: {product.name} - {product.price:.2f} DH")
                    return
                    
            # Product not found
            self.result_label.config(text=f"✗ No product found for barcode: {barcode}")
        
        def run(self):
            self.root.mainloop()
    
    if __name__ == "__main__":
        app = TestApp()
        app.run()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
