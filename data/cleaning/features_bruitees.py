"""
SCRIPT 6 : CALCUL FEATURES - DONNÉES BRUITÉES-NETTOYÉES
Ton code adapté pour all_stocks_bruitees_cleaned.csv
"""

import numpy as np
import pandas as pd

print("\n" + "="*70)
print("📈 SCRIPT 6 : CALCUL FEATURES - DONNÉES BRUITÉES-NETTOYÉES")
print("="*70)

# Charger données bruitées NETTOYÉES
input_file = 'data/processed/all_stocks_bruitees_cleaned.csv'
print(f"\n📂 Input: {input_file}")

df = pd.read_csv(input_file)

# Conversion numérique explicite
numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'adjusted_close']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['stock', 'date'])

print(f"✅ {len(df)} lignes chargées")

# GroupBy
g = df.groupby('stock')

# ===== GROUPE 1 : MOYENNES MOBILES =====
print("\n1️⃣ Moyennes mobiles...")
df['SMA_7']  = g['adjusted_close'].transform(lambda x: x.rolling(window=7).mean())
df['SMA_30'] = g['adjusted_close'].transform(lambda x: x.rolling(window=30).mean())
df['SMA_90'] = g['adjusted_close'].transform(lambda x: x.rolling(window=90).mean())
df['EMA_12'] = g['adjusted_close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
df['EMA_26'] = g['adjusted_close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())

# ===== GROUPE 2 : RSI =====
print("2️⃣ RSI...")
def compute_rsi(x, period=14):
    delta = x.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df['RSI_14'] = g['adjusted_close'].transform(lambda x: compute_rsi(x, period=14))

# ===== GROUPE 3 : BOLLINGER BANDS =====
print("3️⃣ Bollinger Bands...")
df['BB_Middle'] = g['adjusted_close'].transform(lambda x: x.rolling(window=20).mean())
std_20 = g['adjusted_close'].transform(lambda x: x.rolling(window=20).std())
df['BB_Upper'] = df['BB_Middle'] + (2 * std_20)
df['BB_Lower'] = df['BB_Middle'] - (2 * std_20)
df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']

# ===== GROUPE 4 : MACD =====
print("4️⃣ MACD...")
df['MACD'] = df['EMA_12'] - df['EMA_26']
df['MACD_Signal'] = df.groupby('stock')['MACD'].transform(lambda x: x.ewm(span=9, adjust=False).mean())
df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

# ===== GROUPE 5 : VOLUME =====
print("5️⃣ Indicateurs volume...")
df['Volume_MA_20'] = g['volume'].transform(lambda x: x.rolling(window=20).mean())
df['Volume_Ratio'] = df['volume'] / df['Volume_MA_20']

def compute_obv(group):
    direction = np.sign(group['adjusted_close'].diff().fillna(0))
    return (direction * group['volume']).cumsum()

df['OBV'] = g.apply(compute_obv, include_groups=False).reset_index(level=0, drop=True)

# ===== GROUPE 6 : FEATURES DÉRIVÉES =====
print("6️⃣ Features dérivées...")
df['Returns'] = g['adjusted_close'].transform(lambda x: x.pct_change())
df['Log_Returns'] = g['adjusted_close'].transform(lambda x: np.log(x / x.shift(1)))
df['Volatility_30'] = g['Returns'].transform(lambda x: x.rolling(window=30).std())
df['High_Low_Spread'] = (df['high'] - df['low']) / df['adjusted_close']

# Supprimer NaN
print("\n🧹 Suppression NaN...")
avant = len(df)
df = df.dropna()
apres = len(df)
print(f"✅ {avant} → {apres} lignes ({avant-apres} supprimées)")

# Sauvegarder
output_path = 'data/processed/all_stocks_bruitees_features.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"\n💾 Fichier enregistré : {output_path}")
print(f"📊 {len(df)} lignes | {len(df.columns)} colonnes")

print("\n" + "="*70)
print("✅ TERMINÉ")
print("="*70)
print("\n🎯 Prochaine étape: Script 7 - Détection anomalies sur bruitées\n")