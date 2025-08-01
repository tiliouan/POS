#!/usr/bin/env python3
"""
Simple test to check if tkinter windows work
"""

import tkinter as tk
from tkinter import messagebox

def test_tkinter():
    """Test basic tkinter functionality."""
    print("Creating tkinter window...")
    
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("300x200")
    
    # Add a simple button
    button = tk.Button(root, text="Test Button", 
                      command=lambda: messagebox.showinfo("Test", "Button works!"))
    button.pack(pady=50)
    
    print("Window created, starting mainloop...")
    root.mainloop()
    print("Window closed.")

if __name__ == "__main__":
    test_tkinter()
