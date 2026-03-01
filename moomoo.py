import yfinance as yf
import pandas as pd
import requests
import time
import os

# LINE設定
ACCESS_TOKEN = os.environ['LINE_ACCESS_TOKEN']
USER_ID = os.environ['LINE_USER_ID']

def send_line_message(text):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {ACCESS_TOKEN}'}
    data = {'to': USER_ID, 'messages': [{'type': 'text', 'text': text}]}
    requests.post(url, headers=headers, json=data)

# ★ここにお気に入り銘柄を追加してください★
# ★お気に入り銘柄リスト（最新版）
MY_WATCHLIST = [
    "9434.T", "6315.T", "7203.T", "6920.T", "6366.T", "274A.T", "5803.T", "4502.T", 
    "6146.T", "6862.T", "2780.T", "6890.T", "6590.T", "6525.T", "5016.T", "5711.T", 
    "6269.T", "3103.T", "9531.T", "8591.T", "1306.T", "7974.T", "6022.T", "4519.T", 
    "6301.T", "3350.T", "6501.T", "2146.T", "7182.T", "1928.T", "6946.T", "6326.T", 
    "7012.T", "7936.T", "2644.T", "1542.T", "8801.T", "1476.T", "7453.T", "8035.T", 
    "8830.T", "8306.T", "135A.T", "5942.T", "9501.T", "4506.T", "1301.T", "2515.T", 
    "6330.T", "1662.T", "6615.T", "5262.T", "9348.T", "5038.T", "9211.T", "5592.T", 
    "6855.T", "4412.T", "7011.T", "8136.T", "7832.T", "9697.T", "4063.T", "6857.T", 
    "4503.T", "3915.T", "5020.T", "7735.T", "6871.T", "5845.T", "3916.T", "3486.T", 
    "2418.T", "2970.T"
    # ここにムームーのお気に入り銘柄をどんどん追加できます
]

hit_list = []
print(f"{len(MY_WATCHLIST)}銘柄の分析を開始します...")

for t in MY_WATCHLIST:
    try:
        df = yf.download(t, period="1y", interval="1d", progress=False)
        if len(df) < 50: continue
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        
        # テクニカル指標の計算（自作ロジック）
        # 25日移動平均
        df['sma25'] = df['Close'].rolling(window=25).mean()
        # RSI (14日)
        diff = df['Close'].diff()
        gain = diff.clip(lower=0).rolling(window=14).mean()
        loss = -diff.clip(upper=0).rolling(window=14).mean()
        df['rsi'] = 100 - (100 / (1 + gain / loss))
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        # ストキャスティクス
        low_min = df['Low'].rolling(window=14).min()
        high_max = df['High'].rolling(window=14).max()
        df['stoch'] = ((df['Close'] - low_min) / (high_max - low_min)) * 100

        last = df.iloc[-1]
        price = float(last['Close'])
        
        # あなたが設定した「厳しい判定条件」
        cond_sma   = price > last['sma25']
        cond_macd  = last['macd'] > last['signal']
        cond_stoch = last['stoch'] < 40  # ストキャス40以下
        cond_rsi   = 30 < last['rsi'] < 60 # RSI 30-60の間

        if cond_sma and cond_macd and cond_stoch and cond_rsi:
            # ムームー証券の銘柄ページへ飛ぶリンクも作成（おまけ機能）
            ticker_code = t.replace(".T", "")
            moomoo_url = f"https://www.moomoo.com/jp/stock/{ticker_code}-JP"
            
            hit_list.append(
                f"【★お気に入りヒット】\n{t}\n価格: {price:.1f}円\n"
                f"利確目安: {price*1.05:.1f}\n損切目安: {price*0.97:.1f}\n"
                f"詳細: {moomoo_url}"
            )
        time.sleep(0.1)
    except Exception as e:
        print(f"Error {t}: {e}")
        continue

# LINE送信
if hit_list:
    send_line_message("【マイウォッチリスト診断】\n今日のお宝銘柄です！\n\n" + "\n\n".join(hit_list))
else:
    send_line_message("【マイウォッチリスト診断】\n本日、条件に合うお気に入り銘柄はありませんでした。")

print("完了")
