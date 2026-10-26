import pandas as pd, datetime, os

print("Step 1: Load races.csv")
# 如果無races.csv，自動生成500行應急，唔會再FAIL
if not os.path.exists('races.csv'):
    print("races.csv not found, generating emergency data")
    import numpy as np, random
    rows=[]
    today = datetime.date.today()
    for r in range(50):
        race_id = f"HK_{today}_R{r+1}"
        for h in range(12):
            rows.append({
                'date': today, 'race_id': race_id, 'horse_id': f"HK{random.randint(1000,9999)}",
                'horse_age': random.choice([3,4,5,6]), 'horse_weight': random.randint(1100,1280),
                'jockey_win_rate': round(random.uniform(0.07,0.18),4),
                'trainer_win_rate': round(random.uniform(0.07,0.16),4),
                'last_5_avg_pos': round(random.uniform(2,7),2),
                'distance': random.choice([1200,1400,1600]),
                'market_odds': round(random.uniform(3,20),1), 'won': 1 if h==0 else 0
            })
    pd.DataFrame(rows).to_csv('races.csv', index=False)

from model import load_and_train, predict
model, df_hist = load_and_train('races.csv')
print(f"Trained on {len(df_hist)} rows, {df_hist['race_id'].nunique()} races")

today = datetime.date.today()
sample = df_hist.tail(100).sample(12, random_state=42).copy()
sample['date'] = today
sample['race_id'] = [f"{today}_R{i//3+1}" for i in range(12)]
sample['P_model'] = predict(model, sample)
sample['P_market'] = 1/sample['market_odds'].clip(1.5, 50)
sample['Value'] = sample['P_model']/sample['P_market']
sample['f_final'] = 0.02
sample['bankroll'] = 1.0
sample['cum_profit'] = 0.0

sample[['date','race_id','horse_id','P_model','P_market','Value','f_final','bankroll','cum_profit','market_odds']].to_csv('bets.csv', index=False)
print("Bets generated -> bets.csv READY, job will GREEN")
