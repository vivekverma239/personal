import os
import talib
from talib.abstract import *
from talib import MA_Type
import pandas as pd 
import numpy as np 

STRATEGY_CONFIG = {}

def compute_features(data): 
    high, close, low = data['high'], data['close'], data['low']
    average = MA(close, 200)
    data["adx"] = ADX(high, low, close, timeperiod=14)
    data["cci"] = CCI(high, low, close, timeperiod=14)
    mom = MOM(close, timeperiod=10)
    data["mom"] = np.divide(mom, average)
    data["ppo"] = PPO(close, fastperiod=12, slowperiod=26, matype=0)
    macd, macdsignal, macdhist = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    data["macd"] = np.divide(macd, average)
    data["macdsignal"] = np.divide(macdsignal, average)
    data["macdhist"] = np.divide(macdhist, average)
    data["rocp"] = ROCP(close, timeperiod=10)
    data["rsi"] = RSI(close, timeperiod=14)
    fastk, fastd = STOCHRSI(close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
    data["srsi_fastk"] = fastk
    data["srsi_fastd"] = fastd
    data["srsi_diff"] = fastk - fastd
    upper, middle, lower = talib.BBANDS(close, matype=MA_Type.T3)
    data["bb_upper"] = np.divide(upper - close, average)
    data["bb_middle"] = np.divide(middle - close, average)
    data["bb_lower"] = np.divide(lower - close, average)
    data["cho_1"] = np.divide(EMA(close, timeperiod=3) - EMA(close, timeperiod=5), average)
    data["cho_2"] = np.divide(EMA(close, timeperiod=3) - EMA(close, timeperiod=7), average)
    data["cho_3"] = np.divide(EMA(close, timeperiod=3) - EMA(close, timeperiod=10), average)
    data["cho_4"] = np.divide(EMA(close, timeperiod=3) - EMA(close, timeperiod=20), average)
    data["cho_5"] = np.divide(EMA(close, timeperiod=3) - EMA(close, timeperiod=30), average)
    data["cho_6"] = np.divide(EMA(close, timeperiod=3) - EMA(close, timeperiod=50), average)
    data["cho_7"] = np.divide(EMA(close, timeperiod=3) - EMA(close, timeperiod=100), average)
    return data

def predict_signal(data, stategy, res): 
    pass 