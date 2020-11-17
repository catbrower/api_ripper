import os
import psycopg2
import urllib
import json
import time

def get_response(schema_file, table_key, url):
    schema = {}
    exec(schema_file, {}, schema)
    response = json.loads(urllib.request.urlopen(url).read())

    if exists(schema['response_processors'], table_key):
        schema['response_processors'][table_key](schema, table_key, response)
    else:
        schema['response_processors']['default'](schema, table_key, response)

    return response

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