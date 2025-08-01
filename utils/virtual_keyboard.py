"""
Virtual Keyboard Dialog
======================

A virtual on-screen keyboard for touchscreen interfaces.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
import string

class VirtualKeyboard:
    """Virtual on-screen keyboard for touchscreen devices."""
    
    def __init__(self, parent: tk.Widget, target_entry: tk.Entry, callback: Optional[Callable] = None):
        """Initialize virtual keyboard."""
        self.parent = parent
        self.target_entry = target_entry
        self.callback = callback
        self.window = None
        self.is_caps = False
        self.is_shift = False
        
    def show(self):
        """Show the virtual keyboard."""
        if self.window:
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title("Clavier Virtuel")
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
        
        # Position keyboard at bottom of screen
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Center horizontally, position at bottom
        x = (screen_width - 900) // 2
        y = screen_height - 350
        self.window.geometry(f"900x300+{x}+{y}")
        
        # Configure button style for larger touch-friendly buttons
        style = ttk.Style()
        style.configure("Keyboard.TButton", 
                       font=("Arial", 10, "bold"),
                       padding=(5, 8))
        
        self.create_keyboard()
        
        # Bind window close event
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
    def hide(self):
        """Hide the virtual keyboard."""
        if self.window:
            self.window.destroy()
            self.window = None
            
    def create_keyboard(self):
        """Create the keyboard layout."""
        main_frame = ttk.Frame(self.window, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Function row
        func_frame = ttk.Frame(main_frame)
        func_frame.pack(fill=tk.X, pady=2)
        
        func_keys = ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
        for key in func_keys:
            btn = ttk.Button(func_frame, text=key, width=5, style="Keyboard.TButton",
                           command=lambda k=key: self.key_press(k))
            btn.pack(side=tk.LEFT, padx=1)
        
        # Number row
        num_frame = ttk.Frame(main_frame)
        num_frame.pack(fill=tk.X, pady=2)
        
        num_keys = ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace']
        for key in num_keys:
            width = 10 if key == 'Backspace' else 5
            btn = ttk.Button(num_frame, text=key, width=width, style="Keyboard.TButton",
                           command=lambda k=key: self.key_press(k))
            btn.pack(side=tk.LEFT, padx=1)
        
        # Top letter row
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(top_frame, text='Tab', width=8, style="Keyboard.TButton",
                  command=lambda: self.key_press('Tab')).pack(side=tk.LEFT, padx=1)
        
        top_keys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\']
        for key in top_keys:
            btn = ttk.Button(top_frame, text=key.upper() if self.is_caps else key, width=5, style="Keyboard.TButton",
                           command=lambda k=key: self.key_press(k))
            btn.pack(side=tk.LEFT, padx=1)
        
        # Middle letter row
        mid_frame = ttk.Frame(main_frame)
        mid_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(mid_frame, text='Caps', width=8, style="Keyboard.TButton",
                  command=self.toggle_caps).pack(side=tk.LEFT, padx=1)
        
        mid_keys = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'"]
        for key in mid_keys:
            btn = ttk.Button(mid_frame, text=key.upper() if self.is_caps else key, width=5, style="Keyboard.TButton",
                           command=lambda k=key: self.key_press(k))
            btn.pack(side=tk.LEFT, padx=1)
            
        ttk.Button(mid_frame, text='Enter', width=10, style="Keyboard.TButton",
                  command=lambda: self.key_press('Return')).pack(side=tk.LEFT, padx=1)
        
        # Bottom letter row
        bot_frame = ttk.Frame(main_frame)
        bot_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(bot_frame, text='Shift', width=10, style="Keyboard.TButton",
                  command=self.toggle_shift).pack(side=tk.LEFT, padx=1)
        
        bot_keys = ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
        for key in bot_keys:
            btn = ttk.Button(bot_frame, text=key.upper() if self.is_caps else key, width=5, style="Keyboard.TButton",
                           command=lambda k=key: self.key_press(k))
            btn.pack(side=tk.LEFT, padx=1)
            
        ttk.Button(bot_frame, text='Shift', width=10, style="Keyboard.TButton",
                  command=self.toggle_shift).pack(side=tk.LEFT, padx=1)
        
        # Space row
        space_frame = ttk.Frame(main_frame)
        space_frame.pack(fill=tk.X, pady=2)
        
        ttk.Button(space_frame, text='Ctrl', width=8, style="Keyboard.TButton",
                  command=lambda: self.key_press('Control_L')).pack(side=tk.LEFT, padx=1)
        ttk.Button(space_frame, text='Alt', width=8, style="Keyboard.TButton",
                  command=lambda: self.key_press('Alt_L')).pack(side=tk.LEFT, padx=1)
        ttk.Button(space_frame, text='Space', width=35, style="Keyboard.TButton",
                  command=lambda: self.key_press(' ')).pack(side=tk.LEFT, padx=1)
        ttk.Button(space_frame, text='Alt', width=8, style="Keyboard.TButton",
                  command=lambda: self.key_press('Alt_R')).pack(side=tk.LEFT, padx=1)
        ttk.Button(space_frame, text='Ctrl', width=8, style="Keyboard.TButton",
                  command=lambda: self.key_press('Control_R')).pack(side=tk.LEFT, padx=1)
        
        # Close button
        close_frame = ttk.Frame(main_frame)
        close_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(close_frame, text='Fermer Clavier', style="Keyboard.TButton",
                  command=self.hide).pack(side=tk.RIGHT)
        ttk.Button(close_frame, text='Effacer Tout', style="Keyboard.TButton",
                  command=self.clear_all).pack(side=tk.RIGHT, padx=5)
        
    def key_press(self, key: str):
        """Handle key press."""
        if not self.target_entry:
            return
            
        current_pos = self.target_entry.index(tk.INSERT)
        
        if key == 'Backspace':
            if current_pos > 0:
                self.target_entry.delete(current_pos - 1)
        elif key == 'Delete':
            self.target_entry.delete(current_pos)
        elif key == 'Return':
            if self.callback:
                self.callback()
        elif key == 'Tab':
            # Move to next widget
            self.target_entry.tk_focusNext().focus()
        elif key in ['Shift', 'Ctrl', 'Alt', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            # Modifier keys - do nothing for now
            pass
        elif key in ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
            # Function keys - do nothing for now
            pass
        else:
            # Regular character
            char = key
            if self.is_caps and char.isalpha():
                char = char.upper()
            elif self.is_shift:
                # Handle shift combinations
                shift_map = {
                    '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
                    '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
                    '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
                    ';': ':', "'": '"', ',': '<', '.': '>', '/': '?',
                    '`': '~'
                }
                char = shift_map.get(char, char.upper() if char.isalpha() else char)
                self.is_shift = False  # Reset shift after use
                
            self.target_entry.insert(current_pos, char)
            
        # Update button labels if caps/shift changed
        if key in ['Caps', 'Shift']:
            self.update_button_labels()
            
    def toggle_caps(self):
        """Toggle caps lock."""
        self.is_caps = not self.is_caps
        self.update_button_labels()
        
    def toggle_shift(self):
        """Toggle shift."""
        self.is_shift = not self.is_shift
        self.update_button_labels()
        
    def clear_all(self):
        """Clear all text from target entry."""
        if self.target_entry:
            self.target_entry.delete(0, tk.END)
            
    def update_button_labels(self):
        """Update button labels based on caps/shift state."""
        # This would require keeping references to all buttons
        # For now, we'll recreate the keyboard when caps/shift changes
        if self.window:
            for widget in self.window.winfo_children():
                widget.destroy()
            self.create_keyboard()


class KeyboardButton(ttk.Frame):
    """A keyboard icon button that opens virtual keyboard."""
    
    def __init__(self, parent, target_entry: tk.Entry, **kwargs):
        super().__init__(parent, **kwargs)
        self.target_entry = target_entry
        self.keyboard = None
        
        # Create keyboard icon button - using a more visible icon
        self.button = ttk.Button(self, text="🔤", width=3, 
                                command=self.show_keyboard)
        self.button.pack()
        
        # Add tooltip
        self.create_tooltip()
        
    def show_keyboard(self):
        """Show virtual keyboard for target entry."""
        if self.keyboard:
            self.keyboard.hide()
            
        self.keyboard = VirtualKeyboard(self.winfo_toplevel(), self.target_entry)
        self.keyboard.show()
        
        # Focus the target entry
        self.target_entry.focus_set()
        
    def create_tooltip(self):
        """Create tooltip for keyboard button."""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text="Clavier virtuel", 
                           background="yellow", relief="solid", borderwidth=1,
                           font=("Arial", 8))
            label.pack()
            
            # Hide tooltip after 2 seconds
            self.after(2000, tooltip.destroy)
        
        def hide_tooltip(event):
            # Tooltip auto-hides
            pass
            
        self.button.bind("<Enter>", show_tooltip)
        self.button.bind("<Leave>", hide_tooltip)


def add_keyboard_to_entry(parent: tk.Widget, entry: tk.Entry) -> KeyboardButton:
    """Helper function to add keyboard button next to an entry widget."""
    keyboard_btn = KeyboardButton(parent, entry)
    return keyboard_btn
