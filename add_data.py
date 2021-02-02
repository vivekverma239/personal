import yfinance as yf
import time 
from datetime import datetime, timedelta
from tqdm import tqdm 
import time 
from app import db
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
engine = create_engine('sqlite:///college.db', echo = True)

conn = engine.connect()


interval_to_db = {'1d': 'STOCK_DATA_RES_1D', '5m': 'STOCK_DATA_RES_5M', '15m': 'STOCK_DATA_RES_15M', 
                  '30m': 'STOCK_DATA_RES_30M', '60m': 'STOCK_DATA_RES_1H',  '1m': 'STOCK_DATA_RES_1M',}

def load_data(stock, res='1d'):
  allowed_delta_days = None
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

  db = interval_to_db[res]


  start_date_temp = start_date.strftime("%Y-%m-%d")
  end_date_temp = end_date.strftime("%Y-%m-%d")
  data = yf.download("{}.NS".format(stock), start=start_date_temp, end=end_date_temp, interval=res)
  data['Stock'] = [stock] * len(data)
  data.columns = [i.replace(" ", "_") for i in data.columns]
  # data.to_sql(db, conn, if_exists='append')
  return data

def main():
    for stock in tqdm(stocks):
        load_data(stock,  res='1m')
        time.sleep(2)
        load_data(stock,  res='5m')
        time.sleep(2)
        load_data(stock,  res='30m')
        time.sleep(2)
        load_data(stock,  res='60m')
        time.sleep(2)
        load_data(stock,  res='1d')
        time.sleep(2)


if __name__ == '__main__':
    main()