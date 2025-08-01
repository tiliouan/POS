"""
Language Settings Dialog
=======================

Dialog for configuring language settings in the POS system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from config.language_settings import LanguageManager, get_text

class LanguageSettingsDialog:
    """Dialog for language settings configuration."""
    
    def __init__(self, parent: tk.Widget, callback: Optional[Callable] = None):
        """Initialize the language settings dialog."""
        self.parent = parent
        self.callback = callback
        self.language_manager = LanguageManager()
        self.dialog = None
        
        # Current settings (working copy)
        self.current_language = self.language_manager.settings.current_language
        self.current_rtl_mode = self.language_manager.settings.rtl_mode
        self.current_font_family = self.language_manager.settings.font_family
        self.current_font_size = self.language_manager.settings.font_size
        self.current_arabic_font = self.language_manager.settings.arabic_font_family
        
    def show(self):
        """Show the language settings dialog."""
        if self.dialog:
            self.dialog.lift()
            return
            
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(get_text("language_settings"))
        self.dialog.geometry("500x400")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=get_text("language_settings"), 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Language selection section
        self.create_language_section(main_frame)
        
        # Font settings section
        self.create_font_section(main_frame)
        
        # RTL settings section
        self.create_rtl_section(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_language_section(self, parent):
        """Create language selection section."""
        # Language selection frame
        lang_frame = ttk.LabelFrame(parent, text=get_text("select_language"), padding="10")
        lang_frame.pack(fill="x", pady=(0, 15))
        
        self.language_var = tk.StringVar(value=self.current_language)
        
        # Create radio buttons for each language
        languages = self.language_manager.get_available_languages()
        for code, name in languages.items():
            radio = ttk.Radiobutton(lang_frame, text=f"{name} ({code})", 
                                  variable=self.language_var, value=code,
                                  command=self.on_language_change)
            radio.pack(anchor="w", pady=2)
    
    def create_font_section(self, parent):
        """Create font settings section."""
        font_frame = ttk.LabelFrame(parent, text=get_text("font_settings"), padding="10")
        font_frame.pack(fill="x", pady=(0, 15))
        
        # Regular font family
        ttk.Label(font_frame, text=get_text("font_family") + ":").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.font_var = tk.StringVar(value=self.current_font_family)
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var, 
                                 values=["Arial", "Calibri", "Segoe UI", "Times New Roman", "Verdana"],
                                 state="readonly")
        font_combo.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        
        # Font size
        ttk.Label(font_frame, text=get_text("font_size") + ":").grid(row=0, column=2, sticky="w", padx=(0, 10))
        self.size_var = tk.StringVar(value=str(self.current_font_size))
        size_spin = ttk.Spinbox(font_frame, from_=8, to=16, textvariable=self.size_var, width=5)
        size_spin.grid(row=0, column=3, sticky="w")
        
        # Arabic font family
        ttk.Label(font_frame, text=get_text("arabic_font") + ":").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.arabic_font_var = tk.StringVar(value=self.current_arabic_font)
        arabic_font_combo = ttk.Combobox(font_frame, textvariable=self.arabic_font_var,
                                        values=["Arial Unicode MS", "Tahoma", "Segoe UI", "Microsoft Sans Serif"],
                                        state="readonly")
        arabic_font_combo.grid(row=1, column=1, columnspan=3, sticky="ew", pady=(10, 0))
        
        # Configure grid weights
        font_frame.columnconfigure(1, weight=1)
    
    def create_rtl_section(self, parent):
        """Create RTL settings section."""
        rtl_frame = ttk.LabelFrame(parent, text="RTL (Right-to-Left)", padding="10")
        rtl_frame.pack(fill="x", pady=(0, 15))
        
        self.rtl_var = tk.BooleanVar(value=self.current_rtl_mode)
        rtl_check = ttk.Checkbutton(rtl_frame, text=get_text("enable_rtl"), 
                                   variable=self.rtl_var)
        rtl_check.pack(anchor="w")
        
        # Note about RTL
        note_label = ttk.Label(rtl_frame, text="Note: RTL mode is automatically enabled for Arabic language",
                              font=("Arial", 8), foreground="gray")
        note_label.pack(anchor="w", pady=(5, 0))
    
    def create_buttons(self, parent):
        """Create dialog buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Buttons
        ttk.Button(button_frame, text="Apply Now", 
                  command=self.on_apply).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text=get_text("save"), 
                  command=self.on_save).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text=get_text("cancel"), 
                  command=self.on_cancel).pack(side="right")
        
        # Preview button
        ttk.Button(button_frame, text="Preview", 
                  command=self.on_preview).pack(side="left", padx=(10, 0))
    
    def on_language_change(self):
        """Handle language change."""
        selected_lang = self.language_var.get()
        
        # Auto-enable RTL for Arabic
        if selected_lang == "AR":
            self.rtl_var.set(True)
        else:
            self.rtl_var.set(False)
    
    def on_preview(self):
        """Show preview of selected language."""
        temp_lang = self.language_var.get()
        
        # Temporarily change language for preview
        old_lang = self.language_manager.settings.current_language
        self.language_manager.settings.current_language = temp_lang
        
        # Show preview message
        preview_text = f"""
{get_text("app_title")}

{get_text("products")}: {get_text("add_to_cart")}
{get_text("cart")}: {get_text("clear_cart")}
{get_text("payment")}: {get_text("pay_cash")} / {get_text("pay_card")}
{get_text("total")}: 100.00 د.م
        """
        
        messagebox.showinfo("Preview", preview_text)
        
        # Restore original language
        self.language_manager.settings.current_language = old_lang
    
    def on_apply(self):
        """Apply language settings immediately without closing dialog."""
        try:
            # Apply language change immediately
            self.language_manager.apply_language_immediately(self.language_var.get())
            self.language_manager.update_settings(
                rtl_mode=self.rtl_var.get(),
                font_family=self.font_var.get(),
                font_size=int(self.size_var.get()),
                arabic_font_family=self.arabic_font_var.get()
            )
            
            # Refresh this dialog with new language
            self.refresh_dialog_text()
            
            # Notify language change
            self.language_manager.notify_language_change()
            
            # Call callback if provided
            if self.callback:
                self.callback()
                
            messagebox.showinfo(get_text("success"), 
                              "Language applied successfully!")
            
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Error applying settings: {e}")
    
    def refresh_dialog_text(self):
        """Refresh dialog text with current language."""
        try:
            # Update dialog title
            self.dialog.title(get_text("language_settings"))
            
            # Note: Full UI refresh would require recreating all widgets
            # For now, just show a message that changes are applied
            
        except Exception as e:
            print(f"Error refreshing dialog: {e}")
    
    def on_save(self):
        """Save language settings."""
        try:
            # Update settings
            self.language_manager.update_settings(
                current_language=self.language_var.get(),
                rtl_mode=self.rtl_var.get(),
                font_family=self.font_var.get(),
                font_size=int(self.size_var.get()),
                arabic_font_family=self.arabic_font_var.get()
            )
            
            # Show success message
            messagebox.showinfo(get_text("success"), 
                              "Language settings saved successfully!\nRestart the application to see all changes.")
            
            # Call callback if provided
            if self.callback:
                self.callback()
            
            self.dialog.destroy()
            self.dialog = None
            
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Error saving settings: {e}")
    
    def on_cancel(self):
        """Cancel and close dialog."""
        self.dialog.destroy()
        self.dialog = None
