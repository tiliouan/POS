from utils.csv_import import CSVProductImporter
from database.db_manager import DatabaseManager

# Test with your exact barcode format
test_barcodes = [
    "'-&&&é'é-_à-\"à",
    "'-&&&é'é-_à-'è", 
    "6111258520012",
    "SKU-TEST-001",
    ""
]

importer = CSVProductImporter(DatabaseManager())

print("Testing barcode acceptance:")
for barcode in test_barcodes:
    cleaned = importer.clean_barcode_value(barcode)
    print(f"  Original: '{barcode}' -> Cleaned: '{cleaned}'")
