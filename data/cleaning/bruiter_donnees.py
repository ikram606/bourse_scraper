"""
SCRIPT 4 INTELLIGENT : BRUITAGE SANS RÉDUCTION DE LIGNES
Stratégie : Déformer les valeurs pour créer des anomalies détectables
SANS supprimer de lignes au nettoyage
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("\n" + "="*70)
print("🎯 SCRIPT 4 INTELLIGENT : BRUITAGE CIBLÉ")
print("="*70)

# Chemins
RAW_DIR = Path(r"C:\Users\pc\Desktop\bourse_scraper\data\raw")
PROCESSED_DIR = Path(r"C:\Users\pc\Desktop\bourse_scraper\data\processed")

# Charger données brutes
input_file = RAW_DIR / "all_stocks_raw.csv"
print(f"\n📂 Input : {input_file}")

df = pd.read_csv(input_file)
print(f"✅ {len(df)} lignes chargées")

initial_rows = len(df)

# Seed
np.random.seed(42)

print("\n" + "="*70)
print("🎯 BRUITAGE INTELLIGENT ACTIVÉ")
print("   → Déformation SANS suppression de lignes")
print("="*70)

# ============================================================
# 1. OUTLIERS SUBTILS (30% des lignes)
# ============================================================

print("\n" + "-"*70)
print("1️⃣ OUTLIERS SUBTILS (30%)")
print("-"*70)

n_outliers = int(len(df) * 0.30)
print(f"Cible : {n_outliers} lignes avec outliers subtils")

# Sélectionner 30% des lignes
indices = np.random.choice(df.index, size=n_outliers, replace=False)

for idx in indices:
    # Choisir aléatoirement 1-3 colonnes à modifier
    cols_to_modify = np.random.choice(['close', 'volume', 'high', 'low'], 
                                      size=np.random.randint(1, 4), 
                                      replace=False)
    
    for col in cols_to_modify:
        if not pd.isna(df.loc[idx, col]):
            # Facteur subtil mais détectable : ×0.6 à ×1.6
            factor = np.random.choice([0.6, 0.7, 0.8, 1.3, 1.4, 1.6])
            df.loc[idx, col] = df.loc[idx, col] * factor

print(f"✅ {n_outliers} lignes modifiées avec outliers subtils")
print(f"   → Conservées au nettoyage")

# ============================================================
# 2. DÉFORMATION DE VOLATILITÉ (40% des lignes)
# ============================================================

print("\n" + "-"*70)
print("2️⃣ DÉFORMATION DE VOLATILITÉ (40%)")
print("-"*70)

n_volatility = int(len(df) * 0.40)
print(f"Cible : {n_volatility} lignes")

indices = np.random.choice(df.index, size=n_volatility, replace=False)

for idx in indices:
    if not any(pd.isna(df.loc[idx, ['open', 'high', 'low', 'close']])):
        # Augmenter artificiellement le spread High-Low
        current_close = df.loc[idx, 'close']
        spread_factor = np.random.uniform(1.5, 2.5)
        
        df.loc[idx, 'high'] = current_close * (1 + 0.05 * spread_factor)
        df.loc[idx, 'low'] = current_close * (1 - 0.05 * spread_factor)

print(f"✅ {n_volatility} lignes avec volatilité augmentée")
print(f"   → Affectera RSI, Bollinger, etc.")

# ============================================================
# 3. ANOMALIES DE VOLUME (35% des lignes)
# ============================================================

print("\n" + "-"*70)
print("3️⃣ ANOMALIES DE VOLUME (35%)")
print("-"*70)

n_volume = int(len(df) * 0.35)
print(f"Cible : {n_volume} lignes")

indices = np.random.choice(df.index, size=n_volume, replace=False)

for idx in indices:
    if not pd.isna(df.loc[idx, 'volume']):
        # Volumes anormaux mais pas extrêmes
        factor = np.random.choice([0.3, 0.4, 2.5, 3.0])
        df.loc[idx, 'volume'] = int(df.loc[idx, 'volume'] * factor)

print(f"✅ {n_volume} lignes avec volumes anormaux")
print(f"   → Affectera Volume_Ratio, OBV")

# ============================================================
# 4. BRUIT GAUSSIEN CIBLÉ (100% des lignes)
# ============================================================

print("\n" + "-"*70)
print("4️⃣ BRUIT GAUSSIEN CIBLÉ (σ=15% sur TOUT)")
print("-"*70)

# Bruit sur TOUTES les valeurs
for col in ['open', 'high', 'low', 'close', 'adjusted_close']:
    mask = ~df[col].isna()
    noise = np.random.normal(0, 0.15, size=mask.sum())
    df.loc[mask, col] = df.loc[mask, col] * (1 + noise)
    df.loc[mask, col] = df.loc[mask, col].clip(lower=0.01)

# Volume
mask = ~df['volume'].isna()
noise = np.random.normal(0, 0.15, size=mask.sum())
df.loc[mask, 'volume'] = df.loc[mask, 'volume'] * (1 + noise)
df.loc[mask, 'volume'] = df.loc[mask, 'volume'].clip(lower=1).astype(int)

print(f"✅ Bruit gaussien (σ=15%) sur toutes les lignes")
print(f"   → Affectera Returns, Log_Returns, Volatility")

# ============================================================
# 5. SPIKES DE PRIX (25% des actions par groupe)
# ============================================================

print("\n" + "-"*70)
print("5️⃣ SPIKES DE PRIX (25% par action)")
print("-"*70)

spikes_total = 0
for stock in df['stock'].unique():
    stock_mask = df['stock'] == stock
    stock_indices = df[stock_mask].index
    
    n_spikes = int(len(stock_indices) * 0.25)
    spike_indices = np.random.choice(stock_indices, size=n_spikes, replace=False)
    
    for idx in spike_indices:
        # Spike brutal : ±20-40%
        spike = np.random.choice([-0.40, -0.30, -0.20, 0.20, 0.30, 0.40])
        
        for col in ['open', 'close', 'high', 'low']:
            if not pd.isna(df.loc[idx, col]):
                df.loc[idx, col] = df.loc[idx, col] * (1 + spike)
        
        spikes_total += 1

print(f"✅ {spikes_total} spikes de prix créés")
print(f"   → Affectera MACD, EMA, SMA")

# ============================================================
# 6. PAS DE DOUBLONS (pour garder les lignes)
# ============================================================

print("\n" + "-"*70)
print("6️⃣ AUCUN DOUBLON AJOUTÉ")
print("-"*70)
print(f"✅ Stratégie : Conserver toutes les lignes")
print(f"   → Pas de perte au nettoyage")

# ============================================================
# SAUVEGARDER
# ============================================================

output_file = PROCESSED_DIR / "all_stocks_bruitees.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print("\n" + "="*70)
print("✅ BRUITAGE INTELLIGENT TERMINÉ")
print("="*70)

print(f"\n📊 RÉSUMÉ :")
print(f"   Lignes initiales     : {initial_rows}")
print(f"   Lignes finales       : {len(df)}")
print(f"   ⚠️  AUCUNE ligne supprimée")
print(f"")
print(f"   Outliers subtils     : 30% des lignes")
print(f"   Volatilité augmentée : 40% des lignes")
print(f"   Volume anormal       : 35% des lignes")
print(f"   Bruit gaussien       : 100% (σ=15%)")
print(f"   Spikes de prix       : 25% par action")
print(f"")
print(f"✅ STRATÉGIE : Déformation maximale, suppression minimale")

print(f"\n💾 Output : {output_file}")
print(f"\n🎯 Attendu au nettoyage : ~{len(df)} lignes conservées")
print(f"🎯 Attendu détection : 150-250 anomalies (vs 61 propres)\n")