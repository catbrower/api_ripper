import math
from ApiRipper import Common
import urllib
import urllib.request
import json
import datetime
from datetime import date
import configparser
import psycopg2

def getAllTickers(connection_str):
    connection = psycopg2.connect(connection_str)
    cursor = connection.cursor()
    cursor.execute('SELECT ticker FROM tickers')
    results = [x[0] for x in cursor.fetchall()]
    cursor.close()
    connection.close()
    return results

def rip_single_page(schema, table_key):
    yield Common.buildUrl(schema['endpoints'][table_key], schema['static_params'])

def rip_multi_page(schema, table_key):
    page = count = 1

    #Get one response, process it, and if it has pages then do below
    params = schema['static_params'] + [('page', page)]
    url = Common.buildUrl(schema['endpoints'][table_key], params)
    response = json.loads(urllib.request.urlopen(url).read())

    num_pages = math.ceil(int(response['count']) / int(response['perPage']))
    for page in range(1, num_pages):
        params = schema['static_params'] + [('page', page)]
        yield Common.buildUrl(schema['endpoints'][table_key], params)

def rip_aggregates(schema, table_key):
    from datetime import date
    date_format = '%Y-%m-%d'
    date_from = datetime.datetime.strptime('2000-01-01', date_format)
    date_to = datetime.datetime.strptime(date.today().strftime(date_format), date_format)

    num_days = (date_to - date_from).days + 1
    tickers = getAllTickers(schema['db_connection_str'])

    for ticker in tickers:
        date = date_from
        while date < date_to:
            _date_to = date + datetime.timedelta(days=1)
            params = schema['static_params'] + [('asset', ticker), ('date-from', date.strftime(date_format)), ('date-to', _date_to.strftime(date_format))]
            yield Common.buildUrl(schema['endpoints'][table_key], params)

            date += datetime.timedelta(days=1)

def rip_ticker_detail(schema, table_key):
    tickers = getAllTickers(schema['db_connection_str'])

    for ticker in tickers:
        params = schema['static_params'] + [('asset', ticker)]
        yield Common.buildUrl(schema['endpoints'][table_key], params)
