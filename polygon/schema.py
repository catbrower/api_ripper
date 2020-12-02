import os
from polygon import ResponseProcessors
from polygon import EndpointRippers
import configparser
config = configparser.ConfigParser()
config.read('application_properties.conf')

# path = '/'.join(os.path.realpath(__file__).split('/')[0:-1])
path = config['general']['path']
apiKey = open(path + '/polygon.key', 'r').read().strip()
static_params = [('apiKey', apiKey), ('perPage', '50')]
db_connection_str = ''.join(['dbname=', config['sql']['dbname'], ' user=', config['sql']['user']])
base_url = 'https://api.polygon.io'

endpoints = {
    'types':         '/v2/reference/types?apiKey={apiKey}',
    'markets':       '/v2/reference/markets?apiKey={apiKey}',
    'locales':       '/v2/reference/locales?apiKey={apiKey}',
    'exchanges':     '/v1/meta/exchanges?apiKey={apiKey}',
    'tickers':       '/v2/reference/tickers?apiKey={apiKey}&sort=ticker&perpage={perPage}&page={page}',
    'ticker_detail': '/v1/meta/symbols/{asset}/company?apiKey={apiKey}',
    'financials':    '/v2/reference/financials/{asset}?apiKey={apiKey}',
    'minute':        '/v2/aggs/ticker/{asset}/range/1/minute/{date-from}/{date-to}?apiKey={apiKey}',
    
    'ticker_news':   '/v1/meta/symbols/{asset}/news?apiKey={apiKey}',
    'splits':        '/v2/reference/splits/{asset}?apiKey={apiKey}',
    'dividends':     '/v2/reference/dividends/{asset}?apiKey={apiKey}',
    'market_status': '/v1/marketstatus/now?apiKey={apiKey}',
    'holidays':      '/v1/marketstatus/upcoming?apiKey={apiKey}',
    'trades':        '/v2/ticks/stocks/trades/{asset}/{date}?apiKey={apiKey}'
}

for key in endpoints.keys():
    endpoints[key] = base_url + endpoints[key]

endpoint_rippers = {
    'minute': EndpointRippers.rip_aggregates,
    'ticker_detail': EndpointRippers.rip_ticker_detail,
    'tickers': EndpointRippers.rip_multi_page,
    'default': EndpointRippers.rip_single_page
}

response_processors = {
    'ticker_detail': ResponseProcessors.process_ticker_detail,
    'minute': ResponseProcessors.process_agreggates,
    'types': ResponseProcessors.process_types,
    'default': ResponseProcessors.process_default
}

sql_tables = {
    'types': [
        ['type', 'varchar'],
        ['desc', 'varchar'],
        ['is_index', 'boolean']
    ],
    'markets': [
        ['market', 'varchar'],
        ['desc', 'varchar']
    ],
    'locales': [
        ['locale', 'varchar'],
        ['name', 'varchar']
    ],
    'industries': [
        ['industry', 'varchar']
    ],
    'sectors': [
        ['sector', 'varchar']
    ],
    'exchanges': [
        ['id', 'integer'],
        ['type', 'varchar'],
        ['market', 'varchar'],
        ['mic', 'varchar'],
        ['name', 'varchar'],
        ['tape', 'varchar'],
        ['code', 'varchar']
    ],
    'tickers': [
        ['ticker', 'varchar'],
        ['name', 'varchar'],
        ['market', 'varchar'],
        ['locale', 'varchar'],
        ['currency', 'varchar'],
        ['primaryExch', 'varchar'],
        ['active', 'boolean'],
        ['updated', 'date'],
        ['type', 'varchar']
    ],
    'minute': [
        ['ticker', 'varchar'],
        ['time', 'varchar'],
        ['adj_open', 'double precision'],
        ['adj_high', 'double precision'],
        ['adj_low', 'double precision'],
        ['adj_close', 'double precision'],
        ['adj_volume', 'double precision'],
        ['num_items', 'integer']
    ],
    'ticker_detail': [
        ['ticker', 'varchar'],
        ['logo', 'varchar'],
        ['listdate', 'date'],
        ['cik', 'integer'],
        ['bloomberg', 'varchar'],
        ['figi', 'varchar'],
        ['lei', 'varchar'],
        ['sic', 'integer'],
        ['country', 'varchar'],
        ['industry', 'varchar'],
        ['sector', 'varchar'],
        ['marketcap', 'bigint'],
        ['employees', 'integer'],
        ['phone', 'varchar'],
        ['ceo', 'varchar'],
        ['url', 'varchar'],
        ['description', 'varchar'],
        ['exchange', 'varchar'],
        ['name', 'varchar'],
        ['exchangeSymbo', 'varchar'],
        ['hq_address', 'varchar'],
        ['hq_state', 'varchar'],
        ['hq_country', 'varchar'],
        ['type', 'varchar'],
        ['updated', 'date']
    ],
    'financial': [
        ['ticker', 'VARCHAR'],
        ['period', 'VARCHAR'],
        ['calendarDate', 'DATE'],
        ['reportPeriod', 'DATE'],
        ['updated', 'DATE'],
        ['dateKey', 'DATE'],
        ['accumulatedOtherComprehensiveIncome', 'INTEGER'],
        ['assets', 'BIGINT'],
        ['assetsCurrent', 'BIGINT'],
        ['assetsNonCurrent', 'BIGINT'],
        ['bookValuePerShare', 'REAL'],
        ['capitalExpenditure', 'BIGINT'],
        ['cashAndEquivalents', 'BIGINT'],
        ['cashAndEquivalentsUSD', 'BIGINT'],
        ['costOfRevenue', 'BIGINT'],
        ['consolidatedIncome', 'BIGINT'],
        ['currentRatio', 'REAL'],
        ['debtToEquityRatio', 'REAL'],
        ['debt', 'BIGINT'],
        ['debtCurrent', 'BIGINT'],
        ['debtNonCurrent', 'BIGINT'],
        ['debtUSD', 'BIGINT'],
        ['deferredRevenue', 'BIGINT'],
        ['depreciationAmortizationAndAccretion', 'BIGINT'],
        ['deposits', 'INTEGER'],
        ['dividendYield', 'REAL'],
        ['dividendsPerBasicCommonShare', 'REAL'],
        ['earningBeforeInterestTaxes', 'BIGINT'],
        ['earningsBeforeInterestTaxesDepreciationAmortization', 'BIGINT'],
        ['EBITDAMargin', 'REAL'],
        ['earningsBeforeInterestTaxesDepreciationAmortizationUSD', 'BIGINT'],
        ['earningBeforeInterestTaxesUSD', 'BIGINT'],
        ['earningsBeforeTax', 'BIGINT'],
        ['earningsPerBasicShare', 'REAL'],
        ['earningsPerDilutedShare', 'REAL'],
        ['earningsPerBasicShareUSD', 'REAL'],
        ['shareholdersEquity', 'BIGINT'],
        ['shareholdersEquityUSD', 'BIGINT'],
        ['enterpriseValue', 'BIGINT'],
        ['enterpriseValueOverEBIT', 'INTEGER'],
        ['enterpriseValueOverEBITDA', 'REAL'],
        ['freeCashFlow', 'BIGINT'],
        ['freeCashFlowPerShare', 'REAL'],
        ['foreignCurrencyUSDExchangeRate', 'INTEGER'],
        ['grossProfit', 'BIGINT'],
        ['grossMargin', 'REAL'],
        ['goodwillAndIntangibleAssets', 'INTEGER'],
        ['interestExpense', 'INTEGER'],
        ['investedCapital', 'BIGINT'],
        ['inventory', 'BIGINT'],
        ['investments', 'BIGINT'],
        ['investmentsCurrent', 'BIGINT'],
        ['investmentsNonCurrent', 'BIGINT'],
        ['totalLiabilities', 'BIGINT'],
        ['currentLiabilities', 'BIGINT'],
        ['liabilitiesNonCurrent', 'BIGINT'],
        ['marketCapitalization', 'BIGINT'],
        ['netCashFlow', 'BIGINT'],
        ['netCashFlowBusinessAcquisitionsDisposals', 'BIGINT'],
        ['issuanceEquityShares', 'BIGINT'],
        ['issuanceDebtSecurities', 'BIGINT'],
        ['paymentDividendsOtherCashDistributions', 'BIGINT'],
        ['netCashFlowFromFinancing', 'BIGINT'],
        ['netCashFlowFromInvesting', 'BIGINT'],
        ['netCashFlowInvestmentAcquisitionsDisposals', 'BIGINT'],
        ['netCashFlowFromOperations', 'BIGINT'],
        ['effectOfExchangeRateChangesOnCash', 'INTEGER'],
        ['netIncome', 'BIGINT'],
        ['netIncomeCommonStock', 'BIGINT'],
        ['netIncomeCommonStockUSD', 'BIGINT'],
        ['netLossIncomeFromDiscontinuedOperations', 'INTEGER'],
        ['netIncomeToNonControllingInterests', 'INTEGER'],
        ['profitMargin', 'REAL'],
        ['operatingExpenses', 'BIGINT'],
        ['operatingIncome', 'BIGINT'],
        ['tradeAndNonTradePayables', 'BIGINT'],
        ['payoutRatio', 'REAL'],
        ['priceToBookValue', 'REAL'],
        ['priceEarnings', 'REAL'],
        ['priceToEarningsRatio', 'REAL'],
        ['propertyPlantEquipmentNet', 'BIGINT'],
        ['preferredDividendsIncomeStatementImpact', 'INTEGER'],
        ['sharePriceAdjustedClose', 'REAL'],
        ['priceSales', 'REAL'],
        ['priceToSalesRatio', 'REAL'],
        ['tradeAndNonTradeReceivables', 'BIGINT'],
        ['accumulatedRetainedEarningsDeficit', 'BIGINT'],
        ['revenues', 'BIGINT'],
        ['revenuesUSD', 'BIGINT'],
        ['researchAndDevelopmentExpense', 'BIGINT'],
        ['shareBasedCompensation', 'BIGINT'],
        ['sellingGeneralAndAdministrativeExpense', 'BIGINT'],
        ['shareFactor', 'INTEGER'],
        ['shares', 'BIGINT'],
        ['weightedAverageShares', 'BIGINT'],
        ['weightedAverageSharesDiluted', 'BIGINT'],
        ['salesPerShare', 'REAL'],
        ['tangibleAssetValue', 'BIGINT'],
        ['taxAssets', 'INTEGER'],
        ['incomeTaxExpense', 'BIGINT'],
        ['taxLiabilities', 'INTEGER'],
        ['tangibleAssetsBookValuePerShare', 'REAL'],
        ['workingCapital', 'BIGINT'],
    ]
}

sql_table_constraints = {
    'types': [['primary key', 'type']],
    'markets': [['primary key', 'market']],
    'locales': [['primary key', 'locale']],
    'industries': [['primary key', 'industry']],
    'sectors': [['primary key', 'sector']],
    'exchanges': [['primary key', 'id']],
    'tickers': [
        ['primary key', 'ticker'],
        ['foreign key', 'market', 'markets', 'market'],
        ['foreign key', 'locale', 'locales', 'locale'],
        ['foreign key', 'type', 'types', 'type']
    ],
    'minute': [
        ['primary key', 'ticker', 'time'],
        ['foreign key', 'ticker', 'tickers', 'ticker']
    ],
    'ticker_detail': [
        ['primary key', 'ticker'],
        ['foreign key', 'ticker', 'tickers', 'ticker'],
        ['foreign key', 'industry', 'industries', 'industry'],
        ['foreign key', 'sector', 'sectors', 'sector'],
        ['foreign key', 'type', 'types', 'type']
    ],
    'financial': [
        ['primary key', 'ticker', 'calendarDate'],
        ['foreign key', 'ticker', 'tickers', 'ticker']
    ],
}

table_names = ['types', 'markets', 'locales', 'tickers', 'minute', 'ticker_detail', 'financial']
