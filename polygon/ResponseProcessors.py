import psycopg2
from ApiRipper import Common
from ApiRipper.DBHelper import DBHelper

def getResults(response, table):
    if Common.exists(response, table):
        return response[table]
    elif Common.exists(response, 'results'):
        return response['results']
    else:
        return response

def insert(conn, cursor, table, columns, values):
    sql = Common.buildSQL(table, columns, values)
    insertLock.acquire()
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as err:
        conn.rollback()
        print('Insert failed:\t' + sql + '\n')
    insertLock.release()

def process_types(schema, table, response):
    results = response['results']
    columns = schema['types']

    sql = []
    for key in results['types'].keys():
        values = [key, results['types'][key], False]
        sql.append(DBHelper.buildInsert(table, columns, values))
    for key in results['indexTypes'].keys():
        values = [key, results['indexTypes'][key], True]
        sql.append(DBHelper.buildInsert(table, columns, values))
    return ';'.join(sql)

def process_default(schema, table, response):
    sql = []
    for item in getResults(response, table):
        columns = [x for x in item.keys() if x in schema['tables'][table]]
        values = [item[x] for x in columns]
        sql.append(DBHelper.buildInsert(table, columns, values))
    return ';'.join(sql)

def process_ticker_detail(schema, table, response):
    sql = []
    sql.append(DBHelper.buildInsert('industries', ['industry'], [response['industry']]))
    sql.append(DBHelper.buildInsert('sectors', ['sector'], [response['sector']]))
    
    columns = [x for x in response.keys() if x in schema.tables[table]]
    values = [response[x].upper() if x == 'type' else response[x] for x in columns]
    ticker = response['symbol']
    sql.append(DBHelper.buildInsert(table, ['ticker'] + columns, [ticker] + values))
    return ';'.join(sql)

def process_agreggates(schema, table, response):
    sql = []
    columns = schema.tables[table]
    for item in getResults(response, table):
        values = [response['ticker'], item['t'], item['o'], item['h'], item['l'], item['c'], item['v'], item['n']]
        sql.append(DBHelper.buildInsert(table, columns, values))
    return ';'.join(sql)