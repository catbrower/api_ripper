from ApiRipper import Common

def escape(string):
    # escape(x) if isNumber(x) else "'" + escape(x) + "'"
    if Common.isString(string):
        result = str(string).split("'")
        return "'" + "''".join(result) + "'"
    else:
        return str(string)

def buildInsert(table, columns, values):
    _columns = ', '.join(['"desc"' if x == 'desc' else x for x in columns])
    _values = ', '.join([escape(x) for x in values])
    return ''.join(['INSERT INTO ', table, ' (', _columns, ') VALUES (', _values, ') ON CONFLICT DO NOTHING']).strip()
