from logging import Filter
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters  # import modules
import telegram
#import bot_api
import time
import ccxt
import pandas as pd
import ta.momentum
import ta.trend
import ta.volatility
import ta.volume
import pprint
from binance.client import Client

###텔레그램 설정###
my_token = '5267562862:AAHjhH5u95Fh5uGDMcvWwpnirvmi6aiCEsE'
chat_id = '5267710018'
bot = telegram.Bot(token=my_token)
###바이낸스 설정###
api_key = 'O7JKt8CBROEq5GNsg5wIzeKnhXJDSyIGyaPd0L4Va3f5MAvyR9C7EL9W0sNLUlI7'
secret = 'BpwI9mDrDIjIMQA0NWgYhMeerTPTaCAgJcXSItSkI3lun8X7uvJSBrPizs263gJo'
binance = ccxt.binance(config={'apiKey': api_key, 'secret' : secret, 'options':{'defaultType':'future'}})
client = Client(api_key=api_key, api_secret=secret)
###RSI Line 설정###
rsi_Low = 40
rsi_High = 60
### 레버리지 설정 ###
markets = binance.load_markets()
symbol = "BTC/USDT"
market = binance.market(symbol)
leverage = 50
resp = binance.fapiPrivate_post_leverage({'symbol': market['id'],'leverage': leverage})

### 초기화 ###
position = "관망"
action = "관망"
alarm = 0

## 메인 루프 ##
while True:
    try:

### RSI 연산 ###
        btc = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe='15m', since=None, limit=140)
        df = pd.DataFrame(data = btc, columns=['datetime','open','high','low','close','volume'])
        df['datetime']=pd.to_datetime(df['datetime'],unit='ms')
        rsi = ta.momentum.rsi(df['close'], window=14)
        
### RSI Data 저장 ###
        rsi_past = round(rsi[138],2)
        rsi_now = round(rsi[139],2)
        
### 현재가 ###
        now = ccxt.binance()
        ticker = now.fetch_ticker("BTC/USDT")
        print(ticker['close'])

### 현재 포지션 확인 ###
        
### No Position ###
        #if position == "관망":
          ### RSI Data 비교 ###
          ### 매수 Order ### 1 = Long
        if rsi_past<rsi_Low and rsi_Low < rsi_now :
           action = "매수"
           #(매수 주문)
           order = binance.create_market_buy_order(symbol="BTC/USDT",amount=0.01)
           position = "Long" 
           alarm = 1

          ### 매도 Order ### 2 = Short
        elif rsi_past>rsi_High and rsi_High>rsi_now :
           action = "매도"
           #(매도 주문)
           order = binance.create_market_sell_order(symbol="BTC/USDT",amount=0.01)
           position = "Short"
           alarm = 1

          ### 관망 ### 3 = No position
        else :
           action = "관망"
           position = "관망"
           alarm = 0

### Long Position ###
        #if position == "Long":
  ### 유지 ###
  ### 청산 ###
          # if rsi_past>rsi_High and rsi_High>rsi_now :
          #   action = "매도"
          #   #(매도 주문)
          #   order = binance.create_market_sell_order(symbol="BTC/USDT",amount=0.001)
          #   position = "Short"
          #   order = binance.create_market_sell_order(symbol="BTC/USDT",amount=0.001)
          #   alarm = 1

### Short Position ###
        #if position == "Short":
  ### 유지 ###
  ### 청산 ###
          # if rsi_past<rsi_Low and rsi_Low < rsi_now :
          #   action = "매수"
          #   #(매수 주문)
          #   order = binance.create_market_buy_order(symbol="BTC/USDT",amount=0.001)
          #   position = "Long" 
          #   order = binance.create_market_buy_order(symbol="BTC/USDT",amount=0.001)
          #   alarm = 1

### 텔레그램 메시지 전송 ###
          ### Monitoring ###
        Mess_1 = 'Last action : ' + action 
        Mess_2 = 'RSI : %0.2f -> %0.2f' %(rsi_past,rsi_now)
        balance = binance.fetch_balance()
        #Mess_4 = 'USDT 잔액 : %f' %(balance['USDT'])
        #pprint.pprint(str(Mess_1))
        pprint.pprint(str(Mess_2))
        pprint.pprint(balance['USDT'])
        #bot.sendMessage(chat_id=chat_id, text=str(Mess_1))
        bot.sendMessage(chat_id=chat_id, text=str(Mess_2))
        bot.sendMessage(chat_id=chat_id, text=balance['USDT'])
        #bot.sendMessage(chat_id=chat_id, text=ticker['close'])

          ### Event ###
        if alarm ==1:
          bot.sendMessage(chat_id=chat_id, text=str(Mess_1))
          bot.sendMessage(chat_id=chat_id, text=str(Mess_2))
          bot.sendMessage(chat_id=chat_id, text=balance['USDT'])
          balance_pos = binance.fetch_balance()
          positions = balance_pos['info']['positions']
          for position2 in positions:
            if position2["symbol"] == "BTCUSDT":
             Mess_3 = '@@@@@@@@거래 가격 : ' + position2['entryPrice']
             bot.sendMessage(chat_id=chat_id, text=str(Mess_3))
             #bot.sendMessage(chat_id=chat_id, text=position2['unrealizedProfit'])
          alarm = 0

          ### 대화형 ###

        #df.to_excel("220329.xlsx")
        time.sleep(300)

## 메인 루프 예외 처리 ##
    except Exception as e:
        print("Error Occur")
        print(e)
        time.sleep(120)