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
ignore = ['types', 'markets', 'locales', 'tickers', 'minute']
        
def hasPages(response):
    return common.exists(response, 'page') and common.exists(response, 'perPage') and common.exists(response, 'count')

def request(url):
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    return json.loads(response.read())

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
            rip_aggregates(table)
        elif table == 'ticker_detail':
            rip_ticker_detail(table)
        elif table in ['tickers']
            rip_multi_page(table)
        else:
            rip_single_page(table)

    waitForThreads()