import streamlit as st
import pandas as pd, os
st.set_page_config(page_title="Quant Horse", layout="wide")
st.title("🐎 Quant Horse - SSD投注系統")
st.caption("訓練在後端 | 顯示在前端")

if not os.path.exists('bets.csv'):
    st.warning("等 GitHub Actions 跑完")
    st.stop()

bets = pd.read_csv('bets.csv')
st.success(f"今日推薦 {len(bets)} 場 | Date: {bets['date'].iloc[0]} | 平均Value: {bets['Value'].mean():.2f}")

# 只顯示有用欄，唔顯示bankroll=1果啲怪欄
show_cols = ['race_id','horse_id','P_model','P_market','Value','f_final','market_odds']
st.dataframe(bets[show_cols].style.format({'P_model':'{:.2%}','P_market':'{:.2%}','Value':'{:.2f}','f_final':'{:.1%}'}), use_container_width=True)

c1,c2,c3 = st.columns(3)
c1.metric("平均Value", f"{bets['Value'].mean():.2f}", help=">1.5先有價值")
c2.metric("總注碼", f"{bets['f_final'].sum()*100:.1f}%", help="半Kelly+6%封頂")
c3.metric("平均模型勝率", f"{bets['P_model'].mean()*100:.1f}%")

st.subheader("本金曲線 (模擬)")
st.line_chart(bets[['bankroll']])
st.caption("profit=0 係正常，因為係未來賽事未跑。bankroll只係模擬注碼累加，真profit要賽後先知。")
