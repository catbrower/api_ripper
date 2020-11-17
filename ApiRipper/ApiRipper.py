import sys
import datetime
from datetime import date
from alive_progress import alive_bar

from ApiRipper import Common
from ApiRipper import TaskManager

schema = {}
schema_file = open('polygon/schema.py').read()
exec(schema_file, {}, schema)
ignore = ['aggregates', 'minute', 'ticker_detail', 'trades', 'market_status', 'holidays']
do_only = ['tickers']
multithreaded = True
tm = TaskManager.TaskManager()

for table_key in schema['endpoints'].keys():
    if len(ignore) > 0 and table_key in ignore:
        continue

    if len(do_only) > 0 and table_key not in do_only:
        continue

    ripper = schema['endpoint_rippers']['default']
    if table_key in schema['endpoint_rippers'].keys():
        ripper = schema['endpoint_rippers'][table_key]
    
    print('Get ' + table_key)
    for url in ripper(schema, table_key):
        if multithreaded:
            tm.do_task(Common.get_response, [schema_file, table_key, url])
        else:
            Common.get_response(schema_file, table_key, url)

    # with alive_bar(num_pages) as bar:
    #     bar()
sys.exit(0)