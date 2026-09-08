import time, numpy as np, pandas as pd, yfinance as yf

NSE_SYMBOLS=[
"RELIANCE","HDFCBANK","ICICIBANK","SBIN","INFY","TCS","ITC","BHARTIARTL","LT","AXISBANK",
"KOTAKBANK","HINDUNILVR","BAJFINANCE","MARUTI","M&M","SUNPHARMA","TATAMOTORS","TATASTEEL",
"NTPC","POWERGRID","ADANIENT","ADANIPORTS","BEL","COALINDIA","ONGC","WIPRO","HCLTECH",
"TECHM","ULTRACEMCO","ASIANPAINT","TITAN","NESTLEIND","JSWSTEEL","GRASIM","HINDALCO",
"DRREDDY","CIPLA","EICHERMOT","HEROMOTOCO","BAJAJFINSV","INDUSINDBK","SBILIFE","HDFCLIFE",
"APOLLOHOSP","TATACONSUM","TRENT","DLF","IOC","BPCL","GAIL","IRFC","HAL","INDIGO"
]

def indicators(df):
    x=df.copy()
    x["EMA20"]=x.Close.ewm(span=20,adjust=False).mean()
    x["EMA50"]=x.Close.ewm(span=50,adjust=False).mean()
    x["VWAP"]=(x.Close*x.Volume).cumsum()/x.Volume.replace(0,np.nan).cumsum()
    pc=x.Close.shift(1)
    tr=pd.concat([x.High-x.Low,(x.High-pc).abs(),(x.Low-pc).abs()],axis=1).max(axis=1)
    x["ATR"]=tr.rolling(14).mean()
    d=x.Close.diff()
    gain=d.clip(lower=0).rolling(14).mean()
    loss=(-d.clip(upper=0)).rolling(14).mean()
    rs=gain/loss.replace(0,np.nan)
    x["RSI"]=100-(100/(1+rs))
    x["VolAvg"]=x.Volume.rolling(20).mean()
    x["VolumeRatio"]=x.Volume/x.VolAvg.replace(0,np.nan)
    x["High20"]=x.High.shift(1).rolling(20).max()
    x["Low20"]=x.Low.shift(1).rolling(20).min()
    return x.dropna()

def signal(symbol,x):
    r=x.iloc[-1]; bull=bear=0; br=[]; sr=[]
    if r.Close>r.EMA20>r.EMA50: bull+=20;br.append("trend")
    if r.Close<r.EMA20<r.EMA50: bear+=20;sr.append("trend")
    if r.Close>r.VWAP: bull+=15;br.append("VWAP")
    if r.Close<r.VWAP: bear+=15;sr.append("VWAP")
    if r.Close>r.High20: bull+=30;br.append("breakout")
    if r.Close<r.Low20: bear+=30;sr.append("breakdown")
    if r.VolumeRatio>=2: bull+=15;bear+=15;br.append("2x volume");sr.append("2x volume")
    elif r.VolumeRatio>=1.5: bull+=8;bear+=8
    if 55<=r.RSI<=75: bull+=10;br.append("RSI")
    if 25<=r.RSI<=45: bear+=10;sr.append("RSI")
    score=min(100,max(bull,bear))
    if score<50:return None
    last=float(r.Close); atr=float(r.ATR)
    if bull>=bear:
        sl=last-1.2*atr;t1=last+1.8*atr;t2=last+2.7*atr;sig="BUY";reason=", ".join(br)
    else:
        sl=last+1.2*atr;t1=last-1.8*atr;t2=last-2.7*atr;sig="SELL";reason=", ".join(sr)
    rr=abs(t1-last)/abs(last-sl)
    return {"Symbol":symbol,"Signal":sig,"Score":score,"Last":round(last,2),"Entry":round(last,2),
            "SL":round(sl,2),"Target1":round(t1,2),"Target2":round(t2,2),"RR":round(rr,2),
            "VolumeRatio":round(float(r.VolumeRatio),2),"Reason":reason}

def scan_universe(interval="5m"):
    rows=[]; warnings=[]
    period="5d" if interval=="5m" else "30d"
    for s in NSE_SYMBOLS:
        try:
            df=yf.Ticker(s+".NS").history(period=period,interval=interval,auto_adjust=False,prepost=False)
            if df.empty or len(df)<60:
                warnings.append(f"{s}: insufficient/no data");continue
            df=df[["Open","High","Low","Close","Volume"]].dropna()
            df=df[df.Volume>0]
            x=indicators(df)
            if len(x)>=30:
                q=signal(s,x)
                if q: rows.append(q)
            time.sleep(.12)
        except Exception as e: warnings.append(f"{s}: {e}")
    return pd.DataFrame(rows),warnings
