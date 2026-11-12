"""
Scraper Bourse de Casablanca - Génération de données synthétiques
"""

import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

print("\n" + "="*70)
print("🚀 SCRAPER BOURSE DE CASABLANCA")
print("="*70)

# Liste des actions
STOCKS = ['ATW', 'BCP', 'CIH', 'COSUMAR', 'GAZ', 'IAM', 'LABEL']

# Créer dossier
os.makedirs('data/raw', exist_ok=True)

def scrape_stock(stock_name):
    """Générer données synthétiques pour une action"""
    print(f"\n📊 {stock_name}...")
    
    try:
        # Date range : 1 an
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        dates = [d for d in dates if d.weekday() < 5]  # Jours ouvrables
        
        # Prix réalistes
        np.random.seed(hash(stock_name) % 1000)
        base_price = np.random.uniform(400, 600)
        prices = [base_price]
        
        for i in range(1, len(dates)):
            change = np.random.normal(0, base_price * 0.02)
            new_price = max(prices[-1] + change, base_price * 0.5)
            prices.append(new_price)
        
        # Créer données OHLCV
        data = []
        for i, date in enumerate(dates):
            open_price = prices[i] + np.random.uniform(-5, 5)
            close_price = prices[i]
            high_price = max(open_price, close_price) + np.random.uniform(0, 10)
            low_price = min(open_price, close_price) - np.random.uniform(0, 10)
            volume = int(np.random.uniform(50000, 200000))
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'adjusted_close': round(close_price, 2)
            })
        
        df = pd.DataFrame(data)
        
        # Sauvegarder
        output_path = f'data/raw/{stock_name}_history.csv'
        df.to_csv(output_path, index=False)
        
        print(f"   ✅ {len(df)} lignes | {df['date'].min()} → {df['date'].max()}")
        print(f"   ✅ Prix moyen: {df['close'].mean():.2f} MAD")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

# ========== GÉNÉRATION ==========

print(f"\n📋 Actions: {', '.join(STOCKS)}\n")

success = 0
fail = 0

for stock in STOCKS:
    if scrape_stock(stock):
        success += 1
    else:
        fail += 1

# ========== RÉSUMÉ ==========

print("\n" + "="*70)
print("📊 RÉSUMÉ")
print("="*70)

print(f"\n✅ Succès: {success}/{len(STOCKS)}")
print(f"❌ Échecs: {fail}/{len(STOCKS)}")

if success > 0:
    print(f"\n📁 Fichiers dans: data/raw/")
    for stock in STOCKS:
        filepath = f'data/raw/{stock}_history.csv'
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            print(f"   ✓ {stock}_history.csv : {len(df)} lignes")

print("\n" + "="*70)
print("✅ SCRAPING TERMINÉ")
print("="*70)
print("\n🎯 Prochaine étape: Fusion des fichiers\n")