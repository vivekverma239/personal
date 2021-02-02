import time 
from tqdm import tqdm 
import yfinance as yf
from datetime import datetime, timedelta
from core.models import Constant
from core.serializers import ConstantSerializer

def load_data_db(stock, res): 
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
    return data

# def load_data(stock, res='1d'):
#   allowed_delta_days = None
#   if res=='1m':
#     allowed_delta_days = 7
#   elif res == '5m' or res == '15m' or res == '30m':
#     allowed_delta_days = 59
#   elif res == '60m':
#     allowed_delta_days = 729
  
#   end_date = datetime.now()
#   if not allowed_delta_days :
#     start_date = datetime.strptime("2001-01-01", "%Y-%m-%d")
#   else:
#     start_date = end_date - timedelta(days=allowed_delta_days)

#   start_date_temp = start_date.strftime("%Y-%m-%d")
#   end_date_temp = end_date.strftime("%Y-%m-%d")
#   data = yf.download("{}.NS".format(stock), start=start_date_temp, end=end_date_temp, interval=res)
#   data['res'] = [res] * len(data)
#   data['stock_symbol'] = [stock] * len(data)
#   data.columns = [i.replace(" ", "_").lower() for i in data.columns]
#   return data

def load_constants(key):
    item = Constant.objects.get(key=key)
    return ConstantSerializer(item).data
