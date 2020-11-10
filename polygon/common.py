import os
import psycopg2

def escape(string):
    # escape(x) if isNumber(x) else "'" + escape(x) + "'"
    if isString(string):
        result = str(string).split("'")
        return "'" + "''".join(result) + "'"
    else:
        return str(string)

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

def getPath():
    return '/'.join(os.path.realpath(__file__).split('/')[0:-1])

def buildSQL(table, columns, values):
    _columns = ', '.join(['"desc"' if x == 'desc' else x for x in columns])
    _values = ', '.join([escape(x) for x in values])
    return ''.join(['INSERT INTO ', table, ' (', _columns, ') VALUES (', _values, ') ON CONFLICT DO NOTHING']).strip()

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