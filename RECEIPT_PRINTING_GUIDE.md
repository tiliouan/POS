# Receipt Printing System - User Guide

## 🖨️ New Receipt Printing Features

Your POS system now includes a comprehensive receipt printing system with the following features:

### ✨ Key Features

1. **Professional 80mm Thermal Receipts**
   - Matches the design shown in your reference image
   - Customizable store information
   - Logo support (image or text)
   - Professional layout with proper spacing

2. **PDF Receipt Generation**
   - High-quality PDF receipts for email or archival
   - Professional formatting with tables
   - Logo and branding support

3. **Customizable Settings**
   - Store name, address, phone number
   - Logo configuration (image file or text)
   - Footer message customization
   - Tax number display (optional)

4. **Printer Management**
   - Automatic printer detection
   - Support for multiple printers
   - Default printer selection
   - "Save as PDF" option

5. **Receipt Preview**
   - Live preview of receipt layout
   - Test printing functionality
   - Real-time settings updates

## 🎯 How to Use

### Accessing Receipt Settings

1. **Open Settings**: Click the "🖨️ PARAMÈTRES REÇU" button in the sidebar
2. **Configure Store Info**: Enter your store details in the "Informations du magasin" tab
3. **Set Printer Options**: Choose your default printer in the "Imprimante" tab
4. **Customize Layout**: Adjust paper size and formatting in the "Mise en page" tab

### Printing Receipts

**Automatic Printing** (when enabled):
- Receipts print automatically after payment completion
- Uses your default printer settings

**Manual Printing**:
- When auto-print is disabled, a dialog appears after payment
- Choose printer: thermal printer or "Save as PDF"
- Select format: thermal receipt or PDF
- Click "Aperçu" to preview before printing

### Configuration Options

#### Store Information Tab
- **Nom du magasin**: Your business name
- **Adresse ligne 1 & 2**: Store address
- **Téléphone**: Contact number
- **Email**: Store email (optional)
- **Logo**: Choose image file or use text logo
- **Message de fin**: Footer message (e.g., "Thanks for your purchase")
- **Numéro fiscal**: Tax ID number (optional)

#### Printer Settings Tab
- **Imprimante par défaut**: Select default printer
- **Impression automatique**: Auto-print after payment
- **Nombre de copies**: Number of receipt copies

#### Layout Settings Tab
- **Taille du papier**: 58mm, 80mm, or A4
- **Largeur**: Character width for formatting

## 📋 Receipt Format

The receipts include all information from your reference image:

```
        your LOGO here

      Nom du magasin
   Calle Rue del Percebe, 13
      28000 - Madrid

=====================================
Order: 452
Date: juillet 31, 2025
Cashier: Jane Doe
-------------------------------------
1 x Sneakers               107,80 د.م
1 x Shopping bag            40,00 د.م
2 x T-shirt                 39,60 د.م
-------------------------------------
TOTAL                      189,40 د.م
Espèce                     190,00 د.م
Rendu de monnaie             0,60 د.م
=====================================

    Thanks for your purchase
```

## 🔧 Technical Features

### Supported Formats
- **Thermal Printing**: 80mm thermal receipts (most common)
- **PDF Generation**: Professional PDF receipts
- **58mm Thermal**: Compact receipt format
- **A4 Format**: Full-page receipts for special cases

### File Management
- Receipts saved automatically in `receipts/` folder
- Naming convention: `receipt_[ID]_[timestamp]`
- Settings stored in `config/receipt_settings.json`

### Printer Compatibility
- Windows thermal printers
- Network printers
- Virtual PDF printer
- Any Windows-compatible printer

## 🎨 Customization Tips

1. **Logo Setup**:
   - Use PNG, JPG, or GIF images
   - Recommended size: 200x200 pixels
   - Keep file size small for faster printing

2. **Store Information**:
   - Keep address lines short for better formatting
   - Include essential contact information only

3. **Footer Message**:
   - Use friendly, professional messages
   - Consider multilingual support if needed

4. **Paper Size**:
   - 80mm is standard for most thermal printers
   - 58mm for compact receipts
   - A4 for detailed invoices

## 📞 Troubleshooting

### Common Issues

**Receipt doesn't print**:
- Check printer connection
- Verify default printer selection
- Try "Save as PDF" to test receipt generation

**Poor print quality**:
- Check thermal paper quality
- Clean printer head
- Adjust printer settings

**Settings not saving**:
- Ensure write permissions in config folder
- Check for file system errors

**Logo not appearing**:
- Verify image file path
- Use supported formats (PNG, JPG, GIF)
- Check image file permissions

### Test Printing

Use the "Test d'impression" button to:
- Verify printer connectivity
- Check receipt formatting
- Test all settings before real transactions

## 🚀 Advanced Features

### Multiple Copies
- Set number of copies (1-5)
- Useful for customer + merchant copies

### PDF Archival
- Automatic PDF generation for record keeping
- Email-ready format for digital receipts

### Printer Selection
- Quick printer switching
- Support for multiple receipt printers
- Fallback to PDF if printer unavailable

---

## 💡 Tips for Best Results

1. **Regular Testing**: Test print receipts regularly to catch issues early
2. **Backup Settings**: Keep a copy of your receipt settings configuration
3. **Paper Management**: Use quality thermal paper for best results
4. **Preview First**: Use the preview feature to check formatting before printing

Your POS system now provides professional-grade receipt printing that matches modern retail standards!
