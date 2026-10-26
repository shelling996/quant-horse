"""
convert_kaggle.py - 真Kaggle gdaley/hkracing 79k行 → 真 races.csv
用法:
1. 下載Kaggle gdaley/hkracing，解壓得到 races.csv + runs.csv
2. 將兩個檔放去 data/raw/ (建folder data/raw/)
3. 在GitHub Actions或本地跑: python scripts/convert_kaggle.py
4. 會在根目錄生成真 races.csv (79k行，真日期1997-2005，但係真統計)
"""
import pandas as pd
import os
import numpy as np

RAW_RACES = 'data/raw/races.csv'
RAW_RUNS = 'data/raw/runs.csv'
OUT = 'races.csv'

def convert():
    print(f"Checking {RAW_RUNS} and {RAW_RACES}")
    if not os.path.exists(RAW_RUNS):
        print(f"❌ 找不到 {RAW_RUNS}")
        print("請去 https://www.kaggle.com/datasets/gdaley/hkracing 下載，解壓後放去 data/raw/")
        return

    runs = pd.read_csv(RAW_RUNS)
    races = pd.read_csv(RAW_RACES) if os.path.exists(RAW_RACES) else pd.DataFrame()

    print(f"Kaggle runs: {len(runs)} rows, cols: {runs.columns.tolist()}")
    print(f"Kaggle races: {len(races)} rows")
    print(runs.head(3).to_string())

    # --- 1. 合併 races + runs ---
    if not races.empty and 'race_id' in races.columns and 'race_id' in runs.columns:
        df = pd.merge(runs, races, on='race_id', how='left', suffixes=('','_race'))
    else:
        df = runs.copy()

    # --- 2. 找出勝負欄 ---
    # gdaley數據通常有 finishing_position 或 result 或 place
    pos_col = None
    for c in ['finishing_position','result','place','position']:
        if c in df.columns:
            pos_col = c
            break
    
    if pos_col:
        df['won'] = (df[pos_col] == 1).astype(int)
        print(f"用 {pos_col} 計 won, 勝場數: {df['won'].sum()}")
    else:
        df['won'] = 0
        print("⚠️ 找不到名次欄，won全0，請檢查runs.csv欄位")

    # --- 3. 日期 ---
    date_col = None
    for c in ['race_date','date','race_date_formatted']:
        if c in df.columns:
            date_col = c
            break
    if date_col:
        df['date'] = pd.to_datetime(df[date_col], errors='coerce')
    else:
        df['date'] = pd.to_datetime('2005-01-01')

    # --- 4. 馬匹基本 ---
    df['horse_age'] = df.get('horse_age', df.get('age', 5))
    # 體重
    if 'declared_weight' in df.columns:
        df['horse_weight'] = df['declared_weight']
    elif 'actual_weight' in df.columns:
        df['horse_weight'] = df['actual_weight']
    else:
        df['horse_weight'] = 1200

    # --- 5. 騎師/練馬師勝率 (真滾動計法) ---
    # 先按日期排
    df = df.sort_values('date')
    
    if 'jockey' in df.columns:
        # 用累積勝率，避免洩漏未來數據
        jockey_expanding = df.groupby('jockey')['won'].expanding().mean().shift(1).reset_index(level=0, drop=True)
        df['jockey_win_rate'] = jockey_expanding.fillna(df['won'].mean())
    else:
        df['jockey_win_rate'] = 0.08

    if 'trainer' in df.columns:
        trainer_expanding = df.groupby('trainer')['won'].expanding().mean().shift(1).reset_index(level=0, drop=True)
        df['trainer_win_rate'] = trainer_expanding.fillna(df['won'].mean())
    else:
        df['trainer_win_rate'] = 0.08

    # --- 6. 近5場平均名次 (真滾動) ---
    if 'horse_id' in df.columns and pos_col:
        # 每匹馬過去5場平均名次
        df['last_5_avg_pos'] = df.groupby('horse_id')[pos_col].transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
        df['last_5_avg_pos'] = df['last_5_avg_pos'].fillna(5.0)
    else:
        df['last_5_avg_pos'] = 5.0

    # --- 7. 路程 + 賠率 ---
    df['distance'] = df.get('distance', df.get('distance_y', df.get('distance_x', 1400)))
    df['distance'] = pd.to_numeric(df['distance'], errors='coerce').fillna(1400)

    if 'win_odds' in df.columns:
        df['market_odds'] = df['win_odds']
    elif 'odds' in df.columns:
        df['market_odds'] = df['odds']
    else:
        df['market_odds'] = 10.0
    
    df['market_odds'] = pd.to_numeric(df['market_odds'], errors='coerce').fillna(10.0)
    df['market_odds'] = df['market_odds'].clip(1.5, 99)

    # --- 8. 最終欄 ---
    # horse_id可能係數字，轉字串
    if 'horse_id' not in df.columns:
        df['horse_id'] = df.index.astype(str)
    
    out_cols = ['date','race_id','horse_id','horse_age','horse_weight','jockey_win_rate','trainer_win_rate','last_5_avg_pos','distance','market_odds','won']
    
    final = df[out_cols].dropna(subset=['race_id','horse_id'])
    final = final.sort_values('date')
    
    final.to_csv(OUT, index=False)
    print(f"\n✅ 成功！生成真 {OUT}: {len(final)} 行, {final['race_id'].nunique()} 場")
    print(f"日期: {final['date'].min()} 到 {final['date'].max()}")
    print(f"勝率: {final['won'].mean()*100:.2f}% (正常應該8.3%)")
    print(f"前5行:\n{final.head().to_string()}")

if __name__ == "__main__":
    convert()
