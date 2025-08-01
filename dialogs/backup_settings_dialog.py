"""
Backup Settings Dialog
======================

This module provides a dialog for configuring backup settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import os
from pathlib import Path
from typing import Dict, Optional
from utils.backup_manager import BackupManager
from config.language_settings import get_text

class BackupSettingsDialog:
    """Dialog for backup settings configuration."""
    
    def __init__(self, parent, backup_manager: BackupManager):
        """Initialize backup settings dialog."""
        self.parent = parent
        self.backup_manager = backup_manager
        self.result = None
        self.dialog = None
        
        # Current settings
        self.settings = backup_manager.backup_settings.copy()
    
    def show(self) -> Optional[Dict]:
        """Show backup settings dialog."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(get_text("backup_settings"))
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()
        self.load_current_settings()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def create_widgets(self):
        """Create dialog widgets."""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 20))
        
        # General tab
        self.create_general_tab(notebook)
        
        # Backup management tab
        self.create_management_tab(notebook)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        # Buttons
        ttk.Button(button_frame, text=get_text("save"), 
                  command=self.save_settings).pack(side="right", padx=(10, 0))
        ttk.Button(button_frame, text=get_text("cancel"), 
                  command=self.cancel).pack(side="right")
    
    def create_general_tab(self, notebook):
        """Create general settings tab."""
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text=get_text("backup_settings"))
        
        # Auto backup section
        auto_frame = ttk.LabelFrame(general_frame, text=get_text("auto_backup"), padding="10")
        auto_frame.pack(fill="x", pady=(0, 10))
        
        # Auto backup enabled
        self.auto_backup_var = tk.BooleanVar()
        ttk.Checkbutton(auto_frame, text=get_text("auto_backup"), 
                       variable=self.auto_backup_var,
                       command=self.toggle_auto_backup).pack(anchor="w")
        
        # Frequency frame
        freq_frame = ttk.Frame(auto_frame)
        freq_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(freq_frame, text=get_text("backup_frequency") + ":").pack(side="left")
        self.frequency_var = tk.StringVar()
        frequency_combo = ttk.Combobox(freq_frame, textvariable=self.frequency_var,
                                     values=[get_text("daily"), get_text("weekly"), get_text("monthly")],
                                     state="readonly", width=15)
        frequency_combo.pack(side="left", padx=(10, 0))
        
        # Time frame
        time_frame = ttk.Frame(auto_frame)
        time_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Label(time_frame, text=get_text("backup_time") + ":").pack(side="left")
        
        # Time input frame
        time_input_frame = ttk.Frame(time_frame)
        time_input_frame.pack(side="left", padx=(10, 0))
        
        self.time_var = tk.StringVar()
        time_entry = ttk.Entry(time_input_frame, textvariable=self.time_var, width=8)
        time_entry.pack(side="left")
        
        # AM/PM selection
        self.ampm_var = tk.StringVar(value="AM")
        ampm_combo = ttk.Combobox(time_input_frame, textvariable=self.ampm_var,
                                 values=["AM", "PM"], state="readonly", width=4)
        ampm_combo.pack(side="left", padx=(5, 0))
        
        ttk.Label(time_frame, text="(HH:MM AM/PM)", foreground="gray").pack(side="left", padx=(5, 0))
        
        # Test backup button
        test_frame = ttk.Frame(auto_frame)
        test_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(test_frame, text="Test Backup Now", 
                  command=self.test_backup).pack(side="left")
        ttk.Button(test_frame, text="Show Status", 
                  command=self.check_scheduler_status).pack(side="left", padx=(10, 0))
        
        # Storage settings section
        storage_frame = ttk.LabelFrame(general_frame, text="Storage Settings", padding="10")
        storage_frame.pack(fill="x", pady=(0, 10))
        
        # Max backups
        max_frame = ttk.Frame(storage_frame)
        max_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(max_frame, text=get_text("max_backups") + ":").pack(side="left")
        self.max_backups_var = tk.StringVar()
        max_entry = ttk.Entry(max_frame, textvariable=self.max_backups_var, width=10)
        max_entry.pack(side="left", padx=(10, 0))
        
        # Compression
        self.compression_var = tk.BooleanVar()
        ttk.Checkbutton(storage_frame, text=get_text("backup_compression"), 
                       variable=self.compression_var).pack(anchor="w", pady=(0, 5))
        
        # Include images
        self.include_images_var = tk.BooleanVar()
        ttk.Checkbutton(storage_frame, text=get_text("include_images"), 
                       variable=self.include_images_var).pack(anchor="w")
        
        # Test buttons frame
        test_frame = ttk.LabelFrame(general_frame, text="Testing", padding="10")
        test_frame.pack(fill="x", pady=(10, 0))
        
        # Test buttons
        test_button_frame = ttk.Frame(test_frame)
        test_button_frame.pack(fill="x")
        
        ttk.Button(test_button_frame, text=get_text("test_backup"), 
                  command=self.test_backup).pack(side="left", padx=(0, 10))
        
        ttk.Button(test_button_frame, text=get_text("check_scheduler"), 
                  command=self.check_scheduler_status).pack(side="left")
    
    def test_backup(self):
        """Create a test backup to verify functionality."""
        try:
            messagebox.showinfo(get_text("info"), "Creating test backup...")
            
            # Create backup with test prefix
            test_file = self.backup_manager.create_backup(custom_name="TEST")
            
            if test_file and Path(test_file).exists():
                messagebox.showinfo(get_text("success"), 
                                  f"Test backup created successfully!\nFile: {Path(test_file).name}")
            else:
                messagebox.showerror(get_text("error"), "Failed to create test backup")
                
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Test backup failed: {e}")
    
    def check_scheduler_status(self):
        """Check if scheduler is running and show next scheduled backup."""
        try:
            if hasattr(self.backup_manager, 'scheduler_thread') and \
               self.backup_manager.scheduler_thread and \
               self.backup_manager.scheduler_thread.is_alive():
                
                # Get next run time if available
                import schedule
                jobs = schedule.jobs
                next_run = "Unknown"
                if jobs:
                    next_run = str(jobs[0].next_run) if jobs[0].next_run else "Not scheduled"
                
                messagebox.showinfo(get_text("info"), 
                                  f"Scheduler Status: Running\nNext backup: {next_run}")
            else:
                messagebox.showinfo(get_text("info"), 
                                  "Scheduler Status: Not running\nEnable auto backup to start scheduler")
                
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Error checking scheduler: {e}")
    
    def create_management_tab(self, notebook):
        """Create backup management tab."""
        management_frame = ttk.Frame(notebook, padding="10")
        notebook.add(management_frame, text="Backup Management")
        
        # Actions frame
        actions_frame = ttk.LabelFrame(management_frame, text="Actions", padding="10")
        actions_frame.pack(fill="x", pady=(0, 10))
        
        # Action buttons
        actions_button_frame = ttk.Frame(actions_frame)
        actions_button_frame.pack(fill="x")
        
        ttk.Button(actions_button_frame, text=get_text("create_backup"), 
                  command=self.create_manual_backup).pack(side="left", padx=(0, 10))
        ttk.Button(actions_button_frame, text=get_text("import_backup"), 
                  command=self.import_backup).pack(side="left", padx=(0, 10))
        ttk.Button(actions_button_frame, text=get_text("export_data"), 
                  command=self.export_data).pack(side="left")
        
        # Backup list frame
        list_frame = ttk.LabelFrame(management_frame, text=get_text("backup_list"), padding="10")
        list_frame.pack(fill="both", expand=True)
        
        # Treeview for backup list
        columns = ("name", "date", "size", "type")
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        self.backup_tree.heading("name", text="Name")
        self.backup_tree.heading("date", text=get_text("backup_date"))
        self.backup_tree.heading("size", text=get_text("backup_size"))
        self.backup_tree.heading("type", text=get_text("backup_type"))
        
        self.backup_tree.column("name", width=200)
        self.backup_tree.column("date", width=150)
        self.backup_tree.column("size", width=100)
        self.backup_tree.column("type", width=100)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.backup_tree.yview)
        self.backup_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.backup_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Backup list buttons
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(list_buttons_frame, text=get_text("refresh"), 
                  command=self.refresh_backup_list).pack(side="left", padx=(0, 10))
        ttk.Button(list_buttons_frame, text=get_text("restore_backup"), 
                  command=self.restore_selected_backup).pack(side="left", padx=(0, 10))
        ttk.Button(list_buttons_frame, text=get_text("delete"), 
                  command=self.delete_selected_backup).pack(side="left")
        
        # Load backup list
        self.refresh_backup_list()
    
    def toggle_auto_backup(self):
        """Toggle auto backup controls."""
        # This method can be used to enable/disable controls based on auto backup setting
        pass
    
    def load_current_settings(self):
        """Load current settings into dialog."""
        self.auto_backup_var.set(self.settings.get("auto_backup_enabled", False))
        
        # Map frequency
        frequency_map = {"daily": get_text("daily"), "weekly": get_text("weekly"), "monthly": get_text("monthly")}
        frequency = self.settings.get("backup_frequency", "daily")
        self.frequency_var.set(frequency_map.get(frequency, get_text("daily")))
        
        # Handle time format (convert from 24-hour to 12-hour AM/PM)
        time_24h = self.settings.get("backup_time", "02:00")
        time_12h, ampm = BackupSettingsDialog.convert_24h_to_12h(time_24h)
        self.time_var.set(time_12h)
        self.ampm_var.set(ampm)
        
        self.max_backups_var.set(str(self.settings.get("max_backups", 30)))
        self.compression_var.set(self.settings.get("compression", True))
        self.include_images_var.set(self.settings.get("include_images", False))
    
    @staticmethod
    def convert_24h_to_12h(time_24h: str) -> tuple:
        """Convert 24-hour time to 12-hour AM/PM format."""
        try:
            dt = datetime.strptime(time_24h, "%H:%M")
            time_12h = dt.strftime("%I:%M").lstrip('0')  # Remove leading zero
            ampm = dt.strftime("%p")
            return time_12h, ampm
        except:
            return "2:00", "AM"
    
    @staticmethod
    def convert_12h_to_24h(time_12h: str, ampm: str) -> str:
        """Convert 12-hour AM/PM time to 24-hour format."""
        try:
            dt = datetime.strptime(f"{time_12h} {ampm}", "%I:%M %p")
            return dt.strftime("%H:%M")
        except:
            return "02:00"
    
    def save_settings(self):
        """Save settings and close dialog."""
        try:
            # Validate time format and convert to 24-hour
            time_12h = self.time_var.get()
            ampm = self.ampm_var.get()
            
            if not self.validate_12h_time_format(time_12h):
                messagebox.showerror(get_text("error"), "Invalid time format. Use H:MM or HH:MM")
                return
            
            # Convert to 24-hour format for storage
            time_24h = BackupSettingsDialog.convert_12h_to_24h(time_12h, ampm)
            
            # Validate max backups
            try:
                max_backups = int(self.max_backups_var.get())
                if max_backups < 1:
                    raise ValueError()
            except ValueError:
                messagebox.showerror(get_text("error"), "Max backups must be a positive number")
                return
            
            # Map frequency back
            frequency_map = {get_text("daily"): "daily", get_text("weekly"): "weekly", get_text("monthly"): "monthly"}
            frequency = frequency_map.get(self.frequency_var.get(), "daily")
            
            # Update settings
            new_settings = {
                "auto_backup_enabled": self.auto_backup_var.get(),
                "backup_frequency": frequency,
                "backup_time": time_24h,  # Store in 24-hour format
                "max_backups": max_backups,
                "compression": self.compression_var.get(),
                "include_images": self.include_images_var.get()
            }
            
            # Save settings
            self.backup_manager.save_backup_settings(new_settings)
            
            self.result = new_settings
            messagebox.showinfo(get_text("success"), 
                              f"Backup settings saved successfully!\nNext backup: {frequency} at {time_12h} {ampm}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Error saving settings: {e}")
    
    def validate_12h_time_format(self, time_str: str) -> bool:
        """Validate 12-hour time format H:MM or HH:MM."""
        try:
            # Try both H:MM and HH:MM formats
            try:
                datetime.strptime(time_str, "%H:%M")
                return True
            except ValueError:
                datetime.strptime(time_str, "%I:%M")
                return True
        except ValueError:
            return False
    
    def validate_time_format(self, time_str: str) -> bool:
        """Validate time format HH:MM."""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False
    
    def cancel(self):
        """Cancel dialog."""
        self.dialog.destroy()
    
    def create_manual_backup(self):
        """Create a manual backup."""
        try:
            # Ask for backup name
            name = simpledialog.askstring(
                get_text("custom_backup"), 
                get_text("backup_name") + ":",
                parent=self.dialog
            )
            
            if name:
                backup_path = self.backup_manager.create_backup(name)
                messagebox.showinfo(
                    get_text("success"), 
                    f"{get_text('backup_created')}\n\n{backup_path}"
                )
                self.refresh_backup_list()
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('backup_failed')}: {e}")
    
    def import_backup(self):
        """Import backup from file."""
        file_path = filedialog.askopenfilename(
            parent=self.dialog,
            title=get_text("import_backup"),
            filetypes=[("Backup files", "*.zip *.db"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Copy to backup directory
                backup_dir = Path("backups")
                backup_dir.mkdir(exist_ok=True)
                
                import shutil
                filename = Path(file_path).name
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"imported_{timestamp}_{filename}"
                new_path = backup_dir / new_name
                
                shutil.copy2(file_path, new_path)
                
                messagebox.showinfo(
                    get_text("success"), 
                    f"Backup imported successfully\n\n{new_path}"
                )
                self.refresh_backup_list()
                
            except Exception as e:
                messagebox.showerror(get_text("error"), f"Import failed: {e}")
    
    def export_data(self):
        """Export data to various formats."""
        # Ask for format
        format_choice = messagebox.askyesno(
            get_text("export_data"),
            "Export as JSON? (Yes = JSON, No = CSV)"
        )
        
        format_type = "json" if format_choice else "csv"
        extension = "json" if format_choice else "csv"
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            parent=self.dialog,
            title=get_text("export_data"),
            defaultextension=f".{extension}",
            filetypes=[(f"{extension.upper()} files", f"*.{extension}"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.backup_manager.export_data(file_path, format_type)
                messagebox.showinfo(
                    get_text("success"), 
                    f"Data exported successfully\n\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror(get_text("error"), f"Export failed: {e}")
    
    def refresh_backup_list(self):
        """Refresh backup list."""
        # Clear existing items
        for item in self.backup_tree.get_children():
            self.backup_tree.delete(item)
        
        # Load backups
        backups = self.backup_manager.get_backup_list()
        
        for backup in backups:
            # Format size
            size_mb = backup["size"] / (1024 * 1024)
            size_str = f"{size_mb:.1f} MB"
            
            # Format date
            date_str = backup["created"].strftime("%Y-%m-%d %H:%M")
            
            self.backup_tree.insert("", "end", values=(
                backup["filename"],
                date_str,
                size_str,
                backup["type"]
            ))
    
    def restore_selected_backup(self):
        """Restore selected backup."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning(get_text("warning"), "Please select a backup to restore")
            return
        
        # Confirm restore
        if not messagebox.askyesno(
            get_text("confirm_restore"),
            get_text("restore_warning")
        ):
            return
        
        try:
            # Get selected backup path
            item = self.backup_tree.item(selection[0])
            filename = item["values"][0]
            backup_path = Path("backups") / filename
            
            # Restore backup
            self.backup_manager.restore_backup(str(backup_path))
            
            messagebox.showinfo(
                get_text("success"), 
                get_text("backup_restored")
            )
            
        except Exception as e:
            messagebox.showerror(get_text("error"), f"{get_text('restore_failed')}: {e}")
    
    def delete_selected_backup(self):
        """Delete selected backup."""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning(get_text("warning"), "Please select a backup to delete")
            return
        
        # Confirm delete
        if not messagebox.askyesno(
            get_text("confirm_delete"),
            "Are you sure you want to delete this backup?"
        ):
            return
        
        try:
            # Get selected backup path
            item = self.backup_tree.item(selection[0])
            filename = item["values"][0]
            backup_path = Path("backups") / filename
            
            # Delete backup file
            if backup_path.exists():
                backup_path.unlink()
                messagebox.showinfo(get_text("success"), "Backup deleted successfully")
                self.refresh_backup_list()
            
        except Exception as e:
            messagebox.showerror(get_text("error"), f"Delete failed: {e}")
