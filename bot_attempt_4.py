import requests
import json
import alpaca_trade_api as tradeapi
import datetime
import time
import pytz

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

APCA_API_KEY_ID = 'PKCMP2FAA67V51UNW5PB'
APCA_API_SECRET_KEY = 'PzNILg337BbrNzLNst6Ycmo4XBOjewDPDyzG8JPi'

trading_client = TradingClient(APCA_API_KEY_ID,
                               APCA_API_SECRET_KEY,
                               paper=True)
api = tradeapi.REST(key_id=APCA_API_KEY_ID,
                    secret_key=APCA_API_SECRET_KEY,
                    base_url='https://paper-api.alpaca.markets',
                    api_version='v2')

#Alphavantage API
key_alpha = '5P7JV2JO5S4TYZ9P'
key_12 = '8515b571558e4c368b34611f1b43e31e'
key_12_2 = 'dba34346238c4f158ed7680a219d0d23'
intrvl = '5min'
tkr = 'AAPL'

def TI_req():
  data = []
  data.append(requests.get(
        'https://api.twelvedata.com/macd?symbol=%s&interval=%s&apikey=%s' %
        (tkr, intrvl, key_12)).json())
  data.append(requests.get(
        'https://api.twelvedata.com/rsi?symbol=%s&interval=%s&apikey=%s' %
        (tkr, intrvl, key_12)).json())
  data.append(requests.get(
        'https://api.twelvedata.com/ema?symbol=%s&interval=%s&apikey=%s' %
        (tkr, intrvl, key_12)).json())
  data.append(requests.get(
        'https://api.twelvedata.com/time_series?symbol=%s&interval=%s&apikey=%s'
        % (tkr, intrvl, key_12)).json())
  return data

# returns long if MACD histogram is >= .2, RSI < 30, and the current asset price is less than the EMA
def long(TI_list):
  
  dp_macdH = float(TI_list[0]['values'][0]['macd_hist'])
  dp_rsi   = float(TI_list[1]['values'][0]['rsi'])
  dp_ema   = float(TI_list[2]['values'][0]['ema'])
  dp_price = float(TI_list[3]['values'][0]['close'])

  print("dp_macdH: " + str(dp_macdH))
  print("dp_rsi: " + str(dp_rsi))
  print("dp_ema: " + str(dp_ema))
  print("dp_price: " + str(dp_price))

  return ((dp_macdH >= 0.2) and (dp_rsi < 30.0) and (dp_price < dp_ema))
  
count = 0
while (True):
    
  TI = TI_req()
  if (long(TI)):
    price = float(TI_req[3]['values'][0]['close'])
    api.submit_order(symbol=tkr,
                         qty=1,
                         side='buy',
                         type='market',
                         time_in_force='gtc',
                         order_class='bracket',
                         stop_loss={
                             'stop_price': price * 0.95,
                             'limit_price': price * 0.94
                         },
                         take_profit={'limit_price': price * 1.05})
    print("trade taken")
    flag = True
    while (flag):
      position = api.get_open_position(tkr)
      if len(position) == 1:
        time.sleep(300)
      else:
        flag = False
  else:
    print("Loop: " + str(count))
    time.sleep(300)
    count += 1
    

