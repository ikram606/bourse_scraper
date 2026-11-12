"""
SCRIPT 8 : COMPARAISON FINALE
Compare les anomalies détectées : propres vs bruitées
Génère 4 GRAPHIQUES SÉPARÉS et rapport détaillé
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

print("\n" + "="*70)
print("📊 SCRIPT 8 : COMPARAISON FINALE")
print("="*70)

# Configuration
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Chemins
PROCESSED_DIR = Path(r"C:\Users\pc\Desktop\bourse_scraper\data\processed")

# ============================================================
# CHARGER LES RÉSULTATS
# ============================================================

print("\n📂 Chargement des résultats...")

# Résultats propres
propres_file = PROCESSED_DIR / "resultats_propres.csv"
df_propres = pd.read_csv(propres_file)
print(f"✅ Propres : {len(df_propres)} lignes")

# Résultats bruitées
bruitees_file = PROCESSED_DIR / "resultats_bruitees.csv"
df_bruitees = pd.read_csv(bruitees_file)
print(f"✅ Bruitées : {len(df_bruitees)} lignes")

# ============================================================
# STATISTIQUES GLOBALES
# ============================================================

print("\n" + "="*70)
print("📊 STATISTIQUES GLOBALES")
print("="*70)

# Anomalies
anom_propres = df_propres['IF_Anomaly'].sum()
pct_propres = (anom_propres / len(df_propres)) * 100

anom_bruitees = df_bruitees['IF_Anomaly'].sum()
pct_bruitees = (anom_bruitees / len(df_bruitees)) * 100

diff_anom = anom_bruitees - anom_propres
diff_pct = pct_bruitees - pct_propres

print(f"\nDONNÉES PROPRES :")
print(f"   Total lignes  : {len(df_propres)}")
print(f"   Anomalies     : {anom_propres} ({pct_propres:.2f}%)")
print(f"   Score moyen   : {df_propres['IF_Score'].mean():.4f}")

print(f"\nDONNÉES BRUITÉES-NETTOYÉES :")
print(f"   Total lignes  : {len(df_bruitees)}")
print(f"   Anomalies     : {anom_bruitees} ({pct_bruitees:.2f}%)")
print(f"   Score moyen   : {df_bruitees['IF_Score'].mean():.4f}")

print(f"\n🔥 DIFFÉRENCE :")
print(f"   Anomalies     : +{diff_anom} ({diff_pct:+.2f}%)")
print(f"   Impact relatif: +{(diff_anom/anom_propres)*100:.1f}%")

# ============================================================
# COMPARAISON PAR ACTION
# ============================================================

print("\n" + "="*70)
print("📈 COMPARAISON PAR ACTION")
print("="*70)

# Grouper par action
propres_by_stock = df_propres.groupby('stock')['IF_Anomaly'].agg(['sum', 'count'])
propres_by_stock['pct'] = (propres_by_stock['sum'] / propres_by_stock['count'] * 100)

bruitees_by_stock = df_bruitees.groupby('stock')['IF_Anomaly'].agg(['sum', 'count'])
bruitees_by_stock['pct'] = (bruitees_by_stock['sum'] / bruitees_by_stock['count'] * 100)

print(f"\n{'Action':<10} | {'Propres':<15} | {'Bruitées':<15} | {'Différence'}")
print("-" * 70)

for stock in sorted(propres_by_stock.index):
    prop_anom = int(propres_by_stock.loc[stock, 'sum'])
    prop_pct = propres_by_stock.loc[stock, 'pct']
    
    bruit_anom = int(bruitees_by_stock.loc[stock, 'sum'])
    bruit_pct = bruitees_by_stock.loc[stock, 'pct']
    
    diff = bruit_anom - prop_anom
    
    print(f"{stock:<10} | {prop_anom:3} ({prop_pct:5.2f}%) | {bruit_anom:3} ({bruit_pct:5.2f}%) | {diff:+3}")

# ============================================================
# GRAPHIQUE 1 : COMPARAISON GLOBALE
# ============================================================

print("\n" + "="*70)
print("📊 GÉNÉRATION DES GRAPHIQUES")
print("="*70)

print("\n1️⃣ Graphique 1 : Comparaison globale...")

fig1, ax1 = plt.subplots(figsize=(10, 7))
fig1.suptitle('Comparaison Globale : Propres vs Bruitées-Nettoyées', 
              fontsize=16, fontweight='bold', y=0.98)

categories = ['Données Propres', 'Données Bruitées-Nettoyées']
anomalies = [anom_propres, anom_bruitees]
colors = ['#2ecc71', '#e74c3c']

bars = ax1.bar(categories, anomalies, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
ax1.set_ylabel('Nombre d\'anomalies détectées', fontsize=13, fontweight='bold')
ax1.set_ylim(0, max(anomalies) * 1.2)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Annotations
for i, (bar, val) in enumerate(zip(bars, anomalies)):
    height = bar.get_height()
    pct = [pct_propres, pct_bruitees][i]
    ax1.text(bar.get_x() + bar.get_width()/2., height + max(anomalies)*0.02,
             f'{int(val)} anomalies\n({pct:.2f}%)',
             ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
graph1_file = PROCESSED_DIR / "graphique1_comparaison_globale.png"
plt.savefig(graph1_file, dpi=300, bbox_inches='tight')
print(f"   ✅ {graph1_file.name}")
plt.close()

# ============================================================
# GRAPHIQUE 2 : COMPARAISON PAR ACTION
# ============================================================

print("\n2️⃣ Graphique 2 : Comparaison par action...")

fig2, ax2 = plt.subplots(figsize=(12, 7))
fig2.suptitle('Comparaison par Action : Propres vs Bruitées-Nettoyées',
              fontsize=16, fontweight='bold', y=0.98)

stocks = sorted(propres_by_stock.index)
x = np.arange(len(stocks))
width = 0.35

propres_vals = [int(propres_by_stock.loc[s, 'sum']) for s in stocks]
bruitees_vals = [int(bruitees_by_stock.loc[s, 'sum']) for s in stocks]

bars1 = ax2.bar(x - width/2, propres_vals, width, label='Données Propres', 
                color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
bars2 = ax2.bar(x + width/2, bruitees_vals, width, label='Données Bruitées-Nettoyées',
                color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)

ax2.set_xlabel('Action', fontsize=13, fontweight='bold')
ax2.set_ylabel('Nombre d\'anomalies détectées', fontsize=13, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(stocks, rotation=0, ha='center', fontsize=11)
ax2.legend(fontsize=11, loc='upper left')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Ajouter valeurs au-dessus des barres
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
graph2_file = PROCESSED_DIR / "graphique2_comparaison_par_action.png"
plt.savefig(graph2_file, dpi=300, bbox_inches='tight')
print(f"   ✅ {graph2_file.name}")
plt.close()

# ============================================================
# GRAPHIQUE 3 : DISTRIBUTION SCORES PROPRES
# ============================================================

print("\n3️⃣ Graphique 3 : Distribution scores propres...")

fig3, ax3 = plt.subplots(figsize=(10, 7))
fig3.suptitle('Distribution des Scores d\'Anomalie - Données Propres',
              fontsize=16, fontweight='bold', y=0.98)

ax3.hist(df_propres['IF_Score'], bins=50, color='#2ecc71', alpha=0.7, 
         edgecolor='black', linewidth=1.2, label='Scores')
ax3.axvline(df_propres['IF_Score'].mean(), color='darkgreen', 
            linestyle='--', linewidth=3, label=f'Moyenne: {df_propres["IF_Score"].mean():.4f}')

ax3.set_xlabel('Score d\'anomalie (négatif = anormal)', fontsize=13, fontweight='bold')
ax3.set_ylabel('Fréquence', fontsize=13, fontweight='bold')
ax3.legend(fontsize=12, loc='upper left')
ax3.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
graph3_file = PROCESSED_DIR / "graphique3_distribution_propres.png"
plt.savefig(graph3_file, dpi=300, bbox_inches='tight')
print(f"   ✅ {graph3_file.name}")
plt.close()

# ============================================================
# GRAPHIQUE 4 : DISTRIBUTION SCORES BRUITÉES
# ============================================================

print("\n4️⃣ Graphique 4 : Distribution scores bruitées...")

fig4, ax4 = plt.subplots(figsize=(10, 7))
fig4.suptitle('Distribution des Scores d\'Anomalie - Données Bruitées-Nettoyées',
              fontsize=16, fontweight='bold', y=0.98)

ax4.hist(df_bruitees['IF_Score'], bins=50, color='#e74c3c', alpha=0.7,
         edgecolor='black', linewidth=1.2, label='Scores')
ax4.axvline(df_bruitees['IF_Score'].mean(), color='darkred',
            linestyle='--', linewidth=3, label=f'Moyenne: {df_bruitees["IF_Score"].mean():.4f}')

ax4.set_xlabel('Score d\'anomalie (négatif = anormal)', fontsize=13, fontweight='bold')
ax4.set_ylabel('Fréquence', fontsize=13, fontweight='bold')
ax4.legend(fontsize=12, loc='upper left')
ax4.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
graph4_file = PROCESSED_DIR / "graphique4_distribution_bruitees.png"
plt.savefig(graph4_file, dpi=300, bbox_inches='tight')
print(f"   ✅ {graph4_file.name}")
plt.close()

print("\n✅ 4 graphiques générés !")

# ============================================================
# RAPPORT FINAL
# ============================================================

print("\n" + "="*70)
print("📄 GÉNÉRATION DU RAPPORT FINAL")
print("="*70)

report = []
report.append("="*70)
report.append("RAPPORT FINAL - COMPARAISON PROPRES vs BRUITÉES-NETTOYÉES")
report.append("="*70)
report.append("")
report.append("PROJET : Détection d'anomalies - Bourse de Casablanca")
report.append("OBJECTIF : Démontrer l'impact du bruit sur la qualité des données")
report.append("")
report.append("="*70)
report.append("1. RÉSULTATS GLOBAUX")
report.append("="*70)
report.append("")
report.append("DONNÉES PROPRES :")
report.append(f"  - Total lignes       : {len(df_propres)}")
report.append(f"  - Anomalies détectées: {anom_propres} ({pct_propres:.2f}%)")
report.append(f"  - Score moyen        : {df_propres['IF_Score'].mean():.4f}")
report.append(f"  - Score min          : {df_propres['IF_Score'].min():.4f}")
report.append(f"  - Score max          : {df_propres['IF_Score'].max():.4f}")
report.append("")
report.append("DONNÉES BRUITÉES-NETTOYÉES :")
report.append(f"  - Total lignes       : {len(df_bruitees)}")
report.append(f"  - Anomalies détectées: {anom_bruitees} ({pct_bruitees:.2f}%)")
report.append(f"  - Score moyen        : {df_bruitees['IF_Score'].mean():.4f}")
report.append(f"  - Score min          : {df_bruitees['IF_Score'].min():.4f}")
report.append(f"  - Score max          : {df_bruitees['IF_Score'].max():.4f}")
report.append("")
report.append("DIFFÉRENCE :")
report.append(f"  - Anomalies supplémentaires: +{diff_anom} ({diff_pct:+.2f}%)")
report.append(f"  - Augmentation relative    : +{(diff_anom/anom_propres)*100:.1f}%")
report.append("")
report.append("="*70)
report.append("2. COMPARAISON PAR ACTION")
report.append("="*70)
report.append("")
report.append(f"{'Action':<10} | {'Propres':<12} | {'Bruitées':<12} | {'Diff'}")
report.append("-" * 60)

for stock in sorted(propres_by_stock.index):
    prop_anom = int(propres_by_stock.loc[stock, 'sum'])
    prop_pct = propres_by_stock.loc[stock, 'pct']
    bruit_anom = int(bruitees_by_stock.loc[stock, 'sum'])
    bruit_pct = bruitees_by_stock.loc[stock, 'pct']
    diff = bruit_anom - prop_anom
    
    report.append(f"{stock:<10} | {prop_anom:3} ({prop_pct:5.2f}%) | {bruit_anom:3} ({bruit_pct:5.2f}%) | {diff:+3}")

report.append("")
report.append("="*70)
report.append("3. CONCLUSIONS")
report.append("="*70)
report.append("")
report.append("✓ Impact du bruit :")
report.append(f"  Même après nettoyage, les données bruitées conservent des traces")
report.append(f"  d'anomalies (+{diff_anom} anomalies, soit +{(diff_anom/anom_propres)*100:.1f}%).")
report.append("")
report.append("✓ Efficacité du pipeline de nettoyage :")
report.append(f"  Le pipeline a permis de réduire significativement le bruit,")
report.append(f"  mais ne peut pas restaurer parfaitement l'état initial.")
report.append("")
report.append("✓ Recommandation principale :")
report.append(f"  LA PRÉVENTION EST SUPÉRIEURE À LA CORRECTION")
report.append(f"  → Privilégier la qualité des données à la source")
report.append(f"  → Mettre en place des contrôles de validation en temps réel")
report.append(f"  → Éviter l'introduction de bruit dès la collecte")
report.append("")
report.append("✓ Actions les plus affectées :")
most_affected = bruitees_by_stock['sum'] - propres_by_stock['sum']
most_affected = most_affected.sort_values(ascending=False).head(3)
for stock, diff in most_affected.items():
    report.append(f"  - {stock}: +{int(diff)} anomalies supplémentaires")
report.append("")
report.append("="*70)
report.append("4. FICHIERS GÉNÉRÉS")
report.append("="*70)
report.append("")
report.append("GRAPHIQUES :")
report.append("  - graphique1_comparaison_globale.png")
report.append("  - graphique2_comparaison_par_action.png")
report.append("  - graphique3_distribution_propres.png")
report.append("  - graphique4_distribution_bruitees.png")
report.append("")
report.append("="*70)
report.append("FIN DU RAPPORT")
report.append("="*70)

report_text = "\n".join(report)
report_file = PROCESSED_DIR / "rapport_comparaison_finale.txt"

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"✅ Rapport sauvegardé : {report_file}")

# ============================================================
# RÉSUMÉ FINAL
# ============================================================

print("\n" + "="*70)
print("🎉 PROJET TERMINÉ")
print("="*70)

print(f"\n📊 Fichiers générés :")
print(f"   ✓ graphique1_comparaison_globale.png")
print(f"   ✓ graphique2_comparaison_par_action.png")
print(f"   ✓ graphique3_distribution_propres.png")
print(f"   ✓ graphique4_distribution_bruitees.png")
print(f"   ✓ rapport_comparaison_finale.txt")

print(f"\n🎯 CONCLUSION PRINCIPALE :")
print(f"   Les données bruitées-nettoyées ont {anom_bruitees} anomalies")
print(f"   contre {anom_propres} pour les données propres.")
print(f"   Différence : +{diff_anom} anomalies (+{(diff_anom/anom_propres)*100:.1f}%)")
print(f"")
print(f"   → LA PRÉVENTION > CORRECTION")
print(f"")
print(f"📁 Tous les fichiers sont dans : {PROCESSED_DIR}")
print("\n")