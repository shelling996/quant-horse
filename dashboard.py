import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Quant Horse", layout="wide")
st.title("🐎 Quant Horse - SSD投注系統")
st.caption("訓練在後端 (GitHub Actions) | 顯示在前端 (Streamlit)")

if not os.path.exists('bets.csv'):
    st.warning("未有 bets.csv，請等 GitHub Actions 跑完 (31s)")
    st.stop()

try:
    bets = pd.read_csv('bets.csv')
    st.success(f"今日推薦 {len(bets)} 場 | Date: {bets['date'].iloc[0]}")
    
    # 容錯：舊版有profit，新版無就即時計
    if 'profit' not in bets.columns:
        bets['profit'] = 0
    if 'bankroll' not in bets.columns:
        bets['bankroll'] = 1 + bets['f_final'].cumsum() if 'f_final' in bets.columns else 1
    if 'cum_profit' not in bets.columns:
        bets['cum_profit'] = bets['f_final'].cumsum() if 'f_final' in bets.columns else 0
    
    st.dataframe(bets, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    if 'Value' in bets.columns:
        col1.metric("平均 Value", f"{bets['Value'].mean():.2f}")
    if 'f_final' in bets.columns:
        col2.metric("總注碼", f"{bets['f_final'].sum()*100:.1f}%")
        col3.metric("平均 P_model", f"{bets['P_model'].mean()*100:.1f}%" if 'P_model' in bets.columns else "N/A")
    
    if 'bankroll' in bets.columns:
        st.subheader("本金曲線")
        st.line_chart(bets[['bankroll']])
    if 'cum_profit' in bets.columns:
        st.subheader("累積Profit")
        st.line_chart(bets[['cum_profit']])
        
except Exception as e:
    st.error(f"讀取 bets.csv 失敗: {e}")
    st.code(str(e))
    if os.path.exists('bets.csv'):
        st.text(open('bets.csv','r').read()[:2000])
