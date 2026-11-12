import numpy as np
import pandas as pd

# Charger données PROPRES nettoyées
df = pd.read_csv('data/processed/all_stocks_cleaned.csv')

# Conversion numérique
numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'adjusted_close']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['stock', 'date'])

g = df.groupby('stock')

# MOYENNES MOBILES
df['SMA_7']  = g['adjusted_close'].transform(lambda x: x.rolling(window=7).mean())
df['SMA_30'] = g['adjusted_close'].transform(lambda x: x.rolling(window=30).mean())
df['SMA_90'] = g['adjusted_close'].transform(lambda x: x.rolling(window=90).mean())
df['EMA_12'] = g['adjusted_close'].transform(lambda x: x.ewm(span=12, adjust=False).mean())
df['EMA_26'] = g['adjusted_close'].transform(lambda x: x.ewm(span=26, adjust=False).mean())

# RSI
def compute_rsi(x, period=14):
    delta = x.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

df['RSI_14'] = g['adjusted_close'].transform(lambda x: compute_rsi(x, period=14))

# BOLLINGER BANDS
df['BB_Middle'] = g['adjusted_close'].transform(lambda x: x.rolling(window=20).mean())
std_20 = g['adjusted_close'].transform(lambda x: x.rolling(window=20).std())
df['BB_Upper'] = df['BB_Middle'] + (2 * std_20)
df['BB_Lower'] = df['BB_Middle'] - (2 * std_20)
df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']

# MACD
df['MACD'] = df['EMA_12'] - df['EMA_26']
df['MACD_Signal'] = df.groupby('stock')['MACD'].transform(lambda x: x.ewm(span=9, adjust=False).mean())
df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

# VOLUME
df['Volume_MA_20'] = g['volume'].transform(lambda x: x.rolling(window=20).mean())
df['Volume_Ratio'] = df['volume'] / df['Volume_MA_20']

def compute_obv(group):
    direction = np.sign(group['adjusted_close'].diff().fillna(0))
    return (direction * group['volume']).cumsum()

df['OBV'] = g.apply(compute_obv, include_groups=False).reset_index(level=0, drop=True)

# FEATURES DÉRIVÉES
df['Returns'] = g['adjusted_close'].transform(lambda x: x.pct_change())
df['Log_Returns'] = g['adjusted_close'].transform(lambda x: np.log(x / x.shift(1)))
df['Volatility_30'] = g['Returns'].transform(lambda x: x.rolling(window=30).std())
df['High_Low_Spread'] = (df['high'] - df['low']) / df['adjusted_close']

# Supprimer NaN
df = df.dropna()
print(f"Lignes restantes : {len(df)}")

# Sauvegarder
output_path = 'data/processed/all_stocks_features_propres.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"✅ Fichier enregistré : {output_path}")