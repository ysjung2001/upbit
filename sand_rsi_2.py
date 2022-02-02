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
myToken = "xoxb-3039386859121-3012140270775-EPHGuBjrzdiuDv0da2pgsVFp"
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
    return round(rsi[139],2)
def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

condition_Total1 =0
condition_Total2 =0
condition_MA =0
condition_vol =0
condition_rsi_l =0
condition_rsi_h =0
cross1 =0
cross2 =0 
alarm_vol =0
condition_BB=0
coin_time=0
rsi= 0
buy_status = 0
buy_mode = 0
loss_target = 0
earn_target= 0
buy_price= 0

access = "FICHOGCS0LF4s7mQXxJJLsl4k6CZrTlmJF9gX6gz"          
secret = "sOxljDJS0ZxJVEkzBuqBWz0MZM4szO1rUazoc92O"  
upbit = pyupbit.Upbit(access,secret)

while True:
    try:
        now = datetime.now()
        start_time = get_start_time("KRW-SAND")
        end_time = start_time + timedelta(days=1)

        if start_time < now < end_time - timedelta(seconds=20):
                       
             ma10 = get_ma10("KRW-SAND")
             ma20 = get_ma20("KRW-SAND")
             ma60 = get_ma60("KRW-SAND")
             current_price = get_current_price("KRW-SAND")
             vol = get_vol("KRW-SAND")
             rsi = get_rsi("KRW-SAND")

             #매수 조건 List
             if vol>200000:
                 condition_vol = 1
             else : 
                 condition_vol = 0
             if  ma20 < ma10 and ma60 < ma20:#ma10 > current_price and
                 condition_MA =1
             else :
                 condition_MA =0
             if current_price<get_lbb("KRW-SAND") :
                 condition_BB =1
             else :
                 condition_BB = 0
             if rsi<30:
                 condition_rsi_l =1
             else :
                 condition_rsi_l =0
             if rsi>70:
                 condition_rsi_h =1
             else :
                 condition_rsi_h =0

             #매수 조건
             condition_Total1 = condition_rsi_l
             condition_Tatal2 = condition_BB

             #잔액
             df = pd.DataFrame(upbit.get_balances())
             length = len(df.index)
             money = float(df.iloc[0]['balance'])

             #Monitoring Message
             #1
             buymessage = "\n---------------------------------------\n[[  샌드박스(SAND) Monitoring  ]]\n 정배열 / 거래량 / BB하단 / RSI \n    %d   / %d /    %d  /  %d \n[[       잔액 : %d KRW      ]]" %(condition_MA, vol, condition_BB, get_rsi("KRW-SAND"), money)
             print(buymessage)         
             post_message(myToken,"#monitor",buymessage)
             #2 구매한 경우의 상태 Report
             if buy_status == 1 :
              buymessage = "\n\n구매 Stauts\n구매가 / 현재가 / 익절가 / 손절가 : %d / %d / %d / %d \n 잔액 : %d KRW" %(buy_price, current_price, earn_target, loss_target, money)
              print(buymessage)         
              post_message(myToken,"#monitor",buymessage)
              buymessage = "구매 mode : %d" %(buy_mode)
              print(buymessage)         
              post_message(myToken,"#monitor",buymessage)
              
             #조건 달성시 매수 행동
             if buy_status == 0 :
                #구매조건 1 - RSI
                if condition_Total1 ==1:
                    #실제 구매 행동
                    if money > 5000:
                       upbit.buy_market_order("KRW-SAND", money*0.9)
                       buymessage = "조건 1 매수\n구매평단가 : %0.1f" %(current_price)
                       post_message(myToken,"#auto",buymessage)
                       buymessage = time.ctime()
                       post_message(myToken,"#auto",buymessage)
                       buymessage = "잔액 : %d KRW" %(money)
                       post_message(myToken,"#auto",buymessage)
                       #손절가 익절가 세팅
                       loss_target = current_price * 0.98
                       earn_target = current_price * 10
                       buy_price = current_price
                       buy_mode = 1
                       buy_status = 1
                #구매조건 2 - BB
                elif condition_Total2 ==1:
                    #실제 구매 행동
                    if money > 5000:
                       upbit.buy_market_order("KRW-SAND", money*0.9)
                       buymessage = "조건 2 매수\n구매평단가 : %0.1f" %(current_price)
                       post_message(myToken,"#auto",buymessage)
                       buymessage = time.ctime()
                       post_message(myToken,"#auto",buymessage)
                       buymessage = "잔액 : %d KRW" %(money)
                       post_message(myToken,"#auto",buymessage)
                       #손절가 익절가 세팅
                       loss_target = current_price * 0.98
                       earn_target = current_price * 1.008
                       buy_price = current_price
                       buy_mode = 2
                       buy_status = 1
              
             #매도 행동
             elif buy_status == 1 :
                sand = float(df.loc[df['currency']=='SAND','balance'])
                # case 1 매도
                if buy_mode ==1:
                    # case 1 매도 - 익절
                    if condition_rsi_h ==1:
                        if sand > 1.5:
                             upbit.sell_market_order("KRW-SAND", sand*0.995)
                             buymessage = "case 1 (RSI) 익절, \n구매가 : %0.1f\n판매가: %0.1f" %(buy_price, current_price)
                             post_message(myToken,"#auto",buymessage)
                             buy_mode = 0
                             buy_status = 0
                    # case 1 매도 - 손절
                    elif current_price < loss_target :
                        if sand > 1.5:
                             upbit.sell_market_order("KRW-SAND", sand*0.995)
                             buymessage = "case 1 (RSI) 손절, \n구매가 : %0.1f\n판매가: %0.1f" %(buy_price, current_price)
                             post_message(myToken,"#auto",buymessage)
                             buy_mode = 0
                             buy_status = 0
                # case 2 매도
                if buy_mode ==2:
                    # case 2 매도 - 익절
                    if (condition_rsi_h ==1) or (earn_target <current_price):
                        if sand > 1.5:
                             upbit.sell_market_order("KRW-SAND", sand*0.995)
                             buymessage = "case 2 (BB) 익절, \n구매가 : %0.1f\n판매가: %0.1f" %(buy_price, current_price)
                             post_message(myToken,"#auto",buymessage)
                             buy_mode = 0
                             buy_status = 0
                    # case 2 매도 - 손절
                    elif current_price < loss_target :
                        if sand > 1.5:
                             upbit.sell_market_order("KRW-SAND", sand*0.995)
                             buymessage = "case 2 (BB) 손절, \n구매가 : %0.1f\n판매가: %0.1f" %(buy_price, current_price)
                             post_message(myToken,"#auto",buymessage)
                             buy_mode = 0
                             buy_status = 0
         
        time.sleep(3)

    except Exception as e:
        print(e)
        time.sleep(1)
