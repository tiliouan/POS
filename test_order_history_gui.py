"""
Test order history print functionality in GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from utils.advanced_receipt_printer import AdvancedReceiptPrinter
from config.language_settings import get_text

class OrderHistoryTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Order History Print")
        self.root.geometry("800x600")
        
        self.db_manager = DatabaseManager()
        self.sales_data = {}
        
        self.create_interface()
        
    def create_interface(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text="Test Order History", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Get sales
        sales = self.db_manager.get_all_sales()
        
        if not sales:
            ttk.Label(main_frame, text="No orders found").pack(pady=50)
            return
        
        # Create treeview
        columns = ("Order", "Time", "Total", "Status")
        self.orders_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.orders_tree.heading(col, text=col)
            
        # Add sales data
        for sale in sales[:10]:  # Show only first 10 for testing
            time_str = sale.timestamp.strftime("%d/%m/%Y %H:%M") if sale.timestamp else ""
            payment_method = "Cash" if sale.payment and sale.payment.is_cash_payment else "Card"
            item_id = self.orders_tree.insert("", "end", values=(
                f"#{sale.id}",
                time_str,
                f"{sale.total:.2f} DH",
                f"Paid by {payment_method} - Complete"
            ))
            self.sales_data[item_id] = sale.id
        
        self.orders_tree.pack(fill="both", expand=True, pady=(0, 20))
        
        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill="x")
        
        ttk.Button(buttons_frame, text="View Details", command=self.show_details).pack(side="left", padx=(0, 10))
        ttk.Button(buttons_frame, text="Print Receipt", command=self.print_receipt).pack(side="left")
        
    def get_selected_sale_id(self):
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "No order selected")
            return None
        
        item_id = selection[0]
        return self.sales_data.get(item_id)
    
    def show_details(self):
        sale_id = self.get_selected_sale_id()
        if sale_id:
            sale = self.db_manager.get_sale_by_id(sale_id)
            if sale:
                details = f"Order #{sale.id}\\n"
                details += f"Date: {sale.timestamp}\\n"
                details += f"Total: {sale.total:.2f} DH\\n"
                details += f"Items: {len(sale.items)}\\n"
                for item in sale.items:
                    details += f"  - {item.product.name}: {item.quantity} x {item.unit_price:.2f} DH\\n"
                messagebox.showinfo("Order Details", details)
            else:
                messagebox.showerror("Error", f"Order #{sale_id} not found")
    
    def print_receipt(self):
        sale_id = self.get_selected_sale_id()
        if sale_id:
            try:
                sale = self.db_manager.get_sale_by_id(sale_id)
                if sale:
                    printer = AdvancedReceiptPrinter()
                    result = printer.print_receipt(sale)
                    if "Error" not in result:
                        messagebox.showinfo("Success", f"Receipt for order #{sale_id} printed successfully")
                    else:
                        messagebox.showerror("Print Failed", result)
                else:
                    messagebox.showerror("Error", f"Order #{sale_id} not found")
            except Exception as e:
                messagebox.showerror("Error", f"Print failed: {e}")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = OrderHistoryTest()
    app.run()
