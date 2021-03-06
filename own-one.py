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

def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    print(response)
myToken = "xoxb-3039386859121-3012140270775-9jLU5uYNKfgSrp0Gu3xMIIy8"
def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price
def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time
def get_ma10(ticker):
    """10일 5분봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=10)
    ma10 = df['close'].rolling(10).mean().iloc[-1]
    return round(ma10,2)
def get_vol(ticker):
    """거래량 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=1)
    vol = df['volume'].iloc[-1]
    return round(vol,2)
def get_ma20(ticker):
    """20일 5분봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=20)
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    return round(ma20,2)
def get_ma60(ticker):
    """60일 5분봉 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=60)
    ma60 = df['close'].rolling(60).mean().iloc[-1]
    return round(ma60,2)
def get_mbb(ticker):
    """중심선"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=20)
    mbb = df['close'].rolling(10).mean().iloc[-1]
    return round(mbb,2)
def get_std(ticker):
    """표준편차"""
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=20)
    std = df['close'].rolling(10).std().iloc[-1]
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
    df = pyupbit.get_ohlcv(ticker, interval="minute5", count=140)
    rsi = ta.momentum.rsi(df['close'], window=14)
    return round(rsi,2)
def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

condition_Total =0
condition_MA =0
condition_vol =0
cross1 =0
cross2 =0 
alarm_vol =0
condition_BB=0
coin_time=0
rsi=0
buy_status = 0
loss_target =0
earn_target=0
buy_price=0

access = "FICHOGCS0LF4s7mQXxJJLsl4k6CZrTlmJF9gX6gz"          
secret = "sOxljDJS0ZxJVEkzBuqBWz0MZM4szO1rUazoc92O"  
upbit = pyupbit.Upbit(access,secret)

while True:
    try:
        now = datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + timedelta(days=1)

        if start_time < now < end_time - timedelta(seconds=20):
                       
             ma10 = get_ma10("KRW-BTC")
             ma20 = get_ma20("KRW-BTC")
             ma60 = get_ma60("KRW-BTC")
             current_price = get_current_price("KRW-BTC")
             vol = get_vol("KRW-BTC")

             #매수 조건 List
             if vol>5:
                 condition_vol = 1
             else : 
                 condition_vol = 0
             if ma10 < current_price and ma20 < ma10 and ma60 < ma20:
                 condition_MA =1
             else :
                 condition_MA =0
             if current_price<get_lbb("KRW-BTC") :
                 condition_BB =1
             else :
                 condition_BB = 0

             #매수 조건
             condition_Total = (condition_vol * condition_MA) + (condition_vol * condition_BB)
            
             df = pd.DataFrame(upbit.get_balances())
             #print(df)
             length = len(df.index)
             money = float(df.iloc[0]['balance'])
             #for i in "KRW" :#range(1,length):
             #money = money + float(df.iloc[1]['balance'])*float(df.iloc[1]['avg_buy_price'])

             buymessage = "\n\n비트코인\n매수 조건 거래량 / 이동평균선 / 볼린져밴드 : %d / %d / %d \n 매수의견 : %d \n 잔액 : %d KRW" %(condition_vol, condition_MA, condition_BB, condition_Total, money)
             print(buymessage)      
             krw = upbit.get_balances("KRW")        
             
              #조건 달성시 매수 행동
             if buy_status == 0 and condition_Total>0:
                buymessage = "매수\n구매평단가 : %0.1f" %(current_price)
                post_message(myToken,"#auto",buymessage)
                # buymessage = time.ctime()
                # post_message(myToken,"#auto",buymessage)
                buymessage = "비트코인\n매수 조건 거래량 / 이동평균선 / 볼린져밴드 : %d / %d / %d \n 매수의견 : %d \n 잔액 : %d KRW" %(condition_vol, condition_MA, condition_BB, condition_Total, money)
                post_message(myToken,"#auto",buymessage)
                buy_status = 1
                loss_target = current_price * 0.99
                earn_target = current_price * 1.005
                buy_price = current_price
                ######if krw > 5000:
                ######    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        

             elif buy_status == 1 :
                if current_price < loss_target:
                        buymessage = "손절, \n구매가 : %0.1f\n판매가: %0.1f" %(buy_price, current_price)
                        post_message(myToken,"#auto",buymessage)
                        buy_status = 0
                        #####btc = upbit.get_balances("BTC")
                        #####if btc > 0.00008:
                        #####upbit.sell_market_order("KRW-BTC", btc*0.9995)
                elif current_price > earn_target:
                        buymessage = "익절, \n구매가: %0.1f\n판매가: %0.1f" %(buy_price, current_price)
                        post_message(myToken,"#auto",buymessage)
                        buy_status = 0
                        #####btc = upbit.get_balances("BTC")
                        #####if btc > 0.00008:
                        #####upbit.sell_market_order("KRW-BTC", btc*0.9995)

             print('비트코인 구매여부', buy_status)
             print('비트코인 현재가격', current_price)
             print('구매가', buy_price)
             print('손절가', loss_target)
             print('익절가', earn_target)

        time.sleep(10)

    except Exception as e:
        print(e)
        time.sleep(1)
