import os
import psycopg2
import urllib
import json
import time

#schema_file, table_key, url
def get_response(args):
    schema = {}
    exec(args[0], {}, schema)
    try:
        response = json.loads(urllib.request.urlopen(args[2]).read())
    except urllib.error.HTTPError as err:
        # print('Error on URL:\t' + args[2])
        return None

    try:
        if exists(schema['response_processors'], args[1]):
            return schema['response_processors'][args[1]](schema, args[1], response)
        else:
            return schema['response_processors']['default'](schema, args[1], response)
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