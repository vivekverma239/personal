import os
import yfinance as yf
import time 
from datetime import datetime, timedelta
from tqdm import tqdm 
import talib
from talib.abstract import *
from talib import MA_Type

def load_data(stock, res='1d', allowed_delta_days=None):
  allowed_delta_days = allowed_delta_days
  if res=='1m':
    allowed_delta_days = 7
  elif res == '5m' or res == '15m' or res == '30m':
    allowed_delta_days = 59
  elif res == '60m':
    allowed_delta_days = 729
  
  end_date = datetime.now()
  if not allowed_delta_days :
    start_date = datetime.strptime("2001-01-01", "%Y-%m-%d")
  else:
    start_date = end_date - timedelta(days=allowed_delta_days)

  start_date_temp = start_date.strftime("%Y-%m-%d")
  end_date_temp = end_date.strftime("%Y-%m-%d")
  data = yf.download("{}.NS".format(stock), start=start_date_temp, end=end_date_temp, interval=res)
  data['res'] = [res] * len(data)
  data['stock_symbol'] = [stock] * len(data)
  data.dropna(inplace=True)
  data.reset_index(inplace=True)
  if 'Datetime' in data.columns: 
      data['Datetime'] = data['Datetime'].apply(lambda x: x.strftime("%Y-%m-%d %H:%MZ"))
  else:
      data['Datetime'] = data['Date'].apply(lambda x: x.strftime("%Y-%m-%d %H:%MZ"))
      data.drop('Date', inplace=True, axis=1)

  data.columns = [i.replace(" ", "_").lower() for i in data.columns]
  data = json.loads(data.to_json(orient='records'))
  bulk = []
  for item in data: 
    item['close'] = item['adj_close']
    item.pop('adj_close', None)
    # print(item)
    StockData(**item)
  StockData.objects.bulk_create(bulk)
