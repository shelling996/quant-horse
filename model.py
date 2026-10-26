import pandas as pd
from catboost import CatBoostClassifier

FEATURES = ['horse_age','horse_weight','jockey_win_rate','trainer_win_rate','last_5_avg_pos','distance']

def load_and_train(path='races.csv'):
    df = pd.read_csv(path)
    # 日期欄容錯
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values('date')
    X = df[FEATURES].fillna(df[FEATURES].median())
    y = df['won']
    model = CatBoostClassifier(iterations=200, depth=6, learning_rate=0.05, verbose=False, random_seed=42)
    model.fit(X, y, verbose=False)
    return model, df

def predict(model, df_future):
    X = df_future[FEATURES].fillna(0)
    return model.predict_proba(X)[:,1]
