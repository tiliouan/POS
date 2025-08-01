"""
Language Settings
================

This module manages language settings for the POS system.
Supports French (FR), Arabic (AR), and English (EN).
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class LanguageSettings:
    """Language settings for the POS system."""
    
    # Current language
    current_language: str = "FR"  # FR, AR, EN
    
    # RTL support for Arabic
    rtl_mode: bool = False
    
    # Font settings for different languages
    font_family: str = "Arial"
    font_size: int = 10
    arabic_font_family: str = "Arial Unicode MS"
    
    def is_arabic(self) -> bool:
        """Check if current language is Arabic."""
        return self.current_language == "AR"
    
    def is_rtl(self) -> bool:
        """Check if RTL mode should be enabled."""
        return self.is_arabic() and self.rtl_mode
    
    def get_font_family(self) -> str:
        """Get appropriate font family for current language."""
        if self.is_arabic():
            return self.arabic_font_family
        return self.font_family

class LanguageManager:
    """Manages language settings and translations."""
    
    def __init__(self, settings_file: str = "config/language_settings.json"):
        self.settings_file = settings_file
        self.settings = LanguageSettings()
        self.translations = self._load_translations()
        self.load_settings()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load translation dictionaries."""
        return {
            "FR": {
                # Main UI
                "app_title": "Système de Point de Vente - RIMAL",
                "cash_register": "Caisse",
                "products": "Produits",
                "cart": "Panier",
                "total": "Total",
                "payment": "Paiement",
                "receipt": "Reçu",
                "settings": "Paramètres",
                
                # Sidebar Navigation
                "register_screen": "ÉCRAN DU REGISTRE",
                "order_history": "HISTORIQUE DES COMMANDES",
                "daily_profit": "RAPORT",
                "manage_cash": "GÉRER L'ESPÈCE",
                "receipt_settings": "PARAMÈTRES REÇU",
                "language_settings_menu": "PARAMÈTRES LANGUE",
                "backup_settings": "SAUVEGARDE",
                "close_register": "FERMER LE REGISTRE",
                
                # Product Management
                "product_name": "Nom du produit",
                "product_price": "Prix",
                "product_category": "Catégorie",
                "product_barcode": "Code-barres",
                "add_product": "Ajouter produit",
                "edit_product": "Modifier produit",
                "delete_product": "Supprimer produit",
                "search_products": "Rechercher produits",
                
                # Cart Operations
                "item_quantity": "Quantité",
                "item_price": "Prix unitaire",
                "item_total": "Total",
                "remove_item": "Supprimer",
                "cart_empty": "Panier vide",
                "subtotal": "Sous-total",
                "tax_amount": "Montant TVA",
                "grand_total": "Total général",
                
                # Payment Interface
                "payment_method": "Méthode de paiement",
                "cash_payment": "Paiement espèces",
                "card_payment": "Paiement carte",
                "amount_paid": "Montant payé",
                "change_due": "Monnaie à rendre",
                "process_payment": "Traiter le paiement",
                "payment_complete": "Paiement terminé",
                
                # Buttons
                "add_to_cart": "Ajouter au panier",
                "clear_cart": "Vider le panier",
                "pay_cash": "Espèces",
                "pay_card": "Carte",
                "print": "Imprimer",
                "save": "Enregistrer",
                "cancel": "Annuler",
                "close": "Fermer",
                "edit": "Modifier",
                "delete": "Supprimer",
                "add": "Ajouter",
                "search": "Rechercher",
                "refresh": "Actualiser",
                "back": "Retour",
                "next": "Suivant",
                "previous": "Précédent",
                "ok": "OK",
                "yes": "Oui",
                "no": "Non",
                
                # Messages
                "sale_completed": "Vente terminée",
                "payment_successful": "Paiement réussi",
                "error": "Erreur",
                "warning": "Attention",
                "success": "Succès",
                "confirm": "Confirmer",
                "information": "Information",
                "loading": "Chargement...",
                "please_wait": "Veuillez patienter",
                "operation_completed": "Opération terminée",
                "operation_failed": "Opération échouée",
                
                # Receipt
                "receipt_title": "REÇU DE VENTE",
                "date": "Date",
                "time": "Heure",
                "items": "Articles",
                "quantity": "Qté",
                "price": "Prix",
                "subtotal": "Sous-total",
                "tax": "TVA",
                "change": "Monnaie",
                "thank_you": "Merci pour votre achat",
                "cashier": "Caissier",
                "transaction_id": "ID Transaction",
                
                # Settings
                "language_settings": "Paramètres de langue",
                "receipt_settings": "Paramètres du reçu",
                "select_language": "Sélectionner la langue",
                "french": "Français",
                "arabic": "العربية",
                "english": "English",
                "enable_rtl": "Activer le mode RTL (droite à gauche)",
                "font_settings": "Paramètres de police",
                "font_family": "Famille de police",
                "font_size": "Taille de police",
                "arabic_font": "Police arabe",
                
                # Backup Settings
                "backup_settings": "Paramètres de sauvegarde",
                "create_backup": "Créer une sauvegarde",
                "restore_backup": "Restaurer une sauvegarde",
                "auto_backup": "Sauvegarde automatique",
                "backup_frequency": "Fréquence de sauvegarde",
                "backup_time": "Heure de sauvegarde",
                "max_backups": "Nombre max de sauvegardes",
                "backup_location": "Emplacement de sauvegarde",
                "backup_compression": "Compression",
                "include_images": "Inclure les images",
                "test_backup": "Test de sauvegarde",
                "check_scheduler": "Vérifier planificateur",
                "backup_created": "Sauvegarde créée avec succès",
                "backup_restored": "Sauvegarde restaurée avec succès",
                "backup_failed": "Échec de la sauvegarde",
                "restore_failed": "Échec de la restauration",
                "backup_list": "Liste des sauvegardes",
                "backup_date": "Date de sauvegarde",
                "backup_size": "Taille",
                "backup_type": "Type",
                "daily": "Quotidienne",
                "weekly": "Hebdomadaire",
                "monthly": "Mensuelle",
                "import_backup": "Importer une sauvegarde",
                "export_data": "Exporter les données",
                "confirm_restore": "Confirmer la restauration",
                "restore_warning": "Cette action remplacera toutes les données actuelles. Continuer?",
                "backup_name": "Nom de la sauvegarde",
                "custom_backup": "Sauvegarde personnalisée",
                
                # Validation Messages
                "field_required": "Ce champ est obligatoire",
                "invalid_price": "Prix invalide",
                "invalid_quantity": "Quantité invalide",
                "product_not_found": "Produit non trouvé",
                "insufficient_stock": "Stock insuffisant",
                "cart_is_empty": "Le panier est vide",
                "payment_amount_invalid": "Montant de paiement invalide",
                
                # Dialog Titles
                "add_product_dialog": "Ajouter un produit",
                "edit_product_dialog": "Modifier le produit",
                "payment_dialog": "Traitement du paiement",
                "print_receipt_dialog": "Imprimer le reçu",
                "confirm_delete": "Confirmer la suppression",
                "select_printer": "Sélectionner l'imprimante",
                
                # Additional message box translations
                "cart_empty_error": "Le panier est vide!",
                "insufficient_payment": "Montant de paiement insuffisant!",
                "scanner": "Scanner",
                "scanner_message": "Fonction scanner à implémenter",
                "barcode_scanner": "Scanner de code-barres",
                "scan_barcode": "Scanner le code-barres",
                "enter_barcode": "Entrez le code-barres:",
                "scan_button": "Scanner",
                "product_not_found_barcode": "Produit non trouvé avec ce code-barres",
                "removed_from_cart": "retiré du panier",
                "suspend_function": "Suspendre",
                "cart_suspended": "Panier suspendu",
                "no_active_session": "Aucune session active. Veuillez d'abord ouvrir la caisse.",
                "logout": "Déconnexion",
                "logout_confirm": "Êtes-vous sûr de vouloir vous déconnecter?",
                "settings_error": "Erreur lors de l'ouverture des paramètres",
                "language_settings_error": "Erreur lors de l'ouverture des paramètres de langue",
                "sale_finalization_error": "Erreur lors de la finalisation de la vente",
                
                # Additional UI elements
                "languages": "LANGUES",
                "current_language": "Langue actuelle",
                "point_of_sale": "POINT DE VENTE",
                "pos": "PDV",
                "admin": "Admin",
                "logout_btn": "DÉCONNEXION",
                "add_first_product": "Ajouter votre premier produit au panier",
                "cart_header": "🛒 Panier",
                "subtotal_label": "SOUS-TOTAL",
                "total_label": "TOTAL",
                "no_products_available": "Aucun produit disponible. Cliquez sur '📦 Inventory' pour ajouter des produits.",
                "back_to_register": "← RETOUR À L'ÉCRAN DU REGISTRE",
                "order_history_title": "HISTORIQUE DES COMMANDES",
                "filters": "Filtres",
                "all_registers": "Tous les registres",
                "no_orders_found": "Aucune commande trouvée",
                "order": "Commande",
                "time": "Heure",
                "client": "Client",
                "status": "Statut",
                "daily_profit_title": "Raport",
                "total_sales": "Total des ventes",
                "total_cash": "Total en espèce",
                
                # Report translations
                "report_analytics": "Analyses et Rapports",
                "time_period": "Période",
                "daily_report": "Rapport Quotidien",
                "monthly_report": "Rapport Mensuel", 
                "yearly_report": "Rapport Annuel",
                "sales_overview": "Aperçu des Ventes",
                "product_analysis": "Analyse des Produits",
                "stock_analysis": "Analyse du Stock",
                "financial_summary": "Résumé Financier",
                "top_products": "Produits les Plus Vendus",
                "low_stock": "Stock Faible",
                "in_stock": "En Stock",
                "revenue": "Chiffre d'Affaires",
                "profit": "Bénéfice",
                "units_sold": "Unités Vendues",
                "total_orders": "Total Commandes",
                "average_order": "Commande Moyenne",
                "items_per_order": "Articles par Commande",
                "payment_methods": "Méthodes de Paiement",
                "cash_payments": "Paiements Espèce",
                "card_payments": "Paiements Carte",
                "export_report": "Exporter Rapport",
                "generate_chart": "Générer Graphique",
                "date_range": "Plage de Dates",
                "from_date": "Date de début",
                "to_date": "Date de fin",
                "apply_filter": "Appliquer Filtre",
                "clear_filter": "Effacer Filtre",
                "select_printer": "Sélectionner l'imprimante",
                "printer_label": "Imprimante:",
                "format_label": "Format:",
                "thermal_receipt": "Reçu thermique (80mm)",
                "pdf_format": "PDF",
                
                # Store and register info
                "store_name": "PDV",
                "register_info": "Caisse : principale",
                
                # Receipt dialog
                "preview": "Aperçu",
                "test_print": "Test d'impression", 
                "store_info": "Informations du magasin",
                "store_name_label": "Nom du magasin:",
                "address_line1": "Adresse ligne 1:",
                "address_line2": "Adresse ligne 2:", 
                "phone": "Téléphone:",
                "email": "Email:",
                "logo": "Logo:",
                "show_logo": "Afficher le logo",
                "choose_image": "Choisir image",
                "logo_text": "Texte du logo:",
                "end_message": "Message de fin:",
                "tax_number": "Numéro fiscal:",
                "show": "Afficher",
                "printer": "Imprimante",
                "default_printer": "Imprimante par défaut:",
                "auto_print": "Impression automatique après paiement",
                
                # Top action buttons
                "all": "Tous",
                "inventory": "📦 Inventory",
                "scan_product": "📷 Scanner un produit",
                
                # Inventory management window
                "inventory_management": "📦 Gestion d'Inventaire",
                "search_placeholder": "Rechercher produit...",
                "add_new_product": "Nouveau produit",
                "product_id": "ID",
                "product_name": "Nom",
                "category": "Catégorie",
                "price": "Prix",
                "stock": "Stock",
                "actions": "Actions",
                "edit": "Modifier",
                "delete": "Supprimer",
                
                # More inventory elements
                "search_colon": "Rechercher:",
                "category_colon": "Catégorie:",
                "all_categories": "Toutes",
                "product_list": "Liste des Produits",
                "product_details": "Détails du Produit",
                "supplier": "Fournisseur",
                "cost_price": "Prix Coût",
                "sell_price": "Prix Vente",
                "status": "Statut",
                
                # Additional translation keys
                "close": "Fermer",
                "split_payment": "Paiement séparé",
                "payment_details": "Détails du paiement",
                "total_paid": "Total réglé",
                "remaining": "Restant",
                "change": "Monnaie",
                "payment_method": "Mode de paiement",
                "product_name_label": "Nom du produit:",
                "price_label": "Prix (DH):",
                "description_label": "Description:",
                "save": "Enregistrer",
                "cancel": "Annuler",
                "product_id_label": "ID Produit:",
                "product_name_label_detailed": "Nom du Produit:",
                "category_label": "Catégorie:",
                "supplier_label": "Fournisseur:",
                "barcode_label": "Code-barres:",
                "cost_price_no_tax": "Prix Coût (Sans Taxe):",
                "selling_price": "Prix de Vente:",
                "stock_quantity": "Quantité en Stock:",
                "description": "Description:",
                "status_label": "Statut:",
                "active_product": "Produit Actif",
                "save_product": "💾 Sauvegarder",
                "new_product": "➕ Nouveau Produit",
                "delete_product": "🗑️ Supprimer",
                
                # Error messages
                "print_error": "Erreur d'impression",
                "invalid_amount": "Montant invalide. Veuillez entrer un nombre valide.",
                "product_name_required": "Le nom du produit est requis",
                "price_must_be_positive": "Le prix doit être supérieur à 0",
                "invalid_price": "Prix invalide",
                "error_loading_products": "Erreur lors du chargement des produits",
                "validation_error": "Erreur de validation",
                "save_error": "Erreur lors de la sauvegarde",
                "no_product_selected": "Aucun produit sélectionné",
                
                # Login and User Management
                "login_title": "Connexion POS",
                "pos_login": "Connexion au Système POS",
                "username": "Nom d'utilisateur",
                "password": "Mot de passe",
                "login": "Se connecter",
                "logout": "Se déconnecter",
                "enter_credentials": "Veuillez saisir le nom d'utilisateur et le mot de passe",
                "authenticating": "Authentification...",
                "invalid_credentials": "Nom d'utilisateur ou mot de passe invalide",
                "default_accounts": "Comptes par défaut",
                "user_management": "Gestion des utilisateurs",
                "add_user": "Ajouter utilisateur",
                "edit_user": "Modifier utilisateur",
                "remove_user": "Supprimer utilisateur",
                "change_password": "Changer mot de passe",
                "refresh": "Actualiser",
                "create_user": "Créer utilisateur",
                "user_created": "Utilisateur créé avec succès",
                "user_limit": "Limite d'utilisateurs atteinte",
                "logged_in_as": "Connecté en tant que",
                "welcome_user": "Bienvenue",
                "admin_panel": "Panneau d'administration",
                "user_activities": "Activités des utilisateurs",
                "user_sales_report": "Rapport des ventes par utilisateur",
                "user_operations": "Opérations utilisateur",
                "cannot_delete_product": "Impossible de supprimer le produit",
                "delete_error": "Erreur lors de la suppression",
                "amount_cannot_be_negative": "Le montant ne peut pas être négatif",
                "enter_valid_amount": "Veuillez entrer un montant valide",
                "select_amount": "Veuillez sélectionner un montant",
                "amount_must_be_positive": "Le montant doit être positif"
            },
            
            "AR": {
                # Main UI
                "app_title": "نظام نقطة البيع - ريمال",
                "cash_register": "الصندوق",
                "products": "المنتجات",
                "cart": "السلة",
                "total": "المجموع",
                "payment": "الدفع",
                "receipt": "الإيصال",
                "settings": "الإعدادات",
                
                # Sidebar Navigation
                "register_screen": "شاشة الصندوق",
                "order_history": "تاريخ الطلبات",
                "daily_profit": "تقرير",
                "manage_cash": "إدارة النقد",
                "receipt_settings": "إعدادات الإيصال",
                "language_settings_menu": "إعدادات اللغة",
                "backup_settings": "النسخ الاحتياطي",
                "close_register": "إغلاق الصندوق",
                
                # Product Management
                "product_name": "اسم المنتج",
                "product_price": "السعر",
                "product_category": "الفئة",
                "product_barcode": "الباركود",
                "add_product": "إضافة منتج",
                "edit_product": "تعديل منتج",
                "delete_product": "حذف منتج",
                "search_products": "البحث عن منتجات",
                
                # Cart Operations
                "item_quantity": "الكمية",
                "item_price": "سعر الوحدة",
                "item_total": "المجموع",
                "remove_item": "حذف",
                "cart_empty": "السلة فارغة",
                "subtotal": "المجموع الفرعي",
                "tax_amount": "مبلغ الضريبة",
                "grand_total": "المجموع الإجمالي",
                
                # Payment Interface
                "payment_method": "طريقة الدفع",
                "cash_payment": "دفع نقدي",
                "card_payment": "دفع بالبطاقة",
                "amount_paid": "المبلغ المدفوع",
                "change_due": "الباقي",
                "process_payment": "معالجة الدفع",
                "payment_complete": "اكتمال الدفع",
                
                # Buttons
                "add_to_cart": "أضف للسلة",
                "clear_cart": "مسح السلة",
                "pay_cash": "نقداً",
                "pay_card": "بطاقة",
                "print": "طباعة",
                "save": "حفظ",
                "cancel": "إلغاء",
                "close": "إغلاق",
                "edit": "تعديل",
                "delete": "حذف",
                "add": "إضافة",
                "search": "بحث",
                "refresh": "تحديث",
                "back": "رجوع",
                "next": "التالي",
                "previous": "السابق",
                "ok": "موافق",
                "yes": "نعم",
                "no": "لا",
                
                # Messages
                "sale_completed": "تمت عملية البيع",
                "payment_successful": "تم الدفع بنجاح",
                "error": "خطأ",
                "warning": "تحذير",
                "success": "نجح",
                "confirm": "تأكيد",
                "information": "معلومات",
                "loading": "جارٍ التحميل...",
                "please_wait": "يرجى الانتظار",
                "operation_completed": "اكتملت العملية",
                "operation_failed": "فشلت العملية",
                
                # Receipt
                "receipt_title": "إيصال البيع",
                "date": "التاريخ",
                "time": "الوقت",
                "items": "المواد",
                "quantity": "الكمية",
                "price": "السعر",
                "subtotal": "المجموع الفرعي",
                "tax": "الضريبة",
                "change": "الباقي",
                "thank_you": "شكراً لشرائكم",
                "cashier": "الكاشير",
                "transaction_id": "رقم المعاملة",
                
                # Settings
                "language_settings": "إعدادات اللغة",
                "receipt_settings": "إعدادات الإيصال",
                "select_language": "اختر اللغة",
                "french": "Français",
                "arabic": "العربية",
                "english": "English",
                "enable_rtl": "تفعيل وضع RTL (من اليمين لليسار)",
                "font_settings": "إعدادات الخط",
                "font_family": "نوع الخط",
                "font_size": "حجم الخط",
                "arabic_font": "الخط العربي",
                
                # Backup Settings
                "backup_settings": "إعدادات النسخ الاحتياطي",
                "create_backup": "إنشاء نسخة احتياطية",
                "restore_backup": "استرجاع نسخة احتياطية",
                "auto_backup": "نسخ احتياطي تلقائي",
                "backup_frequency": "تكرار النسخ الاحتياطي",
                "backup_time": "وقت النسخ الاحتياطي",
                "max_backups": "الحد الأقصى للنسخ الاحتياطية",
                "backup_location": "مكان النسخ الاحتياطي",
                "backup_compression": "ضغط",
                "include_images": "تضمين الصور",
                "test_backup": "اختبار النسخ الاحتياطي",
                "check_scheduler": "فحص المجدول",
                "backup_created": "تم إنشاء النسخة الاحتياطية بنجاح",
                "backup_restored": "تم استرجاع النسخة الاحتياطية بنجاح",
                "backup_failed": "فشل في النسخ الاحتياطي",
                "restore_failed": "فشل في الاسترجاع",
                "backup_list": "قائمة النسخ الاحتياطية",
                "backup_date": "تاريخ النسخ الاحتياطي",
                "backup_size": "الحجم",
                "backup_type": "النوع",
                "daily": "يومي",
                "weekly": "أسبوعي",
                "monthly": "شهري",
                "import_backup": "استيراد نسخة احتياطية",
                "export_data": "تصدير البيانات",
                "confirm_restore": "تأكيد الاسترجاع",
                "restore_warning": "سيتم استبدال جميع البيانات الحالية. هل تريد المتابعة؟",
                "backup_name": "اسم النسخة الاحتياطية",
                "custom_backup": "نسخة احتياطية مخصصة",
                
                # Validation Messages
                "field_required": "هذا الحقل مطلوب",
                "invalid_price": "سعر غير صحيح",
                "invalid_quantity": "كمية غير صحيحة",
                "product_not_found": "المنتج غير موجود",
                "insufficient_stock": "المخزون غير كافي",
                "cart_is_empty": "السلة فارغة",
                "payment_amount_invalid": "مبلغ الدفع غير صحيح",
                
                # Dialog Titles
                "add_product_dialog": "إضافة منتج",
                "edit_product_dialog": "تعديل المنتج",
                "payment_dialog": "معالجة الدفع",
                "print_receipt_dialog": "طباعة الإيصال",
                "confirm_delete": "تأكيد الحذف",
                "select_printer": "اختيار الطابعة",
                
                # Additional message box translations
                "cart_empty_error": "السلة فارغة!",
                "insufficient_payment": "مبلغ الدفع غير كافي!",
                "scanner": "الماسح الضوئي",
                "scanner_message": "وظيفة الماسح الضوئي قيد التطوير",
                "barcode_scanner": "ماسح الباركود",
                "scan_barcode": "مسح الباركود",
                "enter_barcode": "أدخل الباركود:",
                "scan_button": "مسح",
                "product_not_found_barcode": "لم يتم العثور على منتج بهذا الباركود",
                "removed_from_cart": "تم إزالته من السلة",
                "suspend_function": "إيقاف مؤقت",
                "cart_suspended": "السلة متوقفة مؤقتاً",
                "no_active_session": "لا توجد جلسة نشطة. يرجى فتح الصندوق أولاً.",
                "logout": "تسجيل الخروج",
                "logout_confirm": "هل أنت متأكد من تسجيل الخروج؟",
                "settings_error": "خطأ في فتح الإعدادات",
                "language_settings_error": "خطأ في فتح إعدادات اللغة",
                "sale_finalization_error": "خطأ في إتمام البيع",
                
                # Additional UI elements
                "languages": "اللغات",
                "current_language": "اللغة الحالية",
                "point_of_sale": "نقطة البيع",
                "pos": "نقطة البيع",
                "admin": "المدير",
                "logout_btn": "تسجيل الخروج",
                "add_first_product": "أضف منتجك الأول إلى السلة",
                "cart_header": "🛒 السلة",
                "subtotal_label": "المجموع الفرعي",
                "total_label": "المجموع",
                "no_products_available": "لا توجد منتجات متاحة. انقر على '📦 المخزون' لإضافة منتجات.",
                "back_to_register": "← العودة إلى شاشة الصندوق",
                "order_history_title": "تاريخ الطلبات",
                "filters": "المرشحات",
                "all_registers": "جميع الصناديق",
                "no_orders_found": "لم يتم العثور على طلبات",
                "order": "الطلب",
                "time": "الوقت",
                "client": "العميل",
                "status": "الحالة",
                "daily_profit_title": "تقرير",
                "total_sales": "إجمالي المبيعات",
                "total_cash": "إجمالي النقد",
                
                # Report translations
                "report_analytics": "التحليلات والتقارير",
                "time_period": "الفترة الزمنية",
                "daily_report": "تقرير يومي",
                "monthly_report": "تقرير شهري",
                "yearly_report": "تقرير سنوي",
                "sales_overview": "نظرة عامة على المبيعات",
                "product_analysis": "تحليل المنتجات",
                "stock_analysis": "تحليل المخزون",
                "financial_summary": "الملخص المالي",
                "top_products": "المنتجات الأكثر مبيعاً",
                "low_stock": "مخزون منخفض",
                "in_stock": "متوفر في المخزون",
                "revenue": "الإيرادات",
                "profit": "الربح",
                "units_sold": "الوحدات المباعة",
                "total_orders": "إجمالي الطلبات",
                "average_order": "متوسط الطلب",
                "items_per_order": "العناصر لكل طلب",
                "payment_methods": "طرق الدفع",
                "cash_payments": "مدفوعات نقدية",
                "card_payments": "مدفوعات بالبطاقة",
                "export_report": "تصدير التقرير",
                "generate_chart": "إنشاء رسم بياني",
                "date_range": "نطاق التاريخ",
                "from_date": "من تاريخ",
                "to_date": "إلى تاريخ",
                "apply_filter": "تطبيق الفلتر",
                "clear_filter": "مسح الفلتر",
                "select_printer": "اختيار الطابعة",
                "printer_label": "الطابعة:",
                "format_label": "التنسيق:",
                "thermal_receipt": "إيصال حراري (80 ملم)",
                "pdf_format": "PDF",
                
                # Store and register info
                "store_name": "نقطة البيع",
                "register_info": "الصندوق : الرئيسي",
                
                # Receipt dialog
                "preview": "معاينة",
                "test_print": "اختبار الطباعة", 
                "store_info": "معلومات المتجر",
                "store_name_label": "اسم المتجر:",
                "address_line1": "العنوان السطر 1:",
                "address_line2": "العنوان السطر 2:", 
                "phone": "الهاتف:",
                "email": "البريد الإلكتروني:",
                "logo": "الشعار:",
                "show_logo": "إظهار الشعار",
                "choose_image": "اختيار صورة",
                "logo_text": "نص الشعار:",
                "end_message": "رسالة الختام:",
                "tax_number": "الرقم الضريبي:",
                "show": "إظهار",
                "printer": "الطابعة",
                "default_printer": "الطابعة الافتراضية:",
                "auto_print": "طباعة تلقائية بعد الدفع",
                
                # Top action buttons
                "all": "الكل",
                "inventory": "📦 المخزون",
                "scan_product": "📷 مسح منتج",
                
                # Inventory management window
                "inventory_management": "📦 إدارة المخزون",
                "search_placeholder": "البحث عن منتج...",
                "add_new_product": "منتج جديد",
                "product_id": "المعرف",
                "product_name": "الاسم",
                "category": "الفئة",
                "price": "السعر",
                "stock": "المخزون",
                "actions": "الإجراءات",
                "edit": "تعديل",
                "delete": "حذف",
                
                # More inventory elements
                "search_colon": "البحث:",
                "category_colon": "الفئة:",
                "all_categories": "الكل",
                "product_list": "قائمة المنتجات",
                "product_details": "تفاصيل المنتج",
                "supplier": "المورد",
                "cost_price": "سعر التكلفة",
                "sell_price": "سعر البيع",
                "status": "الحالة",
                
                # Additional translation keys
                "close": "إغلاق",
                "split_payment": "دفع مقسم",
                "payment_details": "تفاصيل الدفع",
                "total_paid": "المبلغ المدفوع",
                "remaining": "المتبقي",
                "change": "المتبقي",
                "payment_method": "طريقة الدفع",
                "product_name_label": "اسم المنتج:",
                "price_label": "السعر (DH):",
                "description_label": "الوصف:",
                "save": "حفظ",
                "cancel": "إلغاء",
                "product_id_label": "رقم المنتج:",
                "product_name_label_detailed": "اسم المنتج:",
                "category_label": "الفئة:",
                "supplier_label": "المورد:",
                "barcode_label": "الباركود:",
                "cost_price_no_tax": "سعر التكلفة (بدون ضريبة):",
                "selling_price": "سعر البيع:",
                "stock_quantity": "كمية المخزون:",
                "description": "الوصف:",
                "status_label": "الحالة:",
                "active_product": "منتج نشط",
                "save_product": "💾 حفظ",
                "new_product": "➕ منتج جديد",
                "delete_product": "🗑️ حذف",
                
                # Error messages
                "print_error": "خطأ في الطباعة",
                "invalid_amount": "مبلغ غير صالح. يرجى إدخال رقم صالح.",
                "product_name_required": "اسم المنتج مطلوب",
                "price_must_be_positive": "يجب أن يكون السعر أكبر من 0",
                "invalid_price": "سعر غير صالح",
                "error_loading_products": "خطأ في تحميل المنتجات",
                "validation_error": "خطأ في التحقق",
                "save_error": "خطأ في الحفظ",
                "no_product_selected": "لم يتم تحديد منتج",
                "cannot_delete_product": "لا يمكن حذف المنتج",
                "delete_error": "خطأ في الحذف",
                "amount_cannot_be_negative": "لا يمكن أن يكون المبلغ سالباً",
                "enter_valid_amount": "يرجى إدخال مبلغ صالح",
                "select_amount": "يرجى تحديد مبلغ",
                "amount_must_be_positive": "يجب أن يكون المبلغ موجباً",
                
                # Login and User Management
                "login_title": "دخول نظام POS",
                "pos_login": "دخول نظام نقاط البيع",
                "username": "اسم المستخدم",
                "password": "كلمة المرور",
                "login": "دخول",
                "logout": "خروج",
                "enter_credentials": "يرجى إدخال اسم المستخدم وكلمة المرور",
                "authenticating": "جاري التحقق...",
                "invalid_credentials": "اسم المستخدم أو كلمة المرور غير صحيحة",
                "default_accounts": "الحسابات الافتراضية",
                "user_management": "إدارة المستخدمين",
                "add_user": "إضافة مستخدم",
                "edit_user": "تحرير مستخدم",
                "remove_user": "حذف مستخدم",
                "change_password": "تغيير كلمة المرور",
                "refresh": "تحديث",
                "create_user": "إنشاء مستخدم",
                "user_created": "تم إنشاء المستخدم بنجاح",
                "user_limit": "تم الوصول لحد المستخدمين",
                "logged_in_as": "متصل كـ",
                "welcome_user": "مرحباً",
                "admin_panel": "لوحة الإدارة",
                "user_activities": "أنشطة المستخدمين",
                "user_sales_report": "تقرير مبيعات المستخدمين",
                "user_operations": "عمليات المستخدم",
            },
            
            "EN": {
                # Main UI
                "app_title": "Point of Sale System - RIMAL",
                "cash_register": "Cash Register",
                "products": "Products",
                "cart": "Cart",
                "total": "Total",
                "payment": "Payment",
                "receipt": "Receipt",
                "settings": "Settings",
                
                # Sidebar Navigation
                "register_screen": "REGISTER SCREEN",
                "order_history": "ORDER HISTORY",
                "daily_profit": "REPORT",
                "manage_cash": "MANAGE CASH",
                "receipt_settings": "RECEIPT SETTINGS",
                "language_settings_menu": "LANGUAGE SETTINGS",
                "backup_settings": "BACKUP",
                "close_register": "CLOSE REGISTER",
                
                # Product Management
                "product_name": "Product Name",
                "product_price": "Price",
                "product_category": "Category",
                "product_barcode": "Barcode",
                "add_product": "Add Product",
                "edit_product": "Edit Product",
                "delete_product": "Delete Product",
                "search_products": "Search Products",
                
                # Cart Operations
                "item_quantity": "Quantity",
                "item_price": "Unit Price",
                "item_total": "Total",
                "remove_item": "Remove",
                "cart_empty": "Cart Empty",
                "subtotal": "Subtotal",
                "tax_amount": "Tax Amount",
                "grand_total": "Grand Total",
                
                # Payment Interface
                "payment_method": "Payment Method",
                "cash_payment": "Cash Payment",
                "card_payment": "Card Payment",
                "amount_paid": "Amount Paid",
                "change_due": "Change Due",
                "process_payment": "Process Payment",
                "payment_complete": "Payment Complete",
                
                # Buttons
                "add_to_cart": "Add to Cart",
                "clear_cart": "Clear Cart",
                "pay_cash": "Cash",
                "pay_card": "Card",
                "print": "Print",
                "save": "Save",
                "cancel": "Cancel",
                "close": "Close",
                "edit": "Edit",
                "delete": "Delete",
                "add": "Add",
                "search": "Search",
                "refresh": "Refresh",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "ok": "OK",
                "yes": "Yes",
                "no": "No",
                
                # Messages
                "sale_completed": "Sale Completed",
                "payment_successful": "Payment Successful",
                "error": "Error",
                "warning": "Warning",
                "success": "Success",
                "confirm": "Confirm",
                "information": "Information",
                "loading": "Loading...",
                "please_wait": "Please wait",
                "operation_completed": "Operation completed",
                "operation_failed": "Operation failed",
                
                # Receipt
                "receipt_title": "SALES RECEIPT",
                "date": "Date",
                "time": "Time",
                "items": "Items",
                "quantity": "Qty",
                "price": "Price",
                "subtotal": "Subtotal",
                "tax": "Tax",
                "change": "Change",
                "thank_you": "Thank you for your purchase",
                "cashier": "Cashier",
                "transaction_id": "Transaction ID",
                
                # Settings
                "language_settings": "Language Settings",
                "receipt_settings": "Receipt Settings",
                "select_language": "Select Language",
                "french": "Français",
                "arabic": "العربية",
                "english": "English",
                "enable_rtl": "Enable RTL Mode (Right to Left)",
                "font_settings": "Font Settings",
                "font_family": "Font Family",
                "font_size": "Font Size",
                "arabic_font": "Arabic Font",
                
                # Backup Settings
                "backup_settings": "Backup Settings",
                "create_backup": "Create Backup",
                "restore_backup": "Restore Backup",
                "auto_backup": "Auto Backup",
                "backup_frequency": "Backup Frequency",
                "backup_time": "Backup Time",
                "max_backups": "Max Backups",
                "backup_location": "Backup Location",
                "backup_compression": "Compression",
                "include_images": "Include Images",
                "test_backup": "Test Backup",
                "check_scheduler": "Check Scheduler",
                "backup_created": "Backup created successfully",
                "backup_restored": "Backup restored successfully",
                "backup_failed": "Backup failed",
                "restore_failed": "Restore failed",
                "backup_list": "Backup List",
                "backup_date": "Backup Date",
                "backup_size": "Size",
                "backup_type": "Type",
                "daily": "Daily",
                "weekly": "Weekly",
                "monthly": "Monthly",
                "import_backup": "Import Backup",
                "export_data": "Export Data",
                "confirm_restore": "Confirm Restore",
                "restore_warning": "This will replace all current data. Continue?",
                "backup_name": "Backup Name",
                "custom_backup": "Custom Backup",
                
                # Validation Messages
                "field_required": "This field is required",
                "invalid_price": "Invalid price",
                "invalid_quantity": "Invalid quantity",
                "product_not_found": "Product not found",
                "insufficient_stock": "Insufficient stock",
                "cart_is_empty": "Cart is empty",
                "payment_amount_invalid": "Invalid payment amount",
                
                # Dialog Titles
                "add_product_dialog": "Add Product",
                "edit_product_dialog": "Edit Product",
                "payment_dialog": "Process Payment",
                "print_receipt_dialog": "Print Receipt",
                "confirm_delete": "Confirm Delete",
                "select_printer": "Select Printer",
                
                # Additional message box translations
                "cart_empty_error": "Cart is empty!",
                "insufficient_payment": "Insufficient payment amount!",
                "scanner": "Scanner",
                "scanner_message": "Scanner feature to be implemented",
                "barcode_scanner": "Barcode Scanner",
                "scan_barcode": "Scan Barcode",
                "enter_barcode": "Enter barcode:",
                "scan_button": "Scan",
                "product_not_found_barcode": "Product not found with this barcode",
                "removed_from_cart": "removed from cart",
                "suspend_function": "Suspend",
                "cart_suspended": "Cart suspended",
                "no_active_session": "No active session. Please open register first.",
                "logout": "Logout",
                "logout_confirm": "Are you sure you want to logout?",
                "settings_error": "Error opening settings",
                "language_settings_error": "Error opening language settings",
                "sale_finalization_error": "Error finalizing sale",
                
                # Additional UI elements
                "languages": "LANGUAGES",
                "current_language": "Current Language",
                "point_of_sale": "POINT OF SALE",
                "pos": "POS",
                "admin": "Admin",
                "logout_btn": "LOGOUT",
                "add_first_product": "Add your first product to cart",
                "cart_header": "🛒 Cart",
                "subtotal_label": "SUBTOTAL",
                "total_label": "TOTAL",
                "no_products_available": "No products available. Click on '📦 Inventory' to add products.",
                "back_to_register": "← BACK TO REGISTER SCREEN",
                "order_history_title": "ORDER HISTORY",
                "filters": "Filters",
                "all_registers": "All registers",
                "no_orders_found": "No orders found",
                "order": "Order",
                "time": "Time",
                "client": "Client",
                "status": "Status",
                "daily_profit_title": "Report",
                "total_sales": "Total Sales",
                "total_cash": "Total Cash",
                
                # Report translations
                "report_analytics": "Analytics & Reports",
                "time_period": "Time Period",
                "daily_report": "Daily Report",
                "monthly_report": "Monthly Report",
                "yearly_report": "Yearly Report",
                "sales_overview": "Sales Overview",
                "product_analysis": "Product Analysis",
                "stock_analysis": "Stock Analysis",
                "financial_summary": "Financial Summary",
                "top_products": "Top Selling Products",
                "low_stock": "Low Stock",
                "in_stock": "In Stock",
                "revenue": "Revenue",
                "profit": "Profit",
                "units_sold": "Units Sold",
                "total_orders": "Total Orders",
                "average_order": "Average Order",
                "items_per_order": "Items per Order",
                "payment_methods": "Payment Methods",
                "cash_payments": "Cash Payments",
                "card_payments": "Card Payments",
                "export_report": "Export Report",
                "generate_chart": "Generate Chart",
                "date_range": "Date Range",
                "from_date": "From Date",
                "to_date": "To Date",
                "apply_filter": "Apply Filter",
                "clear_filter": "Clear Filter",
                "total_sales": "Total Sales",
                "total_cash": "Total Cash",
                "select_printer": "Select Printer",
                "printer_label": "Printer:",
                "format_label": "Format:",
                "thermal_receipt": "Thermal Receipt (80mm)",
                "pdf_format": "PDF",
                
                # Store and register info
                "store_name": "POS",
                "register_info": "Register : main",
                
                # Receipt dialog
                "preview": "Preview",
                "test_print": "Test Print", 
                "store_info": "Store Information",
                "store_name_label": "Store Name:",
                "address_line1": "Address Line 1:",
                "address_line2": "Address Line 2:", 
                "phone": "Phone:",
                "email": "Email:",
                "logo": "Logo:",
                "show_logo": "Show Logo",
                "choose_image": "Choose Image",
                "logo_text": "Logo Text:",
                "end_message": "End Message:",
                "tax_number": "Tax Number:",
                "show": "Show",
                "printer": "Printer",
                "default_printer": "Default Printer:",
                "auto_print": "Auto print after payment",
                
                # Top action buttons
                "all": "All",
                "inventory": "📦 Inventory",
                "scan_product": "📷 Scan Product",
                
                # Inventory management window
                "inventory_management": "📦 Inventory Management",
                "search_placeholder": "Search product...",
                "add_new_product": "New Product",
                "product_id": "ID",
                "product_name": "Name",
                "category": "Category",
                "price": "Price",
                "stock": "Stock",
                "actions": "Actions",
                "edit": "Edit",
                "delete": "Delete",
                
                # More inventory elements
                "search_colon": "Search:",
                "category_colon": "Category:",
                "all_categories": "All",
                "product_list": "Product List",
                "product_details": "Product Details",
                "supplier": "Supplier",
                "cost_price": "Cost Price",
                "sell_price": "Sell Price",
                "status": "Status",
                
                # Additional translation keys
                "close": "Close",
                "split_payment": "Split Payment",
                "payment_details": "Payment Details",
                "total_paid": "Total Paid",
                "remaining": "Remaining",
                "change": "Change",
                "payment_method": "Payment Method",
                "product_name_label": "Product Name:",
                "price_label": "Price (DH):",
                "description_label": "Description:",
                "save": "Save",
                "cancel": "Cancel",
                "product_id_label": "Product ID:",
                "product_name_label_detailed": "Product Name:",
                "category_label": "Category:",
                "supplier_label": "Supplier:",
                "barcode_label": "Barcode:",
                "cost_price_no_tax": "Cost Price (No Tax):",
                "selling_price": "Selling Price:",
                "stock_quantity": "Stock Quantity:",
                "description": "Description:",
                "status_label": "Status:",
                "active_product": "Active Product",
                "save_product": "💾 Save",
                "new_product": "➕ New Product",
                "delete_product": "🗑️ Delete",
                
                # Error messages
                "print_error": "Print error",
                "invalid_amount": "Invalid amount. Please enter a valid number.",
                "product_name_required": "Product name is required",
                "price_must_be_positive": "Price must be greater than 0",
                "invalid_price": "Invalid price",
                "error_loading_products": "Error loading products",
                "validation_error": "Validation error",
                "save_error": "Save error",
                "no_product_selected": "No product selected",
                "cannot_delete_product": "Cannot delete product",
                "delete_error": "Delete error",
                "amount_cannot_be_negative": "Amount cannot be negative",
                "enter_valid_amount": "Please enter a valid amount",
                "select_amount": "Please select an amount",
                "amount_must_be_positive": "Amount must be positive",
                
                # Login and User Management
                "login_title": "POS Login",
                "pos_login": "POS System Login",
                "username": "Username",
                "password": "Password",
                "login": "Login",
                "logout": "Logout",
                "enter_credentials": "Please enter username and password",
                "authenticating": "Authenticating...",
                "invalid_credentials": "Invalid username or password",
                "default_accounts": "Default Accounts",
                "user_management": "User Management",
                "add_user": "Add User",
                "edit_user": "Edit User",
                "remove_user": "Remove User",
                "change_password": "Change Password",
                "refresh": "Refresh",
                "create_user": "Create User",
                "user_created": "User created successfully",
                "user_limit": "User limit reached",
                "logged_in_as": "Logged in as",
                "welcome_user": "Welcome",
                "admin_panel": "Admin Panel",
                "user_activities": "User Activities",
                "user_sales_report": "User Sales Report",
                "user_operations": "User Operations",
            }
        }
    
    def load_settings(self) -> None:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Update settings with saved values
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
        except Exception as e:
            print(f"Error loading language settings: {e}")
    
    def save_settings(self) -> None:
        """Save settings to file."""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving language settings: {e}")
    
    def get_settings(self) -> LanguageSettings:
        """Get current settings."""
        return self.settings
    
    def set_language(self, language_code: str) -> None:
        """Set current language."""
        if language_code in self.translations:
            self.settings.current_language = language_code
            # Enable RTL for Arabic
            if language_code == "AR":
                self.settings.rtl_mode = True
            else:
                self.settings.rtl_mode = False
            self.save_settings()
    
    def apply_language_immediately(self, language_code: str) -> None:
        """Apply language change immediately without saving to file."""
        if language_code in self.translations:
            self.settings.current_language = language_code
            # Enable RTL for Arabic
            if language_code == "AR":
                self.settings.rtl_mode = True
            else:
                self.settings.rtl_mode = False
    
    def get_text(self, key: str) -> str:
        """Get translated text for current language."""
        current_lang = self.settings.current_language
        if current_lang in self.translations and key in self.translations[current_lang]:
            return self.translations[current_lang][key]
        
        # Fallback to French if translation not found
        if key in self.translations["FR"]:
            return self.translations["FR"][key]
        
        # If still not found, return the key itself
        return key
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their display names."""
        return {
            "FR": self.get_text("french"),
            "AR": self.get_text("arabic"),
            "EN": self.get_text("english")
        }
    
    def update_settings(self, **kwargs) -> None:
        """Update settings."""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        self.save_settings()
    
    def refresh_ui_callback(self, callback_func=None):
        """Set a callback function to refresh the UI when language changes."""
        self.ui_refresh_callback = callback_func
    
    def notify_language_change(self):
        """Notify that language has changed and UI should refresh."""
        if hasattr(self, 'ui_refresh_callback') and self.ui_refresh_callback:
            self.ui_refresh_callback()

# Global language manager instance
language_manager = LanguageManager()

def get_text(key: str) -> str:
    """Convenience function to get translated text."""
    return language_manager.get_text(key)

def set_language(language_code: str) -> None:
    """Convenience function to set language."""
    language_manager.set_language(language_code)

def get_current_language() -> str:
    """Get current language code."""
    return language_manager.settings.current_language
