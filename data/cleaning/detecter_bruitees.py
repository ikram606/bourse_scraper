"""
SCRIPT 7 : DÉTECTION ANOMALIES - SEUIL AUTOMATIQUE
Utilise les scores SANS forcer 5%
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

print("\n" + "="*70)
print("🔍 SCRIPT 7 : DÉTECTION ANOMALIES - SEUIL AUTOMATIQUE")
print("="*70)

# Chemins
PROCESSED_DIR = r"C:\Users\pc\Desktop\bourse_scraper\data\processed"

# Charger données avec features
input_file = f"{PROCESSED_DIR}/all_stocks_bruitees_features.csv"
print(f"\n📂 Input : {input_file}")

df = pd.read_csv(input_file)
print(f"✅ {len(df)} lignes chargées")

# ============================================================
# SÉLECTION DES FEATURES
# ============================================================

print("\n" + "-"*70)
print("📊 SÉLECTION DES FEATURES")
print("-"*70)

features_to_use = [
    'Returns',
    'Log_Returns',
    'Volatility_30',
    'High_Low_Spread',
    'RSI_14',
    'BB_Width',
    'MACD_Hist',
    'Volume_Ratio'
]

print(f"\nFeatures utilisées ({len(features_to_use)}) :")
for f in features_to_use:
    print(f"   ✓ {f}")

df_features = df[features_to_use].copy()

nan_count = df_features.isnull().sum().sum()
if nan_count > 0:
    print(f"\n⚠️  {nan_count} NaN détectés, suppression...")
    df_features = df_features.dropna()
    df = df.loc[df_features.index]
    print(f"✅ Lignes restantes : {len(df)}")

# ============================================================
# ISOLATION FOREST - SEUIL AUTOMATIQUE
# ============================================================

print("\n" + "="*70)
print("🌳 ISOLATION FOREST - SEUIL AUTOMATIQUE")
print("="*70)

print("\n⚙️ Configuration :")
print("   • contamination = 'auto' (seuil automatique)")
print("   • n_estimators = 100")
print("   • random_state = 42")

# Modèle SANS contamination fixe
iso_forest = IsolationForest(
    contamination='auto',  # ← Seuil automatique !
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

print("\n⏳ Entraînement du modèle...")
predictions = iso_forest.fit_predict(df_features)

# Scores
anomaly_scores = iso_forest.decision_function(df_features)
df['IF_Score'] = anomaly_scores

# Seuil automatique : percentile 10 (plus permissif)
threshold = np.percentile(anomaly_scores, 10)
df['IF_Anomaly'] = (anomaly_scores < threshold)

# ============================================================
# RÉSULTATS
# ============================================================

print("\n" + "="*70)
print("📊 RÉSULTATS - DONNÉES BRUITÉES-NETTOYÉES")
print("="*70)

total_anomalies = df['IF_Anomaly'].sum()
percentage = (total_anomalies / len(df)) * 100

print(f"\n✅ Anomalies détectées : {total_anomalies} / {len(df)} ({percentage:.2f}%)")
print(f"   Seuil utilisé : {threshold:.4f}")

# Répartition par action
print("\n📈 Répartition par action :")
anomaly_by_stock = df.groupby('stock')['IF_Anomaly'].agg(['sum', 'count'])
anomaly_by_stock['percentage'] = (anomaly_by_stock['sum'] / anomaly_by_stock['count'] * 100)
anomaly_by_stock = anomaly_by_stock.sort_values('sum', ascending=False)

for stock, row in anomaly_by_stock.iterrows():
    print(f"   {stock:10} : {int(row['sum']):3} anomalies ({row['percentage']:5.2f}%) sur {int(row['count'])} lignes")

# Top 10 anomalies
print("\n🔥 Top 10 anomalies les plus sévères :")
top_anomalies = df[df['IF_Anomaly']].nsmallest(10, 'IF_Score')
print("\n   Date       | Stock   | Close    | Volume   | Score")
print("   " + "-"*60)
for _, row in top_anomalies.iterrows():
    print(f"   {row['date'][:10]} | {row['stock']:7} | {row['close']:7.2f} | {int(row['volume']):8} | {row['IF_Score']:.4f}")

# Statistiques
print("\n📊 Distribution des scores :")
print(f"   Min (plus anormal) : {df['IF_Score'].min():.4f}")
print(f"   Seuil détection    : {threshold:.4f}")
print(f"   Moyenne            : {df['IF_Score'].mean():.4f}")
print(f"   Max (plus normal)  : {df['IF_Score'].max():.4f}")

# ============================================================
# SAUVEGARDER
# ============================================================

output_file = f"{PROCESSED_DIR}/resultats_bruitees.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n💾 Résultats sauvegardés : {output_file}")

# Rapport
report_lines = []
report_lines.append("="*70)
report_lines.append("RAPPORT - DÉTECTION ANOMALIES (SEUIL AUTOMATIQUE)")
report_lines.append("="*70)
report_lines.append(f"\nAlgorithme : Isolation Forest (contamination=auto)")
report_lines.append(f"Seuil : {threshold:.4f} (percentile 10)")
report_lines.append(f"\nRÉSULTATS :")
report_lines.append(f"  Total lignes : {len(df)}")
report_lines.append(f"  Anomalies : {total_anomalies} ({percentage:.2f}%)")
report_lines.append(f"\nPAR ACTION :")
for stock, row in anomaly_by_stock.iterrows():
    report_lines.append(f"  {stock} : {int(row['sum'])} anomalies ({row['percentage']:.2f}%)")

report_text = "\n".join(report_lines)
report_file = f"{PROCESSED_DIR}/rapport_bruitees.txt"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"📄 Rapport sauvegardé : {report_file}")

print("\n" + "="*70)
print("✅ BRANCHE 2 TERMINÉE")
print("="*70)
print(f"\n🎯 Anomalies détectées : {total_anomalies} ({percentage:.2f}%)")
print(f"🎯 Prochaine étape : Comparaison avec propres (61 anomalies)\n")