
# dashboard.py - 量化賽馬監控儀表板 (對應 main.py bets.csv)
# pip install streamlit plotly pandas
# 執行: streamlit run dashboard.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Quant Horse Dashboard", layout="wide")
st.title("量化賽馬系統 - 監控儀表板 (SSD v1.0)")

# 載入
if not os.path.exists('bets.csv'):
    st.warning("找不到 bets.csv，請先跑 main.py")
    st.stop()

bets = pd.read_csv('bets.csv')
bets['date'] = pd.to_datetime(bets['date'])
bets = bets.sort_values('date')

# 若有 test_calibrated.csv 讀Top命中率
top_win_rate = None
if os.path.exists('test_calibrated.csv'):
    test = pd.read_csv('test_calibrated.csv')
    test['date'] = pd.to_datetime(test['date'])
    # 假設已有 date_rank
    if 'date_rank' in test.columns:
        top_win_rate = (test[test['date_rank']<=0.10]['finish_position']==1).mean()

# 指標
col1, col2, col3, col4, col5 = st.columns(5)
total_bets = len(bets)
win_bets = (bets['is_win']==1).sum() if 'is_win' in bets else 0
win_rate = win_bets/total_bets if total_bets else 0
total_profit = bets['cum_profit'].iloc[-1] if 'cum_profit' in bets else bets['profit'].sum() if 'profit' in bets else 0
roi = bets['profit'].sum() / bets['f_final'].sum() if 'f_final' in bets and bets['f_final'].sum()>0 else 0
max_dd = bets['drawdown'].min() if 'drawdown' in bets else 0

col1.metric("投注場次", total_bets)
col2.metric("命中率", f"{win_rate:.1%}")
col3.metric("ROI", f"{roi:.2%}", delta="目標>3%")
col4.metric("累積Profit", f"{total_profit:.4f}")
col5.metric("最大回撤", f"{max_dd:.2%}")

if top_win_rate is not None:
    st.metric(f"Top10%信心命中率 (全測試集)", f"{top_win_rate:.2%}", delta="目標>18%, <12%停用", delta_color="normal")

# 本金曲線
st.subheader("本金曲線")
fig = go.Figure()
if 'bankroll' in bets:
    fig.add_trace(go.Scatter(x=bets['date'], y=bets['bankroll'], mode='lines', name='Bankroll'))
else:
    # 簡易累積
    fig.add_trace(go.Scatter(x=bets['date'], y=(1+bets['profit'].cumsum()), mode='lines', name='Bankroll'))
fig.update_layout(yaxis_title="Bankroll (初始=1)", xaxis_title="Date")
st.plotly_chart(fig, use_container_width=True)

# 累積ROI
st.subheader("累積Profit")
fig2 = go.Figure()
y = bets['cum_profit'] if 'cum_profit' in bets else bets['profit'].cumsum()
fig2.add_trace(go.Scatter(x=bets['date'], y=y, mode='lines', name='Cum Profit'))
st.plotly_chart(fig2, use_container_width=True)

# 每日明細
st.subheader("每日投注明細 (bets.csv)")
st.dataframe(bets[['date','race_id','horse_id','P_model','P_market','Value','final_odds','f_final','is_win','profit']].tail(100))

# 檢查Value合理性
st.subheader("Value分佈")
st.bar_chart(bets['Value'])

st.caption("SSD提醒：只投5-8%場次，模型30%準已夠，90%功夫在知道何時不投。Top<12%持續2週停用。")
