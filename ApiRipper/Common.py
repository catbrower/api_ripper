import os
import psycopg2
import urllib
import json
import time

#schema_file, table_key, url
def get_response(args):
    return True
    schema = {}
    exec(args[0], {}, schema)
    response = json.loads(urllib.request.urlopen(args[2]).read())

    try:
        if exists(schema['response_processors'], args[1]):
            schema['response_processors'][table_key](schema, args[1], response)
        else:
            schema['response_processors']['default'](schema, args[1], response)

        return response
    except Exception as err:
        print(err)

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