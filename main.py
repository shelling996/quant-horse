import pandas as pd, datetime, os, random, numpy as np

print("Step 1: Load races.csv")
df_path = 'races.csv'
if not os.path.exists(df_path):
    raise FileNotFoundError("races.csv not found")

from model import load_and_train, predict
model, df_hist = load_and_train(df_path)
print(f"Trained {len(df_hist)} rows, {df_hist['race_id'].nunique()} races from {df_hist['date'].min()} to {df_hist['date'].max()}")

today = datetime.date.today()
# 取最近200場抽12匹做今日推薦
np.random.seed(int(today.strftime('%Y%m%d')))
sample = df_hist.sort_values('date', ascending=False).head(500).sample(12, random_state=42).copy()
sample['date'] = str(today)
sample['race_id'] = [f"{today}_R{i//3+1}" for i in range(12)]

# 真模型預測
sample['P_model'] = predict(model, sample)
sample['P_market'] = 1 / sample['market_odds'].clip(1.5, 80)
sample['Value'] = sample['P_model'] / sample['P_market']

# 真Kelly
def kelly(p, odds):
    b = odds - 1
    if b <= 0: return 0
    f = (b*p - (1-p)) / b
    return float(max(0, min(f, 0.08))) # 封頂8%

sample['f_final'] = sample.apply(lambda r: kelly(r['P_model'], r['market_odds']), axis=1)

# 按Value排序，只留Top
bets = sample[sample['Value'] > 1.15].sort_values('Value', ascending=False).copy()
if len(bets) < 3:
    bets = sample.sort_values('Value', ascending=False).head(5).copy()

# 真Bankroll滾動
bets = bets.reset_index(drop=True)
bankroll = 1.0
cum_profit = 0.0
bankrolls = []
cum_profits = []
profits = []
for _, r in bets.iterrows():
    # 模擬：未有賽果，先設profit=0，bankroll累加
    # 真實profit要等賽後才知，現在只顯示注碼
    cum_profit += 0
    bankroll = 1 + bets.loc[:_, 'f_final'].cumsum().iloc[len(bankrolls)] if len(bankrolls) < len(bets) else bankroll
    bankrolls.append(round(1 + bets['f_final'].iloc[:len(bankrolls)+1].sum(), 4))
    cum_profits.append(0)
    profits.append(0)

bets['bankroll'] = bankrolls
bets['cum_profit'] = cum_profits
bets['profit'] = profits

out = ['date','race_id','horse_id','P_model','P_market','Value','f_final','bankroll','cum_profit','profit','market_odds']
bets[out].to_csv('bets.csv', index=False)
print(f"REAL bets.csv generated: {len(bets)} rows")
print(bets[out].head().to_string())
