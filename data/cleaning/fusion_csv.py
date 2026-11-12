"""
Fusion des fichiers CSV
"""

import pandas as pd
from pathlib import Path

print("\n" + "="*70)
print("📦 FUSION DES FICHIERS CSV")
print("="*70)

# Chemin ABSOLU en dur
raw_dir = Path(r"C:\Users\pc\Desktop\bourse_scraper\data\raw")

print(f"\n📁 Recherche dans: {raw_dir}")

csv_files = list(raw_dir.glob('*_history.csv'))

print(f"📊 {len(csv_files)} fichiers trouvés\n")

all_data = []

for i, filepath in enumerate(csv_files, 1):
    stock_name = filepath.stem.replace('_history', '')
    print(f"[{i}/{len(csv_files)}] {stock_name}...")
    
    try:
        df = pd.read_csv(filepath)
        df['stock'] = stock_name
        all_data.append(df)
        print(f"   ✓ {len(df)} lignes")
    except Exception as e:
        print(f"   ❌ {e}")

if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    combined = combined.sort_values(['stock', 'date'])
    
    output = raw_dir / 'all_stocks_raw.csv'
    combined.to_csv(output, index=False, encoding='utf-8-sig')
    
    print("\n" + "="*70)
    print("✅ FUSION TERMINÉE")
    print("="*70)
    print(f"\n📊 Total: {len(combined):,} lignes")
    print(f"📊 Actions: {combined['stock'].nunique()}")
    print(f"\n📈 Distribution:")
    for stock, count in combined['stock'].value_counts().sort_index().items():
        print(f"   {stock}: {count} lignes")
    print(f"\n💾 {output}")
    print("\n🎯 Prochaine étape: Nettoyage\n")
else:
    print("\n❌ Aucune donnée\n")