import psycopg2
from ApiRipper import Common

class DBHelper():
    def buildInsert(table, columns, values):
        _columns = ', '.join(['"desc"' if x == 'desc' else x for x in columns])
        _values = ', '.join([DBHelper.escape(x) for x in values])
        return ''.join(['INSERT INTO ', table, ' (', _columns, ') VALUES (', _values, ') ON CONFLICT DO NOTHING']).strip()

    def buildTable(table, rows, constraints):
        rows = [['"' + x[0] + '"', x[1]] if x[0] == 'desc' else [x[0], x[1]] for x in rows]
        # constraints = [DBHelper.escape(x) for x in constraints]
        sql = "CREATE TABLE IF NOT EXISTS " + table + " ("
        _sql = []
        for row in rows:
            _sql.append(' '.join(row))
        for constraint in constraints:
            if constraint[0].upper() == 'PRIMARY KEY':
                _sql.append('PRIMARY KEY(' + ','.join(constraint[1::]) + ')')
            elif constraint[0].upper() == 'FOREIGN KEY':
                _sql.append(''.join(['FOREIGN KEY(', constraint[1], ') REFERENCES ', constraint[2], '(', constraint[3], ')']))
        
        return sql + ','.join(_sql) + ')'

    def escape(string):
        # escape(x) if isNumber(x) else "'" + escape(x) + "'"
        if Common.isString(string):
            if(string == 'desc'):
                return '"desc"'
            else:
                result = str(string).split("'")
                return "'" + "''".join(result) + "'"
        else:
            return str(string)

    def __init__(self, connection_str):
        self.connection = psycopg2.connect(connection_str)
        self.cursor = self.connection.cursor()

    def execute(self, sql):
        if self.cursor is None:
            print('DBHelper, cursor not initialized')
        else:
            try:
                self.cursor.execute(sql)
                self.connection.commit()
            except:
                self.connection.rollback()
                print('Error on sql:\n' + sql)

    def close(self):
        self.connection.close()
        self.cursor.close()
        