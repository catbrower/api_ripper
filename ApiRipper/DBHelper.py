import psycopg2
from ApiRipper import Common

class DBHelper():
    connection = None
    cursor = None

    def __init__(self, connection_str):
        if DBHelper.connection is None:
            DBHelper.connection = psycopg2.connect(connection_str)
            DBHelper.cursor = DBHelper.connection.cursor()

    def escape(string):
        # escape(x) if isNumber(x) else "'" + escape(x) + "'"
        if Common.isString(string):
            result = str(string).split("'")
            return "'" + "''".join(result) + "'"
        else:
            return str(string)

    def buildInsert(table, columns, values):
        _columns = ', '.join(['"desc"' if x == 'desc' else x for x in columns])
        _values = ', '.join([DBHelper.escape(x) for x in values])
        return ''.join(['INSERT INTO ', table, ' (', _columns, ') VALUES (', _values, ') ON CONFLICT DO NOTHING']).strip()

    def execute(self, sql):
        if DBHelper.cursor is None:
            print('DBHelper, cursor not initialized')
        else:
            try:
                DBHelper.cursor.execute(sql)
                DBHelper.connection.commit()
            except:
                DBHelper.connection.rollback()
                print('Error on sql:\n' + sql)

    def close(self):
        DBHelper.connection.close()
        DBHelper.cursor.close()
        