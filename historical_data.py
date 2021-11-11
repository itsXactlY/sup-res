from binance import Client
import csv
import binance_api
import pandas as pd
import datetime
import time

duration = 1000  # milliseconds
freq = 440  # Hz

client = Client(binance_api.api, binance_api.secret)  # Your Binance api and secret key
symbol_list = ["BTCUSDT"]
headerList = ['unix', 'open', 'high', 'low', 'close', 'volume', 'close time', 'quote asset volume', 'number of trades',
              'taker buy vol', 'takerbuy quote vol', 'ignore']


def historical_Data_Write():
    csvFileW = open(symbol + "btc.csv", "w", newline='')
    klines_writer = csv.writer(csvFileW, delimiter=",")

    for candlestick in candlesticks:
        klines_writer.writerow(candlestick)

    csvFileW.close()
    df = pd.read_csv(symbol + "btc.csv")
    df.to_csv(symbol + "btc.csv", header=headerList, index=False)
    df = pd.read_csv(symbol + "btc.csv")
    df['unix'] = pd.to_datetime(df['unix'], unit='ms')
    print(df.head(10))
    df.to_csv(symbol + "btc.csv", index=False)


for symbol in symbol_list:
    print("Data writing: ", symbol)
    candlesticks = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR,
                                                "2 November, 2021")  # KLINE_INTERVAL_1DAY= '1d'
    historical_Data_Write()
