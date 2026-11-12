"""
SCRIPT 5 MINIMAL : NETTOYAGE MINIMAL
Ne fait que le STRICT minimum pour que les features se calculent
CONSERVE au maximum les données bruitées
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("\n" + "="*70)
print("🔧 SCRIPT 5 MINIMAL : NETTOYAGE MINIMAL")
print("="*70)

# Chemins
PROCESSED_DIR = Path(r"C:\Users\pc\Desktop\bourse_scraper\data\processed")

# Charger données bruitées
input_file = PROCESSED_DIR / "all_stocks_bruitees.csv"
print(f"\n📂 Input : {input_file}")

df = pd.read_csv(input_file)
print(f"✅ {len(df)} lignes chargées")

initial_rows = len(df)

# ============================================================
# ÉTAPE 1 : VALEURS MANQUANTES (INTERPOLATION SIMPLE)
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 1/3 : INTERPOLATION DES NaN")
print("-"*70)

missing_before = df.isnull().sum().sum()
print(f"NaN avant : {missing_before}")

# Interpolation linéaire simple
for col in ['open', 'high', 'low', 'close', 'adjusted_close', 'volume']:
    if col in df.columns:
        df[col] = df.groupby('stock')[col].transform(
            lambda x: x.interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
        )

missing_after = df.isnull().sum().sum()
print(f"NaN après : {missing_after}")
print(f"✅ {missing_before - missing_after} NaN traités par interpolation")

# ============================================================
# ÉTAPE 2 : CORRECTION MINIMALE DES TYPES
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 2/3 : CORRECTION DES TYPES (MINIMAL)")
print("-"*70)

# Convertir en numérique (mais GARDER les valeurs même étranges)
df['date'] = pd.to_datetime(df['date'], errors='coerce')

for col in ['open', 'high', 'low', 'close', 'adjusted_close', 'volume']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Remplacer négatifs par valeur absolue (ne PAS supprimer !)
for col in ['open', 'high', 'low', 'close', 'adjusted_close']:
    mask = df[col] < 0
    if mask.sum() > 0:
        df.loc[mask, col] = df.loc[mask, col].abs()
        print(f"   {col} : {mask.sum()} négatifs → abs()")

mask_vol = df['volume'] < 0
if mask_vol.sum() > 0:
    df.loc[mask_vol, 'volume'] = df.loc[mask_vol, 'volume'].abs()
    print(f"   volume : {mask_vol.sum()} négatifs → abs()")

df['volume'] = df['volume'].astype(int)
df['stock'] = df['stock'].astype('category')

print("✅ Types corrigés sans suppression")

# ============================================================
# ÉTAPE 3 : DOUBLONS SEULEMENT
# ============================================================

print("\n" + "-"*70)
print("ÉTAPE 3/3 : SUPPRESSION DOUBLONS UNIQUEMENT")
print("-"*70)

duplicates = df.duplicated(subset=['date', 'stock']).sum()
print(f"Doublons détectés : {duplicates}")

if duplicates > 0:
    df = df.drop_duplicates(subset=['date', 'stock'], keep='first')
    print(f"✅ {duplicates} doublons supprimés")

# ============================================================
# FINALISATION
# ============================================================

# Supprimer SEULEMENT les lignes avec NaN résiduels
df = df.dropna()

# Trier
df = df.sort_values(['stock', 'date']).reset_index(drop=True)

output_file = PROCESSED_DIR / "all_stocks_bruitees_cleaned.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\n" + "="*70)
print("✅ NETTOYAGE MINIMAL TERMINÉ")
print("="*70)

final_rows = len(df)
removed = initial_rows - final_rows

print(f"\n📊 RÉSUMÉ :")
print(f"   Lignes initiales  : {initial_rows}")
print(f"   Lignes finales    : {final_rows}")
print(f"   Lignes supprimées : {removed} ({removed/initial_rows*100:.1f}%)")
print(f"")
print(f"✅ CONSERVATION MAXIMALE :")
print(f"   • Outliers conservés")
print(f"   • Incohérences OHLC conservées")
print(f"   • Valeurs étranges conservées")
print(f"   → Toutes ces anomalies seront DÉTECTÉES !")

print(f"\n📈 Distribution par action :")
for stock, count in df['stock'].value_counts().sort_index().items():
    print(f"   {stock}: {count} lignes")

print(f"\n💾 Output : {output_file}")
print(f"\n🎯 Prochaine étape : Calcul features\n")