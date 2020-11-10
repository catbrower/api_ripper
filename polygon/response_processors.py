def process_type(table, response):
    results = response['results']
    columns = schema.types

    for key in results['types'].keys():
        values = [key, results['types'][key], False]
        insert(conn, cursor, 'types', columns, values)
    for key in results['indexTypes'].keys():
        values = [key, results['indexTypes'][key], True]
        insert(conn, cursor, 'types', columns, values)
    conn.commit()

def process_default(table, response):
    for item in getResults(response, table):
        columns = [x for x in item.keys() if x in schema.tables[table]]
        values = [item[x] for x in columns]
        insert(conn, cursor, table, columns, values)

def process_ticker_detail(table, response):
    insert(conn, cursor, 'industries', ['industry'], [response['industry']])
    insert(conn, cursor, 'sectors', ['sector'], [response['sector']])
    
    columns = [x for x in response.keys() if x in schema.tables[table]]
    values = [response[x].upper() if x == 'type' else response[x] for x in columns]
    ticker = response['symbol']
    insert(conn, cursor, table, ['ticker'] + columns, [ticker] + values)

def process_agreggates(table, response):
    for item in getResults(response, table):
        columns = schema.tables[table]
        values = [response['ticker'], item['t'], item['o'], item['h'], item['l'], item['c'], item['v'], item['n']]
        insert(conn, cursor, table, columns, values)
    conn.commit()

response_processors = {
    'ticker_detail': process_ticker_detail,
    'minute': process_agreggates,
    'types': process_type,
    'default': process_default
}