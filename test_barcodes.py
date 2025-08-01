from utils.csv_import import CSVProductImporter
from database.db_manager import DatabaseManager
importer = CSVProductImporter(DatabaseManager())
preview_data, errors, format_detected = importer.preview_csv_import('sample_products.csv')
print(f'Testing improved sample: {len(preview_data)} products')
for p in preview_data:
    print(f'  {p["name"]}: barcode="{p.get("barcode", "None")}"')
