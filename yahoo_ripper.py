import psycopg2
import talib
import os
import math
import pandas as pd
import numpy as np
import urllib
import urllib.request
import multiprocessing
import threading
import time
from alive_progress import alive_bar

import common

#debug
debug_one_asset = False
debug_asset = 'REPV2-USD'

debug_max_assets = False
num_assets_retrieved = 0
max_assets = 20

threading_delay = 0.1
request_delay = 0.25
max_requests = 10
cpu_count = common.getMaxThreads()
threads = []
path = common.getPath()
data_dir =  path + '/data'
conn_str = 'dbname=finance user=brower'
indicator_windows = [32, 64, 128]
indicators = ['std', 'mean', 'sharpe', 'rsi', 'ema', 't3', 'cci', 'willr', 'adx']
data_columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'adj_close', 'pct_returns']
data_countries = ['us']
data_assets = ['crypto', 'currency', 'etf', 'future', 'index', 'stock']
data_periods = ['1d']
data_paths = [data_countries, data_periods, data_assets]
url_prefix = 'https://query1.finance.yahoo.com/v7/finance/download/'
url_suffix = '&interval=1d&events=history&includeAdjustedClose=true'
period_1 = '0'
period_2 = '1602892800'

def cullThreads(numThreads = cpu_count):
    if numThreads < 0:
        numThreads = 0
    elif numThreads > cpu_count:
        numThreads = cpu_count

    while len(threads) >= numThreads:
        time.sleep(threading_delay)
        new_threads = [t for t in threads if t.is_alive()]

def isDefined(value):
    if value is None:
        return False

    try:
        return not math.isnan(value)
    except:
        return True

def buildUrl(ticker):
    period_str = urllib.parse.quote_plus(ticker) + '?period1=' + period_1 + "&period2=" + period_2
    return url_prefix + period_str + url_suffix

def getAllIndicators():
    result = []
    for i in indicators:
        for w in indicator_windows:
            result.append(i + '_' + str(w))

    result.extend(['obv', 'macd', 'macd_signal', 'macd_hist'])
    return result

def compute_indicators(df):
    close = 'Close'
    # Need to make sure all this data is stationary and normalized
    #Convert pct_returns from float64 (default) to float32 The extra precision can cause overflow issues, and is unnessecary
    df['pct_returns'] = (df[close] -  df[close].shift(1)) / df[close].shift(1)
    df['pct_returns'] = df['pct_returns'].astype(np.float32)
    #Calculate 1 week indicators

    for window in indicator_windows:
        w = str(window)
        df['std_'    + w] = df['pct_returns'].rolling(window).std()
        df['mean_'   + w] = df['pct_returns'].rolling(window).mean()
        df['sharpe_' + w] = df['mean_' + w] / df['std_' + w]
        df['rsi_'    + w] = talib.RSI(df[close], timeperiod=window)
        df['ema_'    + w] = talib.EMA(df[close], timeperiod=window)
        df['t3_'     + w] = talib.T3(df[close], timeperiod=window)
        df['cci_'    + w] = talib.CCI(df['High'], df['Low'], df[close], timeperiod=window)
        df['willr_'  + w] = talib.WILLR(df['High'], df['Low'], df[close], timeperiod=window)
        df['adx_'    + w] = talib.ADX(df['High'], df['Low'], df[close], timeperiod=window)

    df['obv'] = talib.OBV(df[close], df['Volume'])
    df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df[close])

    return df

def createDirectories(root, paths):
    #we have to do this. I don't know if it's pipenv or what but
    #os.path.exists returns true even when it shouldn't
    try:
        os.makedirs(root)
    except:
        pass

    if len(paths) > 0:
        for path in paths[0]:
            createDirectories('/'.join([root, path]), paths[1::])

def processAsset(asset):
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    path = '/'.join([data_dir, asset + '.csv'])

    if not os.path.exists(path):
        requests = 0
        while requests < max_requests:
            try:
                urllib.request.urlretrieve(buildUrl(asset), path)
                requests = max_requests + 1
            except:
                time.sleep(request_delay)
                requests += 1
                if requests >= max_requests:
                    print("Failed to retreive asset " + asset)
                    print(buildUrl(asset))
                    quit()

    csv_data = compute_indicators(pd.read_csv(path))
    columns = ['Ticker']
    columns.extend(csv_data.columns.values)

    for i in range(len(csv_data)):
        values = [asset]
        values.extend(csv_data.iloc[i].values)
        values = [x for x in list(zip(columns, values)) if isDefined(x[1])]
        _columns = ['_'.join(x[0].split(' ')) for x in values]
        _values = [x[1] for x in values]
        
        for index in range(2):
            _values[index] = "'" + _values[index] + "'"

        sql = ''.join(['INSERT INTO daily (', ', '.join(_columns), ') VALUES (', ', '.join([str(x) for x in _values]), ');'])

        try:
            cursor.execute(sql)
        except Exception as err:
            conn.rollback()
            print('Error inserting data')
            print('SQL: ' + sql)
            print(err)
            quit()
    os.remove(path)
    conn.commit()
    cursor.close()
    conn.close()

def buildSQLStr():
    baseStr = open(path + '/create.sql', 'r').read()
    columns = getAllIndicators()
    column_str = ',\n'.join([''.join(['\t', x, ' double precision']) for x in columns])
    return baseStr.replace('$1', column_str)

# print('Create directory structure')
# createDirectories(data_dir_root, data_paths)

try:
    os.makedirs(data_dir)
except:
    pass

print('Create table')
table_conn = psycopg2.connect(conn_str)
table_cursor = table_conn.cursor()
table_cursor.execute(buildSQLStr())
table_conn.commit()
table_cursor.close()
table_conn.close()

print('Retreive Data...')
assets = []

if not debug_one_asset:
    for asset in data_assets:
        with open('lists/' + asset + '.txt', 'r') as f:
            asset_str = "".join(f.read().split())
            assets.extend(asset_str.split(','))
else:
    assets = [debug_asset]

with alive_bar(len(assets)) as bar:
    for asset in assets:
        while len(threads) >= cpu_count:
            time.sleep(threading_delay)
            threads = [t for t in threads if t.is_alive()]

        t = threading.Thread(target=processAsset, args=(asset,))
        t.start()
        threads.append(t)
        num_assets_retrieved += 1
        
        bar()
        if debug_max_assets and num_assets_retrieved > max_assets:
            break

while len(threads) > 0:
    time.sleep(threading_delay)
    threads = [t for t in threads if t.is_alive()]
# for x in ['stock', 'etf']:
#     for file in os.listdir(directory + x):
#         data = compute_indicators(pd.read_csv(directory + x + "/" + file))
#         fileParts = str(file).split('.')
#         print(data.columns)