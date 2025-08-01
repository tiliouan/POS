#!/usr/bin/env python3
"""
Simple cash drawer opening dialog test
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.session_manager import SessionManager

class SimpleCashDrawerDialog:
    """Simplified cash drawer opening dialog."""
    
    def __init__(self, parent, session_manager):
        self.session_manager = session_manager
        self.result = None
        
        # Create dialog window
        self.window = tk.Toplevel(parent)
        self.window.title("Ouvrir la caisse")
        self.window.geometry("400x300")
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # Center on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 400) // 2
        y = (self.window.winfo_screenheight() - 300) // 2
        self.window.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Ouvrir la caisse", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Amount input
        ttk.Label(main_frame, text="Montant de départ (د.م):").pack(anchor="w")
        
        self.amount_var = tk.StringVar(value="0")
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var,
                                font=("Arial", 12), width=20)
        amount_entry.pack(pady=(5, 20))
        amount_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ok_btn = ttk.Button(button_frame, text="OUVRIR",
                           command=self.save_and_close)
        ok_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text="ANNULER",
                               command=self.cancel)
        cancel_btn.pack(side="right")
        
    def save_and_close(self):
        """Save and close dialog."""
        try:
            amount = float(self.amount_var.get().replace(',', '.'))
            
            if amount < 0:
                messagebox.showerror("Erreur", "Le montant ne peut pas être négatif")
                return
            
            # Start session
            session_info = self.session_manager.start_session(amount, "Ouverture manuelle")
            self.result = session_info
            self.window.destroy()
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide")
            
    def cancel(self):
        """Cancel dialog."""
        self.result = None
        self.window.destroy()

def test_simple_dialog():
    """Test the simplified dialog."""
    root = tk.Tk()
    root.title("POS Test")
    root.geometry("600x400")
    
    session_manager = SessionManager()
    
    def show_dialog():
        """Show the dialog."""
        dialog = SimpleCashDrawerDialog(root, session_manager)
        root.wait_window(dialog.window)
        if dialog.result:
            print(f"Dialog completed: {dialog.result}")
        else:
            print("Dialog cancelled")
            
    # Auto-show dialog
    root.after(500, show_dialog)
    
    root.mainloop()

if __name__ == "__main__":
    test_simple_dialog()
