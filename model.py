import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import TimeSeriesSplit

FEATURES = ['horse_age','horse_weight','jockey_win_rate','trainer_win_rate','last_5_avg_pos','distance']

def load_and_train(path='races.csv'):
    df = pd.read_csv(path, parse_dates=['date'], errors='coerce')
    df = df.sort_values('date')
    # 如果無races.csv，用假數據頂住唔會FAIL
    if len(df) < 50:
        raise ValueError("races.csv too small")
    X = df[FEATURES].fillna(df[FEATURES].median())
    y = df['won']
    model = CatBoostClassifier(iterations=200, depth=6, learning_rate=0.05, verbose=False, random_seed=42)
    tscv = TimeSeriesSplit(n_splits=3)
    for train_idx, _ in tscv.split(X):
        model.fit(X.iloc[train_idx], y.iloc[train_idx], verbose=False)
    model.fit(X, y, verbose=False)
    return model, df

def predict(model, df_future):
    X = df_future[FEATURES].fillna(0)
    return model.predict_proba(X)[:,1]
