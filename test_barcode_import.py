"""
Test Barcode Import Issue
"""

from utils.csv_import import CSVProductImporter
from database.db_manager import DatabaseManager

def test_barcode_import():
    """Test barcode import with WooCommerce-like data."""
    
    # Create test CSV with problematic barcodes like in your WooCommerce export
    test_csv_content = """ID,Type,UGS,"GTIN, UPC, EAN ou ISBN",Nom,Publié,"Mis en avant ?","Visibilité dans le catalogue","Description courte",Description,"Date de début de promo","Date de fin de promo","État de la TVA","Classe de TVA","En stock ?",Stock,"Montant de stock faible","Autoriser les commandes de produits en rupture ?","Vendre individuellement ?","Poids (kg)","Longueur (cm)","Largeur (cm)","Hauteur (cm)","Autoriser les avis clients ?","Note de commande","Tarif promo","Tarif régulier",Catégories,Étiquettes,"Classe d'expédition",Images,"Limite de téléchargement","Jours d'expiration du téléchargement",Parent,"Groupes de produits","Produits suggérés","Ventes croisées","URL externe","Libellé du bouton",Position,Brands
40,simple,"'-&&&é'é-_à-""à",,"Presto Riz Long",1,0,hidden,,,,,taxable,,1,12,,0,0,,,,,1,,,20,Uncategorized,,,,,,,,,,,,0,
42,simple,'-&&&é'é-_à-'è,,"Presto Riz Rond",1,0,hidden,,,,,taxable,,1,12,,0,0,,,,,1,,,18,Uncategorized,,,,,,,,,,,,0,
96,simple,6111258520012,,"PIPAS NOWARA 50G",1,0,hidden,,,,,taxable,,1,108,,0,0,,,,,1,,,"3,5",Uncategorized,,,,,,,,,,,,0,"""
    
    with open("test_woocommerce.csv", "w", encoding="utf-8") as f:
        f.write(test_csv_content)
    
    # Test import
    db_manager = DatabaseManager()
    importer = CSVProductImporter(db_manager)
    
    print("Testing WooCommerce CSV with barcode issues...")
    preview_data, errors, format_detected = importer.preview_csv_import("test_woocommerce.csv", max_preview=10)
    
    print(f"Format detected: {format_detected}")
    print(f"Preview data count: {len(preview_data)}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("Errors found:")
        for error in errors:
            print(f"  - {error}")
    
    if preview_data:
        print("\\nBarcode analysis:")
        for i, product in enumerate(preview_data):
            print(f"  Product {i+1}:")
            print(f"    Name: {product.get('name')}")
            print(f"    Original barcode: {product.get('original_barcode', 'N/A')}")
            print(f"    Cleaned barcode: {product.get('barcode')}")
            print(f"    Price: {product.get('price')}")
    
    # Clean up
    import os
    os.remove("test_woocommerce.csv")

if __name__ == "__main__":
    test_barcode_import()
