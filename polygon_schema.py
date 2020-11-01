import configparser
config = configparser.ConfigParser()
config.read('config.conf')

endpoints = {
    'minute':    config['urls']['polygon_aggregates'],
    'tickers':       config['urls']['polygon_tickers'],
    'types':         config['urls']['polygon_types'],
    'ticker_detail':       config['urls']['polygon_details'],
    'ticker_news':   config['urls']['polygon_ticker_news'],
    'markets':       config['urls']['polygon_markets'],
    'locales':       config['urls']['polygon_locales'],
    'splits':        config['urls']['polygon_splits'],
    'dividends':     config['urls']['polygon_dividends'],
    'financials':    config['urls']['polygon_financials'],
    'market_status': config['urls']['polygon_market_status'],
    'holidays':      config['urls']['polygon_holidays'],
    'exchanges':     config['urls']['polygon_exchanges'],
    'trades':        config['urls']['polygon_trades']
}

for key in endpoints.keys():
    endpoints[key] = config['urls']['polygon_base'] + endpoints[key]

types = [
    'type',
    'desc',
    'is_index'
]

markets = [
    'market',
    'desc'
]

locales = [
    'locale',
    'name'
]

tickers = ['ticker',
    'name',
    'market',
    'locale',
    'currency',
    'primaryExch',
    'active',
    'updated']

minute = ['ticker',
    'time',
    'adj_open',
    'adj_high',
    'adj_low',
    'adj_close',
    'adj_volume',
    'num_items']

ticker_detail = ['ticker',
    'logo',
    'listdate',
    'cik',
    'bloomberg',
    'figi',
    'lei',
    'sic',
    'country',
    'industry',
    'sector',
    'marketcap',
    'employees',
    'phone',
    'ceo',
    'url',
    'description',
    'exchange',
    'name',
    'symbol',
    'exchangeSymbo',
    'hq_address',
    'hq_state',
    'hq_country',
    'type',
    'updated']

financial = ['ticker',
    'period',
    'calendarDate',
    'reportPeriod',
    'updated',
    'dateKey',
    'accumulatedOtherComprehensiveIncome',
    'assets',
    'assetsCurrent',
    'assetsNonCurrent',
    'bookValuePerShare',
    'capitalExpenditure',
    'cashAndEquivalents',
    'cashAndEquivalentsUSD',
    'costOfRevenue',
    'consolidatedIncome',
    'currentRatio',
    'debtToEquityRatio',
    'debt',
    'debtCurrent',
    'debtNonCurrent',
    'debtUSD',
    'deferredRevenue',
    'depreciationAmortizationAndAccretion',
    'deposits',
    'dividendYield',
    'dividendsPerBasicCommonShare',
    'earningBeforeInterestTaxes',
    'earningsBeforeInterestTaxesDepreciationAmortization',
    'EBITDAMargin',
    'earningsBeforeInterestTaxesDepreciationAmortizationUSD',
    'earningBeforeInterestTaxesUSD',
    'earningsBeforeTax',
    'earningsPerBasicShare',
    'earningsPerDilutedShare',
    'earningsPerBasicShareUSD',
    'shareholdersEquity',
    'shareholdersEquityUSD',
    'enterpriseValue',
    'enterpriseValueOverEBIT',
    'enterpriseValueOverEBITDA',
    'freeCashFlow',
    'freeCashFlowPerShare',
    'foreignCurrencyUSDExchangeRate',
    'grossProfit',
    'grossMargin',
    'goodwillAndIntangibleAssets',
    'interestExpense',
    'investedCapital',
    'inventory',
    'investments',
    'investmentsCurrent',
    'investmentsNonCurrent',
    'totalLiabilities',
    'currentLiabilities',
    'liabilitiesNonCurrent',
    'marketCapitalization',
    'netCashFlow',
    'netCashFlowBusinessAcquisitionsDisposals',
    'issuanceEquityShares',
    'issuanceDebtSecurities',
    'paymentDividendsOtherCashDistributions',
    'netCashFlowFromFinancing',
    'netCashFlowFromInvesting',
    'netCashFlowInvestmentAcquisitionsDisposals',
    'netCashFlowFromOperations',
    'effectOfExchangeRateChangesOnCash',
    'netIncome',
    'netIncomeCommonStock',
    'netIncomeCommonStockUSD',
    'netLossIncomeFromDiscontinuedOperations',
    'netIncomeToNonControllingInterests',
    'profitMargin',
    'operatingExpenses',
    'operatingIncome',
    'tradeAndNonTradePayables',
    'payoutRatio',
    'priceToBookValue',
    'priceEarnings',
    'priceToEarningsRatio',
    'propertyPlantEquipmentNet',
    'preferredDividendsIncomeStatementImpact',
    'sharePriceAdjustedClose',
    'priceSales',
    'priceToSalesRatio',
    'tradeAndNonTradeReceivables',
    'accumulatedRetainedEarningsDeficit',
    'revenues',
    'revenuesUSD',
    'researchAndDevelopmentExpense',
    'shareBasedCompensation',
    'sellingGeneralAndAdministrativeExpense',
    'shareFactor',
    'shares',
    'weightedAverageShares',
    'weightedAverageSharesDiluted',
    'salesPerShare',
    'tangibleAssetValue',
    'taxAssets',
    'incomeTaxExpense',
    'taxLiabilities',
    'tangibleAssetsBookValuePerShare',
    'workingCapital']

table_names = ['types', 'markets', 'locales', 'tickers', 'minute', 'ticker_detail', 'financial']

tables = {
    'types': types,
    'markets': markets,
    'locales': locales,
    'tickers': tickers,
    'minute': minute,
    'ticker_detail': ticker_detail,
    'financial': financial
}