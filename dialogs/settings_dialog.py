"""
Settings Dialog
===============

This module contains a comprehensive settings dialog that consolidates all
settings functionality from the sidebar into a centralized menu.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config.language_settings import get_text, language_manager
from database.user_manager import user_manager

class SettingsDialog:
    """Comprehensive settings dialog with all configuration options."""
    
    def __init__(self, parent, pos_app):
        """Initialize the settings dialog."""
        self.parent = parent
        self.pos_app = pos_app
        self.dialog = None
        
    def show(self):
        """Show the settings dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(get_text("settings"))
        self.dialog.geometry("800x600")
        self.dialog.configure(bg="white")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create all widgets for the settings dialog."""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=get_text("settings"), 
                               font=("Arial", 18, "bold"),
                               foreground="#1976d2")
        title_label.pack(pady=(0, 20))
        
        # Create notebook for different settings categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # General tab
        self.create_general_tab(notebook)
        
        # Reports tab
        self.create_reports_tab(notebook)
        
        # System tab
        self.create_system_tab(notebook)
        
        # Language tab
        self.create_language_tab(notebook)
        
        # Close button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        close_btn = ttk.Button(button_frame, text=get_text("close"),
                              command=self.close_dialog,
                              style="Accent.TButton")
        close_btn.pack(side="right")
        
    def create_general_tab(self, notebook):
        """Create the general settings tab."""
        general_frame = ttk.Frame(notebook, padding="20")
        notebook.add(general_frame, text="⚙️ " + get_text("general"))
        
        # Receipt Settings Section
        receipt_section = ttk.LabelFrame(general_frame, text="📋 " + get_text("receipt_settings"), 
                                       padding="15")
        receipt_section.pack(fill="x", pady=(0, 15))
        
        receipt_btn = ttk.Button(receipt_section, 
                               text=get_text("receipt_settings"),
                               command=self.pos_app.open_receipt_settings,
                               style="Info.TButton")
        receipt_btn.pack(fill="x", pady=5)
        
        receipt_desc = ttk.Label(receipt_section, 
                               text="Configure receipt templates, printer settings, and format options",
                               font=("Arial", 9),
                               foreground="#666666")
        receipt_desc.pack(fill="x")
        
        # Cash Management Section
        cash_section = ttk.LabelFrame(general_frame, text="💳 " + get_text("manage_cash"), 
                                    padding="15")
        cash_section.pack(fill="x", pady=(0, 15))
        
        cash_btn = ttk.Button(cash_section, 
                            text=get_text("manage_cash"),
                            command=self.pos_app.manage_cash,
                            style="Success.TButton")
        cash_btn.pack(fill="x", pady=5)
        
        cash_desc = ttk.Label(cash_section, 
                            text="Open cash drawer, count money, and manage register transactions",
                            font=("Arial", 9),
                            foreground="#666666")
        cash_desc.pack(fill="x")
        
    def create_reports_tab(self, notebook):
        """Create the reports tab."""
        reports_frame = ttk.Frame(notebook, padding="20")
        notebook.add(reports_frame, text="📊 " + get_text("reports"))
        
        # Register Screen Section
        register_section = ttk.LabelFrame(reports_frame, text="📊 " + get_text("register_screen"), 
                                        padding="15")
        register_section.pack(fill="x", pady=(0, 15))
        
        register_btn = ttk.Button(register_section, 
                                text=get_text("register_screen"),
                                command=self.pos_app.show_register_screen,
                                style="Info.TButton")
        register_btn.pack(fill="x", pady=5)
        
        register_desc = ttk.Label(register_section, 
                                text="View main point of sale interface and current session",
                                font=("Arial", 9),
                                foreground="#666666")
        register_desc.pack(fill="x")
        
        # Order History Section
        history_section = ttk.LabelFrame(reports_frame, text="📋 " + get_text("order_history"), 
                                       padding="15")
        history_section.pack(fill="x", pady=(0, 15))
        
        history_btn = ttk.Button(history_section, 
                               text=get_text("order_history"),
                               command=self.pos_app.show_order_history,
                               style="Info.TButton")
        history_btn.pack(fill="x", pady=5)
        
        history_desc = ttk.Label(history_section, 
                               text="View transaction history and search past orders",
                               font=("Arial", 9),
                               foreground="#666666")
        history_desc.pack(fill="x")
        
        # Daily Profit Section
        profit_section = ttk.LabelFrame(reports_frame, text="💰 " + get_text("daily_profit"), 
                                      padding="15")
        profit_section.pack(fill="x", pady=(0, 15))
        
        profit_btn = ttk.Button(profit_section, 
                              text=get_text("daily_profit"),
                              command=self.pos_app.show_daily_profit,
                              style="Warning.TButton")
        profit_btn.pack(fill="x", pady=5)
        
        profit_desc = ttk.Label(profit_section, 
                              text="View daily sales reports and profit analysis",
                              font=("Arial", 9),
                              foreground="#666666")
        profit_desc.pack(fill="x")
        
    def create_system_tab(self, notebook):
        """Create the system settings tab."""
        system_frame = ttk.Frame(notebook, padding="20")
        notebook.add(system_frame, text="🔧 " + get_text("system"))
        
        # Backup Settings Section
        backup_section = ttk.LabelFrame(system_frame, text="🗂️ " + get_text("backup_settings"), 
                                      padding="15")
        backup_section.pack(fill="x", pady=(0, 15))
        
        backup_btn = ttk.Button(backup_section, 
                              text=get_text("backup_settings"),
                              command=self.pos_app.open_backup_settings,
                              style="Secondary.TButton")
        backup_btn.pack(fill="x", pady=5)
        
        backup_desc = ttk.Label(backup_section, 
                              text="Configure automatic backups and data export options",
                              font=("Arial", 9),
                              foreground="#666666")
        backup_desc.pack(fill="x")
        
        # Close Register Section
        close_section = ttk.LabelFrame(system_frame, text="🔐 " + get_text("close_register"), 
                                     padding="15")
        close_section.pack(fill="x", pady=(0, 15))
        
        close_btn = ttk.Button(close_section, 
                             text=get_text("close_register"),
                             command=self.pos_app.close_register,
                             style="Danger.TButton")
        close_btn.pack(fill="x", pady=5)
        
        close_desc = ttk.Label(close_section, 
                             text="End current session and close the cash register",
                             font=("Arial", 9),
                             foreground="#666666")
        close_desc.pack(fill="x")
        
    def create_language_tab(self, notebook):
        """Create the language settings tab."""
        language_frame = ttk.Frame(notebook, padding="20")
        notebook.add(language_frame, text="🌐 " + get_text("language"))
        
        # Language Settings Section
        lang_settings_section = ttk.LabelFrame(language_frame, text="🌐 " + get_text("language_settings_menu"), 
                                             padding="15")
        lang_settings_section.pack(fill="x", pady=(0, 15))
        
        lang_settings_btn = ttk.Button(lang_settings_section, 
                                     text=get_text("language_settings_menu"),
                                     command=self.pos_app.open_language_settings,
                                     style="Info.TButton")
        lang_settings_btn.pack(fill="x", pady=5)
        
        lang_settings_desc = ttk.Label(lang_settings_section, 
                                     text="Configure language preferences and regional settings",
                                     font=("Arial", 9),
                                     foreground="#666666")
        lang_settings_desc.pack(fill="x")
        
        # Quick Language Switch Section
        quick_lang_section = ttk.LabelFrame(language_frame, text="🔄 Quick Language Switch", 
                                          padding="15")
        quick_lang_section.pack(fill="x", pady=(0, 15))
        
        # Current language display
        current_lang = language_manager.settings.current_language
        current_lang_label = ttk.Label(quick_lang_section, 
                                     text=f"Current Language: {current_lang}",
                                     font=("Arial", 11, "bold"),
                                     foreground="#1976d2")
        current_lang_label.pack(pady=(0, 10))
        
        # Language buttons
        language_buttons_data = [
            ("🇫🇷", "Français", "FR", "#81c784"),   # Soft green
            ("🇸🇦", "العربية", "AR", "#ce93d8"),    # Soft purple  
            ("🇺🇸", "English", "EN", "#64b5f6")     # Soft blue
        ]
        
        for flag, name, code, color in language_buttons_data:
            lang_btn = tk.Button(quick_lang_section, 
                               text=f"{flag} {name}",
                               command=lambda c=code: self.quick_change_language(c),
                               bg=color, fg="black",
                               font=("Arial", 10, "bold"),
                               padx=20, pady=8,
                               relief="flat",
                               cursor="hand2",
                               activebackground="#ffffff",
                               activeforeground="black")
            lang_btn.pack(fill="x", pady=2)
            
            # Add hover effects
            def on_enter(e, btn=lang_btn, original_color=color):
                btn.config(bg="#ffffff")
            def on_leave(e, btn=lang_btn, original_color=color):
                btn.config(bg=original_color)
                
            lang_btn.bind("<Enter>", on_enter)
            lang_btn.bind("<Leave>", on_leave)
    
    def quick_change_language(self, language_code):
        """Quickly change the application language."""
        try:
            language_manager.set_language(language_code)
            messagebox.showinfo("Language Changed", 
                              f"Language changed to {language_code}. Some changes may require restart.")
            
            # Update the current language display
            current_lang = language_manager.settings.current_language
            
            # Refresh the dialog if it's still open
            if self.dialog and self.dialog.winfo_exists():
                self.dialog.destroy()
                self.show()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change language: {e}")
    
    def close_dialog(self):
        """Close the settings dialog."""
        if self.dialog:
            self.dialog.destroy()
