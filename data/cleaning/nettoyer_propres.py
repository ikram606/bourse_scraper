"""
SCRIPT 1 : NETTOYAGE DES DONNÉES PROPRES
Pipeline complet en 5 étapes
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("\n" + "="*70)
print("🧹 SCRIPT 1 : NETTOYAGE DES DONNÉES PROPRES")
print("="*70)

# Chemins
RAW_DIR = Path(r"C:\Users\pc\Desktop\bourse_scraper\data\raw")
PROCESSED_DIR = Path(r"C:\Users\pc\Desktop\bourse_scraper\data\processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Charger données brutes
input_file = RAW_DIR / "all_stocks_raw.csv"
print(f"\n📂 Input : {input_file}")

df = pd.read_csv(input_file)
print(f"✅ {len(df)} lignes chargées")
print(f"✅ Colonnes : {list(df.columns)}")
print(f"✅ Actions : {df['stock'].unique()}")

initial_rows = len(df)

# ============================================================
# ÉTAPE 1 : GESTION DES VALEURS MANQUANTES
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 1/5 : GESTION DES VALEURS MANQUANTES")
print("-"*70)

missing_before = df.isnull().sum().sum()
print(f"Valeurs manquantes avant : {missing_before}")

if missing_before > 0:
    # Interpolation pour les prix
    for col in ['open', 'high', 'low', 'close', 'adjusted_close']:
        if col in df.columns:
            df[col] = df.groupby('stock')[col].transform(
                lambda x: x.interpolate(method='linear')
            )
    
    # Médiane pour le volume
    if 'volume' in df.columns:
        df['volume'] = df.groupby('stock')['volume'].transform(
            lambda x: x.fillna(x.median())
        )
    
    missing_after = df.isnull().sum().sum()
    print(f"✅ Valeurs manquantes après : {missing_after}")
else:
    print("✅ Aucune valeur manquante")

# ============================================================
# ÉTAPE 2 : DÉTECTION ET TRAITEMENT DES OUTLIERS
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 2/5 : DÉTECTION DES OUTLIERS (IQR)")
print("-"*70)

outliers_detected = 0

for stock in df['stock'].unique():
    mask = df['stock'] == stock
    
    for col in ['close', 'volume']:
        if col in df.columns:
            Q1 = df.loc[mask, col].quantile(0.25)
            Q3 = df.loc[mask, col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df.loc[mask, col] < lower_bound
            outliers |= df.loc[mask, col] > upper_bound
            
            outliers_detected += outliers.sum()

print(f"Outliers IQR détectés : {outliers_detected}")
print("✅ Conservation des outliers (variations normales du marché)")

# ============================================================
# ÉTAPE 3 : VÉRIFICATION COHÉRENCE OHLC
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 3/5 : VÉRIFICATION COHÉRENCE OHLC")
print("-"*70)

# High doit être >= Open, Close, Low
invalid_high = (df['high'] < df['open']) | (df['high'] < df['close']) | (df['high'] < df['low'])

# Low doit être <= Open, Close, High
invalid_low = (df['low'] > df['open']) | (df['low'] > df['close']) | (df['low'] > df['high'])

# Prix négatifs
invalid_negative = (df['open'] < 0) | (df['high'] < 0) | (df['low'] < 0) | (df['close'] < 0)

# Volume négatif
invalid_volume = df['volume'] < 0

total_invalid = (invalid_high | invalid_low | invalid_negative | invalid_volume).sum()

print(f"Lignes incohérentes : {total_invalid}")

if total_invalid > 0:
    df = df[~(invalid_high | invalid_low | invalid_negative | invalid_volume)]
    print(f"✅ {total_invalid} lignes supprimées")
else:
    print("✅ Toutes les lignes sont cohérentes")

# ============================================================
# ÉTAPE 4 : CORRECTION DES TYPES DE DONNÉES
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 4/5 : CORRECTION DES TYPES")
print("-"*70)

# Convertir date
df['date'] = pd.to_datetime(df['date'])
print("✅ Date convertie en datetime")

# S'assurer que les prix sont float
for col in ['open', 'high', 'low', 'close', 'adjusted_close']:
    if col in df.columns:
        df[col] = df[col].astype(float)
print("✅ Prix convertis en float")

# Volume en int
df['volume'] = df['volume'].astype(int)
print("✅ Volume converti en int")

# Stock en catégorie
df['stock'] = df['stock'].astype('category')
print("✅ Stock converti en catégorie")

# ============================================================
# ÉTAPE 5 : SUPPRESSION DES DOUBLONS
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 5/5 : SUPPRESSION DES DOUBLONS")
print("-"*70)

duplicates_before = df.duplicated(subset=['date', 'stock']).sum()
print(f"Doublons (date + stock) : {duplicates_before}")

if duplicates_before > 0:
    df = df.drop_duplicates(subset=['date', 'stock'], keep='first')
    print(f"✅ {duplicates_before} doublons supprimés")
else:
    print("✅ Aucun doublon")

# ============================================================
# SAUVEGARDER
# ============================================================

# Trier
df = df.sort_values(['stock', 'date']).reset_index(drop=True)

output_file = PROCESSED_DIR / "all_stocks_cleaned.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\n" + "="*70)
print("✅ NETTOYAGE TERMINÉ")
print("="*70)

final_rows = len(df)
removed = initial_rows - final_rows

print(f"\n📊 RÉSUMÉ :")
print(f"   Lignes initiales : {initial_rows}")
print(f"   Lignes finales   : {final_rows}")
print(f"   Lignes supprimées: {removed} ({removed/initial_rows*100:.1f}%)")

print(f"\n📈 Distribution par action :")
for stock, count in df['stock'].value_counts().sort_index().items():
    print(f"   {stock}: {count} lignes")

print(f"\n💾 Output : {output_file}")
print(f"\n🎯 Prochaine étape : Script 2 - Calcul des features\n")