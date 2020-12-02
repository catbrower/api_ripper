import psycopg2
from ApiRipper import Common
from ApiRipper.DBHelper import DBHelper

def getColumns(schema, table_key, response):
    allowed_fields = [x[0] for x in schema['sql_tables'][table_key]]
    present_fields = [key for key in response.keys() if response[key] is not None]
    return [x for x in present_fields if x in allowed_fields]

def getResults(response, table):
    if Common.exists(response, table):
        return response[table]
    elif Common.exists(response, 'results'):
        return response['results']
    else:
        return response

def process_types(schema, table_key, response):
    results = response['results']
    columns = [x[0] for x in schema['sql_tables'][table_key]]

    sql = []
    for key in results['types'].keys():
        values = [key, results['types'][key], False]
        sql.append(DBHelper.buildInsert(table_key, columns, values))
    for key in results['indexTypes'].keys():
        values = [key, results['indexTypes'][key], True]
        sql.append(DBHelper.buildInsert(table_key, columns, values))
    return ';'.join(sql)

def process_default(schema, table_key, response):
    sql = []
    for item in getResults(response, table_key):
        columns = getColumns(schema, table_key, item)
        values = [item[x] for x in columns]
        sql.append(DBHelper.buildInsert(table_key, columns, values))
    return ';'.join(sql)

def process_ticker_detail(schema, table_key, response):
    sql = []
    if response['industry'] is not None:
        sql.append(DBHelper.buildInsert('industries', ['industry'], [response['industry']]))
    
    if response['sector'] is not None:
        sql.append(DBHelper.buildInsert('sectors', ['sector'], [response['sector']]))
    
    columns = getColumns(schema, table_key, response)
    values = [response[x].upper() if x == 'type' else response[x] for x in columns]
    ticker = response['symbol']
    if None in values or None in columns:
        print()
    sql.append(DBHelper.buildInsert(table_key, ['ticker'] + columns, [ticker] + values))
    return ';'.join(sql)

def process_agreggates(schema, table_key, response):
    sql = []
    columns = getColumns(schema, table_key, response)
    for item in getResults(response, table_key):
        values = [response['ticker'], item['t'], item['o'], item['h'], item['l'], item['c'], item['v'], item['n']]
        sql.append(DBHelper.buildInsert(table_key, columns, values))
    return ';'.join(sql)