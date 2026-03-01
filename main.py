import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import time
import os

# GitHubのSecretsから読み込む設定
ACCESS_TOKEN = os.environ['LINE_ACCESS_TOKEN']
USER_ID = os.environ['LINE_USER_ID']

def send_line_message(text):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {ACCESS_TOKEN}'}
    data = {'to': USER_ID, 'messages': [{'type': 'text', 'text': text}]}
    res = requests.post(url, headers=headers, json=data)
    return res

# コア30銘柄
CORE30 = ["9432.T", "9433.T", "9434.T", "9984.T", "8306.T", "8316.T", "8411.T", "8766.T", "7203.T", "6758.T", "6501.T", "6861.T", "7974.T", "8035.T", "4063.T", "6367.T", "6954.T", "6273.T", "8058.T", "8031.T", "8001.T", "9983.T", "3382.T", "4502.T", "4568.T", "4519.T", "4503.T", "2914.T", "6098.T", "7741.T"]

print("分析開始...")
hit_messages = []

for ticker in CORE30:
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df.ta.sma(length=25, append=True)
        df.ta.macd(append=True)
        df.ta.stoch(append=True)
        
        last = df.iloc[-1]
        price = last['Close']
        
        # 判定ロジック
        condition = (price > last['SMA_25']) and (last['MACD_12_26_9'] > last['MACDs_12_26_9']) and (last['STOCHk_14_3_3'] < 50)
        
        if condition:
            hit_messages.append(f"【買い】{ticker}: {price:.1f}円\n利確目安: {price*1.05:.1f}円\n損切目安: {price*0.97:.1f}円")
        time.sleep(0.5)
    except:
        pass

summary = "【Core30診断結果】\n\n" + ("\n\n".join(hit_messages) if hit_messages else "本日の合致銘柄はありません。")
send_line_message(summary)
print("完了")
