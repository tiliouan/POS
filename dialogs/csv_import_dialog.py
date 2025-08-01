"""
CSV Import Dialog
=================

This module provides a GUI for importing products from CSV files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import List, Dict
from utils.csv_import import CSVProductImporter
from database.db_manager import DatabaseManager
from config.language_settings import get_text
from utils.virtual_keyboard import KeyboardButton

class CSVImportDialog:
    """Dialog for importing products from CSV files."""
    
    def __init__(self, parent, db_manager: DatabaseManager):
        """Initialize the CSV import dialog."""
        self.parent = parent
        self.db_manager = db_manager
        self.importer = CSVProductImporter(db_manager)
        self.csv_file_path = None
        self.preview_data = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Importer des Produits CSV")
        self.dialog.geometry("900x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"900x700+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Importer des Produits depuis un fichier CSV", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection
        file_frame = ttk.LabelFrame(main_frame, text="Sélection du Fichier", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        self.file_path_var = tk.StringVar()
        ttk.Label(file_frame, text="Fichier CSV:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Add keyboard button for file path
        keyboard_btn = KeyboardButton(file_frame, file_entry, width=2)
        keyboard_btn.grid(row=0, column=2, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Parcourir...", command=self.browse_file)
        browse_btn.grid(row=0, column=3)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options d'Importation", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.update_existing_var = tk.BooleanVar(value=False)
        update_check = ttk.Checkbutton(options_frame, text="Mettre à jour les produits existants", 
                                     variable=self.update_existing_var)
        update_check.grid(row=0, column=0, sticky=tk.W)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(main_frame, text="Aperçu des Données", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        # Preview buttons
        preview_btn_frame = ttk.Frame(preview_frame)
        preview_btn_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        preview_btn = ttk.Button(preview_btn_frame, text="Aperçu", command=self.preview_import)
        preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.preview_info_label = ttk.Label(preview_btn_frame, text="")
        self.preview_info_label.pack(side=tk.LEFT)
        
        # Preview table
        self.setup_preview_table(preview_frame)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Importer", command=self.import_products).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Exporter Template", command=self.export_template).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Annuler", command=self.dialog.destroy).pack(side=tk.RIGHT)
    
    def setup_preview_table(self, parent):
        """Setup the preview table."""
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('row', 'name', 'price', 'barcode', 'category', 'stock', 'errors')
        self.preview_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.preview_tree.heading('row', text='Ligne')
        self.preview_tree.heading('name', text='Nom')
        self.preview_tree.heading('price', text='Prix')
        self.preview_tree.heading('barcode', text='Code Barre')
        self.preview_tree.heading('category', text='Catégorie')
        self.preview_tree.heading('stock', text='Stock')
        self.preview_tree.heading('errors', text='Erreurs')
        
        self.preview_tree.column('row', width=50, anchor=tk.CENTER)
        self.preview_tree.column('name', width=200)
        self.preview_tree.column('price', width=80, anchor=tk.E)
        self.preview_tree.column('barcode', width=150)
        self.preview_tree.column('category', width=100)
        self.preview_tree.column('stock', width=60, anchor=tk.CENTER)
        self.preview_tree.column('errors', width=200)
        
        self.preview_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.preview_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.preview_tree.configure(xscrollcommand=h_scrollbar.set)
    
    def browse_file(self):
        """Browse for CSV file."""
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.csv_file_path = file_path
    
    def preview_import(self):
        """Preview the CSV import."""
        if not self.file_path_var.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier CSV")
            return
        
        if not os.path.exists(self.file_path_var.get()):
            messagebox.showerror("Erreur", "Le fichier sélectionné n'existe pas")
            return
        
        try:
            # Clear previous preview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
            
            # Get preview data
            preview_data, errors, format_detected = self.importer.preview_csv_import(self.file_path_var.get(), max_preview=50)
            
            if errors:
                error_msg = "\\n".join(errors[:5])  # Show first 5 errors
                if len(errors) > 5:
                    error_msg += f"\\n... et {len(errors) - 5} autres erreurs"
                messagebox.showerror("Erreurs de Preview", error_msg)
                return
            
            self.preview_data = preview_data
            
            # Update info label
            valid_count = len([p for p in preview_data if 'errors' not in p])
            invalid_count = len([p for p in preview_data if 'errors' in p])
            
            info_text = f"Format détecté: {format_detected.upper()} | "
            info_text += f"Valides: {valid_count} | Invalides: {invalid_count}"
            self.preview_info_label.config(text=info_text)
            
            # Populate preview table
            for product in preview_data:
                # Show original barcode if available, otherwise cleaned barcode
                barcode_display = product.get('barcode', '')
                original_barcode = product.get('original_barcode', '')
                
                # Show barcode status
                if barcode_display and barcode_display.strip():
                    barcode_display = f"✓ {barcode_display}"
                elif original_barcode and not barcode_display:
                    barcode_display = f"❌ {original_barcode[:20]}" + ("..." if len(original_barcode) > 20 else "")
                else:
                    barcode_display = ""
                
                row_values = (
                    product.get('row_number', ''),
                    product.get('name', ''),
                    f"{product.get('price', 0):.2f} DH",
                    barcode_display,
                    product.get('category', ''),
                    product.get('stock_quantity', 0),
                    ', '.join(product.get('errors', []))
                )
                
                # Color code based on errors
                item = self.preview_tree.insert('', tk.END, values=row_values)
                if 'errors' in product:
                    self.preview_tree.set(item, 'errors', ', '.join(product['errors']))
        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'aperçu: {str(e)}")
    
    def import_products(self):
        """Import products from CSV."""
        if not self.file_path_var.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier CSV")
            return
        
        if not self.preview_data:
            messagebox.showerror("Erreur", "Veuillez d'abord prévisualiser les données")
            return
        
        # Confirm import
        valid_count = len([p for p in self.preview_data if 'errors' not in p])
        if valid_count == 0:
            messagebox.showerror("Erreur", "Aucun produit valide à importer")
            return
        
        confirm_msg = f"Voulez-vous importer {valid_count} produits?"
        if self.update_existing_var.get():
            confirm_msg += "\\nLes produits existants seront mis à jour."
        
        if not messagebox.askyesno("Confirmer l'Importation", confirm_msg):
            return
        
        try:
            # Show progress
            progress_dialog = self.show_progress_dialog()
            
            # Perform import
            imported_count, updated_count, errors = self.importer.import_csv_products(
                self.file_path_var.get(), 
                update_existing=self.update_existing_var.get()
            )
            
            # Close progress dialog
            progress_dialog.destroy()
            
            # Show results
            result_msg = f"Importation terminée!\\n"
            result_msg += f"Produits importés: {imported_count}\\n"
            result_msg += f"Produits mis à jour: {updated_count}"
            
            if errors:
                result_msg += f"\\nErreurs: {len(errors)}"
                error_details = "\\n".join(errors[:10])  # Show first 10 errors
                if len(errors) > 10:
                    error_details += f"\\n... et {len(errors) - 10} autres erreurs"
                result_msg += f"\\n\\nDétails des erreurs:\\n{error_details}"
            
            if errors:
                messagebox.showwarning("Importation Terminée avec Erreurs", result_msg)
            else:
                messagebox.showinfo("Importation Réussie", result_msg)
            
            # Close dialog if successful
            if imported_count > 0 or updated_count > 0:
                self.dialog.destroy()
        
        except Exception as e:
            messagebox.showerror("Erreur d'Importation", f"Erreur lors de l'importation: {str(e)}")
    
    def show_progress_dialog(self):
        """Show progress dialog during import."""
        progress_dialog = tk.Toplevel(self.dialog)
        progress_dialog.title("Importation en cours...")
        progress_dialog.geometry("300x100")
        progress_dialog.transient(self.dialog)
        progress_dialog.grab_set()
        
        # Center the dialog
        progress_dialog.update_idletasks()
        x = (progress_dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (progress_dialog.winfo_screenheight() // 2) - (100 // 2)
        progress_dialog.geometry(f"300x100+{x}+{y}")
        
        ttk.Label(progress_dialog, text="Importation des produits en cours...", 
                 font=('Arial', 12)).pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_dialog, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        progress_bar.start(10)
        
        progress_dialog.update()
        return progress_dialog
    
    def export_template(self):
        """Export a CSV template."""
        file_path = filedialog.asksaveasfilename(
            title="Sauvegarder le modèle CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                import csv
                
                with open(file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    
                    # Write headers
                    headers = [
                        'Name', 'Description', 'Price', 'Barcode', 
                        'Category', 'Stock', 'Cost Price'
                    ]
                    writer.writerow(headers)
                    
                    # Write sample data
                    sample_rows = [
                        ['Produit Exemple 1', 'Description du produit 1', '25.50', '1234567890123', 'Catégorie A', '100', '15.00'],
                        ['Produit Exemple 2', 'Description du produit 2', '18.75', '9876543210987', 'Catégorie B', '50', '12.00'],
                        ['Produit Exemple 3', 'Description du produit 3', '45.00', '5555666677778', 'Catégorie A', '25', '30.00']
                    ]
                    
                    for row in sample_rows:
                        writer.writerow(row)
                
                messagebox.showinfo("Succès", f"Modèle CSV sauvegardé: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")

def show_csv_import_dialog(parent, db_manager: DatabaseManager):
    """Show the CSV import dialog."""
    dialog = CSVImportDialog(parent, db_manager)
    return dialog
