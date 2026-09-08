import streamlit as st
from scanner import scan_universe

st.set_page_config(page_title="NSE Top 5 Big Move", layout="wide")
st.title("🚀 NSE Intraday — Top 5 Big Move")
st.caption("Personal-use scanner. Probability-based signals; not guaranteed predictions or investment advice.")

c1,c2,c3=st.columns(3)
with c1: interval=st.selectbox("Candle",["5m","15m"])
with c2: minimum=st.slider("Minimum signal strength",50,95,65)
with c3: st.write("")

if st.button("🔎 SCAN TOP 5", type="primary"):
    with st.spinner("Scanning NSE universe..."):
        df, warnings=scan_universe(interval)

    if df.empty:
        st.error("No valid setups returned. Free data can be delayed or rate-limited.")
    else:
        df=df[df.Score>=minimum].sort_values("Score",ascending=False).head(5).copy()
        df.insert(0,"Rank",range(1,len(df)+1))
        df["Strength"]=df.Score.map(lambda x: "🔥 VERY STRONG" if x>=85 else ("🟢 STRONG" if x>=75 else "🟡 MODERATE"))
        st.dataframe(df[["Rank","Symbol","Signal","Strength","Score","Last","Entry","SL","Target1","Target2","RR","VolumeRatio","Reason"]],
                     use_container_width=True,hide_index=True)
        if warnings:
            with st.expander(f"Data warnings ({len(warnings)})"): st.write(warnings)

st.divider()
st.subheader("Trailing SL rules")
st.markdown("""
- **BUY:** initial SL = Entry − 1.2×ATR. After price moves +1×ATR, trail to Entry. Then trail at `Close − 1.2×ATR`.
- **SELL:** initial SL = Entry + 1.2×ATR. After price moves −1×ATR, trail to Entry. Then trail at `Close + 1.2×ATR`.
- Trailing SL only moves in the trade's favor; it never widens.
""")
st.warning("Verify every live price in your broker terminal. Free public data is not a professional real-time execution feed.")
