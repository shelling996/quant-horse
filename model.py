import pandas as pd
from catboost import CatBoostClassifier
FEATURES = ['horse_age','horse_weight','jockey_win_rate','trainer_win_rate','last_5_avg_pos','distance']

def load_and_train(path='races.csv'):
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values('date')
    
    # --- 你講嘅 ADD_MONTHS(SYSDATE,-48) 至 SYSDATE ---
    cutoff = pd.Timestamp.now() - pd.DateOffset(months=48)
    df_48m = df[df['date'] >= cutoff].copy()
    print(f"原始 {len(df)} 行, 48個月內 {len(df_48m)} 行 ({cutoff.date()} 至 {pd.Timestamp.now().date()})")
    
    if len(df_48m) < 500:
        print("⚠️ 48個月內數據太少，用全部數據頂住")
        df_48m = df
    
    X = df_48m[FEATURES].fillna(df_48m[FEATURES].median())
    y = df_48m['won']
    model = CatBoostClassifier(iterations=300, depth=6, learning_rate=0.05, verbose=False, random_seed=42)
    model.fit(X, y, verbose=False)
    return model, df_48m
