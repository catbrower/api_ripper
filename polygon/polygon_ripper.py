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
import TaskManager as tm

import common
import polygon_schema as schema

config = configparser.ConfigParser()
config.read('config.conf')

max_requests = 10
max_threads = 24
max_per_page = 50
path = common.getPath()
apiKey = open(path + '/polygon.key', 'r').read().strip()
conn_str = 'dbname=finance user=brower'
date_format = '%Y-%m-%d'
date_from = datetime.datetime.strptime('2000-01-01', date_format)
date_to = datetime.datetime.strptime(date.today().strftime(date_format), date_format)
static_params = [('apiKey', apiKey), ('perPage', '50')]
ignore = ['types', 'markets', 'locales', 'tickers', 'minute']

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

def get_response(table, url):
    response = request(url)

    if common.exists(asset_processors, table):
        asset_processors[table](table, response)
    else:
        asset_processors['default'](table, response)

    return response

def get_all_data():
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
        elif table in ['tickers']
            rip_multi_page(table, threads)
        else:
            rip_single_page(table, threads)

    waitForThreads()