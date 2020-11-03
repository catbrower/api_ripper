import re
import math
import time
import json
import urllib
import urllib.request
import threading
import psycopg2
import configparser
import datetime
from datetime import date
from alive_progress import alive_bar

import common
import polygon_schema as schema

config = configparser.ConfigParser()
config.read('config.conf')

max_requests = 10
max_threads = common.getMaxThreads()
max_per_page = 50
path = common.getPath()
apiKey = open(path + '/polygon.key', 'r').read().strip()
conn_str = 'dbname=finance user=brower'
date_format = '%Y-%m-%d'
date_from = datetime.datetime.strptime('2000-01-01', date_format)
date_to = datetime.datetime.strptime(date.today().strftime(date_format), date_format)
static_params = [('apiKey', apiKey), ('perPage', '50')]
ignore = ['types', 'markets', 'locales', 'tickers', 'minute']
insertLock = threading.Lock()
conn = psycopg2.connect(conn_str)
cursor = conn.cursor()

#Threading
threads = []

def getAllTickers():
    conn, cur = getConnection()
    cur.execute('SELECT ticker FROM tickers')
    results = [x[0] for x in cur.fetchall()]
    closeConnection(conn, cur)
    return results

def getResults(response, table):
    if common.exists(response, table):
        return response[table]
    elif common.exists(response, 'results'):
        return response['results']
    else:
        return response

def waitForThreads():
    while len(threads) >= cpu_count:
        time.sleep(threading_delay)
        threads = [t for t in threads if t.is_alive()]

def getConnection():
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    return conn, cursor

def closeConnection(cursor, conn):
    cursor.close()
    conn.close()

def process_type(table, response):
    results = response['results']
    columns = schema.types

    for key in results['types'].keys():
        values = [key, results['types'][key], False]
        insert(conn, cursor, 'types', columns, values)
    for key in results['indexTypes'].keys():
        values = [key, results['indexTypes'][key], True]
        insert(conn, cursor, 'types', columns, values)
    conn.commit()

def process_default(table, response):
    for item in getResults(response, table):
        columns = [x for x in item.keys() if x in schema.tables[table]]
        values = [item[x] for x in columns]
        insert(conn, cursor, table, columns, values)

def process_ticker_detail(table, response):
    insert(conn, cursor, 'industries', ['industry'], [response['industry']])
    insert(conn, cursor, 'sectors', ['sector'], [response['sector']])
    
    columns = [x for x in response.keys() if x in schema.tables[table]]
    values = [response[x].upper() if x == 'type' else response[x] for x in columns]
    insert(conn, cursor, table, ['ticker'] + columns, [response['symbol']] + values)

def process_agreggates(table, response):
    for item in getResults(response, table):
        columns = schema.tables[table]
        values = [response['ticker'], item['t'], item['o'], item['h'], item['l'], item['c'], item['v'], item['n']]
        insert(conn, cursor, table, columns, values)
    conn.commit()

def rip_aggregates(table, threads):
    num_days = (date_to - date_from).days + 1
    tickers = getAllTickers()

    with alive_bar(num_days * len(tickers)) as bar:
        while len(threads) >= max_threads:
            time.sleep(float(config['delay']['threading']))
            threads = [t for t in threads if t.is_alive()]

        for ticker in tickers:
            date = date_from
            while date < date_to:
                _date_to = date + datetime.timedelta(days=1)
                params = static_params + [('asset', ticker), ('date-from', date.strftime(date_format)), ('date-to', _date_to.strftime(date_format))]
                url = common.buildUrl(schema.endpoints[table], params)
                t = threading.Thread(target=get_response, args=(table, url))
                t.start()
                threads.append(t)

                date += datetime.timedelta(days=1)
                bar()

def rip_ticker_detail(table, threads):
    tickers = getAllTickers()

    with alive_bar(len(tickers)) as bar:
        while len(threads) >= max_threads:
            time.sleep(float(config['delay']['threading']))
            threads = [t for t in threads if t.is_alive()]

        for ticker in tickers:
            date = date_from
            while date < date_to:
                _date_to = date + datetime.timedelta(days=1)
                params = static_params + [('asset', ticker)]
                url = common.buildUrl(schema.endpoints[table], params)
                t = threading.Thread(target=get_response, args=(table, url))
                t.start()
                threads.append(t)

                date += datetime.timedelta(days=1)
                bar()

def hasPages(response):
    return common.exists(response, 'page') and common.exists(response, 'perPage') and common.exists(response, 'count')

def insert(conn, cursor, table, columns, values):
    sql = common.buildSQL(table, columns, values)
    insertLock.acquire()
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as err:
        conn.rollback()
        print('Insert failed:\t' + sql + '\n')
    insertLock.release()

def request(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    return json.loads(response.read())

def cullThreads(numThreads = max_threads):
    if numThreads < 0:
        numThreads = 0
    elif numThreads > cpu_count:
        numThreads = cpu_count

    while len(threads) >= numThreads:
        time.sleep(threading_delay)
        new_threads = [t for t in threads if t.is_alive()]

def get_response(table, url):
    response = request(url)

    if common.exists(asset_processors, table):
        asset_processors[table](table, response)
    else:
        asset_processors['default'](table, response)

    return response

asset_processors = {
    'ticker_detail': process_ticker_detail,
    'minute': process_agreggates,
    'types': process_type,
    'default': process_default
}

print('Create table')
with open('sql/polygon_schema.sql', 'r') as f:
    common.buildTable(conn_str, f.read())

#Insert
for table in schema.table_names:
    print('Load ' + table)

    if table in ignore:
        print('Skip')
        continue

    if table == 'minute':
        rip_aggregates(table, threads)
    elif table == 'ticker_detail':
        rip_ticker_detail(table, threads)
    else:
        page = count = 1

        #Get one response, process it, and if it has pages then do below
        params = static_params + [('page', page)]
        url = common.buildUrl(schema.endpoints[table], params)
        response = get_response(table, url)

        if hasPages(response):
            num_pages = math.ceil(int(response['count']) / int(response['perPage']))

            with alive_bar(num_pages) as bar:
                for page in range(2, num_pages):
                    while len(threads) >= max_threads:
                        time.sleep(float(config['delay']['threading']))
                        threads = [t for t in threads if t.is_alive()]
                    
                    params = static_params + [('page', page)]
                    url = common.buildUrl(schema.endpoints[table], params)
                    t = threading.Thread(target=get_response, args=(table, common.buildUrl(url, params)))
                    t.start()
                    threads.append(t)

                    bar()

waitForThreads()
quit()