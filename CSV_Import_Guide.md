# CSV Product Import Guide

## Vue d'ensemble
Le système POS supporte maintenant l'importation et l'exportation de produits via des fichiers CSV. Cette fonctionnalité permet d'importer facilement des produits en lot depuis des fichiers de tableur ou d'autres systèmes.

## Accès à la fonctionnalité
1. Ouvrez le système POS
2. Cliquez sur "Inventaire" dans l'interface principale
3. Dans la fenêtre de gestion d'inventaire, vous trouverez au bas :
   - **📥 Importer CSV** : Pour importer des produits depuis un fichier CSV
   - **📤 Exporter CSV** : Pour exporter les produits actuels vers un fichier CSV

## Formats CSV supportés

### 1. Format WooCommerce
Le système détecte automatiquement les fichiers CSV exportés depuis WooCommerce basé sur les colonnes suivantes :
- `Nom` ou `Name` : Nom du produit
- `Tarif régulier` ou `Regular price` : Prix de vente
- `UGS` ou `SKU` : Code barre/référence produit
- `Catégories` ou `Categories` : Catégorie du produit
- `Stock` : Quantité en stock
- `Description` ou `Description courte` : Description du produit

### 2. Format générique
Pour un format CSV standard, utilisez ces colonnes :
- `name` : Nom du produit (obligatoire)
- `description` : Description du produit
- `price` : Prix de vente (obligatoire, doit être > 0)
- `barcode` : Code barre (optionnel)
- `category` : Catégorie (optionnel, "Uncategorized" par défaut)
- `stock` : Quantité en stock (optionnel, 0 par défaut)
- `cost_price` : Prix d'achat (optionnel, 0 par défaut)

## Processus d'importation

### Étape 1 : Sélection du fichier
1. Cliquez sur "📥 Importer CSV"
2. Utilisez "Parcourir..." pour sélectionner votre fichier CSV
3. Vous pouvez utiliser l'icône 🔤 pour taper le chemin avec le clavier virtuel

### Étape 2 : Options d'importation
- **Mettre à jour les produits existants** : Si coché, les produits existants (même nom ou code barre) seront mis à jour avec les nouvelles données

### Étape 3 : Aperçu
1. Cliquez sur "Aperçu" pour prévisualiser l'importation
2. Le système affiche :
   - Format détecté (WooCommerce ou générique)
   - Nombre de produits valides/invalides
   - Liste des erreurs éventuelles
3. Vérifiez les données dans le tableau de prévisualisation

### Étape 4 : Importation
1. Après vérification, cliquez sur "Importer"
2. Confirmez l'importation dans la boîte de dialogue
3. Le système affiche un rapport final avec le nombre de produits importés/mis à jour

## Validation des données

### Règles de validation
- **Nom du produit** : Obligatoire, maximum 255 caractères
- **Prix** : Obligatoire, doit être supérieur à 0
- **Code barre** : Optionnel, minimum 3 caractères alphanumériques
- **Stock** : Nombre entier positif
- **Prix d'achat** : Nombre positif

### Nettoyage automatique des données
- **Prix** : Suppression des symboles monétaires, gestion des séparateurs décimaux
- **Stock** : Extraction des chiffres uniquement
- **Code barre** : Accepte tous les formats de codes barres
  - ✅ **Codes numériques** : UPC/EAN (ex: `1234567890123`)
  - ✅ **Codes alphanumériques** : SKU, références (ex: `SKU-PROD-001`)
  - ✅ **Codes WooCommerce** : Avec caractères spéciaux (ex: `'-&&&é'é-_à-"à`)
  - ✅ **Codes vides** : Produits sans code barre acceptés

## Gestion des codes barres

### Codes barres acceptés
Le système accepte TOUS les formats de codes barres trouvés dans votre CSV :
- **Codes numériques** : UPC, EAN (ex: `1234567890123`)
- **Codes alphanumériques** : SKU, références internes (ex: `PROD-001`, `SKU-ABC-123`)
- **Codes WooCommerce** : Format avec caractères spéciaux (ex: `'-&&&é'é-_à-"à`)
- **Codes vides** : Les produits sans code barre sont acceptés

### Affichage dans l'aperçu
Dans l'aperçu d'importation :
- ✅ **Code accepté** : Tous les codes barres valides sont affichés avec une coche verte
- **Code vide** : Affiché sans icône (normal pour les produits sans code)

### Compatibilité WooCommerce
Votre export WooCommerce est entièrement compatible ! Tous les codes barres sont importés exactement comme ils apparaissent dans votre fichier CSV, y compris les formats spéciaux WooCommerce.

## Gestion des erreurs

### Erreurs communes
1. **"Could not find product name column"** : La colonne nom n'est pas reconnue
2. **"Price must be greater than 0"** : Prix invalide ou manquant
3. **"Product name is required"** : Nom de produit vide
4. **"Row X: Error processing"** : Erreur générale sur une ligne

### Solutions
- Vérifiez que votre CSV contient les colonnes requises
- Assurez-vous que les prix sont en format numérique
- Vérifiez l'encodage du fichier (UTF-8 recommandé)

## Exportation CSV

### Fonctionnalité d'export
- Exporte tous les produits actifs vers un fichier CSV
- Format standardisé compatible avec l'importation
- Inclut toutes les données produit (ID, nom, description, prix, etc.)

### Utilisation
1. Cliquez sur "📤 Exporter CSV"
2. Choisissez l'emplacement et le nom du fichier
3. Le fichier est généré avec horodatage automatique

## Exemples de fichiers CSV

### Exemple format générique
```csv
name,description,price,barcode,category,stock,cost_price
Produit Test 1,Description du produit test 1,25.50,1234567890123,Électronique,100,15.00
Produit Test 2,Description du produit test 2,18.75,9876543210987,Alimentaire,50,12.00
```

### Template disponible
Utilisez le bouton "Exporter Template" dans la boîte de dialogue d'importation pour générer un fichier CSV template avec des exemples de données.

## Conseils et bonnes pratiques

### Préparation des données
1. **Sauvegardez** votre base de données avant l'importation
2. **Testez** avec un petit échantillon d'abord
3. **Vérifiez** les prix et codes barres
4. **Utilisez** l'aperçu pour valider avant l'importation

### Performance
- Pour de gros volumes (>1000 produits), importez par petits lots
- Fermez les autres applications durant l'importation
- Surveillez les messages d'erreur

### Maintenance
- Exportez régulièrement vos produits pour sauvegarde
- Mettez à jour les stocks via CSV si nécessaire
- Utilisez des catégories cohérentes

## Support technique

En cas de problème :
1. Vérifiez les messages d'erreur affichés
2. Consultez ce guide pour les solutions communes
3. Testez avec le fichier sample_products.csv fourni
4. Assurez-vous que votre fichier CSV est bien formaté

La fonctionnalité d'import CSV rend la gestion des produits beaucoup plus efficace et permet une intégration facile avec d'autres systèmes de gestion.
