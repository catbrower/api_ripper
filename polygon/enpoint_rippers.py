def rip_single_page(table, response):
    params = static_params + [('page', page)]
    url = common.buildUrl(schema.endpoints[table], params)
    response = get_response(table, url)

def rip_multi_page(table, response):
    page = count = 1

    #Get one response, process it, and if it has pages then do below
    params = static_params + [('page', page)]
    url = common.buildUrl(schema.endpoints[table], params)
    response = get_response(table, url)

    if hasPages(response):
        num_pages = math.ceil(int(response['count']) / int(response['perPage']))

        with alive_bar(num_pages) as bar:
            for page in range(2, num_pages):
                while len(threads) >= max_threads:
                    time.sleep(float(config['delay']['threading']))
                    threads = [t for t in threads if t.is_alive()]
                
                params = static_params + [('page', page)]
                url = common.buildUrl(schema.endpoints[table], params)
                t = threading.Thread(target=get_response, args=(table, common.buildUrl(url, params)))
                t.start()
                threads.append(t)

                bar()

def rip_aggregates(table, threads):
    num_days = (date_to - date_from).days + 1
    tickers = getAllTickers()

    with alive_bar(num_days * len(tickers)) as bar:
        while len(threads) >= max_threads:
            time.sleep(float(config['delay']['threading']))
            threads = [t for t in threads if t.is_alive()]

        for ticker in tickers:
            date = date_from
            while date < date_to:
                _date_to = date + datetime.timedelta(days=1)
                params = static_params + [('asset', ticker), ('date-from', date.strftime(date_format)), ('date-to', _date_to.strftime(date_format))]
                url = common.buildUrl(schema.endpoints[table], params)
                t = threading.Thread(target=get_response, args=(table, url))
                t.start()
                threads.append(t)

                date += datetime.timedelta(days=1)
                bar()

def rip_ticker_detail(table, threads):
    tickers = getAllTickers()

    with alive_bar(len(tickers)) as bar:
        while len(threads) >= max_threads:
            time.sleep(float(config['delay']['threading']))
            threads = [t for t in threads if t.is_alive()]

        for ticker in tickers:
            params = static_params + [('asset', ticker)]
            url = common.buildUrl(schema.endpoints[table], params)
            t = threading.Thread(target=get_response, args=(table, url))
            t.start()
            threads.append(t)

            bar()
