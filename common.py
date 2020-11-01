import os
import psycopg2
import multiprocessing

def isNumber(value):
    try:
        float(vlaue)
        return True
    except:
        return False

def isString(value):
    try:
        str(value)
        return True
    except:
        return False

def exists(collection, index):
    try:
        if collection[index]:
            return True
    except:
        return False

def getMaxThreads():
    return 2 * int(multiprocessing.cpu_count()) - 1

def getPath():
    return '/'.join(os.path.realpath(__file__).split('/')[0:-1])

def buildSQL(table, columns, values):
    _columns = ', '.join(['"desc"' if x == 'desc' else x for x in columns])
    _values = ', '.join([str(x) if isNumber(x) else "'" + str(x) + "'" for x in values])
    return ''.join(['INSERT INTO ', table, ' (', _columns, ') VALUES (', _values, ') ON CONFLICT DO NOTHING;'])

def buildUrl(base, params):
    result = base
    for item in params:
        result = result.replace('{' + str(item[0]) + '}', str(item[1]))
    return result

def buildTable(conn_str, sql):
    table_conn = psycopg2.connect(conn_str)
    table_cursor = table_conn.cursor()
    table_cursor.execute(sql)
    table_conn.commit()
    table_cursor.close()
    table_conn.close()