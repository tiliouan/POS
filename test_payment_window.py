"""
Payment Window Layout Test
==========================

Test the payment window auto-sizing and layout.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pos_system import PaymentWindow

def test_payment_window():
    """Test the payment window with different total amounts."""
    root = tk.Tk()
    root.title("Payment Window Test")
    root.geometry("400x300")
    
    def open_payment_window(total):
        def dummy_callback(payment):
            print(f"Payment processed: {payment.amount:.2f} د.م with method {payment.method.value}")
        
        PaymentWindow(root, total, dummy_callback)
    
    # Create test buttons for different total amounts
    ttk.Label(root, text="Test Payment Window Auto-Sizing", 
              font=("Arial", 14, "bold")).pack(pady=20)
    
    test_amounts = [15.50, 125.75, 999.99]
    
    for amount in test_amounts:
        btn = tk.Button(root, text=f"Test avec {amount:.2f} د.م",
                       command=lambda a=amount: open_payment_window(a),
                       font=("Arial", 11),
                       pady=10, padx=20)
        btn.pack(pady=10)
    
    ttk.Label(root, text="Cliquez sur un bouton pour tester la fenêtre de paiement",
              font=("Arial", 10)).pack(pady=20)
    
    ttk.Label(root, text="Raccourcis clavier dans la fenêtre de paiement:",
              font=("Arial", 10, "bold")).pack(pady=(20, 5))
    
    ttk.Label(root, text="• Entrée: Valider le paiement",
              font=("Arial", 9)).pack()
    ttk.Label(root, text="• Échap: Annuler",
              font=("Arial", 9)).pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_payment_window()
