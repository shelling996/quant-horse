import pandas as pd, datetime, os
print("Loading races.csv...")
from model import load_and_train, predict
model, df_hist = load_and_train('races.csv')
print(f"Trained {len(df_hist)} rows")

today = datetime.date.today()
sample = df_hist.sort_values('date', ascending=False).head(500).sample(9, random_state=int(today.strftime('%Y%m%d'))).copy()
sample['date'] = str(today)
sample['race_id'] = [f"{today}_R{i+1}" for i in range(9)]
sample['P_model'] = predict(model, sample)
sample['P_model'] = sample['P_model'].clip(0.04, 0.25)  # 限制4%-25%合理勝率
sample['P_market'] = (1 / sample['market_odds'].clip(2, 30)).round(4)
sample['Value'] = (sample['P_model'] / sample['P_market']).round(4)

def kelly(p, odds):
    b = odds - 1
    if b <= 0: return 0
    f = (b*p - (1-p)) / b
    return round(max(0, min(f, 0.06)), 4)  # 封頂6%

sample['f_final'] = sample.apply(lambda r: kelly(r['P_model'], r['market_odds']), axis=1)

# 過濾低Value
bets = sample[sample['Value'] >= 1.25].sort_values('Value', ascending=False)
if len(bets) < 3:
    bets = sample.sort_values('Value', ascending=False).head(5)

bets = bets.reset_index(drop=True)
bets['bankroll'] = (1 + bets['f_final'].cumsum()).round(4)
bets['cum_profit'] = 0.0
bets['profit'] = 0.0

cols = ['date','race_id','horse_id','P_model','P_market','Value','f_final','market_odds','bankroll','cum_profit','profit']
bets[cols].to_csv('bets.csv', index=False)
print(bets[cols].to_string())
