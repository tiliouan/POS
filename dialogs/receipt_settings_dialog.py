"""
Receipt Settings Dialog
=======================

This module provides a GUI for configuring receipt printing settings.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config.receipt_settings import ReceiptSettingsManager, get_available_printers
from config.language_settings import get_text
from utils.advanced_receipt_printer import AdvancedReceiptPrinter
from models.sale import Sale, SaleItem
from models.product import Product
from models.payment import Payment, PaymentMethod
from datetime import datetime

class ReceiptSettingsDialog:
    """Dialog for configuring receipt printing settings."""
    
    def __init__(self, parent):
        self.parent = parent
        self.settings_manager = ReceiptSettingsManager()
        self.settings = self.settings_manager.get_settings()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Paramètres de reçu")
        self.dialog.geometry("800x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"800x700+{x}+{y}")
        
        self.create_widgets()
        self.load_current_settings()
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        # Store Information Tab
        self.create_store_tab(notebook)
        
        # Printer Settings Tab
        self.create_printer_tab(notebook)
        
        # Layout Settings Tab
        self.create_layout_tab(notebook)
        
        # Preview Frame
        preview_frame = ttk.LabelFrame(main_frame, text=get_text("preview"), padding="10")
        preview_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        
        # Preview text area
        self.preview_text = tk.Text(preview_frame, width=50, height=15, font=("Courier", 8))
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        preview_scrollbar.grid(row=0, column=1, sticky="ns")
        
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text=get_text("preview"), command=self.update_preview).pack(side="left", padx=5)
        ttk.Button(button_frame, text=get_text("test_print"), command=self.test_print).pack(side="left", padx=5)
        ttk.Button(button_frame, text=get_text("save"), command=self.save_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text=get_text("cancel"), command=self.dialog.destroy).pack(side="left", padx=5)
        
        # Initial preview
        self.update_preview()
    
    def create_store_tab(self, notebook):
        """Create store information tab."""
        store_frame = ttk.Frame(notebook, padding="10")
        notebook.add(store_frame, text="Informations du magasin")
        
        row = 0
        
        # Store name
        ttk.Label(store_frame, text="Nom du magasin:").grid(row=row, column=0, sticky="w", pady=5)
        self.store_name_var = tk.StringVar()
        ttk.Entry(store_frame, textvariable=self.store_name_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Address line 1
        ttk.Label(store_frame, text="Adresse ligne 1:").grid(row=row, column=0, sticky="w", pady=5)
        self.address1_var = tk.StringVar()
        ttk.Entry(store_frame, textvariable=self.address1_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Address line 2
        ttk.Label(store_frame, text="Adresse ligne 2:").grid(row=row, column=0, sticky="w", pady=5)
        self.address2_var = tk.StringVar()
        ttk.Entry(store_frame, textvariable=self.address2_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Phone
        ttk.Label(store_frame, text="Téléphone:").grid(row=row, column=0, sticky="w", pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(store_frame, textvariable=self.phone_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Email
        ttk.Label(store_frame, text="Email:").grid(row=row, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(store_frame, textvariable=self.email_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Logo settings
        ttk.Label(store_frame, text="Logo:").grid(row=row, column=0, sticky="w", pady=5)
        logo_frame = ttk.Frame(store_frame)
        logo_frame.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        
        self.logo_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(logo_frame, text="Afficher le logo", variable=self.logo_enabled_var, 
                       command=self.update_preview).pack(side="left")
        
        ttk.Button(logo_frame, text="Choisir image", command=self.choose_logo).pack(side="left", padx=(10, 0))
        row += 1
        
        # Logo text
        ttk.Label(store_frame, text="Texte du logo:").grid(row=row, column=0, sticky="w", pady=5)
        self.logo_text_var = tk.StringVar()
        ttk.Entry(store_frame, textvariable=self.logo_text_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Footer message
        ttk.Label(store_frame, text="Message de fin:").grid(row=row, column=0, sticky="w", pady=5)
        self.footer_var = tk.StringVar()
        ttk.Entry(store_frame, textvariable=self.footer_var, width=40).grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Tax number
        ttk.Label(store_frame, text="Numéro fiscal:").grid(row=row, column=0, sticky="w", pady=5)
        tax_frame = ttk.Frame(store_frame)
        tax_frame.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        
        self.tax_number_var = tk.StringVar()
        ttk.Entry(tax_frame, textvariable=self.tax_number_var, width=30).pack(side="left")
        
        self.show_tax_var = tk.BooleanVar()
        ttk.Checkbutton(tax_frame, text="Afficher", variable=self.show_tax_var, 
                       command=self.update_preview).pack(side="left", padx=(10, 0))
        
        store_frame.grid_columnconfigure(1, weight=1)
    
    def create_printer_tab(self, notebook):
        """Create printer settings tab."""
        printer_frame = ttk.Frame(notebook, padding="10")
        notebook.add(printer_frame, text="Imprimante")
        
        row = 0
        
        # Available printers
        ttk.Label(printer_frame, text="Imprimante par défaut:").grid(row=row, column=0, sticky="w", pady=5)
        self.printer_var = tk.StringVar()
        self.printer_combo = ttk.Combobox(printer_frame, textvariable=self.printer_var, 
                                         values=get_available_printers(), state="readonly")
        self.printer_combo.grid(row=row, column=1, sticky="ew", padx=(10, 0))
        row += 1
        
        # Auto print
        self.auto_print_var = tk.BooleanVar()
        ttk.Checkbutton(printer_frame, text="Impression automatique après paiement", 
                       variable=self.auto_print_var).grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Number of copies
        ttk.Label(printer_frame, text="Nombre de copies:").grid(row=row, column=0, sticky="w", pady=5)
        self.copies_var = tk.IntVar()
        ttk.Spinbox(printer_frame, from_=1, to=5, textvariable=self.copies_var, width=10).grid(row=row, column=1, sticky="w", padx=(10, 0))
        row += 1
        
        printer_frame.grid_columnconfigure(1, weight=1)
    
    def create_layout_tab(self, notebook):
        """Create layout settings tab."""
        layout_frame = ttk.Frame(notebook, padding="10")
        notebook.add(layout_frame, text="Mise en page")
        
        row = 0
        
        # Paper size
        ttk.Label(layout_frame, text="Taille du papier:").grid(row=row, column=0, sticky="w", pady=5)
        self.paper_size_var = tk.StringVar()
        size_combo = ttk.Combobox(layout_frame, textvariable=self.paper_size_var, 
                                 values=["58mm", "80mm", "A4"], state="readonly")
        size_combo.grid(row=row, column=1, sticky="w", padx=(10, 0))
        size_combo.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        row += 1
        
        # Receipt width
        ttk.Label(layout_frame, text="Largeur (caractères):").grid(row=row, column=0, sticky="w", pady=5)
        self.width_var = tk.IntVar()
        ttk.Spinbox(layout_frame, from_=20, to=80, textvariable=self.width_var, width=10,
                   command=self.update_preview).grid(row=row, column=1, sticky="w", padx=(10, 0))
        row += 1
        
        layout_frame.grid_columnconfigure(1, weight=1)
    
    def choose_logo(self):
        """Choose logo image file."""
        filename = filedialog.askopenfilename(
            title="Choisir une image de logo",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Tous", "*.*")]
        )
        if filename:
            self.settings.logo_path = filename
            self.update_preview()
    
    def load_current_settings(self):
        """Load current settings into the dialog."""
        self.store_name_var.set(self.settings.store_name)
        self.address1_var.set(self.settings.store_address_line1)
        self.address2_var.set(self.settings.store_address_line2)
        self.phone_var.set(self.settings.store_phone)
        self.email_var.set(self.settings.store_email)
        self.logo_enabled_var.set(self.settings.logo_enabled)
        self.logo_text_var.set(self.settings.logo_text)
        self.footer_var.set(self.settings.footer_message)
        self.tax_number_var.set(self.settings.tax_number)
        self.show_tax_var.set(self.settings.show_tax_number)
        self.printer_var.set(self.settings.default_printer)
        self.auto_print_var.set(self.settings.auto_print)
        self.copies_var.set(self.settings.print_copies)
        self.paper_size_var.set(self.settings.paper_size)
        self.width_var.set(self.settings.receipt_width)
    
    def update_preview(self):
        """Update the receipt preview."""
        # Create a sample sale for preview
        sample_product1 = Product(
            id=1, name="Sneakers", description="", price=107.80, 
            category="Chaussures", stock_quantity=10
        )
        sample_product2 = Product(
            id=2, name="Shopping bag", description="", price=40.00, 
            category="Accessoires", stock_quantity=5
        )
        sample_product3 = Product(
            id=3, name="T-shirt", description="", price=19.80, 
            category="Vêtements", stock_quantity=20
        )
        
        sample_items = [
            SaleItem(product=sample_product1, quantity=1, unit_price=107.80),
            SaleItem(product=sample_product2, quantity=1, unit_price=40.00),
            SaleItem(product=sample_product3, quantity=2, unit_price=19.80)
        ]
        
        sample_payment = Payment(
            method=PaymentMethod.CASH,
            amount=190.00,
            change_amount=0.60
        )
        
        sample_sale = Sale(
            id=452,
            timestamp=datetime.now(),
            items=sample_items,
            tax_rate=0.0,
            discount=0.0,
            payment=sample_payment,
            cashier_id="Jane Doe"
        )
        
        # Update settings with current form values for preview (use a copy)
        from copy import deepcopy
        temp_settings = deepcopy(self.settings_manager.get_settings())
        temp_settings.store_name = self.store_name_var.get()
        temp_settings.store_address_line1 = self.address1_var.get()
        temp_settings.store_address_line2 = self.address2_var.get()
        temp_settings.store_phone = self.phone_var.get()
        temp_settings.logo_enabled = self.logo_enabled_var.get()
        temp_settings.logo_text = self.logo_text_var.get()
        temp_settings.footer_message = self.footer_var.get()
        temp_settings.show_tax_number = self.show_tax_var.get()
        temp_settings.tax_number = self.tax_number_var.get()
        temp_settings.paper_size = self.paper_size_var.get()
        temp_settings.receipt_width = self.width_var.get()
        
        # Create printer with temporary settings
        printer = AdvancedReceiptPrinter()
        printer.settings = temp_settings
        printer.settings_manager.settings = temp_settings
        
        # Generate preview text
        preview_text = printer.generate_thermal_receipt_text(sample_sale)
        
        # Update preview
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
    
    def test_print(self):
        """Test print the current settings."""
        try:
            self.save_current_to_settings()
            
            # Create sample sale
            sample_product = Product(
                id=999, name="Test Product", description="", price=10.00, 
                category="Test", stock_quantity=1
            )
            
            sample_item = SaleItem(product=sample_product, quantity=1, unit_price=10.00)
            sample_payment = Payment(method=PaymentMethod.CASH, amount=10.00, change_amount=0.0)
            
            test_sale = Sale(
                id=999,
                timestamp=datetime.now(),
                items=[sample_item],
                payment=sample_payment,
                cashier_id="Test User"
            )
            
            printer = AdvancedReceiptPrinter()
            printer_name = self.printer_var.get()
            
            result = printer.print_receipt(test_sale, printer_name)
            messagebox.showinfo("Test d'impression", "Test d'impression effectué avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du test d'impression: {e}")
    
    def save_current_to_settings(self):
        """Save current form values to settings object."""
        self.settings.store_name = self.store_name_var.get()
        self.settings.store_address_line1 = self.address1_var.get()
        self.settings.store_address_line2 = self.address2_var.get()
        self.settings.store_phone = self.phone_var.get()
        self.settings.store_email = self.email_var.get()
        self.settings.logo_enabled = self.logo_enabled_var.get()
        self.settings.logo_text = self.logo_text_var.get()
        self.settings.footer_message = self.footer_var.get()
        self.settings.tax_number = self.tax_number_var.get()
        self.settings.show_tax_number = self.show_tax_var.get()
        self.settings.default_printer = self.printer_var.get()
        self.settings.auto_print = self.auto_print_var.get()
        self.settings.print_copies = self.copies_var.get()
        self.settings.paper_size = self.paper_size_var.get()
        self.settings.receipt_width = self.width_var.get()
    
    def save_settings(self):
        """Save settings and close dialog."""
        try:
            self.save_current_to_settings()
            self.settings_manager.settings = self.settings
            self.settings_manager.save_settings()
            messagebox.showinfo("Succès", "Paramètres sauvegardés avec succès!")
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {e}")
