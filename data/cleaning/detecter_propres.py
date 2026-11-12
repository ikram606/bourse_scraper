"""
SCRIPT 3 : DÉTECTION ANOMALIES - DONNÉES PROPRES
Isolation Forest sur all_stocks_features_propres.csv
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

print("\n" + "="*70)
print("🔍 SCRIPT 3 : DÉTECTION ANOMALIES - DONNÉES PROPRES")
print("="*70)

# Chemins
PROCESSED_DIR = r"C:\Users\pc\Desktop\bourse_scraper\data\processed"

# Charger données avec features
input_file = f"{PROCESSED_DIR}/all_stocks_features_propres.csv"
print(f"\n📂 Input : {input_file}")

df = pd.read_csv(input_file)
print(f"✅ {len(df)} lignes chargées")
print(f"✅ {len(df.columns)} colonnes")

# ============================================================
# SÉLECTION DES FEATURES POUR LA DÉTECTION
# ============================================================

print("\n" + "-"*70)
print("📊 SÉLECTION DES FEATURES")
print("-"*70)

# Features pour Isolation Forest
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

# Vérifier que toutes les features existent
missing = [f for f in features_to_use if f not in df.columns]
if missing:
    print(f"\n❌ Features manquantes : {missing}")
    print("Colonnes disponibles :", df.columns.tolist())
    exit()

# Extraire les features
df_features = df[features_to_use].copy()

# Vérifier NaN
nan_count = df_features.isnull().sum().sum()
if nan_count > 0:
    print(f"\n⚠️  {nan_count} NaN détectés, suppression...")
    df_features = df_features.dropna()
    df = df.loc[df_features.index]
    print(f"✅ Lignes restantes : {len(df)}")

# ============================================================
# ISOLATION FOREST
# ============================================================

print("\n" + "="*70)
print("🌳 ISOLATION FOREST")
print("="*70)

print("\n⚙️ Configuration :")
print("   • contamination = 0.05 (5% d'anomalies attendues)")
print("   • n_estimators = 100 (arbres)")
print("   • random_state = 42 (reproductibilité)")

# Créer et entraîner le modèle
iso_forest = IsolationForest(
    contamination=0.05,
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

print("\n⏳ Entraînement du modèle...")
predictions = iso_forest.fit_predict(df_features)

# -1 = anomalie, 1 = normal
df['IF_Anomaly'] = (predictions == -1)

# Scores d'anomalie (plus négatif = plus anormal)
anomaly_scores = iso_forest.decision_function(df_features)
df['IF_Score'] = anomaly_scores

# ============================================================
# RÉSULTATS
# ============================================================

print("\n" + "="*70)
print("📊 RÉSULTATS - DONNÉES PROPRES")
print("="*70)

total_anomalies = df['IF_Anomaly'].sum()
percentage = (total_anomalies / len(df)) * 100

print(f"\n✅ Anomalies détectées : {total_anomalies} / {len(df)} ({percentage:.2f}%)")

# Répartition par action
print("\n📈 Répartition par action :")
anomaly_by_stock = df.groupby('stock')['IF_Anomaly'].agg(['sum', 'count'])
anomaly_by_stock['percentage'] = (anomaly_by_stock['sum'] / anomaly_by_stock['count'] * 100)
anomaly_by_stock = anomaly_by_stock.sort_values('sum', ascending=False)

for stock, row in anomaly_by_stock.iterrows():
    print(f"   {stock:10} : {int(row['sum']):3} anomalies ({row['percentage']:5.2f}%) sur {int(row['count'])} lignes")

# Top 10 anomalies les plus sévères
print("\n🔥 Top 10 anomalies les plus sévères :")
top_anomalies = df[df['IF_Anomaly']].nsmallest(10, 'IF_Score')
print("\n   Date       | Stock   | Close    | Volume   | Score")
print("   " + "-"*60)
for _, row in top_anomalies.iterrows():
    print(f"   {row['date'][:10]} | {row['stock']:7} | {row['close']:7.2f} | {int(row['volume']):8} | {row['IF_Score']:.4f}")

# Statistiques des scores
print("\n📊 Distribution des scores d'anomalie :")
print(f"   Min (plus anormal) : {df['IF_Score'].min():.4f}")
print(f"   Max (plus normal)  : {df['IF_Score'].max():.4f}")
print(f"   Moyenne            : {df['IF_Score'].mean():.4f}")
print(f"   Médiane            : {df['IF_Score'].median():.4f}")

# ============================================================
# SAUVEGARDER
# ============================================================

output_file = f"{PROCESSED_DIR}/resultats_propres.csv"
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n💾 Résultats sauvegardés : {output_file}")

# ============================================================
# RAPPORT
# ============================================================

report_lines = []
report_lines.append("="*70)
report_lines.append("RAPPORT - DÉTECTION ANOMALIES SUR DONNÉES PROPRES")
report_lines.append("="*70)
report_lines.append(f"\nAlgorithme : Isolation Forest")
report_lines.append(f"Contamination : 5%")
report_lines.append(f"Features utilisées : {len(features_to_use)}")
report_lines.append(f"\nRÉSULTATS :")
report_lines.append(f"  Total lignes : {len(df)}")
report_lines.append(f"  Anomalies détectées : {total_anomalies} ({percentage:.2f}%)")
report_lines.append(f"\nPAR ACTION :")

for stock, row in anomaly_by_stock.iterrows():
    report_lines.append(f"  {stock} : {int(row['sum'])} anomalies ({row['percentage']:.2f}%)")

report_lines.append(f"\nAction la plus volatile : {anomaly_by_stock.index[0]} ({int(anomaly_by_stock.iloc[0]['sum'])} anomalies)")
report_lines.append("")

report_text = "\n".join(report_lines)
report_file = f"{PROCESSED_DIR}/rapport_propres.txt"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"📄 Rapport sauvegardé : {report_file}")

# ============================================================
# RÉSUMÉ FINAL
# ============================================================

print("\n" + "="*70)
print("✅ BRANCHE 1 TERMINÉE : DONNÉES PROPRES")
print("="*70)

print(f"\n📊 Fichiers créés :")
print(f"   ✓ all_stocks_cleaned.csv")
print(f"   ✓ all_stocks_features_propres.csv")
print(f"   ✓ resultats_propres.csv")
print(f"   ✓ rapport_propres.txt")

print(f"\n🎯 PROCHAINE ÉTAPE : BRANCHE 2 - Données bruitées")
print(f"   Script 4 : Bruitage des données")
print("\n")