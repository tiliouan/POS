# Additional launcher for Windows PowerShell
param(
    [switch]$Test
)

Write-Host "Point of Sale System - Démarrage..." -ForegroundColor Green
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python détecté: $pythonVersion" -ForegroundColor Blue
} catch {
    Write-Host "Erreur: Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Veuillez installer Python 3.8 ou plus récent" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour continuer"
    exit 1
}

# Change to script directory
Set-Location -Path $PSScriptRoot

if ($Test) {
    Write-Host "Mode test - Vérification des composants..." -ForegroundColor Yellow
    
    # Test database
    python -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); print(f'Base de données: {len(db.get_all_products())} produits trouvés')"
    
    # Test imports
    python -c "from pos_system import POSApplication; print('Tous les modules importés avec succès')"
    
    Write-Host "Test terminé avec succès!" -ForegroundColor Green
} else {
    Write-Host "Lancement du système de caisse..." -ForegroundColor Blue
    python main.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Une erreur est survenue lors du lancement" -ForegroundColor Red
        Read-Host "Appuyez sur Entrée pour continuer"
    }
}
