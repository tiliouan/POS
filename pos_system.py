"""
POS System GUI Application
==========================

This module contains the main GUI application for the Point of Sale system.
It provides a modern interface similar to the reference images with French localization.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import sqlite3
from typing import List, Dict, Optional
from models.product import Product
from models.sale import Sale, SaleItem
from models.payment import Payment, PaymentMethod
from database.db_manager import DatabaseManager
from database.user_manager import user_manager
from utils.receipt_printer import ReceiptPrinter
from utils.advanced_receipt_printer import AdvancedReceiptPrinter
from utils.session_manager import SessionManager
from dialogs.receipt_settings_dialog import ReceiptSettingsDialog
from dialogs.language_settings_dialog import LanguageSettingsDialog
from dialogs.login_dialog import LoginDialog, UserManagementDialog
from dialogs.settings_dialog import SettingsDialog
from config.language_settings import language_manager, get_text

class POSApplication:
    """Main POS Application class with GUI interface."""
    
    def __init__(self):
        """Initialize the POS application."""
        self.root = tk.Tk()
        self.setup_window()
        
        # Initialize database
        self.db_manager = DatabaseManager()
        self.receipt_printer = ReceiptPrinter()
        self.advanced_receipt_printer = AdvancedReceiptPrinter()
        
        # Initialize backup manager
        from utils.backup_manager import BackupManager
        self.backup_manager = BackupManager()
        
        # Set up language change callback
        language_manager.refresh_ui_callback(self.refresh_ui_language)
        
        # Initialize session manager with error handling
        try:
            self.session_manager = SessionManager()
        except Exception as e:
            print(f"Warning: Session manager initialization failed: {e}")
            self.session_manager = None
        
        # Current sale and cart
        self.current_sale = Sale()
        self.cart_items: List[SaleItem] = []
        self.products = []  # Initialize products list for barcode scanning
        
        # Store and register info
        self.current_store = get_text("store_name")
        self.current_register = get_text("register_info")
        
        # Check if user is logged in, if not show login
        if not user_manager.is_logged_in():
            if not self.show_login():
                # User cancelled login, exit application
                self.root.destroy()
                return
        
        # GUI components
        self.create_widgets()
        
        # Show main window first
        self.root.update()
        self.root.deiconify()
        
        # Setup layout first
        self.setup_layout()
        
        # Note: Cash drawer opening is handled in on_login_success after user login
        # No need to check here as well
        
        # Store and register info (moved to __init__)
        # These are now set in __init__ method
    
    def show_login(self) -> bool:
        """Show login dialog. Returns True if login successful, False if cancelled."""
        self.root.withdraw()  # Hide main window
        
        login_dialog = LoginDialog(None, self.on_login_success)
        user = login_dialog.show()
        
        if not user:
            # User cancelled login
            return False
        
        self.root.deiconify()  # Show main window
        return True
    
    def on_login_success(self, user):
        """Handle successful login."""
        self.update_user_display()
        
        # Log login activity
        if user_manager.current_user:
            user_manager.log_activity(
                user_manager.current_user.id,
                "POS_LOGIN",
                f"Logged into POS system"
            )
        
        # Check if cash drawer opening is needed after login
        if self.session_manager:
            needs_drawer = self.session_manager.needs_cash_drawer_opening()
            if needs_drawer:
                self.root.after(500, self._show_cash_drawer_delayed)
    
    def update_user_display(self):
        """Update the display to show current user."""
        if hasattr(self, 'user_label') and user_manager.current_user:
            user_text = f"{get_text('logged_in_as')}: {user_manager.current_user.name}"
            self.user_label.config(text=user_text)
    
    def logout_user(self):
        """Logout current user."""
        if user_manager.current_user:
            # Log logout activity
            user_manager.log_activity(
                user_manager.current_user.id,
                "POS_LOGOUT",
                f"Logged out from POS system"
            )
            
            # End session (this will require cash drawer opening on next login)
            if self.session_manager:
                self.session_manager.end_session("Déconnexion utilisateur")
            
            user_manager.logout()
            
            # Clear current sale
            self.clear_cart()
            
            # Hide main window and show login
            if not self.show_login():
                # User cancelled login during logout, exit application
                self.root.destroy()
    
    def show_user_management(self):
        """Show user management dialog (admin only)."""
        if not user_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can manage users")
            return
        
        dialog = UserManagementDialog(self.root)
        dialog.show()
        
    def setup_window(self):
        """Configure the main window with responsive behavior."""
        self.root.title(get_text("app_title"))
        self.root.geometry("1600x1000")  # Increased for better responsive design
        self.root.configure(bg="white")  # Changed to white background
        self.root.minsize(1200, 800)  # Minimum size for responsive design
        
        # Make window resizable and responsive
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Bind window resize event to update product layout
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Force window to front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
    
    def on_window_resize(self, event):
        """Handle window resize events to update product layout."""
        # Only respond to window resize events, not widget resizes
        if event.widget == self.root:
            # Schedule product display refresh after resize is complete
            if hasattr(self, 'products_canvas') and hasattr(self, 'current_products'):
                self.root.after(200, self.refresh_product_layout)
    
    def refresh_product_layout(self):
        """Refresh the product layout after window resize."""
        if hasattr(self, 'current_products') and self.current_products:
            self.display_products(self.current_products)
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container with reduced padding
        self.main_frame = ttk.Frame(self.root, padding="5")  # Reduced from 10 to 5
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)  # Only header (row 0) and content (row 1), no footer
        
        # Header
        self.create_header()
        
        # Create main content area without sidebar
        self.create_main_content_area_full()
        
        # No footer - removed to maximize content space
    
    def create_sidebar_and_content(self):
        """Create the sidebar navigation and main content area."""
        content_container = ttk.Frame(self.main_frame)
        content_container.grid(row=1, column=0, columnspan=3, sticky="nsew")
        content_container.columnconfigure(1, weight=1)
        content_container.rowconfigure(0, weight=1)
        
        # Left sidebar
        self.create_sidebar(content_container)
        
        # Main content area
        self.create_main_content_area(content_container)
        
    def create_sidebar(self, parent):
        """Create the sliding left sidebar with navigation buttons."""
        # Sidebar container that can slide
        self.sidebar_container = tk.Frame(parent, bg="#e3f2fd")  # Changed to soft blue background
        self.sidebar_container.grid(row=0, column=0, sticky="nsw")
        
        # Sidebar state
        self.sidebar_expanded = True
        self.sidebar_width_expanded = 250
        self.sidebar_width_collapsed = 60
        self.sidebar_width_mobile = 40  # For very small screens
        self.animation_duration = 200  # milliseconds
        self.animation_steps = 10
        
        # Main sidebar frame with soft blue background
        self.sidebar_frame = tk.Frame(self.sidebar_container, bg="#e3f2fd",  # Changed to soft blue
                                     width=self.sidebar_width_expanded)
        self.sidebar_frame.pack(fill="both", expand=True)
        self.sidebar_frame.grid_propagate(False)
        
        # Toggle button at the top with soft blue theme
        self.toggle_btn = tk.Button(self.sidebar_frame, text="◀",
                                   command=self.toggle_sidebar,
                                   bg="#bbdefb", fg="black",  # Soft blue with black text
                                   font=("Arial", 12, "bold"),
                                   padx=10, pady=10,
                                   relief="flat",
                                   cursor="hand2",
                                   borderwidth=0,
                                   highlightthickness=0)
        self.toggle_btn.pack(fill="x", padx=5, pady=(5, 10))
        
        # Add hover effects for toggle button with soft blue theme
        self.toggle_btn.bind("<Enter>", lambda e: self.toggle_btn.config(bg="#90caf9"))  # Lighter blue on hover
        self.toggle_btn.bind("<Leave>", lambda e: self.toggle_btn.config(bg="#bbdefb"))  # Back to soft blue
        
        # Scrollable content for sidebar with soft blue theme
        self.sidebar_canvas = tk.Canvas(self.sidebar_frame, bg="#e3f2fd",  # Changed to soft blue
                                       highlightthickness=0, bd=0)
        sidebar_scrollbar = ttk.Scrollbar(self.sidebar_frame, orient="vertical", 
                                         command=self.sidebar_canvas.yview)
        self.sidebar_scrollable_frame = tk.Frame(self.sidebar_canvas, bg="#e3f2fd")  # Changed to soft blue
        
        # Optimized scrolling configuration
        self.sidebar_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
        )
        
        self.sidebar_canvas.create_window((0, 0), window=self.sidebar_scrollable_frame, anchor="nw")
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        
        # Enable mouse wheel scrolling
        self.sidebar_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.sidebar_scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Sidebar buttons with icons and text
        self.sidebar_buttons_data = [
            ("📊", "register_screen", "#64b5f6", self.show_register_screen),
            ("📋", "order_history", "#81c784", self.show_order_history),
            ("💰", "daily_profit", "#ffb74d", self.show_daily_profit),
            ("💳", "manage_cash", "#a5d6a7", self.manage_cash),
            ("⚙️", "receipt_settings", "#ce93d8", self.open_receipt_settings),
            ("🌐", "language_settings_menu", "#b39ddb", self.open_language_settings),
            ("�", "backup_settings", "#90a4ae", self.open_backup_settings),
            ("�🔐", "close_register", "#f48fb1", self.close_register)
        ]
        
        self.sidebar_buttons = []
        for i, (icon, text_key, color, command) in enumerate(self.sidebar_buttons_data):
            btn_frame = tk.Frame(self.sidebar_scrollable_frame, bg="#e3f2fd")  # Changed to soft blue
            btn_frame.pack(fill="x", padx=5, pady=3)
            
            btn = tk.Button(btn_frame, text=f"{icon} {get_text(text_key)}",
                           command=command,
                           bg=color, fg="black",  # Changed text to black
                           font=("Arial", 10, "bold"),
                           padx=15, pady=12,
                           relief="flat",
                           activebackground="#ffffff",  # White on active
                           activeforeground="black",     # Black text on active
                           cursor="hand2",
                           anchor="w",
                           borderwidth=0,
                           highlightthickness=0)
            btn.pack(fill="x")
            
            # Add hover effects for better UX
            btn.bind("<Enter>", lambda e, b=btn, c=color: self._on_button_hover(b, c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: self._on_button_leave(b, c))
            
            # Store button reference for later updates
            self.sidebar_buttons.append((btn, icon, text_key))
            
        # Language section
        self.create_language_section()
        
        # Bind window resize event for responsive behavior
        self.root.bind('<Configure>', self._on_window_resize)
        
        # Set up initial responsive behavior
        self.root.after(100, self._setup_initial_responsive_layout)
        
        # Set initial state
        self.update_sidebar_display()
        
    def _setup_initial_responsive_layout(self):
        """Setup initial responsive layout based on window size."""
        try:
            window_width = self.root.winfo_width()
            
            # If window is too small, start with collapsed sidebar
            if window_width < 1024:
                if self.sidebar_expanded:
                    self.toggle_sidebar()
                    
            # Trigger initial responsive adjustments
            self._on_window_resize(type('Event', (), {'widget': self.root})())
            
        except Exception as e:
            # Silently handle any setup errors
            pass
    
    def create_language_section(self):
        """Create language switching section in sidebar."""
        # Separator
        separator = tk.Frame(self.sidebar_scrollable_frame, bg="#bbdefb", height=2)  # Changed to soft blue
        separator.pack(fill="x", padx=10, pady=(20, 10))
        
        # Language section header
        self.lang_header_frame = tk.Frame(self.sidebar_scrollable_frame, bg="#e3f2fd")  # Changed to soft blue
        self.lang_header_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.lang_header = tk.Label(self.lang_header_frame, text=f"🌐 {get_text('languages')}", 
                                   bg="#e3f2fd", fg="black",  # Changed text to black
                                   font=("Arial", 10, "bold"),
                                   anchor="w")
        self.lang_header.pack(fill="x")
        
        # Language buttons with soft color scheme
        self.language_buttons_data = [
            ("🇫🇷", "Français", "FR", "#81c784"),   # Soft green
            ("🇸🇦", "العربية", "AR", "#ce93d8"),    # Soft purple  
            ("🇺🇸", "English", "EN", "#64b5f6")     # Soft blue
        ]
        
        self.language_buttons = []
        for flag, name, code, color in self.language_buttons_data:
            btn_frame = tk.Frame(self.sidebar_scrollable_frame, bg="#e3f2fd")  # Changed to soft blue
            btn_frame.pack(fill="x", padx=5, pady=2)
            
            btn = tk.Button(btn_frame, text=f"{flag} {name}",
                           command=lambda c=code: self.quick_change_language(c),
                           bg=color, fg="black",  # Changed text to black
                           font=("Arial", 9, "bold"),
                           padx=10, pady=8,
                           relief="flat",
                           activebackground="#ffffff",  # White on active
                           activeforeground="black",     # Black text on active
                           cursor="hand2",
                           anchor="w")
            btn.pack(fill="x")
            
            self.language_buttons.append((btn, flag, name, code))
        
        # Current language indicator
        self.current_lang_indicator = tk.Label(self.sidebar_scrollable_frame, 
                                              text=f"• {get_text('current_language')}: Français",
                                              bg="#e3f2fd", fg="#757575",  # Changed to soft blue bg with gray text
                                              font=("Arial", 8),
                                              anchor="w")
        self.current_lang_indicator.pack(fill="x", padx=10, pady=(10, 20))
    
    def toggle_sidebar(self):
        """Toggle sidebar between expanded and collapsed states with smooth animation."""
        self.sidebar_expanded = not self.sidebar_expanded
        target_width = self.sidebar_width_expanded if self.sidebar_expanded else self.sidebar_width_collapsed
        
        # Smooth animation
        self._animate_sidebar_width(target_width)
        
        # Update toggle button immediately
        self.toggle_btn.config(text="◀" if self.sidebar_expanded else "▶")
        
        # Update display after animation
        self.root.after(self.animation_duration, self.update_sidebar_display)
    
    def _animate_sidebar_width(self, target_width):
        """Animate sidebar width change with improved smooth transition."""
        if not hasattr(self, 'animation_duration'):
            self.animation_duration = 150  # Slightly faster for better UX
            self.animation_steps = 8  # Fewer steps for smoother animation
            
        current_width = self.sidebar_frame.winfo_width()
        if abs(current_width - target_width) < 5:  # If difference is small, snap to target
            self.sidebar_frame.config(width=target_width)
            return
            
        step_size = (target_width - current_width) / self.animation_steps
        step_delay = self.animation_duration // self.animation_steps
        
        def animate_step(step):
            if step <= self.animation_steps:
                new_width = int(current_width + (step_size * step))
                # Ensure width doesn't go below minimum or above maximum
                new_width = max(self.sidebar_width_mobile, min(new_width, self.sidebar_width_expanded))
                self.sidebar_frame.config(width=new_width)
                
                # Update grid weights for better responsive behavior
                if hasattr(self, 'sidebar_container'):
                    if new_width <= self.sidebar_width_mobile + 10:
                        # Very small sidebar - minimize impact on layout
                        self.sidebar_container.grid_configure(sticky="nsw")
                    else:
                        # Normal sidebar behavior
                        self.sidebar_container.grid_configure(sticky="nsw")
                
                self.root.after(step_delay, lambda: animate_step(step + 1))
            else:
                # Ensure final width is exact
                self.sidebar_frame.config(width=target_width)
                # Force layout update
                self.root.update_idletasks()
        
        animate_step(1)
    
    def update_sidebar_display(self):
        """Update sidebar display based on expanded/collapsed state with responsive behavior."""
        window_width = self.root.winfo_width()
        
        if self.sidebar_expanded:
            # Show full buttons with text
            for btn, icon, text_key in self.sidebar_buttons:
                # On very small screens, use shorter text
                if window_width < 768:
                    btn.config(text=f"{icon} {get_text(text_key)[:8]}...")  # Truncate text
                    btn.config(font=("Arial", 8, "bold"))  # Smaller font
                else:
                    btn.config(text=f"{icon} {get_text(text_key)}")
                    btn.config(font=("Arial", 10, "bold"))  # Normal font
                
            for btn, flag, name, code in self.language_buttons:
                if window_width < 768:
                    btn.config(text=f"{flag} {name[:3]}")  # Shorter language names
                    btn.config(font=("Arial", 8, "bold"))
                else:
                    btn.config(text=f"{flag} {name}")
                    btn.config(font=("Arial", 9, "bold"))
                
            # Language header
            if window_width < 768:
                self.lang_header.config(text="🌐")
            else:
                self.lang_header.config(text=f"🌐 {get_text('languages')}")
                
            # Show/hide language indicator based on space
            if window_width > 600:
                self.current_lang_indicator.pack(fill="x", padx=5, pady=(5, 10))
            else:
                self.current_lang_indicator.pack_forget()
            
        else:
            # Show icon-only buttons for collapsed state
            for btn, icon, text_key in self.sidebar_buttons:
                btn.config(text=icon)
                btn.config(font=("Arial", 12, "bold"))  # Larger icons for collapsed
                
            for btn, flag, name, code in self.language_buttons:
                btn.config(text=flag)
                btn.config(font=("Arial", 10, "bold"))
                
            self.lang_header.config(text="🌐")
            self.current_lang_indicator.pack_forget()
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling in sidebar."""
        try:
            self.sidebar_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except:
            # Fallback for different platforms
            self.sidebar_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")
        
    def _on_button_hover(self, button, base_color):
        """Handle button hover effect with smooth color transition for soft blue theme."""
        # Lighten the color on hover for better visual feedback with soft blue theme
        hover_colors = {
            "#64b5f6": "#90caf9",  # Lighter soft blue
            "#81c784": "#a5d6a7",  # Lighter soft green
            "#ffb74d": "#ffcc80",  # Lighter soft orange
            "#a5d6a7": "#c8e6c9",  # Lighter light green
            "#ce93d8": "#e1bee7",  # Lighter soft purple
            "#b39ddb": "#d1c4e9",  # Lighter light purple
            "#90a4ae": "#b0bec5",  # Lighter soft gray
            "#f48fb1": "#f8bbd9",  # Lighter soft pink
        }
        hover_color = hover_colors.get(base_color, "#e0e0e0")  # Default light gray
        button.config(bg=hover_color)
        
    def _on_button_leave(self, button, base_color):
        """Handle button leave effect."""
        button.config(bg=base_color)
        
    def _on_window_resize(self, event):
        """Handle window resize for enhanced responsive behavior."""
        if event.widget == self.root:
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            # Enhanced responsive behavior with better breakpoints
            
            # Very small screens (mobile-like) - Auto-collapse and use minimal width
            if window_width < 768:
                if self.sidebar_expanded:
                    self.toggle_sidebar()
                # Use mobile width for collapsed state
                self.sidebar_width_collapsed = self.sidebar_width_mobile
                
            # Small screens (tablet-like) - Auto-collapse but normal width
            elif window_width < 1024:
                if self.sidebar_expanded:
                    self.toggle_sidebar()
                # Use normal collapsed width
                self.sidebar_width_collapsed = 60
                
            # Medium screens - Keep current state but optimize widths
            elif window_width < 1280:
                # Adjust sidebar width based on available space
                optimal_expanded_width = min(250, window_width * 0.2)  # Max 20% of screen
                self.sidebar_width_expanded = max(200, optimal_expanded_width)  # Min 200px
                self.sidebar_width_collapsed = 60
                
            # Large screens - Allow full sidebar if desired
            else:
                # Reset to optimal widths for large screens
                self.sidebar_width_expanded = 250
                self.sidebar_width_collapsed = 60
                
            # Update sidebar display if needed
            if hasattr(self, 'sidebar_frame'):
                current_width = self.sidebar_width_expanded if self.sidebar_expanded else self.sidebar_width_collapsed
                self.sidebar_frame.config(width=current_width)
                
            # Trigger layout refresh for product grid and other responsive elements
            self.root.after(100, self._refresh_responsive_layout)
    
    def _refresh_responsive_layout(self):
        """Refresh layout elements that need to adapt to window size changes."""
        try:
            # Refresh product grid if it exists
            if hasattr(self, 'current_products') and self.current_products:
                self.display_products(self.current_products)
                
            # Update any other responsive elements here
            
        except Exception as e:
            # Silently handle any layout refresh errors
            pass
    
    def quick_change_language(self, lang_code):
        """Quick change language and refresh UI."""
        try:
            print(f"Quick changing language to: {lang_code}")
            
            # Apply language immediately
            language_manager.apply_language_immediately(lang_code)
            language_manager.save_settings()
            
            # Refresh UI including sidebar
            self.refresh_ui_language()
            self.update_sidebar_display()
            
            # Update current language indicator
            lang_names = {"FR": "Français", "AR": "العربية", "EN": "English"}
            current_name = lang_names.get(lang_code, lang_code)
            if hasattr(self, 'current_lang_indicator'):
                self.current_lang_indicator.config(text=f"• {get_text('current_language')}: {current_name}")
            
            print(f"Language changed to: {language_manager.settings.current_language}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change language: {e}")
        
    def create_main_content_area(self, parent):
        """Create the responsive main content area."""
        self.content_area = ttk.Frame(parent)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        
        # Enhanced responsive grid configuration
        self.content_area.columnconfigure(0, weight=3, minsize=400)  # Products area - minimum width
        self.content_area.columnconfigure(1, weight=1, minsize=250)  # Cart area - minimum width
        self.content_area.rowconfigure(1, weight=1)
        
        # Configure parent to properly distribute space
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        
        # Initially show the register screen
        self.show_register_screen()
        
    def create_main_content_area_full(self):
        """Create the main content area without sidebar - full width."""
        self.content_area = ttk.Frame(self.main_frame)
        self.content_area.grid(row=1, column=0, sticky="nsew")
        
        # Enhanced responsive grid configuration for full width
        self.content_area.columnconfigure(0, weight=3, minsize=400)  # Products area - minimum width
        self.content_area.columnconfigure(1, weight=1, minsize=250)  # Cart area - minimum width
        self.content_area.rowconfigure(0, weight=1)  # Row 0 should get the expandable space
        
        # Configure main frame to properly distribute space
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Initially show the register screen
        self.show_register_screen()
        
    def create_header(self):
        """Create a compact header with store info and navigation."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 5))  # Reduced padding from 10 to 5
        header_frame.columnconfigure(1, weight=1)
        
        # Logo and title - more compact
        logo_frame = ttk.Frame(header_frame)
        logo_frame.grid(row=0, column=0, sticky="w")
        
        title_label = ttk.Label(logo_frame, text=get_text("point_of_sale"), 
                               font=("Arial", 14, "bold"),  # Reduced from 16 to 14
                               foreground="#1976d2")  # Changed to soft blue
        title_label.pack()
        
        subtitle_label = ttk.Label(logo_frame, text=get_text("pos"),
                                  font=("Arial", 10),  # Reduced from 12 to 10
                                  foreground="#424242")  # Changed to dark gray
        subtitle_label.pack()
        
        # Store and register info - more compact
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=1, sticky="")
        
        store_label = ttk.Label(info_frame, text=f"Magasin: {self.current_store}",
                               font=("Arial", 10))  # Reduced from 12 to 10
        store_label.pack()
        
        register_label = ttk.Label(info_frame, text=self.current_register,
                                  font=("Arial", 10))  # Reduced from 12 to 10
        register_label.pack()
        
        # User info and logout - more compact
        user_frame = ttk.Frame(header_frame)
        user_frame.grid(row=0, column=2, sticky="e")
        
        # Settings button - positioned at top right
        settings_btn = ttk.Button(user_frame, text="⚙️ " + get_text("settings"),
                                command=self.open_settings_dialog,
                                style="Accent.TButton")
        settings_btn.pack(side="right", padx=(5, 0))
        
        # Current user display
        current_user = user_manager.get_current_user()
        user_text = f"{get_text('logged_in_as')}: {current_user.name}" if current_user else get_text("admin")
        self.user_label = ttk.Label(user_frame, text=user_text, font=("Arial", 10))  # Reduced from 12 to 10
        self.user_label.pack(side="right", padx=(0, 10))
        
        # Admin panel button (only for admins) - more compact
        if user_manager.is_admin():
            admin_btn = ttk.Button(user_frame, text=get_text("admin_panel"),
                                  command=self.show_user_management,
                                  style="Info.TButton")
            admin_btn.pack(side="right", padx=(0, 5))
        
        # Cash management button - more compact
        cash_mgmt_btn = ttk.Button(user_frame, text=get_text("manage_cash").upper(),
                                  command=self.manage_cash,
                                  style="Warning.TButton")
        cash_mgmt_btn.pack(side="right", padx=(0, 5))
        
        logout_btn = ttk.Button(user_frame, text=get_text("logout"),
                               command=self.logout_user,
                               style="Danger.TButton")
        logout_btn.pack(side="right", padx=(0, 5))
        
    def show_register_screen(self):
        """Show the main register/POS screen."""
        # Clear the content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Recreate the POS interface
        self.create_pos_interface()
        
    def create_pos_interface(self):
        """Create the main POS interface with optimized layout."""
        content_frame = ttk.Frame(self.content_area)
        content_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        # Optimize column weights: more space for products (3), adequate space for cart (2)
        content_frame.columnconfigure(0, weight=3)  # Products area gets more space
        content_frame.columnconfigure(1, weight=2)  # Cart area gets adequate space
        content_frame.rowconfigure(0, weight=0)     # Product buttons row - fixed height
        content_frame.rowconfigure(1, weight=1)     # Main content row - expandable height
        
        # Product management buttons
        self.create_product_buttons(content_frame)
        
        # Left side - Products grid
        self.create_products_area(content_frame)
        
        # Right side - Cart and totals
        self.create_cart_area(content_frame)
        
    def create_product_buttons(self, parent):
        """Create product management buttons with compact spacing."""
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))  # Reduced from 10 to 5
        
        buttons_data = [
            (get_text("all"), "#90a4ae", self.show_all_products),     # Soft gray
            (get_text("inventory"), "#64b5f6", self.show_inventory),  # Soft blue
            (get_text("scan_product"), "#81c784", self.scan_product)  # Soft green
        ]
        
        for i, (text, color, command) in enumerate(buttons_data):
            btn = tk.Button(btn_frame, text=text, 
                           command=command,
                           bg=color, fg="black",  # Changed to black text
                           font=("Arial", 9),  # Slightly smaller font
                           padx=12, pady=4)    # Reduced padding
            btn.grid(row=0, column=i, padx=3, sticky="ew")  # Reduced padx from 5 to 3
            
    def create_products_area(self, parent):
        """Create the responsive products display area with optimized spacing."""
        # Main products container with modern styling
        products_container = tk.Frame(parent, bg="white", relief="solid", borderwidth=1)  # Changed to white background
        products_container.grid(row=1, column=0, sticky="nsew", padx=(0, 5))  # Reduced padx from 10 to 5
        products_container.rowconfigure(1, weight=1)
        products_container.columnconfigure(0, weight=1)
        
        # Products header with search and category info (more compact)
        header_frame = tk.Frame(products_container, bg="#64b5f6", height=35)  # Changed to soft blue
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.columnconfigure(1, weight=1)
        
        # Products title (smaller)
        products_title = tk.Label(header_frame, text="🛍️ Produits", 
                                 font=("Arial", 12, "bold"),  # Reduced from 14 to 12
                                 bg="#64b5f6", fg="black")  # Changed to black text
        products_title.grid(row=0, column=0, padx=10, pady=8, sticky="w")  # Reduced padding
        
        # Product count indicator (will be updated dynamically)
        self.products_count_label = tk.Label(header_frame, text="0 produits",
                                            font=("Arial", 9),  # Reduced from 10 to 9
                                            bg="#64b5f6", fg="#1a237e")  # Dark blue text
        self.products_count_label.grid(row=0, column=1, padx=10, pady=8, sticky="e")  # Reduced padding
        
        # Scrollable frame for products with improved responsiveness
        self.products_canvas = tk.Canvas(products_container, bg="white", highlightthickness=0)  # Changed to white
        scrollbar = ttk.Scrollbar(products_container, orient="vertical", command=self.products_canvas.yview)
        self.products_scrollable_frame = tk.Frame(self.products_canvas, bg="white")  # Changed to white
        
        # Bind canvas resize to update scrollable frame width
        def on_canvas_configure(event):
            # Update the scrollable frame width to match canvas width
            canvas_width = event.width
            self.products_canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
            
        self.products_canvas.bind("<Configure>", on_canvas_configure)
        
        # Configure scrollable frame to update scroll region
        def on_frame_configure(event):
            self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all"))
            
        self.products_scrollable_frame.bind("<Configure>", on_frame_configure)
        
        # Create window and store its ID for width updates
        self.canvas_frame_id = self.products_canvas.create_window((0, 0), window=self.products_scrollable_frame, anchor="nw")
        self.products_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid the canvas and scrollbar
        self.products_canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Mouse wheel binding for smooth scrolling
        def _on_mousewheel(event):
            self.products_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.products_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Add placeholder message for empty state
        self.create_empty_products_placeholder()
        
    def create_empty_products_placeholder(self):
        """Create placeholder for when no products are available."""
        self.empty_products_frame = tk.Frame(self.products_scrollable_frame, bg="#f5f5f5")
        self.empty_products_frame.grid(row=0, column=0, sticky="nsew", pady=100)
        self.products_scrollable_frame.columnconfigure(0, weight=1)
        
        # Empty state icon and message
        empty_icon = tk.Label(self.empty_products_frame, text="📦", 
                             font=("Arial", 48), 
                             bg="#f5f5f5", fg="#ddd")
        empty_icon.pack(pady=(20, 10))
        
        empty_text = tk.Label(self.empty_products_frame, text="Aucun produit disponible",
                             font=("Arial", 14),
                             bg="#f5f5f5", fg="#999")
        empty_text.pack()
        
        add_product_hint = tk.Label(self.empty_products_frame, text="Ajoutez des produits depuis le menu Gestion",
                                   font=("Arial", 11),
                                   bg="#f5f5f5", fg="#bbb")
        add_product_hint.pack(pady=(5, 0))
        
    def create_cart_area(self, parent):
        """Create the modern shopping cart and totals area with optimized spacing."""
        # Main cart container with modern styling
        cart_frame = tk.Frame(parent, bg="white", relief="solid", borderwidth=1)  # Changed to white
        cart_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=5)  # Reduced padx and pady
        cart_frame.rowconfigure(1, weight=1)
        cart_frame.columnconfigure(0, weight=1)
        
        # Cart header with improved styling (more compact)
        header_frame = tk.Frame(cart_frame, bg="#64b5f6", height=40)  # Changed to soft blue
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        
        cart_header = tk.Label(header_frame, text=f"🛒 {get_text('cart_header')}", 
                              font=("Arial", 14, "bold"),  # Reduced from 16 to 14
                              bg="#64b5f6", fg="black")  # Changed to black text
        cart_header.pack(pady=10)  # Reduced from 15 to 10
        
        # Items count indicator
        self.cart_count_label = tk.Label(header_frame, text="0 articles",
                                        font=("Arial", 9),  # Reduced from 10 to 9
                                        bg="#64b5f6", fg="#1a237e")  # Dark blue text
        self.cart_count_label.pack(side="bottom", pady=(0, 3))  # Reduced from 5 to 3
        
        # Cart items list with modern design
        self.create_cart_list(cart_frame)
        
        # Empty cart message (initially visible)
        self.empty_cart_frame = tk.Frame(cart_frame, bg="white")  # Changed to white
        self.empty_cart_frame.grid(row=1, column=0, sticky="nsew")
        
        empty_icon = tk.Label(self.empty_cart_frame, text="🛒", 
                             font=("Arial", 48), 
                             bg="white", fg="#e0e0e0")  # Changed to white bg with light gray icon
        empty_icon.pack(pady=(50, 10))
        
        empty_text = tk.Label(self.empty_cart_frame, text=get_text("cart_empty"),
                             font=("Arial", 12),
                             bg="white", fg="#757575")  # Changed to white bg with gray text
        empty_text.pack()
        
        # Quick actions frame (appears when cart has items)
        self.quick_actions_frame = tk.Frame(cart_frame, bg="white")  # Changed to white
        
        clear_cart_btn = tk.Button(self.quick_actions_frame, text="🗑️ Vider le panier",
                                  command=self.clear_cart,
                                  bg="#f48fb1", fg="black",  # Changed to soft pink with black text
                                  font=("Arial", 10, "bold"),
                                  relief="flat", padx=15, pady=8,
                                  cursor="hand2")
        clear_cart_btn.pack(side="left", padx=(10, 5), pady=10)
        
        # Totals section with enhanced design
        self.create_totals_section(cart_frame)
        
    def create_cart_list(self, parent):
        """Create the modern cart items list."""
        # Container for cart items
        self.cart_container = tk.Frame(parent, bg="#ffffff", relief="flat")
        
        # Scrollable frame for cart items
        self.cart_canvas = tk.Canvas(self.cart_container, bg="#ffffff", highlightthickness=0)
        cart_scrollbar = ttk.Scrollbar(self.cart_container, orient="vertical", command=self.cart_canvas.yview)
        self.cart_scrollable_frame = tk.Frame(self.cart_canvas, bg="#ffffff")
        
        self.cart_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
        )
        
        self.cart_canvas.create_window((0, 0), window=self.cart_scrollable_frame, anchor="nw")
        self.cart_canvas.configure(yscrollcommand=cart_scrollbar.set)
        
        self.cart_canvas.pack(side="left", fill="both", expand=True)
        cart_scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            self.cart_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.cart_canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Configure canvas scrolling region
        def _configure_scroll_region():
            self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
        self.cart_scrollable_frame.bind("<Configure>", lambda e: _configure_scroll_region())
        
    def create_totals_section(self, parent):
        """Create the modern totals and payment section with compact layout."""
        # Totals container with modern styling
        totals_container = tk.Frame(parent, bg="#e3f2fd", relief="solid", borderwidth=1)
        totals_container.grid(row=3, column=0, sticky="ew", padx=0, pady=(5, 0))  # Reduced from 10 to 5
        totals_container.columnconfigure(0, weight=1)
        
        # Totals content frame with reduced padding
        totals_frame = tk.Frame(totals_container, bg="#e3f2fd", padx=15, pady=10)  # Reduced padding
        totals_frame.grid(row=0, column=0, sticky="ew")
        totals_frame.columnconfigure(1, weight=1)
        
        # Items count
        items_frame = tk.Frame(totals_frame, bg="#e3f2fd")
        items_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))  # Reduced from 10 to 8
        
        tk.Label(items_frame, text="Articles:", font=("Arial", 10),  # Reduced from 11 to 10
                bg="#e3f2fd", fg="#555").pack(side="left")
        self.items_count_label = tk.Label(items_frame, text="0", 
                                         font=("Arial", 10, "bold"),  # Reduced from 11 to 10
                                         bg="#e3f2fd", fg="#1976d2")
        self.items_count_label.pack(side="right")
        
        # Subtotal with improved styling
        subtotal_frame = tk.Frame(totals_frame, bg="#e3f2fd")
        subtotal_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=3)  # Reduced from 5 to 3
        
        tk.Label(subtotal_frame, text=get_text("subtotal_label"), 
                font=("Arial", 11),  # Reduced from 12 to 11
                bg="#e3f2fd", fg="#333").pack(side="left")
        self.subtotal_label = tk.Label(subtotal_frame, text="0,00 DH", 
                                      font=("Arial", 11, "bold"),  # Reduced from 12 to 11
                                      bg="#e3f2fd", fg="#666")
        self.subtotal_label.pack(side="right")
        
        # Separator line
        separator = tk.Frame(totals_frame, height=2, bg="#1976d2")
        separator.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 12))  # Reduced padding
        
        # Total with enhanced styling (slightly smaller)
        total_frame = tk.Frame(totals_frame, bg="#e3f2fd")
        total_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        tk.Label(total_frame, text=get_text("total_label"), 
                font=("Arial", 16, "bold"),  # Reduced from 18 to 16
                bg="#e3f2fd", fg="#1976d2").pack(side="left")
        self.total_label = tk.Label(total_frame, text="0,00 DH", 
                                   font=("Arial", 16, "bold"),  # Reduced from 18 to 16
                                   bg="#e3f2fd", fg="#1976d2")
        self.total_label.pack(side="right")
        
        # Payment buttons with modern design
        payment_frame = tk.Frame(totals_container, bg="#e3f2fd", pady=15)
        payment_frame.grid(row=1, column=0, sticky="ew")
        
        # Payment button
        self.pay_button = tk.Button(payment_frame, text=f"💳 {get_text('pay').upper()}",
                                   command=self.process_payment,
                                   bg="#64b5f6", fg="black",  # Changed to soft blue with black text
                                   font=("Arial", 14, "bold"),
                                   relief="flat", padx=30, pady=12,
                                   cursor="hand2", state="disabled")
        self.pay_button.pack(fill="x", padx=20, pady=(0, 5))
        
        # Suspend cart button
        suspend_button = tk.Button(payment_frame, text=f"⏸️ {get_text('suspend_cart')}",
                                  command=self.suspend_cart,
                                  bg="#ffb74d", fg="black",  # Changed to soft orange with black text
                                  font=("Arial", 11, "bold"),
                                  relief="flat", padx=20, pady=8,
                                  cursor="hand2")
        suspend_button.pack(fill="x", padx=20)
        
        # Add hover effects for buttons with soft theme
        def on_pay_enter(e):
            if self.pay_button['state'] == 'normal':
                self.pay_button.config(bg="#90caf9")  # Lighter blue on hover
        def on_pay_leave(e):
            if self.pay_button['state'] == 'normal':
                self.pay_button.config(bg="#64b5f6")  # Back to soft blue
        
        self.pay_button.bind("<Enter>", on_pay_enter)
        self.pay_button.bind("<Leave>", on_pay_leave)
        
        def on_suspend_enter(e):
            suspend_button.config(bg="#ffcc80")  # Lighter orange on hover
        def on_suspend_leave(e):
            suspend_button.config(bg="#ffb74d")  # Back to soft orange
            
        suspend_button.bind("<Enter>", on_suspend_enter)
        suspend_button.bind("<Leave>", on_suspend_leave)
        
    def setup_layout(self):
        """Setup the layout and styling."""
        # Configure styles
        style = ttk.Style()
        style.configure("Danger.TButton", foreground="red")
        
        # Load products
        self.load_products()
        
    def load_products(self):
        """Load products from database."""
        products = self.db_manager.get_all_products()
        self.products = products  # Store products for barcode scanning
        self.current_products = products  # Store for responsive resizing
        self.display_products(products)
        
    def display_products(self, products: List[Product]):
        """Display products in a responsive 3-column grid with dynamic sizing."""
        # Store current products for responsive resizing
        self.current_products = products
        
        # Clear existing products
        for widget in self.products_scrollable_frame.winfo_children():
            widget.destroy()
            
        # Update product count
        if hasattr(self, 'products_count_label'):
            count_text = f"{len(products)} produit{'s' if len(products) != 1 else ''}"
            self.products_count_label.config(text=count_text)
            
        if not products:
            self.create_empty_products_placeholder()
            return
            
        # Calculate responsive grid layout
        # Get current canvas width to determine optimal layout
        self.products_scrollable_frame.update_idletasks()
        canvas_width = self.products_canvas.winfo_width()
        
        # If canvas not yet sized, use default based on window size
        if canvas_width <= 1:
            window_width = self.root.winfo_width()
            canvas_width = max(800, window_width * 0.6)  # Estimate canvas width
            
        # Calculate optimal number of columns and card dimensions
        min_card_width = 180  # Reduced minimum card width
        max_card_width = 280  # Reduced maximum card width for more compact cards
        card_spacing = 10  # Reduced space between cards
        padding = 30  # Reduced horizontal padding
        
        # Calculate optimal columns (between 2-4 for best UX)
        available_width = canvas_width - padding
        max_possible_cols = available_width // (min_card_width + card_spacing)
        optimal_cols = min(max(2, max_possible_cols), 4)  # Between 2-4 columns
        
        # Use 3 columns as requested, optimized for more compact display
        max_cols = 3
        
        # Calculate actual card width for more compact display
        total_spacing = (max_cols - 1) * card_spacing
        available_for_cards = available_width - total_spacing
        card_width = min(max_card_width, max(min_card_width, available_for_cards // max_cols))
        
        # Configure responsive columns with minimal spacing
        for col in range(max_cols):
            self.products_scrollable_frame.columnconfigure(col, weight=1, minsize=card_width)
        
        # Configure row spacing to be minimal for more compact layout
        current_row = -1
            
        # Create product grid with responsive cards
        for i, product in enumerate(products):
            row = i // max_cols
            col = i % max_cols
            
            # Configure row for minimal spacing only when we encounter a new row
            if row != current_row:
                self.products_scrollable_frame.rowconfigure(row, weight=0, minsize=120)  # Fixed height for compactness
                current_row = row
            
            # Determine product card styling based on stock
            if product.stock_quantity == 0:
                card_bg = "#ffebee"  # Light red background
                card_border = "#f44336"  # Red border
                stock_indicator = "🔴"
                stock_status = "Rupture de stock"
            elif product.stock_quantity <= 3:
                card_bg = "#fff3e0"  # Light orange background  
                card_border = "#ff9800"  # Orange border
                stock_indicator = "🟠"
                stock_status = f"Stock faible ({product.stock_quantity})"
            else:
                card_bg = "#e8f5e8"  # Light green background
                card_border = "#4caf50"  # Green border
                stock_indicator = "🟢"
                stock_status = f"En stock ({product.stock_quantity})"
            
            # Create responsive product card - more compact
            product_frame = tk.Frame(self.products_scrollable_frame, 
                                   relief="solid", borderwidth=1,  # Reduced border width
                                   bg=card_bg, 
                                   highlightbackground=card_border,
                                   highlightthickness=1)
            product_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew", ipadx=5, ipady=5)  # Reduced padding
            
            # Remove the individual row configuration since we handle it above
            # Make rows expandable
            # self.products_scrollable_frame.rowconfigure(row, weight=1)  # Removed to use fixed height above
            
            # Configure card internal layout
            product_frame.columnconfigure(0, weight=1)
            
            # Card header with stock indicator - more compact
            header_frame = tk.Frame(product_frame, bg=card_bg)
            header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))  # Reduced padding
            header_frame.columnconfigure(0, weight=1)
            
            # Product category (left) - smaller font
            if product.category:
                category_label = tk.Label(header_frame, text=f"📂 {product.category}",
                                         font=("Arial", 8),  # Reduced font size
                                         bg=card_bg, fg="#666")
                category_label.grid(row=0, column=0, sticky="w")
            
            # Stock indicator (right) - smaller
            stock_label = tk.Label(header_frame, text=f"{stock_indicator}",
                                 font=("Arial", 12),  # Reduced font size
                                 bg=card_bg)
            stock_label.grid(row=0, column=1, sticky="e")
            
            # Product name with responsive text wrapping - more compact
            display_name = product.name
            # Calculate optimal text length based on card width
            max_chars = max(15, card_width // 12)  # Slightly shorter names
            if len(display_name) > max_chars:
                display_name = display_name[:max_chars-3] + "..."
                
            name_label = tk.Label(product_frame, text=display_name,
                                 font=("Arial", 11, "bold"),  # Reduced font size
                                 bg=card_bg, fg="#333",
                                 wraplength=card_width-30,  # Reduced wrap length
                                 justify="center")
            name_label.grid(row=1, column=0, pady=(0, 4), sticky="ew")  # Reduced padding
            
            # Price with enhanced styling - more compact
            price_label = tk.Label(product_frame, text=f"{product.price:.2f} DH",
                                  font=("Arial", 13, "bold"),  # Reduced font size
                                  bg=card_bg, fg="#1976d2")
            price_label.grid(row=2, column=0, pady=(0, 4))  # Reduced padding
            
            # Stock status with responsive text - more compact
            status_color = {"🔴": "#d32f2f", "🟠": "#f57c00", "🟢": "#388e3c"}[stock_indicator]
            status_label = tk.Label(product_frame, text=stock_status,
                                   font=("Arial", 8, "bold"),  # Reduced font size
                                   bg=card_bg, fg=status_color,
                                   wraplength=card_width-15)  # Reduced wrap length
            status_label.grid(row=3, column=0, pady=(0, 6))  # Reduced padding
            
            # Action button with responsive sizing - more compact
            if product.stock_quantity > 0:
                btn_text = f"🛒 Ajouter"
                btn_color = "#4caf50"
                btn_hover_color = "#45a049"
                btn_state = "normal"
                btn_cursor = "hand2"
            else:
                btn_text = f"❌ Indisponible"
                btn_color = "#cccccc"
                btn_hover_color = "#cccccc"
                btn_state = "disabled"
                btn_cursor = "arrow"
            
            add_btn = tk.Button(product_frame, text=btn_text,
                               command=lambda p=product: self.add_to_cart(p),
                               bg=btn_color, fg="black",  # Changed to black text
                               font=("Arial", 9, "bold"),  # Reduced font size
                               state=btn_state,
                               relief="flat",
                               cursor=btn_cursor,
                               padx=8, pady=5)  # Reduced padding
            add_btn.grid(row=4, column=0, sticky="ew", pady=(0, 2))  # Reduced padding
            
            # Add hover effects for enabled buttons
            if product.stock_quantity > 0:
                def make_hover_effect(button, normal_color, hover_color):
                    def on_enter(e):
                        if button['state'] == 'normal':
                            button.config(bg=hover_color)
                    def on_leave(e):
                        if button['state'] == 'normal':
                            button.config(bg=normal_color)
                    return on_enter, on_leave
                
                on_enter, on_leave = make_hover_effect(add_btn, btn_color, btn_hover_color)
                add_btn.bind("<Enter>", on_enter)
                add_btn.bind("<Leave>", on_leave)
        
        # Auto-adjust canvas scroll region after layout
        self.products_scrollable_frame.update_idletasks()
        self.products_canvas.configure(scrollregion=self.products_canvas.bbox("all"))
        
        # Force canvas to recalculate frame width
        def update_frame_width():
            canvas_width = self.products_canvas.winfo_width()
            if canvas_width > 1:
                self.products_canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
        
        # Schedule width update after layout is complete
        self.products_canvas.after(100, update_frame_width)
    
    def add_to_cart(self, product: Product):
        """Add a product to the cart."""
        # Check if product already in cart
        for item in self.cart_items:
            if item.product.id == product.id:
                item.quantity += 1
                break
        else:
            # Add new item
            sale_item = SaleItem(product, 1)
            self.cart_items.append(sale_item)
        
        self.update_cart_display()
        self.update_totals()
    
    def update_cart_display(self):
        """Update the modern cart display."""
        # Clear existing cart items
        for widget in self.cart_scrollable_frame.winfo_children():
            widget.destroy()
            
        total_items = sum(item.quantity for item in self.cart_items)
        
        # Update cart count in header
        if hasattr(self, 'cart_count_label'):
            count_text = f"{total_items} article{'s' if total_items != 1 else ''}"
            self.cart_count_label.config(text=count_text)
        
        # Show/hide empty cart vs cart items
        if not self.cart_items:
            self.cart_container.grid_remove()
            self.empty_cart_frame.grid(row=1, column=0, sticky="nsew")
            self.quick_actions_frame.grid_remove()
            if hasattr(self, 'pay_button'):
                self.pay_button.config(state="disabled")
        else:
            self.empty_cart_frame.grid_remove()
            self.cart_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
            self.quick_actions_frame.grid(row=2, column=0, sticky="ew")
            if hasattr(self, 'pay_button'):
                self.pay_button.config(state="normal")
            
            # Create modern cart item cards
            for idx, item in enumerate(self.cart_items):
                self.create_cart_item_card(idx, item)
        
        # Update totals and items count
        self.update_totals()
        if hasattr(self, 'items_count_label'):
            self.items_count_label.config(text=str(total_items))
        
        # Update canvas scroll region
        self.cart_scrollable_frame.update_idletasks()
        self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))
    
    def create_cart_item_card(self, idx, item):
        """Create a modern cart item card."""
        total_price = item.product.price * item.quantity
        
        # Main item card frame
        card_frame = tk.Frame(self.cart_scrollable_frame, 
                             bg="#ffffff", relief="solid", borderwidth=1,
                             padx=15, pady=12)
        card_frame.grid(row=idx, column=0, sticky="ew", padx=10, pady=5)
        self.cart_scrollable_frame.columnconfigure(0, weight=1)
        
        # Configure card layout
        card_frame.columnconfigure(1, weight=1)
        
        # Product info section
        info_frame = tk.Frame(card_frame, bg="#ffffff")
        info_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # Product name
        name_label = tk.Label(info_frame, text=item.product.name,
                             font=("Arial", 12, "bold"),
                             bg="#ffffff", fg="#333",
                             anchor="w")
        name_label.grid(row=0, column=0, sticky="w")
        
        # Unit price
        price_label = tk.Label(info_frame, text=f"{item.product.price:.2f} DH/unité",
                              font=("Arial", 10),
                              bg="#ffffff", fg="#666",
                              anchor="e")
        price_label.grid(row=0, column=1, sticky="e")
        
        # Quantity controls section
        qty_frame = tk.Frame(card_frame, bg="#ffffff")
        qty_frame.grid(row=1, column=0, sticky="w")
        
        # Decrease button
        minus_btn = tk.Button(qty_frame, text="−",
                             command=lambda: self.update_item_quantity(idx, -1),
                             bg="#f44336", fg="white",
                             font=("Arial", 12, "bold"),
                             width=3, relief="flat",
                             cursor="hand2")
        minus_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Quantity display
        qty_label = tk.Label(qty_frame, text=str(item.quantity),
                            font=("Arial", 12, "bold"),
                            bg="#e3f2fd", fg="#1976d2",
                            width=4, relief="solid", borderwidth=1)
        qty_label.grid(row=0, column=1, padx=5)
        
        # Increase button  
        plus_btn = tk.Button(qty_frame, text="+",
                            command=lambda: self.update_item_quantity(idx, 1),
                            bg="#4caf50", fg="white",
                            font=("Arial", 12, "bold"),
                            width=3, relief="flat",
                            cursor="hand2")
        plus_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Total price section
        total_frame = tk.Frame(card_frame, bg="#ffffff")
        total_frame.grid(row=1, column=1, sticky="e")
        
        total_label = tk.Label(total_frame, text=f"{total_price:.2f} DH",
                              font=("Arial", 14, "bold"),
                              bg="#ffffff", fg="#1976d2")
        total_label.pack()
        
        # Remove button
        remove_btn = tk.Button(card_frame, text="🗑️",
                              command=lambda: self.remove_cart_item(idx),
                              bg="#ff5722", fg="white",
                              font=("Arial", 10),
                              width=3, relief="flat",
                              cursor="hand2")
        remove_btn.grid(row=1, column=2, sticky="e", padx=(10, 0))
        
        # Add hover effects
        def on_minus_enter(e):
            minus_btn.config(bg="#d32f2f")
        def on_minus_leave(e):
            minus_btn.config(bg="#f44336")
        minus_btn.bind("<Enter>", on_minus_enter)
        minus_btn.bind("<Leave>", on_minus_leave)
        
        def on_plus_enter(e):
            plus_btn.config(bg="#45a049")
        def on_plus_leave(e):
            plus_btn.config(bg="#4caf50")
        plus_btn.bind("<Enter>", on_plus_enter)
        plus_btn.bind("<Leave>", on_plus_leave)
        
        def on_remove_enter(e):
            remove_btn.config(bg="#e64a19")
        def on_remove_leave(e):
            remove_btn.config(bg="#ff5722")
        remove_btn.bind("<Enter>", on_remove_enter)
        remove_btn.bind("<Leave>", on_remove_leave)
    
    def update_item_quantity(self, item_index, change):
        """Update the quantity of a cart item."""
        if 0 <= item_index < len(self.cart_items):
            item = self.cart_items[item_index]
            new_quantity = item.quantity + change
            
            if new_quantity <= 0:
                # Remove item if quantity becomes 0 or less
                self.remove_cart_item(item_index)
            elif new_quantity <= item.product.stock_quantity:
                # Update quantity if stock is available
                item.quantity = new_quantity
                self.update_cart_display()
            else:
                # Show stock limit message
                messagebox.showwarning(
                    get_text("warning"),
                    f"Stock disponible: {item.product.stock_quantity} unités"
                )
    
    def remove_cart_item(self, item_index):
        """Remove item from cart with confirmation."""
        if 0 <= item_index < len(self.cart_items):
            removed_item = self.cart_items.pop(item_index)
            self.update_cart_display()
            
            # Show confirmation message
            messagebox.showinfo(get_text("information"), 
                              f"{removed_item.product.name} {get_text('removed_from_cart')}")
            self.qty_label.config(text=str(self.cart_items[self.selected_cart_index].quantity))
    
    def update_totals(self):
        """Update the totals display."""
        subtotal = sum(item.product.price * item.quantity for item in self.cart_items)
        total = subtotal  # Add tax, discounts, etc. here
        
        self.subtotal_label.config(text=f"{subtotal:.2f} DH")
        self.total_label.config(text=f"{total:.2f} DH")
    
    def process_payment(self):
        """Process payment for the current sale."""
        if not self.cart_items:
            messagebox.showwarning(get_text("empty_cart"), get_text("add_products_before_payment"))
            return
            
        total = sum(item.product.price * item.quantity for item in self.cart_items)
        
        # Open payment dialog
        payment_window = PaymentWindow(self.root, total, self.complete_sale)
    
    def complete_sale(self, payment: Payment):
        """Complete the sale after payment."""
        try:
            # Validate cart is not empty
            if not self.cart_items:
                messagebox.showerror(get_text("error"), get_text("cart_empty_error"))
                return
            
            # Calculate total
            total = sum(item.product.price * item.quantity for item in self.cart_items)
            
            # Validate payment amount
            if payment.amount < total:
                messagebox.showerror(get_text("error"), get_text("insufficient_payment"))
                return
            
            # Calculate change for cash payments
            if payment.is_cash_payment:
                payment.calculate_change(total)
            
            # Create sale record
            sale = Sale()
            sale.items = self.cart_items.copy()
            # Note: sale.total is a computed property, no need to set it manually
            sale.payment = payment
            sale.timestamp = datetime.now()
            
            # Set cashier ID from logged in user
            current_user = user_manager.get_current_user()
            sale.cashier_id = current_user.id if current_user else 1
        
            # Save to database
            sale_id = self.db_manager.save_sale(sale)
            sale.id = sale_id
            
            # Update stock quantities - subtract sold items from inventory
            for item in sale.items:
                new_stock = item.product.stock_quantity - item.quantity
                self.db_manager.update_product_stock(item.product.id, new_stock)
                # Update the local product object as well
                item.product.stock_quantity = new_stock
            
            # Refresh product display to show updated stock
            self.load_products()
            
            # Log sale activity
            if current_user:
                user_manager.log_activity(
                    current_user.id,
                    "SALE_COMPLETED",
                    f"Completed sale #{sale_id} - Total: {sale.total:.2f} DH",
                    sale_id=sale_id,
                    amount=sale.total,
                    details=f"Items: {len(sale.items)}, Payment: {payment.method.value}"
                )
            
            # Generate and open PDF receipt automatically with format choice
            try:
                pdf_result = self.show_pdf_format_choice(sale)
                if pdf_result:
                    print(f"Receipt PDF generated: {pdf_result}")
                    pdf_info = f"\n\n📄 Receipt PDF generated and opened automatically!"
                else:
                    pdf_info = f"\n\n📄 PDF generation skipped by user."
                
            except Exception as print_error:
                print(f"Receipt PDF generation error: {print_error}")
                import traceback
                traceback.print_exc()
                pdf_info = "\n\n⚠️ Receipt PDF generation failed - please check console for details."
                
                # Fallback to text receipt
                try:
                    receipt_text = self.advanced_receipt_printer.generate_thermal_receipt_text(sale)
                    print("Receipt (text format):")
                    print(receipt_text)
                except Exception as fallback_error:
                    print(f"Fallback receipt generation error: {fallback_error}")
            
            # Clear cart
            self.clear_cart()
            
            # Show success message with payment details and PDF info
            if payment.is_cash_payment and payment.change_amount > 0:
                messagebox.showinfo(get_text("sale_completed"), 
                                   f"{get_text('sale_completed')} #{sale_id} {get_text('payment_successful')}!\n\n" +
                                   f"{get_text('grand_total')}: {sale.total:.2f} DH\n" +
                                   f"{get_text('amount_paid')}: {payment.amount:.2f} DH\n" +
                                   f"{get_text('change_due')}: {payment.change_amount:.2f} DH" +
                                   (pdf_info if 'pdf_info' in locals() else ""))
            else:
                messagebox.showinfo(get_text("sale_completed"), 
                                   f"{get_text('sale_completed')} #{sale_id} {get_text('payment_successful')}!\n\n" +
                                   f"{get_text('grand_total')}: {sale.total:.2f} DH\n" +
                                   f"{get_text('amount_paid')}: {payment.amount:.2f} DH" +
                                   (pdf_info if 'pdf_info' in locals() else ""))
            
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('sale_finalization_error')}: {str(e)}")
            print(f"Error in complete_sale: {e}")  # For debugging
    
    def clear_cart(self):
        """Clear the current cart."""
        self.cart_items.clear()
        self.update_cart_display()
        self.update_totals()
    
    # Button command methods
    def show_all_products(self):
        self.load_products()
        
    def show_pdf_format_choice(self, sale: Sale):
        """Generate 58mm PDF receipt and open automatically."""
        return self.advanced_receipt_printer.generate_and_open_pdf_receipt(sale, "58mm")
    
    def generate_sale_pdf_receipt(self, sale: Sale, size: str = "58mm"):
        """Generate and open PDF receipt for any sale."""
        try:
            pdf_path = self.advanced_receipt_printer.generate_and_open_pdf_receipt(sale, size)
            messagebox.showinfo(
                get_text("success"), 
                f"Receipt PDF generated and opened!\n\nFile saved at:\n{pdf_path}"
            )
            return pdf_path
        except Exception as e:
            messagebox.showerror(
                get_text("error"), 
                f"Failed to generate PDF receipt:\n{str(e)}"
            )
            return None
        
    def show_inventory(self):
        """Show the inventory management window."""
        inventory_window = InventoryManagementWindow(self.root, self.db_manager)
        self.root.wait_window(inventory_window.window)
        # Refresh products after inventory changes
        self.load_products()
        
    def scan_product(self):
        """Open barcode scanner dialog."""
        scanner_dialog = BarcodeScannerDialog(self.root, self.add_product_by_barcode)
        
    def add_product_by_barcode(self, barcode):
        """Add product to cart by barcode."""
        if not barcode.strip():
            return
            
        # Find product by barcode
        for product in self.products:
            if product.barcode and product.barcode.strip().lower() == barcode.strip().lower():
                self.add_to_cart(product)
                return
                
        # Product not found
        messagebox.showerror(get_text("error"), get_text("product_not_found_barcode"))
        
    def suspend_cart(self):
        messagebox.showinfo(get_text("suspend_function"), get_text("cart_suspended"))
        
    def _show_cash_drawer_delayed(self):
        """Show cash drawer opening dialog after window is ready."""
        try:
            if not self.show_cash_drawer_opening():
                # User cancelled - close application
                self.root.quit()
                self.root.destroy()
        except Exception as e:
            print(f"Error showing cash drawer dialog: {e}")
            # Continue without session management if there's an error
        
    def show_cash_drawer_opening(self) -> bool:
        """Show cash drawer opening dialog."""
        dialog = CashDrawerOpeningDialog(self.root, self.session_manager)
        self.root.wait_window(dialog.window)
        return dialog.result is not None
        
    def manage_cash(self):
        """Open cash management dialog to add or remove cash."""
        if not self.session_manager or not self.session_manager.get_current_session():
            messagebox.showwarning(get_text("warning"), get_text("no_active_session"))
            return
            
        dialog = CashManagementDialog(self.root, self.session_manager)
        self.root.wait_window(dialog.window)
        
    # Navigation methods for sidebar
    def show_order_history(self):
        """Show the order history screen."""
        # Clear the content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        # Create order history interface
        self.create_order_history_interface()
        
    def show_daily_profit(self):
        """Show the advanced reports screen."""
        from utils.advanced_reports import AdvancedReportsDialog
        AdvancedReportsDialog(self.root, self.db_manager)
        
    def close_register(self):
        """Close the register/logout."""
        self.logout()
        
    def create_order_history_interface(self):
        """Create the order history interface."""
        main_frame = ttk.Frame(self.content_area, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.content_area.rowconfigure(0, weight=1)
        self.content_area.columnconfigure(0, weight=1)
        
        # Back button
        back_btn = ttk.Button(main_frame, text=get_text("back_to_register"),
                             command=self.show_register_screen,
                             style="Info.TButton")
        back_btn.pack(anchor="w", pady=(0, 20))
        
        # Title
        title_label = ttk.Label(main_frame, text=get_text("order_history_title"),
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Filter section
        filter_frame = ttk.LabelFrame(main_frame, text=get_text("filters"), padding="10")
        filter_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(filter_frame, text=get_text("all_registers")).pack(anchor="w")
        
        # Orders list
        orders_frame = ttk.Frame(main_frame)
        orders_frame.pack(fill="both", expand=True)
        
        # Get sales from database
        sales = self.db_manager.get_all_sales()
        
        if not sales:
            no_orders_label = ttk.Label(orders_frame, 
                                       text=get_text("no_orders_found"),
                                       font=("Arial", 14),
                                       foreground="#666")
            no_orders_label.pack(pady=50)
        else:
            # Create orders list with treeview
            columns = ("Commande", "Heure", "Client", "Total", "Statut")
            orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings", height=15)
            
            # Configure columns
            orders_tree.heading("Commande", text=get_text("order"))
            orders_tree.heading("Heure", text=get_text("time"))
            orders_tree.heading("Client", text=get_text("client"))
            orders_tree.heading("Total", text=get_text("total"))
            orders_tree.heading("Statut", text=get_text("status"))
            
            orders_tree.column("Commande", width=100)
            orders_tree.column("Heure", width=150)
            orders_tree.column("Client", width=150)
            orders_tree.column("Total", width=100)
            orders_tree.column("Statut", width=120)
            
            # Add sales data
            for sale in sales:
                time_str = sale.timestamp.strftime("%d/%m/%Y %H:%M") if sale.timestamp else ""
                payment_method = get_text("cash") if sale.payment and sale.payment.is_cash_payment else get_text("card")
                orders_tree.insert("", "end", values=(
                    f"#{sale.id}",
                    time_str,
                    "Client invité",
                    f"{sale.total:.2f} DH",
                    f"Payé en : {payment_method} - Terminée"
                ))
            
            # Scrollbar for orders
            orders_scrollbar = ttk.Scrollbar(orders_frame, orient="vertical", command=orders_tree.yview)
            orders_tree.configure(yscrollcommand=orders_scrollbar.set)
            
            orders_tree.pack(side="left", fill="both", expand=True)
            orders_scrollbar.pack(side="right", fill="y")

    def logout(self):
        """Logout and close application."""
        if messagebox.askyesno(get_text("logout"), get_text("logout_confirm")):
            # End session (this will require cash drawer opening on next login)
            if self.session_manager:
                self.session_manager.end_session("Déconnexion manuelle")
            self.root.destroy()
    
    def open_settings_dialog(self):
        """Open the comprehensive settings dialog."""
        try:
            dialog = SettingsDialog(self.root, self)
            dialog.show()
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Settings error: {e}")
    
    def open_receipt_settings(self):
        """Open receipt settings dialog."""
        try:
            dialog = ReceiptSettingsDialog(self.root)
            self.root.wait_window(dialog.dialog)
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('settings_error')}: {e}")
    
    def open_language_settings(self):
        """Open language settings dialog."""
        try:
            dialog = LanguageSettingsDialog(self.root, callback=self.on_language_changed)
            dialog.show()
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('language_settings_error')}: {e}")
    
    def open_backup_settings(self):
        """Open backup settings dialog."""
        try:
            from dialogs.backup_settings_dialog import BackupSettingsDialog
            dialog = BackupSettingsDialog(self.root, self.backup_manager)
            result = dialog.show()
            
            if result:
                messagebox.showinfo(
                    get_text("success"), 
                    "Backup settings updated successfully!"
                )
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Error opening backup settings: {e}")
    
    def on_language_changed(self):
        """Callback when language is changed."""
        # Refresh UI elements that need translation updates
        self.refresh_ui_language()
        
    def refresh_ui_language(self):
        """Refresh UI elements with current language."""
        try:
            # Update window title
            self.root.title(get_text("app_title"))
            
            # Recreate the entire interface with new language
            self.recreate_interface()
            
            messagebox.showinfo(get_text("success"), 
                              get_text("operation_completed") + "!")
            
        except Exception as e:
            print(f"Error refreshing UI language: {e}")
            messagebox.showerror(get_text("error"), f"Error refreshing language: {e}")
    
    def create_interface(self):
        """Create the main interface components."""
        # Main content area without sidebar
        self.create_main_content_area_full()
    
    def recreate_interface(self):
        """Recreate the interface with current language."""
        try:
            # Find and destroy the content container (which contains sidebar and content)
            for widget in self.main_frame.winfo_children():
                if isinstance(widget, ttk.Frame) and widget.grid_info().get('row') == 1:
                    widget.destroy()
                    break
                    
            # Recreate the interface
            self.create_interface()
            
            # Show default screen (register)
            self.show_register_screen()
            
        except Exception as e:
            print(f"Error recreating interface: {e}")
    
    def show_print_dialog(self, sale):
        """Show printer selection dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Imprimer reçu")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        ttk.Label(main_frame, text=get_text("select_printer"), 
                  font=("Arial", 14, "bold")).pack(pady=(0, 20))        # Printer selection
        ttk.Label(main_frame, text=get_text("printer_label")).pack(anchor="w")
        printer_var = tk.StringVar()
        printer_combo = ttk.Combobox(main_frame, textvariable=printer_var,
                                   values=self.advanced_receipt_printer.get_available_printers(),
                                   state="readonly")
        printer_combo.pack(fill="x", pady=(5, 15))
        
        # Set default printer
        settings = self.advanced_receipt_printer.settings
        if settings.default_printer:
            printer_var.set(settings.default_printer)
        elif printer_combo['values']:
            printer_var.set(printer_combo['values'][0])
        
        # Format selection
        ttk.Label(main_frame, text=get_text("format_label")).pack(anchor="w")
        format_var = tk.StringVar(value="thermal")
        
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill="x", pady=(5, 15))
        
        ttk.Radiobutton(format_frame, text=get_text("thermal_receipt"), 
                        variable=format_var, value="thermal").pack(anchor="w")
        ttk.Radiobutton(format_frame, text=get_text("pdf_format"), 
                        variable=format_var, value="pdf").pack(anchor="w")        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        def print_receipt():
            try:
                printer_name = printer_var.get()
                format_type = format_var.get()
                
                if not printer_name:
                    messagebox.showwarning("Attention", "Veuillez sélectionner une imprimante")
                    return
                
                result = self.advanced_receipt_printer.print_receipt(sale, printer_name, format_type)
                
                if format_type == "pdf" or printer_name == "Save as PDF":
                    messagebox.showinfo("Succès", f"Reçu PDF sauvegardé: {result}")
                else:
                    messagebox.showinfo("Succès", "Reçu envoyé à l'imprimante")
                
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror(get_text("error"), f"{get_text('print_error')}: {e}")
        
        ttk.Button(button_frame, text=get_text("print"), command=print_receipt).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text=get_text("cancel"), command=dialog.destroy).pack(side="left")
        
        # Preview button
        def show_preview():
            preview_window = tk.Toplevel(dialog)
            preview_window.title("Aperçu du reçu")
            preview_window.geometry("500x600")
            
            preview_text = tk.Text(preview_window, font=("Courier", 8), wrap="none")
            scrollbar_y = ttk.Scrollbar(preview_window, orient="vertical", command=preview_text.yview)
            scrollbar_x = ttk.Scrollbar(preview_window, orient="horizontal", command=preview_text.xview)
            
            preview_text.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
            
            preview_text.grid(row=0, column=0, sticky="nsew")
            scrollbar_y.grid(row=0, column=1, sticky="ns")
            scrollbar_x.grid(row=1, column=0, sticky="ew")
            
            preview_window.grid_rowconfigure(0, weight=1)
            preview_window.grid_columnconfigure(0, weight=1)
            
            # Generate preview
            preview_content = self.advanced_receipt_printer.generate_thermal_receipt_text(sale)
            preview_text.insert(1.0, preview_content)
            preview_text.config(state="disabled")
        
        ttk.Button(button_frame, text=get_text("preview"), command=show_preview).pack(side="right")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


class PaymentWindow:
    """Payment processing window."""
    
    def __init__(self, parent, total: float, callback):
        self.total = total
        self.callback = callback
        self.result = None
        
        # Create payment window
        self.window = tk.Toplevel(parent)
        self.window.title("Paiement séparé")
        
        # Don't set fixed size - let it auto-size based on content
        self.window.resizable(False, False)  # Prevent manual resizing
        self.window.grab_set()
        
        # Set minimum size to ensure readability
        self.window.minsize(350, 400)
        
        # Center the window on parent
        self.window.transient(parent)
        
        self.create_widgets()
        
        # Auto-size window to fit content
        self.window.update_idletasks()  # Calculate required size
        
        # Center window on parent
        self.center_on_parent(parent)
        
        # Add keyboard shortcuts
        self.window.bind('<Return>', lambda e: self.process_payment())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        self.window.bind('<KP_Enter>', lambda e: self.process_payment())  # Numeric keypad Enter
        
    def center_on_parent(self, parent):
        """Center the payment window on the parent window."""
        parent.update_idletasks()
        
        # Get parent window position and size
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Get payment window size
        self.window.update_idletasks()
        window_width = self.window.winfo_reqwidth()
        window_height = self.window.winfo_reqheight()
        
        # Calculate center position
        x = parent_x + (parent_width - window_width) // 2
        y = parent_y + (parent_height - window_height) // 2
        
        # Ensure window stays on screen
        x = max(0, min(x, parent.winfo_screenwidth() - window_width))
        y = max(0, min(y, parent.winfo_screenheight() - window_height))
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def create_widgets(self):
        """Create payment interface widgets."""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Header - more compact
        header_label = ttk.Label(main_frame, text=get_text("split_payment"), 
                                font=("Arial", 14, "bold"))
        header_label.pack(pady=(0, 10))
        
        total_label = ttk.Label(main_frame, text=f"{self.total:.2f} DH", 
                               font=("Arial", 18, "bold"),
                               foreground="#20B2AA")
        total_label.pack(pady=(0, 15))
        
        # Payment details frame - more compact
        details_frame = ttk.LabelFrame(main_frame, text=get_text("payment_details"), padding="8")
        details_frame.pack(fill="x", pady=(0, 15))
        
        # Total réglé
        ttk.Label(details_frame, text=get_text("total_paid")).grid(row=0, column=0, sticky="w", pady=2)
        self.paid_label = ttk.Label(details_frame, text="0,00 DH")
        self.paid_label.grid(row=0, column=1, sticky="e", pady=2)
        
        # Restant
        ttk.Label(details_frame, text=get_text("remaining"), font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=2)
        self.remaining_label = ttk.Label(details_frame, text=f"{self.total:.2f} DH", 
                 font=("Arial", 10, "bold"), foreground="red")
        self.remaining_label.grid(row=1, column=1, sticky="e", pady=2)
        
        # Monnaie
        ttk.Label(details_frame, text=get_text("change")).grid(row=2, column=0, sticky="w", pady=2)
        self.change_label = ttk.Label(details_frame, text="0,00 DH")
        self.change_label.grid(row=2, column=1, sticky="e", pady=2)
        
        details_frame.columnconfigure(1, weight=1)
        
        # Payment method frame - more compact
        method_frame = ttk.LabelFrame(main_frame, text=get_text("payment_method"), padding="8")
        method_frame.pack(fill="x", pady=(0, 15))
        
        # Payment amount entry
        amount_frame = ttk.Frame(method_frame)
        amount_frame.pack(fill="x", pady=(0, 8))
        
        ttk.Label(amount_frame, text=get_text("amount_paid")).pack(side="left")
        self.amount_var = tk.StringVar(value=str(self.total))
        self.amount_var.trace('w', self.update_payment_details)  # Update details when amount changes
        
        # Amount entry with keyboard icon
        entry_frame = ttk.Frame(amount_frame)
        entry_frame.pack(side="right")
        amount_entry = ttk.Entry(entry_frame, textvariable=self.amount_var, width=15)
        amount_entry.pack(side="left")
        
        # Add keyboard icon
        from utils.virtual_keyboard import KeyboardButton
        keyboard_btn = KeyboardButton(entry_frame, amount_entry)
        keyboard_btn.pack(side="left", padx=(2, 0))
        
        amount_entry.focus()  # Focus on amount entry
        
        # Payment method selection
        method_selection_frame = ttk.Frame(method_frame)
        method_selection_frame.pack(fill="x")
        
        self.payment_method = tk.StringVar(value="cash")
        cash_radio = ttk.Radiobutton(method_selection_frame, text=f"💰 {get_text('cash')}", 
                                    variable=self.payment_method, value="cash")
        cash_radio.pack(side="left")
        
        card_radio = ttk.Radiobutton(method_selection_frame, text=f"💳 {get_text('card')}", 
                                    variable=self.payment_method, value="card")
        card_radio.pack(side="left", padx=(20, 0))
        
        # Numpad
        self.create_numpad(main_frame)
        
        # Action buttons - more compact
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        pay_button = tk.Button(button_frame, text=get_text("pay").upper(), 
                              command=self.process_payment,
                              bg="#90EE90", fg="black",
                              font=("Arial", 11, "bold"),
                              pady=8)
        pay_button.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        cancel_button = tk.Button(button_frame, text=get_text("back").upper(), 
                                 command=self.window.destroy,
                                 bg="#ddd", fg="black",
                                 font=("Arial", 11, "bold"),
                                 pady=8)
        cancel_button.pack(side="right", fill="x", expand=True)
        
    def create_numpad(self, parent):
        """Create numpad for amount entry."""
        numpad_frame = ttk.LabelFrame(parent, text=get_text("quick_entry"), padding="8")
        numpad_frame.pack(fill="x", pady=(0, 15))
        
        # Quick amounts row - more compact
        quick_frame = ttk.Frame(numpad_frame)
        quick_frame.pack(fill="x", pady=(0, 8))
        
        # Add multiple quick amounts based on total
        quick_amounts = []
        if self.total <= 50:
            quick_amounts = [self.total, 50.0, 100.0]
        elif self.total <= 100:
            quick_amounts = [self.total, self.total + 50, 200.0]
        else:
            quick_amounts = [self.total, self.total + 100, self.total + 200]
        
        for i, amount in enumerate(quick_amounts):
            btn = tk.Button(quick_frame, text=f"{amount:.0f} DH",
                           command=lambda a=amount: self.set_amount(a),
                           bg="#e8f4f8", fg="#20B2AA",
                           font=("Arial", 9),
                           pady=5)
            btn.pack(side="left", fill="x", expand=True, padx=(0, 3 if i < len(quick_amounts)-1 else 0))
        
        # Number pad - more compact
        pad_frame = ttk.Frame(numpad_frame)
        pad_frame.pack()
        
        buttons = [
            ['1', '2', '3', 'C'],
            ['4', '5', '6', '←'],
            ['7', '8', '9', ''],
            ['0', ',', '00', '']
        ]
        
        for i, row in enumerate(buttons):
            for j, btn_text in enumerate(row):
                if btn_text == '':
                    # Empty space
                    continue
                elif btn_text == 'C':
                    btn = tk.Button(pad_frame, text=btn_text,
                                   command=self.clear_amount,
                                   bg="#ffebee", fg="#d32f2f",
                                   font=("Arial", 9, "bold"),
                                   width=6, height=1)
                elif btn_text == '←':
                    btn = tk.Button(pad_frame, text=btn_text,
                                   command=self.backspace,
                                   bg="#fff3e0", fg="#f57c00",
                                   font=("Arial", 9, "bold"),
                                   width=6, height=1)
                else:
                    btn = tk.Button(pad_frame, text=btn_text,
                                   command=lambda t=btn_text: self.add_digit(t),
                                   bg="white", fg="black",
                                   font=("Arial", 9),
                                   width=6, height=1)
                
                btn.grid(row=i, column=j, padx=1, pady=1, sticky="nsew")
        
        # Initialize payment details
        self.update_payment_details()
    
    def update_payment_details(self, *args):
        """Update payment details in real-time."""
        try:
            current_amount = float(self.amount_var.get().replace(',', '.'))
        except (ValueError, AttributeError):
            current_amount = 0.0
        
        # Update paid amount
        self.paid_label.config(text=f"{current_amount:.2f} DH")
        
        # Update remaining amount
        remaining = max(0, self.total - current_amount)
        if remaining > 0:
            self.remaining_label.config(text=f"{remaining:.2f} DH", foreground="red")
        else:
            self.remaining_label.config(text="0,00 DH", foreground="green")
        
        # Update change amount
        change = max(0, current_amount - self.total)
        if change > 0:
            self.change_label.config(text=f"{change:.2f} DH", foreground="green")
        else:
            self.change_label.config(text="0,00 DH", foreground="black")
    
    def set_amount(self, amount: float):
        """Set predefined amount."""
        self.amount_var.set(str(amount))
        
    def add_digit(self, digit: str):
        """Add digit to amount."""
        current = self.amount_var.get()
        if current == "0":
            self.amount_var.set(digit)
        else:
            self.amount_var.set(current + digit)
            
    def clear_amount(self):
        """Clear amount."""
        self.amount_var.set("0")
        
    def backspace(self):
        """Remove last digit."""
        current = self.amount_var.get()
        if len(current) > 1:
            self.amount_var.set(current[:-1])
        else:
            self.amount_var.set("0")
    
    def process_payment(self):
        """Process the payment."""
        try:
            amount_str = self.amount_var.get().replace(',', '.')
            amount = float(amount_str)
            
            if amount <= 0:
                messagebox.showwarning("Montant invalide", 
                                     "Le montant doit être supérieur à 0")
                return
            
            if amount < self.total:
                messagebox.showwarning("Montant insuffisant", 
                                     f"Le montant payé ({amount:.2f} DH) est inférieur au total ({self.total:.2f} DH)")
                return
            
            # Create payment object
            method = PaymentMethod.CASH if self.payment_method.get() == "cash" else PaymentMethod.CARD
            payment = Payment(method, amount)
            payment.mark_completed()  # Mark payment as completed
            
            # Show confirmation for cash payments with change
            if payment.is_cash_payment and amount > self.total:
                change = amount - self.total
                result = messagebox.askyesno("Confirmer le paiement", 
                                           f"Montant payé: {amount:.2f} DH\n" +
                                           f"Total: {self.total:.2f} DH\n" +
                                           f"Monnaie à rendre: {change:.2f} DH\n\n" +
                                           "Confirmer le paiement?")
                if not result:
                    return
            
            # Call callback
            self.callback(payment)
            
            self.window.destroy()
            
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("invalid_amount"))


class ProductDialog:
    """Dialog for adding new products."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.result = None
        
        # Create dialog window
        self.window = tk.Toplevel(parent)
        self.window.title("Ajouter un produit")
        self.window.geometry("400x300")
        self.window.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Product name
        ttk.Label(main_frame, text=get_text("product_name_label")).grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, pady=5)
        
        # Product price
        ttk.Label(main_frame, text=get_text("price_label")).grid(row=1, column=0, sticky="w", pady=5)
        self.price_var = tk.StringVar()
        price_entry = ttk.Entry(main_frame, textvariable=self.price_var, width=30)
        price_entry.grid(row=1, column=1, pady=5)
        
        # Product description
        ttk.Label(main_frame, text=get_text("description_label")).grid(row=2, column=0, sticky="nw", pady=5)
        self.description_var = tk.StringVar()
        desc_entry = tk.Text(main_frame, width=25, height=4)
        desc_entry.grid(row=2, column=1, pady=5)
        self.desc_entry = desc_entry
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(button_frame, text=get_text("save"), command=self.save_product)
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = ttk.Button(button_frame, text=get_text("cancel"), command=self.window.destroy)
        cancel_btn.pack(side="right")
        
        # Focus on name entry
        name_entry.focus()
        
    def save_product(self):
        """Save the new product."""
        try:
            name = self.name_var.get().strip()
            price = float(self.price_var.get().replace(',', '.'))
            description = self.desc_entry.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror(get_text("error"), get_text("product_name_required"))
                return
                
            if price <= 0:
                messagebox.showerror(get_text("error"), get_text("price_must_be_positive"))
                return
            
            # Create product
            product = Product(None, name, description, price)
            product_id = self.db_manager.save_product(product)
            
            self.result = product_id
            self.window.destroy()
            
            messagebox.showinfo("Succès", f"Produit '{name}' ajouté avec succès!")
            
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("invalid_price"))


class InventoryManagementWindow:
    """Advanced inventory management window."""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.products = []
        self.filtered_products = []
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Gestion d'Inventaire")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        # Create interface
        self.create_interface()
        
        # Load products
        self.load_products()
        
    def center_window(self):
        """Center the window on parent."""
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 1200) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 700) // 2
        self.window.geometry(f"1200x700+{x}+{y}")
        
    def create_interface(self):
        """Create the inventory management interface."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Content area
        self.create_content_area(main_frame)
        
        # Footer
        self.create_footer(main_frame)
        
    def create_header(self, parent):
        """Create header with title and search."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text=get_text("inventory_management"), 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Search frame
        search_frame = ttk.Frame(header_frame)
        search_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Label(search_frame, text=get_text("search_colon"), font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_products)
        
        # Search entry with keyboard icon
        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(side="left", padx=(0, 10))
        search_entry = ttk.Entry(search_entry_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left")
        
        # Add keyboard icon for search
        from utils.virtual_keyboard import KeyboardButton
        search_keyboard = KeyboardButton(search_entry_frame, search_entry)
        search_keyboard.pack(side="left", padx=(2, 0))
        
        # Category filter
        ttk.Label(search_frame, text=get_text("category_colon"), font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.category_var = tk.StringVar(value=get_text("all_categories"))
        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var, 
                                          width=15, state="readonly")
        self.category_combo.pack(side="left")
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_products())
        
    def create_content_area(self, parent):
        """Create the main content area with product list and details."""
        content_frame = ttk.Frame(parent)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)
        
        # Products list
        self.create_products_list(content_frame)
        
        # Product details/edit panel
        self.create_product_details(content_frame)
        
    def create_products_list(self, parent):
        """Create the products list with treeview."""
        list_frame = ttk.LabelFrame(parent, text=get_text("product_list"), padding="10")
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # Treeview for products
        columns = (get_text("product_id"), get_text("product_name"), get_text("category"), 
                  get_text("supplier"), get_text("cost_price"), get_text("sell_price"), 
                  get_text("stock"), get_text("status"))
        self.products_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=20)
        
        # Configure columns
        column_widths = {get_text("product_id"): 50, get_text("product_name"): 150, 
                        get_text("category"): 100, get_text("supplier"): 100, 
                        get_text("cost_price"): 80, get_text("sell_price"): 80, 
                        get_text("stock"): 60, get_text("status"): 80}
        
        for col in columns:
            self.products_tree.heading(col, text=col, command=lambda c=col: self.sort_products(c))
            self.products_tree.column(col, width=column_widths.get(col, 100))
            
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid scrollbars and treeview
        self.products_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind selection
        self.products_tree.bind('<<TreeviewSelect>>', self.on_product_select)
        
    def create_product_details(self, parent):
        """Create the product details/edit panel."""
        details_frame = ttk.LabelFrame(parent, text=get_text("product_details"), padding="10")
        details_frame.grid(row=0, column=1, sticky="nsew")
        
        # Create scrollable frame for form
        canvas = tk.Canvas(details_frame)
        scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=canvas.yview)
        self.details_scrollable_frame = ttk.Frame(canvas)
        
        self.details_scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.details_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Form fields
        self.create_product_form()
        
    def create_product_form(self):
        """Create the product form fields."""
        form_frame = self.details_scrollable_frame
        
        # Product ID (read-only)
        ttk.Label(form_frame, text=get_text("product_id_label"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.id_var = tk.StringVar()
        id_entry = ttk.Entry(form_frame, textvariable=self.id_var, state="readonly", width=40)
        id_entry.pack(fill="x", pady=(0, 15))
        
        # Product Name
        ttk.Label(form_frame, text=get_text("product_name_label_detailed"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.name_var = tk.StringVar()
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill="x", pady=(0, 15))
        name_entry = ttk.Entry(name_frame, textvariable=self.name_var, width=40)
        name_entry.pack(side="left", fill="x", expand=True)
        from utils.virtual_keyboard import KeyboardButton
        KeyboardButton(name_frame, name_entry).pack(side="right", padx=(5, 0))
        
        # Category
        ttk.Label(form_frame, text=get_text("category_label"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.form_category_var = tk.StringVar()
        category_frame = ttk.Frame(form_frame)
        category_frame.pack(fill="x", pady=(0, 15))
        category_entry = ttk.Entry(category_frame, textvariable=self.form_category_var, width=40)
        category_entry.pack(side="left", fill="x", expand=True)
        KeyboardButton(category_frame, category_entry).pack(side="right", padx=(5, 0))
        
        # Supplier
        ttk.Label(form_frame, text=get_text("supplier_label"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.supplier_var = tk.StringVar()
        supplier_frame = ttk.Frame(form_frame)
        supplier_frame.pack(fill="x", pady=(0, 15))
        supplier_entry = ttk.Entry(supplier_frame, textvariable=self.supplier_var, width=40)
        supplier_entry.pack(side="left", fill="x", expand=True)
        KeyboardButton(supplier_frame, supplier_entry).pack(side="right", padx=(5, 0))
        
        # Barcode
        ttk.Label(form_frame, text=get_text("barcode_label"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.barcode_var = tk.StringVar()
        barcode_frame = ttk.Frame(form_frame)
        barcode_frame.pack(fill="x", pady=(0, 15))
        barcode_entry = ttk.Entry(barcode_frame, textvariable=self.barcode_var, width=40)
        barcode_entry.pack(side="left", fill="x", expand=True)
        KeyboardButton(barcode_frame, barcode_entry).pack(side="right", padx=(5, 0))
        
        # Cost Price
        ttk.Label(form_frame, text=get_text("cost_price_no_tax"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.cost_price_var = tk.StringVar()
        cost_frame = ttk.Frame(form_frame)
        cost_frame.pack(fill="x", pady=(0, 15))
        cost_entry = ttk.Entry(cost_frame, textvariable=self.cost_price_var, width=40)
        cost_entry.pack(side="left", fill="x", expand=True)
        KeyboardButton(cost_frame, cost_entry).pack(side="right", padx=(5, 0))
        
        # Selling Price
        ttk.Label(form_frame, text=get_text("selling_price"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.selling_price_var = tk.StringVar()
        selling_frame = ttk.Frame(form_frame)
        selling_frame.pack(fill="x", pady=(0, 15))
        selling_entry = ttk.Entry(selling_frame, textvariable=self.selling_price_var, width=40)
        selling_entry.pack(side="left", fill="x", expand=True)
        KeyboardButton(selling_frame, selling_entry).pack(side="right", padx=(5, 0))
        
        # Stock Quantity
        ttk.Label(form_frame, text=get_text("stock_quantity"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.stock_var = tk.StringVar()
        stock_frame = ttk.Frame(form_frame)
        stock_frame.pack(fill="x", pady=(0, 15))
        stock_entry = ttk.Entry(stock_frame, textvariable=self.stock_var, width=40)
        stock_entry.pack(side="left", fill="x", expand=True)
        KeyboardButton(stock_frame, stock_entry).pack(side="right", padx=(5, 0))
        
        # Description
        ttk.Label(form_frame, text=get_text("description"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.description_var = tk.StringVar()
        desc_entry = ttk.Entry(form_frame, textvariable=self.description_var, width=40)
        desc_entry.pack(fill="x", pady=(0, 15))
        
        # Status
        ttk.Label(form_frame, text=get_text("status_label"), font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.status_var = tk.BooleanVar(value=True)
        status_check = ttk.Checkbutton(form_frame, text=get_text("active_product"), variable=self.status_var)
        status_check.pack(anchor="w", pady=(0, 20))
        
        # Action buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        self.save_btn = ttk.Button(button_frame, text=get_text("save_product"), command=self.save_product)
        self.save_btn.pack(fill="x", pady=(0, 5))
        
        self.new_btn = ttk.Button(button_frame, text=get_text("new_product"), command=self.new_product)
        self.new_btn.pack(fill="x", pady=(0, 5))
        
        self.delete_btn = ttk.Button(button_frame, text=f"🗑️ {get_text('delete')}", command=self.delete_product)
        self.delete_btn.pack(fill="x")
        
    def create_footer(self, parent):
        """Create footer with close button."""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        # Right side buttons
        right_btn_frame = ttk.Frame(footer_frame)
        right_btn_frame.pack(side="right")
        
        # CSV Import button
        csv_import_btn = ttk.Button(right_btn_frame, text="📥 Importer CSV", command=self.show_csv_import)
        csv_import_btn.pack(side="left", padx=(0, 10))
        
        # CSV Export button
        csv_export_btn = ttk.Button(right_btn_frame, text="📤 Exporter CSV", command=self.export_products_csv)
        csv_export_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ttk.Button(right_btn_frame, text=get_text("close"), command=self.window.destroy)
        close_btn.pack(side="left")
        
        # Product count
        self.count_label = ttk.Label(footer_frame, text="", font=("Arial", 10))
        self.count_label.pack(side="left")
        
    def load_products(self):
        """Load all products from database."""
        try:
            all_products = self.db_manager.get_all_products_for_inventory()
            # Filter out inactive products by default
            self.products = [p for p in all_products if p.is_active]
            self.filtered_products = self.products.copy()
            
            # Update category filter
            categories = set([get_text("all_categories")])
            for product in self.products:
                if product.category:
                    categories.add(product.category)
            
            self.category_combo['values'] = sorted(list(categories))
            
            self.update_products_display()
            self.update_count_label()
            
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('error_loading_products')}: {e}")
            
    def update_products_display(self):
        """Update the products treeview display."""
        # Clear existing items
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        # Add filtered products
        for product in self.filtered_products:
            status = "Actif" if product.is_active else "Inactif"
            values = (
                product.id or "",
                product.name,
                product.category or "",
                product.supplier or "",
                f"{product.cost_price:.2f} DH",
                f"{product.price:.2f} DH",
                product.stock_quantity,
                status
            )
            
            item = self.products_tree.insert("", "end", values=values)
            
            # Color inactive products
            if not product.is_active:
                self.products_tree.item(item, tags=("inactive",))
                
        # Configure tags
        self.products_tree.tag_configure("inactive", foreground="gray")
        
    def filter_products(self, *args):
        """Filter products based on search and category."""
        search_text = self.search_var.get().lower()
        category = self.category_var.get()
        
        self.filtered_products = []
        
        for product in self.products:
            # Category filter
            if category != "Toutes" and product.category != category:
                continue
                
            # Search filter
            if search_text:
                searchable_text = f"{product.name} {product.description or ''} {product.supplier or ''} {product.barcode or ''}".lower()
                if search_text not in searchable_text:
                    continue
                    
            self.filtered_products.append(product)
            
        self.update_products_display()
        self.update_count_label()
        
    def update_count_label(self):
        """Update the product count label."""
        total = len(self.products)
        filtered = len(self.filtered_products)
        active = len([p for p in self.filtered_products if p.is_active])
        
        self.count_label.config(text=f"Affichage: {filtered}/{total} produits ({active} actifs)")
        
    def sort_products(self, column):
        """Sort products by column."""
        # This is a placeholder for sorting functionality
        pass
        
    def on_product_select(self, event):
        """Handle product selection."""
        selection = self.products_tree.selection()
        if not selection:
            return
            
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        
        # Find the product
        product = next((p for p in self.products if str(p.id) == str(product_id)), None)
        if product:
            self.load_product_to_form(product)
            
    def load_product_to_form(self, product):
        """Load product data to form fields."""
        self.id_var.set(str(product.id) if product.id else "")
        self.name_var.set(product.name)
        self.form_category_var.set(product.category or "")
        self.supplier_var.set(product.supplier or "")
        self.barcode_var.set(product.barcode or "")
        self.cost_price_var.set(str(product.cost_price))
        self.selling_price_var.set(str(product.price))
        self.stock_var.set(str(product.stock_quantity))
        self.description_var.set(product.description or "")
        self.status_var.set(product.is_active)
        
    def clear_form(self):
        """Clear all form fields."""
        self.id_var.set("")
        self.name_var.set("")
        self.form_category_var.set("")
        self.supplier_var.set("")
        self.barcode_var.set("")
        self.cost_price_var.set("0.0")
        self.selling_price_var.set("0.0")
        self.stock_var.set("0")
        self.description_var.set("")
        self.status_var.set(True)
        
    def new_product(self):
        """Prepare form for new product."""
        self.clear_form()
        self.products_tree.selection_remove(self.products_tree.selection())
        
    def save_product(self):
        """Save the current product."""
        try:
            # Validate required fields
            if not self.name_var.get().strip():
                messagebox.showerror(get_text("error"), get_text("product_name_required"))
                return
                
            # Create product object
            product = Product(
                id=int(self.id_var.get()) if self.id_var.get() else None,
                name=self.name_var.get().strip(),
                description=self.description_var.get().strip(),
                price=float(self.selling_price_var.get() or 0),
                barcode=self.barcode_var.get().strip() or None,
                category=self.form_category_var.get().strip() or None,
                stock_quantity=int(self.stock_var.get() or 0),
                is_active=self.status_var.get(),
                supplier=self.supplier_var.get().strip() or None,
                cost_price=float(self.cost_price_var.get() or 0)
            )
            
            # Save to database
            product_id = self.db_manager.save_product(product)
            product.id = product_id
            
            # Reload products
            self.load_products()
            
            # Select the saved product
            for item in self.products_tree.get_children():
                values = self.products_tree.item(item)['values']
                if str(values[0]) == str(product_id):
                    self.products_tree.selection_set(item)
                    self.products_tree.see(item)
                    break
                    
            messagebox.showinfo("Succès", "Produit sauvegardé avec succès!")
            
        except ValueError as e:
            messagebox.showerror(get_text("error"), f"{get_text('validation_error')}: {e}")
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('save_error')}: {e}")
            
    def delete_product(self):
        """Delete the selected product."""
        product_id = self.id_var.get()
        if not product_id:
            messagebox.showerror(get_text("error"), get_text("no_product_selected"))
            return
            
        product_name = self.name_var.get()
        if messagebox.askyesno("Confirmer", f"Êtes-vous sûr de vouloir supprimer le produit '{product_name}'?\n\nNote: Si ce produit a été vendu, il sera marqué comme inactif. Sinon, il sera supprimé définitivement."):
            try:
                success = self.db_manager.delete_product(int(product_id))
                if success:
                    # Remove from local lists
                    self.products = [p for p in self.products if str(p.id) != str(product_id)]
                    self.filter_products()  # This will update filtered_products and display
                    self.clear_form()
                    messagebox.showinfo("Succès", "Produit supprimé avec succès!")
                else:
                    messagebox.showerror(get_text("error"), get_text("cannot_delete_product"))
                
            except Exception as e:
                messagebox.showerror(get_text("error"), f"{get_text('delete_error')}: {e}")
    
    def show_csv_import(self):
        """Show CSV import dialog."""
        try:
            from dialogs.csv_import_dialog import show_csv_import_dialog
            show_csv_import_dialog(self.window, self.db_manager)
            # Refresh products after import
            self.load_products()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ouverture de l'import CSV: {str(e)}")
    
    def export_products_csv(self):
        """Export products to CSV file."""
        try:
            from tkinter import filedialog
            from utils.csv_import import CSVProductImporter
            
            # Ask user for file location
            file_path = filedialog.asksaveasfilename(
                title="Exporter les produits vers CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfilename=f"produits_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if file_path:
                importer = CSVProductImporter(self.db_manager)
                if importer.export_products_to_csv(file_path, include_inactive=False):
                    messagebox.showinfo("Succès", f"Produits exportés avec succès vers:\\n{file_path}")
                else:
                    messagebox.showerror("Erreur", "Erreur lors de l'exportation des produits")
                    
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'exportation: {str(e)}")


class CashDrawerOpeningDialog:
    """Dialog for opening cash drawer at session start."""
    
    def __init__(self, parent, session_manager):
        self.session_manager = session_manager
        self.result = None
        
        # Create dialog window
        self.window = tk.Toplevel(parent)
        self.window.title("Ouvrir la caisse")
        self.window.geometry("400x250")
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # Center on screen instead of parent to avoid issues
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 400) // 2
        y = (self.window.winfo_screenheight() - 250) // 2
        self.window.geometry(f"400x250+{x}+{y}")
        
        # Prevent closing without completing
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Ouvrir la caisse", 
                               font=("Arial", 16, "bold"),
                               foreground="#20B2AA")
        title_label.pack(pady=(0, 20))
        
        # Info
        info_label = ttk.Label(main_frame, 
                              text="Saisissez le montant de départ dans le tiroir-caisse",
                              font=("Arial", 10))
        info_label.pack(pady=(0, 15))
        
        # Amount input
        amount_frame = ttk.Frame(main_frame)
        amount_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(amount_frame, text="Montant (DH):", font=("Arial", 12)).pack(anchor="w")
        
        # Entry with keyboard icon
        entry_frame = ttk.Frame(amount_frame)
        entry_frame.pack(pady=(5, 0))
        
        self.amount_var = tk.StringVar(value="0")
        self.amount_entry = ttk.Entry(entry_frame, textvariable=self.amount_var,
                                     font=("Arial", 14), width=20)
        self.amount_entry.pack(side="left")
        
        # Add keyboard icon
        from utils.virtual_keyboard import KeyboardButton
        keyboard_btn = KeyboardButton(entry_frame, self.amount_entry)
        keyboard_btn.pack(side="left", padx=(5, 0))
        
        self.amount_entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = tk.Button(button_frame, text="OUVRIR",
                            command=self.save_and_close,
                            bg="#20B2AA", fg="white",
                            font=("Arial", 12, "bold"),
                            padx=20, pady=5)
        save_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, text="ANNULER",
                              command=self.on_closing,
                              bg="#ddd", fg="black",
                              font=("Arial", 12, "bold"),
                              padx=20, pady=5)
        cancel_btn.pack(side="right")
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self.save_and_close())
        
    def save_and_close(self):
        """Save cash drawer amount and close dialog."""
        try:
            amount = float(self.amount_var.get().replace(',', '.'))
            
            if amount < 0:
                messagebox.showerror(get_text("error"), get_text("amount_cannot_be_negative"))
                return
                
            # Start session
            session_info = self.session_manager.start_session(amount, "Ouverture de session")
            
            self.result = session_info
            self.window.destroy()
            
            # Show confirmation
            messagebox.showinfo("Session ouverte", 
                               f"Session ouverte avec succès!\n\n" +
                               f"Montant en caisse: {amount:.2f} DH")
            
        except ValueError:
            messagebox.showerror(get_text("error"), get_text("enter_valid_amount"))
            
    def on_closing(self):
        """Handle dialog closing."""
        if messagebox.askyesno("Fermer", 
                              "Êtes-vous sûr de vouloir fermer sans ouvrir la caisse?\n" +
                              "L'application se fermera."):
            self.result = None
            self.window.destroy()


class CashManagementDialog:
    """Dialog for managing cash in the drawer (add/remove cash)."""
    
    def __init__(self, parent, session_manager):
        self.session_manager = session_manager
        self.result = None
        
        # Get current cash amount
        current_session = self.session_manager.get_current_session()
        self.current_cash = current_session.get('cash_drawer_amount', 0) if current_session else 0
        
        # Create dialog window
        self.window = tk.Toplevel(parent)
        self.window.title(get_text("cash_management") + " - " + get_text("register"))
        self.window.geometry("500x550")
        self.window.grab_set()
        self.window.resizable(False, False)
        
        # Center on screen
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 500) // 2
        y = (self.window.winfo_screenheight() - 550) // 2
        self.window.geometry(f"500x550+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=get_text("cash_management"), 
                               font=("Arial", 16, "bold"),
                               foreground="#20B2AA")
        title_label.pack(pady=(0, 20))
        
        # Current cash display
        current_frame = ttk.LabelFrame(main_frame, text=get_text("current_cash_in_register"), padding="15")
        current_frame.pack(fill="x", pady=(0, 20))
        
        current_label = ttk.Label(current_frame, 
                                 text=f"{self.current_cash:.2f} DH",
                                 font=("Arial", 18, "bold"),
                                 foreground="#2E8B57")
        current_label.pack()
        
        # Operation selection
        operation_frame = ttk.LabelFrame(main_frame, text="Que voulez-vous faire ?", padding="15")
        operation_frame.pack(fill="x", pady=(0, 20))
        
        self.operation_var = tk.StringVar(value="add")
        
        # Create custom styled radio buttons
        add_frame = ttk.Frame(operation_frame)
        add_frame.pack(fill="x", pady=5)
        
        add_radio = ttk.Radiobutton(add_frame, text="➕ Ajouter de l'argent dans la caisse", 
                                   variable=self.operation_var, value="add",
                                   style="Large.TRadiobutton")
        add_radio.pack(anchor="w")
        
        remove_frame = ttk.Frame(operation_frame)
        remove_frame.pack(fill="x", pady=5)
        
        remove_radio = ttk.Radiobutton(remove_frame, text="➖ Retirer de l'argent de la caisse", 
                                      variable=self.operation_var, value="remove",
                                      style="Large.TRadiobutton")
        remove_radio.pack(anchor="w")
        
        # Amount input
        amount_frame = ttk.LabelFrame(main_frame, text="Sélectionner le Montant", padding="15")
        amount_frame.pack(fill="x", pady=(0, 20))
        
        # Amount input field with larger font
        input_section = ttk.Frame(amount_frame)
        input_section.pack(fill="x", pady=(0, 15))
        
        ttk.Label(input_section, text="Montant à ajouter/retirer (DH):", 
                 font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Entry with keyboard icon
        entry_frame = ttk.Frame(input_section)
        entry_frame.pack(pady=(8, 0))
        
        self.amount_var = tk.StringVar(value="")
        self.amount_entry = ttk.Entry(entry_frame, textvariable=self.amount_var,
                                     font=("Arial", 16), width=15, justify="center")
        self.amount_entry.pack(side="left")
        
        # Add keyboard icon
        from utils.virtual_keyboard import KeyboardButton
        keyboard_btn = KeyboardButton(entry_frame, self.amount_entry)
        keyboard_btn.pack(side="left", padx=(5, 0))
        
        self.amount_entry.focus()
        
        # Add placeholder text
        self.amount_entry.insert(0, "0.00")
        self.amount_entry.bind('<FocusIn>', self.on_entry_click)
        self.amount_entry.bind('<FocusOut>', self.on_entry_leave)
        
        # Quick amount buttons - organized in rows
        quick_frame = ttk.Frame(amount_frame)
        quick_frame.pack(fill="x", pady=(15, 0))
        
        ttk.Label(quick_frame, text="Montants rapides:", 
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 8))
        
        # First row of buttons
        button_frame1 = ttk.Frame(quick_frame)
        button_frame1.pack(fill="x", pady=(0, 5))
        
        quick_amounts1 = [10, 20, 50, 100, 200]
        for amount in quick_amounts1:
            btn = tk.Button(button_frame1, text=f"{amount} DH",
                           command=lambda a=amount: self.set_amount(a),
                           bg="#e8f4f8", fg="#20B2AA",
                           font=("Arial", 10, "bold"),
                           padx=12, pady=8)
            btn.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        # Second row of buttons
        button_frame2 = ttk.Frame(quick_frame)
        button_frame2.pack(fill="x", pady=(0, 5))
        
        quick_amounts2 = [500, 1000, 2000, 5000]
        for amount in quick_amounts2:
            btn = tk.Button(button_frame2, text=f"{amount} DH",
                           command=lambda a=amount: self.set_amount(a),
                           bg="#e8f4f8", fg="#20B2AA",
                           font=("Arial", 10, "bold"),
                           padx=12, pady=8)
            btn.pack(side="left", padx=(0, 5), fill="x", expand=True)
        
        # Clear button
        clear_frame = ttk.Frame(quick_frame)
        clear_frame.pack(fill="x", pady=(5, 0))
        
        clear_btn = tk.Button(clear_frame, text="EFFACER",
                             command=self.clear_amount,
                             bg="#dc3545", fg="white",
                             font=("Arial", 10, "bold"),
                             padx=20, pady=5)
        clear_btn.pack(side="right")
        
        # Reason input
        reason_frame = ttk.LabelFrame(main_frame, text="Motif de la Transaction", padding="15")
        reason_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(reason_frame, text="Décrivez la raison de cette transaction:", 
                 font=("Arial", 10)).pack(anchor="w", pady=(0, 5))
        
        self.reason_var = tk.StringVar(value="Transaction caisse")  # Default reason
        self.reason_entry = ttk.Entry(reason_frame, textvariable=self.reason_var,
                                font=("Arial", 12), width=40)
        self.reason_entry.pack(fill="x", pady=(0, 10))
        
        # Quick reason buttons
        quick_reasons_frame = ttk.Frame(reason_frame)
        quick_reasons_frame.pack(fill="x")
        
        ttk.Label(quick_reasons_frame, text="Motifs courants:", 
                 font=("Arial", 9)).pack(anchor="w", pady=(0, 5))
        
        # Reason buttons for adding money
        add_reasons_frame = ttk.Frame(quick_reasons_frame)
        add_reasons_frame.pack(fill="x", pady=(0, 3))
        
        add_reasons = ["Paiement client", "Dépôt initial", "Fonds de caisse"]
        for reason in add_reasons:
            btn = tk.Button(add_reasons_frame, text=reason,
                           command=lambda r=reason: self.set_reason(r),
                           bg="#d4edda", fg="#155724",
                           font=("Arial", 9, "bold"),
                           padx=10, pady=5,
                           relief="raised", bd=2)
            btn.pack(side="left", padx=(0, 5))
        
        # Reason buttons for removing money
        remove_reasons_frame = ttk.Frame(quick_reasons_frame)
        remove_reasons_frame.pack(fill="x")
        
        remove_reasons = ["Dépôt banque", "Monnaie rendue", "Correction caisse"]
        for reason in remove_reasons:
            btn = tk.Button(remove_reasons_frame, text=reason,
                           command=lambda r=reason: self.set_reason(r),
                           bg="#f8d7da", fg="#721c24",
                           font=("Arial", 9, "bold"),
                           padx=10, pady=5,
                           relief="raised", bd=2)
            btn.pack(side="left", padx=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = tk.Button(button_frame, text="ENREGISTRER",
                            command=self.save_transaction,
                            bg="#20B2AA", fg="white",
                            font=("Arial", 12, "bold"),
                            padx=20, pady=5)
        save_btn.pack(side="left", padx=(0, 10))
        
        history_btn = tk.Button(button_frame, text="HISTORIQUE",
                               command=self.show_history,
                               bg="#17a2b8", fg="white",
                               font=("Arial", 12, "bold"),
                               padx=20, pady=5)
        history_btn.pack(side="left", padx=(0, 10))
        
        cancel_btn = tk.Button(button_frame, text="ANNULER",
                              command=self.cancel,
                              bg="#ddd", fg="black",
                              font=("Arial", 12, "bold"),
                              padx=20, pady=5)
        cancel_btn.pack(side="right")
        
        # Bind Enter key
        self.window.bind('<Return>', lambda e: self.save_transaction())
        
    def set_amount(self, amount):
        """Set predefined amount."""
        self.amount_var.set(str(amount))
        
    def set_reason(self, reason):
        """Set predefined reason."""
        self.reason_var.set(reason)
        
    def clear_amount(self):
        """Clear the amount field."""
        self.amount_var.set("")
        self.amount_entry.focus()
        
    def on_entry_click(self, event):
        """Handle entry field click - clear placeholder."""
        if self.amount_var.get() == "0.00":
            self.amount_var.set("")
            
    def on_entry_leave(self, event):
        """Handle entry field leave - restore placeholder if empty."""
        if not self.amount_var.get().strip():
            self.amount_var.set("0.00")
        
    def show_history(self):
        """Show cash transaction history."""
        current_session = self.session_manager.get_current_session()
        transactions = current_session.get('cash_transactions', []) if current_session else []
        
        if not transactions:
            messagebox.showinfo("Historique", "Aucune transaction trouvée pour aujourd'hui.")
            return
        
        # Create history window
        history_window = tk.Toplevel(self.window)
        history_window.title("Historique des Transactions")
        history_window.geometry("600x400")
        history_window.grab_set()
        
        # Center on parent
        history_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 600) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 400) // 2
        history_window.geometry(f"600x400+{x}+{y}")
        
        main_frame = ttk.Frame(history_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Historique des Transactions", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 15))
        
        # Scrollable text area
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                             font=("Courier", 10), wrap="word")
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Add transaction history
        history_text = f"Montant initial: {current_session.get('cash_drawer_amount', 0):.2f} DH\n"
        history_text += "=" * 50 + "\n\n"
        
        for i, trans in enumerate(transactions, 1):
            time_str = trans['timestamp'][:19].replace('T', ' ')  # Format datetime
            history_text += f"{i}. {trans['type']}\n"
            history_text += f"   Montant: {trans['amount']:.2f} DH\n"
            history_text += f"   Nouveau solde: {trans['new_balance']:.2f} DH\n"
            history_text += f"   Motif: {trans['reason']}\n"
            history_text += f"   Heure: {time_str}\n"
            history_text += "-" * 30 + "\n\n"
        
        text_widget.insert("1.0", history_text)
        text_widget.config(state="disabled")  # Make read-only
        
        # Close button
        close_btn = ttk.Button(main_frame, text="Fermer",
                              command=history_window.destroy)
        close_btn.pack(pady=(15, 0))
        
    def save_transaction(self):
        """Save cash transaction."""
        try:
            amount_text = self.amount_var.get().strip()
            
            # Handle placeholder text
            if amount_text == "0.00" or not amount_text:
                messagebox.showerror(get_text("error"), get_text("select_amount"))
                return
                
            amount = float(amount_text.replace(',', '.'))
            operation = self.operation_var.get()
            reason = self.reason_var.get().strip()
            
            if amount <= 0:
                messagebox.showerror(get_text("error"), get_text("amount_must_be_positive"))
                return
                
            if not reason:
                messagebox.showerror("Erreur", "Veuillez saisir un motif pour cette transaction")
                return
            
            # Calculate new amount
            if operation == "add":
                new_amount = self.current_cash + amount
                operation_text = "Ajout"
            else:  # remove
                new_amount = self.current_cash - amount
                operation_text = "Retrait"
                
                if new_amount < 0:
                    if not messagebox.askyesno("Attention", 
                                             f"Cette opération va créer un solde négatif ({new_amount:.2f} DH).\n"
                                             "Êtes-vous sûr de vouloir continuer?"):
                        return
            
            # Update session cash amount
            self.session_manager.update_cash_amount(new_amount, operation_text, reason, amount)
            
            self.result = {
                'operation': operation,
                'amount': amount,
                'new_total': new_amount,
                'reason': reason
            }
            
            self.window.destroy()
            
            # Show confirmation
            messagebox.showinfo("Transaction enregistrée", 
                               f"{operation_text} de {amount:.2f} DH enregistré!\n\n" +
                               f"Nouveau solde: {new_amount:.2f} DH")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un montant valide")


class BarcodeScannerDialog:
    """Dialog for barcode scanning."""
    
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
        
        # Focus on entry and bind Enter key as backup
        self.barcode_entry.focus_set()
        self.window.bind('<Return>', lambda e: self.process_barcode())
        
    def create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text=get_text("scan_barcode"), 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Instructions
        instruction_label = ttk.Label(main_frame, text="Scannez ou tapez le code-barres:", 
                                     font=("Arial", 10))
        instruction_label.pack(anchor="w", pady=(0, 5))
        
        # Barcode entry
        self.barcode_var = tk.StringVar()
        self.barcode_entry = ttk.Entry(main_frame, textvariable=self.barcode_var,
                                      font=("Arial", 12), width=30)
        self.barcode_entry.pack(fill="x", pady=(0, 20))
        
        # Auto-scan when barcode is entered (bind to text change)
        self.barcode_var.trace('w', self.on_barcode_change)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="En attente du code-barres...", 
                                     font=("Arial", 9), foreground="#666")
        self.status_label.pack(pady=(0, 20))
        
        # Only Cancel button
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        cancel_btn = ttk.Button(button_frame, text=get_text("cancel"), 
                               command=self.window.destroy)
        cancel_btn.pack(side="right")
        
    def on_barcode_change(self, *args):
        """Handle barcode input change for auto-scanning."""
        barcode = self.barcode_var.get().strip()
        
        # Auto-process when barcode has sufficient length (typical barcode length)
        if len(barcode) >= 6:  # Minimum barcode length
            self.status_label.config(text="Code-barres détecté, traitement en cours...")
            # Add small delay to allow for complete barcode scan
            self.window.after(100, self.process_barcode)
    
    def process_barcode(self):
        """Process the barcode automatically."""
        barcode = self.barcode_var.get().strip()
        if barcode:
            self.callback(barcode)
            self.window.destroy()
    
    def scan_barcode(self):
        """Process the scanned barcode (kept for manual trigger)."""
        barcode = self.barcode_var.get().strip()
        if barcode:
            self.callback(barcode)
            self.window.destroy()
        else:
            messagebox.showwarning(get_text("warning"), get_text("enter_barcode"))
