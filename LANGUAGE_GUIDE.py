"""
Language Switching Guide
========================

This guide explains how to enable and use language switching in your POS system.

🌐 LANGUAGE SWITCHING METHODS
=============================

1. IMMEDIATE SWITCHING (Real-time)
----------------------------------
   ✅ Changes apply instantly without restart
   ✅ UI updates immediately
   ✅ Settings are saved automatically

   How to use:
   - Open language settings from POS sidebar: "🌐 PARAMÈTRES LANGUE"
   - Select your language (FR/AR/EN)
   - Click "Apply" button
   - Changes are visible immediately!

2. PERSISTENT SWITCHING (Save & Restart)
----------------------------------------
   ✅ Changes saved to config file
   ✅ Full UI translation on restart
   ✅ All dialogs and messages translated

   How to use:
   - Open language settings from POS sidebar
   - Select your language
   - Click "Save" button
   - Restart application for full effect

🎛️ LANGUAGE SETTINGS FEATURES
=============================

Language Selection:
- 🇫🇷 French (Français) - Default
- 🇸🇦 Arabic (العربية) - With RTL support
- 🇺🇸 English - International

Font Settings:
- Font Family: Choose appropriate fonts
- Font Size: Adjustable 8-16pt
- Arabic Font: Special Unicode font for Arabic

RTL Support:
- Automatically enabled for Arabic
- Right-to-left text layout
- Proper Arabic text rendering

🔧 TECHNICAL IMPLEMENTATION
===========================

For Developers - How to add language switching to any widget:

1. Import the language system:
   ```python
   from config.language_settings import get_text, language_manager
   ```

2. Use get_text() for all user-facing text:
   ```python
   label = ttk.Label(parent, text=get_text("products"))
   button = ttk.Button(parent, text=get_text("save"))
   ```

3. Add a refresh method to update UI:
   ```python
   def refresh_ui(self):
       self.title_label.config(text=get_text("app_title"))
       self.save_button.config(text=get_text("save"))
   ```

4. Set up callback for language changes:
   ```python
   language_manager.refresh_ui_callback(self.refresh_ui)
   ```

5. For immediate language switching:
   ```python
   language_manager.apply_language_immediately("AR")
   language_manager.notify_language_change()
   ```

🚀 QUICK START GUIDE
====================

To enable language switching in your POS:

1. ✅ Already Done: Language system is implemented
2. ✅ Already Done: Settings dialog is created
3. ✅ Already Done: POS integration is complete

To use language switching:

1. 🖱️ Click "🌐 PARAMÈTRES LANGUE" in POS sidebar
2. 🌍 Select your preferred language
3. ⚡ Click "Apply" for immediate change
4. 💾 Click "Save" to make it permanent
5. 🔄 Restart POS for full translation coverage

📋 TRANSLATION COVERAGE
=======================

Currently translated:
✅ Main UI elements (buttons, labels, titles)
✅ Receipt content (headers, totals, dates)
✅ Dialog messages (errors, success, warnings)
✅ Settings interface (all options)
✅ Payment dialogs
✅ Product management
✅ Cart operations

🎯 TIPS FOR BEST EXPERIENCE
===========================

1. Use "Apply" for testing languages quickly
2. Use "Save" when you've chosen your preferred language
3. Arabic automatically enables RTL mode
4. Font settings help with proper text rendering
5. Preview function shows how text will look

🔧 TROUBLESHOOTING
==================

If language doesn't change:
1. Check if you clicked "Apply" or "Save"
2. Try restarting the application
3. Check language_settings.json in config folder
4. Verify translation keys exist in language_settings.py

If Arabic text looks wrong:
1. Change to "Arial Unicode MS" font
2. Enable RTL mode in settings
3. Increase font size if needed

💡 ADVANCED FEATURES
===================

- Fallback system: Missing translations fall back to French
- Unicode support: Full Arabic and special character support
- Settings persistence: All preferences saved automatically
- Callback system: UI updates propagate through application
- Font customization: Per-language font settings

🌟 ENJOY YOUR MULTILINGUAL POS SYSTEM! 🌟
"""

def print_guide():
    """Print the language switching guide."""
    print(__doc__)

if __name__ == "__main__":
    print_guide()
