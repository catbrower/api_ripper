import math
import time
import json
import urllib
import urllib.request
import threading
import psycopg2
import configparser
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
static_params = [('apiKey', apiKey), ('perPage', '50'), ('date-from', '2000-01-01'), ('date-to', '2016-10-26')]
ignore = ['types', 'markets', 'locales', 'tickers']

#prep urls
# for key in schema.urls.keys():
#     schema.urls[key] = schema.urls[key] + '?apiKey=' + apiKey

#Threading
threads = []

def getAllTickers():
    conn, cur = getConnection()
    cur.execute('SELECT ticker FROM tickers')
    results = cur.fetchall()
    closeConnection(conn, cur)
    return results

def getResults(response, table):
    if common.exists(response, table):
        return response[table]
    else:
        return response['results']

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
    conn, cursor = getConnection()

    for key in results['types'].keys():
        values = [key, results['types'][key], False]
        insert(conn, cursor, 'types', columns, values)
    for _type in results['indexTypes'].keys():
        values = [key, results['types'][key], True]
        insert(conn, cursor, 'types', columns, values)
    conn.commit()
    closeConnection(conn, cursor)

def process_default(table, response):
    conn, cursor = getConnection()
    for item in getResults(response, table):
        columns = schema.tables[table]
        values = [item[x] for x in schema.tables[table]]
        insert(conn, cursor, table, columns, values)
    conn.commit()
    closeConnection(conn, cursor)

def process_aggregate(table, response):
    conn, cursor = getConnection()

    

    closeConnection(conn, cursor)

def hasPages(response):
    return common.exists(response, 'page') and common.exists(response, 'perPage') and common.exists(response, 'count')

def insert(conn, cursor, table, columns, values):
    sql = common.buildSQL(table, columns, values)
    try:
        cursor.execute(sql)
    except Exception as err:
        conn.rollback()
        print('Insert failed:\t' + sql)

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

def process_response(table, url):
    response = request(url)

    if common.exists(asset_processors, table):
        asset_processors[table](table, response)
    else:
        asset_processors['default'](table, response)

asset_processors = {
    'aggregates': process_aggregates,
    'types': process_type,
    'default': process_default
}

conn = psycopg2.connect(conn_str)
cursor = conn.cursor()
print('Create table')
with open('sql/polygon_schema.sql', 'r') as f:
    common.buildTable(conn_str, f.read())
conn.close()
cursor.close()

#Insert
for table in schema.table_names:
    print('Load ' + table)

    if table in ignore:
        print('Skip')
        continue

    assets =  [1]
    if('{asset}' in schema.endpoints[table]):
        assets = getAllTickers()

    for asset in assets:
        page = count = 1

        #Get one response, process it, and if it has pages then do below
        params = static_params + [('asset', asset), ('page', page)]
        url = common.buildUrl(schema.endpoints[table], params)
        process_response(table, url)

        if hasPages(response):
            page = 2
            num_pages = math.ceil(int(response['count']) / int(response['perPage']))

            with alive_bar(num_pages) as bar:
                for page in range(num_pages):
                    while len(threads) >= max_threads:
                        time.sleep(float(config['delay']['threading']))
                        threads = [t for t in threads if t.is_alive()]
                    
                    url = common.buildUrl(schema.endpoints[table], params)
                    params = static_params + [('asset', asset), ('page', page)]
                    t = threading.Thread(target=process_response, args=(table, common.buildUrl(url, params)))
                    t.start()
                    threads.append(t)
                    # num_assets_retrieved += 1

                    bar()

waitForThreads()
quit()