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

# 日経225銘柄（簡易リスト）
# 本来は動的取得が望ましいですが、動作安定のため主要銘柄を含むリスト形式にします
TICKERS = ["1605.T", "1801.T", "1802.T", "1803.T", "1812.T", "1925.T", "1928.T", "1963.T", "2002.T", "2267.T", "2269.T", "2282.T", "2413.T", "2432.T", "2501.T", "2502.T", "2503.T", "2531.T", "2768.T", "2801.T", "2802.T", "2871.T", "2914.T", "3086.T", "3099.T", "3101.T", "3103.T", "3105.T", "3289.T", "3382.T", "3401.T", "3402.T", "3405.T", "3407.T", "3436.T", "3659.T", "3861.T", "3863.T", "4004.T", "4005.T", "4021.T", "4042.T", "4043.T", "4061.T", "4063.T", "4151.T", "4183.T", "4188.T", "4208.T", "4272.T", "4324.T", "4385.T", "4452.T", "4502.T", "4503.T", "4506.T", "4507.T", "4519.T", "4523.T", "4543.T", "4568.T", "4578.T", "4661.T", "4689.T", "4704.T", "4751.T", "4755.T", "4887.T", "4901.T", "4902.T", "4911.T", "5019.T", "5020.T", "5101.T", "5108.T", "5201.T", "5202.T", "5214.T", "5232.T", "5233.T", "5301.T", "5332.T", "5333.T", "5401.T", "5406.T", "5411.T", "5541.T", "5631.T", "5703.T", "5706.T", "5707.T", "5711.T", "5713.T", "5714.T", "5802.T", "5803.T", "5901.T", "6005.T", "6098.T", "6103.T", "6113.T", "6178.T", "6201.T", "6273.T", "6301.T", "6302.T", "6305.T", "6326.T", "6361.T", "6367.T", "6471.T", "6472.T", "6473.T", "6501.T", "6503.T", "6504.T", "6506.T", "6645.T", "6674.T", "6701.T", "6702.T", "6703.T", "6723.T", "6724.T", "6752.T", "6753.T", "6758.T", "6762.T", "6770.T", "6841.T", "6857.T", "6861.T", "6902.T", "6920.T", "6952.T", "6954.T", "6971.T", "6976.T", "6981.T", "6988.T", "7003.T", "7004.T", "7011.T", "7012.T", "7013.T", "7182.T", "7186.T", "7201.T", "7202.T", "7203.T", "7205.T", "7211.T", "7261.T", "7267.T", "7269.T", "7270.T", "7272.T", "7731.T", "7733.T", "7735.T", "7741.T", "7751.T", "7752.T", "7832.T", "7911.T", "7912.T", "7951.T", "7974.T", "8001.T", "8002.T", "8015.T", "8031.T", "8035.T", "8053.T", "8058.T", "8233.T", "8252.T", "8253.T", "8267.T", "8303.T", "8304.T", "8306.T", "8308.T", "8309.T", "8316.T", "8331.T", "8354.T", "8411.T", "8601.T", "8604.T", "8628.T", "8630.T", "8697.T", "8725.T", "8750.T", "8766.T", "8795.T", "8801.T", "8802.T", "8804.T", "8830.T", "9001.T", "9005.T", "9007.T", "9008.T", "9009.T", "9020.T", "9021.T", "9022.T", "9064.T", "9101.T", "9104.T", "9107.T", "9201.T", "9202.T", "9301.T", "9412.T", "9432.T", "9433.T", "9434.T", "9501.T", "9502.T", "9503.T", "9531.T", "9532.T", "9602.T", "9613.T", "9681.T", "9735.T", "9766.T", "9843.T", "9983.T", "9984.T"]

print(f"{len(TICKERS)}銘柄の分析開始...")
hit_messages = []

for ticker in TICKERS:
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if len(df) < 30: continue
        
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df.ta.sma(length=25, append=True)
        df.ta.macd(append=True)
        df.ta.stoch(append=True)
        df.ta.rsi(length=14, append=True) # RSIを追加
        
        last = df.iloc[-1]
        price = float(last['Close'])
        
        # 厳しくした判定ロジック
        cond_sma  = price > last['SMA_25']
        cond_macd = last['MACD_12_26_9'] > last['MACDs_12_26_9']
        cond_stoc = last['STOCHk_14_3_3'] < 40
        cond_rsi  = 30 < last['RSI_14'] < 60  # RSI条件を追加（売られすぎず、加熱しすぎず）
        
        if cond_sma and cond_macd and cond_stoc and cond_rsi:
            hit_messages.append(f"【買い】{ticker}: {price:.1f}円\n利確目安: {price*1.05:.1f}円\n損切目安: {price*0.97:.1f}円")
        
        time.sleep(0.2) # 銘柄が多いので少し早く回す
    except Exception as e:
        print(f"Error {ticker}: {e}")

# LINE送信（銘柄が多い場合は分割して送信）
if not hit_messages:
    send_line_message("【日経225診断結果】\n本日の合致銘柄はありません。")
else:
    header = "【日経225診断結果】\n\n"
    current_msg = header
    for msg in hit_messages:
        if len(current_msg + msg) > 4500: # LINEの文字数制限対策
            send_line_message(current_msg)
            current_msg = header
        current_msg += msg + "\n\n"
    send_line_message(current_msg)

print("完了")
