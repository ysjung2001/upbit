import pyupbit
import numpy as np
import time
from datetime import datetime
import pandas as pd
import requests
from datetime import timedelta
import ta.momentum
import ta.trend
import ta.volatility
import ta.volume
from pyupbit.exchange_api import Upbit
from logging import Filter
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters  # import modules
import telegram
import ccxt
import pprint
from binance.client import Client

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)
def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time
def get_ma10(ticker):
    """10일 5분봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=10)
    ma10 = df['close'].rolling(10).mean().iloc[-1]
    return round(ma10,2)
def get_vol(ticker):
    """거래량 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=1)
    vol = df['volume'].iloc[-1]
    return round(vol,2)
def get_ma20(ticker):
    """20일 5분봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=20)
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    return round(ma20,2)
def get_ma60(ticker):
    """60일 5분봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=60)
    ma60 = df['close'].rolling(60).mean().iloc[-1]
    return round(ma60,2)
def get_mbb(ticker):
    """중심선"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=20)
    mbb = df['close'].rolling(20).mean().iloc[-1]
    return round(mbb,2)
def get_std(ticker):
    """표준편차"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=20)
    std = df['close'].rolling(20).std().iloc[-1]
    return round(std,2)
def get_ubb(ticker):
    """ubb표준편차"""
    ubb = get_mbb(ticker) + 2*get_std(ticker)
    return round(ubb,2)
def get_lbb(ticker):
    """lbb표준편차"""
    lbb = get_mbb(ticker) - 2*get_std(ticker)
    return round(lbb,2)
def get_rsi(ticker):
    """rsi"""
    df = pyupbit.get_ohlcv(ticker, interval="minute15", count=140)
    rsi = ta.momentum.rsi(df['close'], window=14)
    return round(rsi[139],2)
def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]
def applytechnicals(df):
    df = pd.DataFrame(df)
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['UBB'] = df['close'].rolling(20).mean().iloc[-1] + 2*(df['close'].rolling(20).std().iloc[-1])
    df['LBB'] = df['close'].rolling(20).mean().iloc[-1] - 2*(df['close'].rolling(20).std().iloc[-1])

    return df
def value_identifyer(line):
    coins = pyupbit.get_tickers(fiat="KRW")
    
    proper_coins = []

    dfx = pd.DataFrame(index=coins, columns=['value'])

    for coin in coins :
        time.sleep(0.1)
        dfx.loc[coin]['value'] = pd.DataFrame(pyupbit.get_ohlcv(coin,"day",count =2)).iloc[-1]['value']

    dfx = dfx.sort_values(by = 'value', ascending=False)

    proper_coins = dfx.index[0:line]

    return proper_coins
def get_coin_info(df_master,alt_duration):
    df_master = pd.DataFrame(df_master)
    #coins=df_master.columns
    #for coin in coins:
    coin = "KRW-BTC"
    df = pyupbit.get_ohlcv(coin, alt_duration,210)
    df = applytechnicals(df)

    df_master[coin].loc['Current'] = df.iloc[-1]['close']
    df_master[coin].loc['RSI'] = df.iloc[-1]['RSI']
    df_master[coin].loc['UBB'] = df.iloc[-1]['UBB']
    df_master[coin].loc['LBB'] = df.iloc[-1]['LBB']
    if (df.iloc[-1]['RSI'] > 40) and (df.iloc[-2]['RSI'] < 40):
        df_master[coin].loc['Buy'] = 1
    else:
        df_master[coin].loc['Buy'] = 0
    if (df.iloc[-1]['RSI'] < 60) and (df.iloc[-2]['RSI']>60):
        df_master[coin].loc['Sell'] = 1
    else:
        df_master[coin].loc['Sell'] = 0

    return df_master
def alarm_u(df):
    df=pd.DataFrame(df)
    coins=df.columns
    for coin in coins:
        if df[coin].loc['RSI'] < 35:
            #post_message(myToken,"#auto",coin+" / RSI Low")
            df[coin].loc['Status'] = 1
            print("RSI Low")
        if df[coin].loc['RSI'] > 65:
            #post_message(myToken,"#auto",coin+" / RSI High")
            df[coin].loc['Status'] = 2
            print("RSI High")
        if df[coin].loc['Current'] > df[coin].loc['UBB']:
            #post_message(myToken,"#auto",coin+" / UBB")
            df[coin].loc['Status'] = 3
            print("UBB")
        if df[coin].loc['Current'] < df[coin].loc['LBB']:
            #post_message(myToken,"#auto",coin+" / LBB")
            df[coin].loc['Status'] = 4
            print("LBB")
        if df[coin].loc['Buy'] == 1:
            Buy_Mess = "Buy : %d\n" %(df[coin].loc['Current'])
            post_message(myToken,"#auto",Buy_Mess)
            upbit.buy_market_order("KRW-BTC", 20000)
            df[coin].loc['Buy'] = 0

        if df[coin].loc['Sell'] == 1:
            Sell_Mess = "Sell : %d\n" %(df[coin].loc['Current'])
            post_message(myToken,"#auto",Sell_Mess)
            #?? = pd.DataFrame(upbit.get_balances())
            #bal_BTC = float(??.loc[??['currency']=='BTC','balance'])
            upbit.sell_market_order("KRW-BTC", 0.0004)
            df[coin].loc['Sell'] = 0
    
    return df

####업비트 설정#####################
myToken = "xoxb-3039386859121-3012140270775-nAPsSpFiWk92sOPU884Q3Wpk"
alt_duration = "minute15"
amount_monitor = 5
#coins = value_identifyer(amount_monitor)
df_master = pd.DataFrame(columns=['KRW-BTC'], index=['Current','RSI','UBB','LBB','Status','Buy','Sell'])
access_u = "FICHOGCS0LF4s7mQXxJJLsl4k6CZrTlmJF9gX6gz"          
secret_u = "sOxljDJS0ZxJVEkzBuqBWz0MZM4szO1rUazoc92O"  
upbit = pyupbit.Upbit(access_u,secret_u)
##################################


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
rsi_Low = 35
rsi_High = 65
### 레버리지 설정 ###
markets = binance.load_markets()
symbol = "BTC/USDT"
market = binance.market(symbol)
leverage = 25
resp = binance.fapiPrivate_post_leverage({'symbol': market['id'],'leverage': leverage})

### 초기화 ###
position = "관망"
action = "관망"
alarm = 0





## 메인 루프 ##
while True:
    try:

### RSI 연산 ###
        btc = binance.fetch_ohlcv(symbol="BTC/USDT", timeframe='1m', since=None, limit=140)
        df = pd.DataFrame(data = btc, columns=['datetime','open','high','low','close','volume'])
        df['datetime']=pd.to_datetime(df['datetime'],unit='ms')
        rsi = ta.momentum.rsi(df['close'], window=14)
        
### RSI Data 저장 ###
        rsi_past = round(rsi[138],2)
        rsi_now = round(rsi[139],2)
        
### 현재 포지션 확인 ###
        
### No Position ###
        if position == "관망":
          ### RSI Data 비교 ###
          ### 매수 Order ### 1 = Long
          if rsi_past<rsi_Low and rsi_Low < rsi_now :
           action = "매수"
           #(매수 주문)
           order = binance.create_market_buy_order(symbol="BTC/USDT",amount=0.001)
           position = "Long" 
           alarm = 1

          ### 매도 Order ### 2 = Short
          elif rsi_past>rsi_High and rsi_High>rsi_now :
           action = "매도"
           #(매도 주문)
           order = binance.create_market_sell_order(symbol="BTC/USDT",amount=0.001)
           position = "Short"
           alarm = 1

          ### 관망 ### 3 = No position
          else :
           action = "관망"
           position = "관망"
           alarm = 0

### Long Position ###
        if position == "Long":
  ### 유지 ###
  ### 청산 ###
          if rsi_past>rsi_High and rsi_High>rsi_now :
            action = "매도"
            #(매도 주문)
            order = binance.create_market_sell_order(symbol="BTC/USDT",amount=0.001)
            position = "Short"
            order = binance.create_market_sell_order(symbol="BTC/USDT",amount=0.001)
            alarm = 1

### Short Position ###
        if position == "Short":
  ### 유지 ###
  ### 청산 ###
          if rsi_past<rsi_Low and rsi_Low < rsi_now :
            action = "매수"
            #(매수 주문)
            order = binance.create_market_buy_order(symbol="BTC/USDT",amount=0.001)
            position = "Long" 
            order = binance.create_market_buy_order(symbol="BTC/USDT",amount=0.001)
            alarm = 1

### 텔레그램 메시지 전송 ###
          ### Monitoring ###
        Mess_1 = 'action : ' + action + ', Postion : ' + position
        Mess_2 = 'RSI : %0.2f -> %0.2f' %(rsi_past,rsi_now)
        balance = binance.fetch_balance()
        #Mess_4 = 'USDT 잔액 : %f' %(balance['USDT'])
        pprint.pprint(str(Mess_1))
        pprint.pprint(str(Mess_2))
        pprint.pprint(balance['USDT'])

          ### Event ###
        if alarm ==1:
          bot.sendMessage(chat_id=chat_id, text=str(Mess_1))
          bot.sendMessage(chat_id=chat_id, text=str(Mess_2))
          bot.sendMessage(chat_id=chat_id, text=balance['USDT'])
          balance_pos = binance.fetch_balance()
          positions = balance_pos['info']['positions']
          for position2 in positions:
            if position2["symbol"] == "BTCUSDT":
             Mess_3 = '거래 가격 : ' + position2['entryPrice']
             bot.sendMessage(chat_id=chat_id, text=str(Mess_3))
             #bot.sendMessage(chat_id=chat_id, text=position2['unrealizedProfit'])
          alarm = 0

          ### 대화형 ###




        ####업비트####
        now = datetime.now()
        df_master = get_coin_info(df_master,alt_duration)
        #print(df_master)
        df_master = alarm_u(df_master)
        print(df_master)
        curr_BTC = df_master['KRW-BTC'].loc['Current']
        Mess = "Online! Market Price : %d\n" %(curr_BTC) + str(now) 
        post_message(myToken,"#monitor",Mess)
        post_message(myToken,"#monitor",df_master['KRW-BTC'].loc['RSI'])

        time.sleep(30)

## 메인 루프 예외 처리 ##
    except Exception as e:
        print("Error Occur")
        print(e)
        time.sleep(120)







