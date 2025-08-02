"""
Test Order Details Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models.sale import Sale, SaleItem  
from models.product import Product
from models.payment import Payment, PaymentMethod, PaymentStatus
from datetime import datetime

def create_test_sale():
    """Create a test sale for the dialog."""
    # Create test products
    product1 = Product(id=1, name="Café", price=15.00, barcode="CAFE001", category="Boissons", stock_quantity=50)
    product2 = Product(id=2, name="Croissant", price=8.00, barcode="CROI001", category="Pâtisserie", stock_quantity=20)
    
    # Create sale items
    item1 = SaleItem(product=product1, quantity=2, unit_price=15.00)
    item2 = SaleItem(product=product2, quantity=1, unit_price=8.00)
    
    # Create payment
    payment = Payment(
        method=PaymentMethod.CASH,
        amount=40.00,
        status=PaymentStatus.COMPLETED,
        change_amount=2.00
    )
    
    # Create sale
    sale = Sale(
        id=123,
        items=[item1, item2],
        timestamp=datetime.now(),
        payment=payment,
        cashier_id="user_1"
    )
    
    return sale

def create_order_details_dialog(parent, sale):
    """Create order details dialog."""
    dialog = tk.Toplevel(parent)
    dialog.title(f"Order Details - #{sale.id}")
    dialog.geometry("600x500")
    dialog.configure(bg="white")
    dialog.resizable(False, False)
    
    # Center the dialog
    dialog.transient(parent)
    dialog.grab_set()
    
    # Main frame
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.pack(fill="both", expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text=f"Order #{sale.id}", 
                           font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Order info
    info_frame = ttk.LabelFrame(main_frame, text="Order Information", padding="10")
    info_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(info_frame, text=f"Date: {sale.timestamp.strftime('%d/%m/%Y %H:%M') if sale.timestamp else 'N/A'}").pack(anchor="w")
    ttk.Label(info_frame, text=f"Cashier: {sale.cashier_id or 'N/A'}").pack(anchor="w")
    if sale.payment:
        payment_method = "Cash" if sale.payment.method.value == "cash" else "Card"
        ttk.Label(info_frame, text=f"Payment Method: {payment_method}").pack(anchor="w")
    
    # Items
    items_frame = ttk.LabelFrame(main_frame, text="Items", padding="10")
    items_frame.pack(fill="both", expand=True, pady=(0, 20))
    
    # Items treeview
    columns = ("Product", "Quantity", "Unit Price", "Total")
    items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=8)
    
    for col in columns:
        items_tree.heading(col, text=col)
        
    items_tree.column("Product", width=200)
    items_tree.column("Quantity", width=80)
    items_tree.column("Unit Price", width=100)
    items_tree.column("Total", width=100)
    
    # Add items
    for item in sale.items:
        items_tree.insert("", "end", values=(
            item.product.name,
            item.quantity,
            f"{item.unit_price:.2f} DH",
            f"{item.total:.2f} DH"
        ))
    
    items_tree.pack(fill="both", expand=True)
    
    # Totals
    totals_frame = ttk.Frame(main_frame)
    totals_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(totals_frame, text=f"Subtotal: {sale.subtotal:.2f} DH", 
             font=("Arial", 10)).pack(anchor="e")
    if sale.tax_amount > 0:
        ttk.Label(totals_frame, text=f"Tax: {sale.tax_amount:.2f} DH",
                 font=("Arial", 10)).pack(anchor="e")
    if sale.discount > 0:
        ttk.Label(totals_frame, text=f"Discount: -{sale.discount:.2f} DH",
                 font=("Arial", 10)).pack(anchor="e")
    ttk.Label(totals_frame, text=f"Total: {sale.total:.2f} DH", 
             font=("Arial", 12, "bold")).pack(anchor="e")
    
    # Buttons
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill="x")
    
    def print_receipt():
        messagebox.showinfo("Print", f"Printing receipt for order #{sale.id}")
    
    ttk.Button(buttons_frame, text="Print Receipt", command=print_receipt).pack(side="left", padx=(0, 10))
    ttk.Button(buttons_frame, text="Close", command=dialog.destroy).pack(side="right")

def test_order_details():
    """Test the order details dialog."""
    root = tk.Tk()
    root.title("Test Order Details")
    root.geometry("300x200")
    
    def show_dialog():
        test_sale = create_test_sale()
        create_order_details_dialog(root, test_sale)
    
    ttk.Button(root, text="Show Order Details", command=show_dialog).pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    test_order_details()
