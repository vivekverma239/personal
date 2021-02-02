import talib
import django
import os
import json 
from talib.abstract import *
from talib import MA_Type
import numpy as np
from django.db import transaction
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "experiments.settings")
django.setup()
from core.models import StockData
from core.utils import load_constants
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
import xgboost as xgb
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import pandas as pd 
import pickle

from core.models import StrategySignal
from core.utils.strategy import compute_features

def _compute_target(data):
    returns = lambda x: (x.max() - x.iloc[0]) / x.iloc[0]
    data['target'] = data.close.rolling(10).apply(returns)
    data["target"] = data['target'].apply(lambda x: 1 if x > 0.005 else 0)
    return data

def get_features(stocks=None, start_date=None, end_date=None, res='1d'):
  if not stocks: 
    stocks = load_constants('stock')["data"]["list"]
  train_dfs = []
  test_dfs = []
  for stock in stocks:
    queryset = StockData.objects.filter(stock_symbol=stock, res=res).all().order_by('datetime')
    data = {'datetime': [], 'open': [], 'close': [], 'low': [], 'high': [], 'volume': []}
    for item in queryset: 
      data['datetime'].append(item.datetime)
      data['open'].append(float(item.open))
      data['close'].append(float(item.close))
      data['low'].append(float(item.low))
      data['high'].append(float(item.high))
      data['volume'].append(float(item.volume))

    data = pd.DataFrame(data)
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
    count = int(0.7* len(data))
    data = _compute_target(data)
    print(data['target'].value_counts())
    train_idx = len(data)
    train_df , test_df = data.iloc[:train_idx-100], data.iloc[train_idx-100:]
    train_dfs.append(train_df)
    test_dfs.append(test_df)

  train_df = pd.concat(train_dfs)
  test_df = pd.concat(test_dfs)
  return train_df, test_df

def main(res='60m'): 
  cols = ['volume', 'adx',
       'cci', 'mom', 'ppo', 'macd', 'macdsignal', 'macdhist', 'rocp', 'rsi',
       'srsi_fastk', 'srsi_fastd', 'srsi_diff', 'bb_upper', 'bb_middle',
       'bb_lower', 'cho_1', 'cho_2', 'cho_3', 'cho_4', 'cho_5', 'cho_6', 'cho_7',]
  # train_df, test_df = get_features(res=res)
  # print(test_df['datetime'].min())
  # X_train,  X_val, y_train, y_val = train_df[cols].values, test_df[cols].values, train_df['target'].values, test_df['target'].values
  # model = xgb.XGBClassifier()
  # model.fit(X_train, y_train)
  # y_train_pred = model.predict(X_train)
  # y_pred = model.predict(X_val)

  # print(classification_report(y_train, y_train_pred))
  # print(classification_report(y_val, y_pred))
  # pickle.dump(model, open('data/models/ml_{}.pkl'.format(res), 'wb'))
  model = pickle.load(open('data/models/ml_{}.pkl'.format(res), 'rb'))
  stocks = load_constants('stock')["data"]["list"]
  for stock in stocks:
    queryset = StockData.objects.filter(stock_symbol=stock, res=res).all().order_by('datetime')
    data = {'datetime': [], 'open': [], 'close': [], 'low': [], 'high': [], 'volume': []}
    for item in queryset: 
      data['datetime'].append(item.datetime)
      data['open'].append(float(item.open))
      data['close'].append(float(item.close))
      data['low'].append(float(item.low))
      data['high'].append(float(item.high))
      data['volume'].append(float(item.volume))
    data = pd.DataFrame(data)
    data = compute_features(data)
    data['datetime'] = data['datetime'].map(lambda x : x.strftime("%Y-%m-%d %H:%MZ"))
    features = data[cols].values 
    data['score'] = model.predict_proba(features)[:, 1]

    records = json.loads(data.to_json(orient='records'))
    for item in records: 
      StrategySignal(data=item, datetime=item['datetime'], stock_symbol=stock,\
        strategy_name='ml_{}'.format(res), res=res, score=item['score'], signal="SOME").save()


if __name__ == '__main__':
  StrategySignal.objects.all().delete()
  main('1m')
  # main('5m')
  # main('30m')
  # main('60m')
  # main('1d')




