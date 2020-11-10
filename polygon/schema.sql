CREATE TABLE IF NOT EXISTS types (
    type VARCHAR PRIMARY KEY,
    "desc" VARCHAR,
    is_index BOOLEAN
);

CREATE TABLE IF NOT EXISTS markets (
    market VARCHAR PRIMARY KEY,
    "desc" VARCHAR
);

CREATE TABLE IF NOT EXISTS locales (
    locale VARCHAR PRIMARY KEY,
    name VARCHAR
);

CREATE TABLE IF NOT EXISTS industries (
    industry VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS sectors (
    sector VARCHAR PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS detail_tags (
    id SERIAL PRIMARY KEY,
    value VARCHAR
);

CREATE TABLE IF NOT EXISTS tickers (
    ticker  VARCHAR,
    name    VARCHAR NOT NULL,
    market  VARCHAR NOT NULL,
    locale   VARCHAR NOT NULL,
    currency VARCHAR NOT NULL,
    primaryExch VARCHAR,
    active BOOLEAN NOT NULL,
    updated DATE NOT NULL,
    type VARCHAR,
    PRIMARY KEY(ticker),
    FOREIGN KEY(market) REFERENCES markets(market),
    FOREIGN KEY(locale) REFERENCES locales(locale),
    FOREIGN KEY(type) REFERENCES types(type)
);

CREATE TABLE IF NOT EXISTS minute (
    ticker VARCHAR,
    time BIGINT,
    adj_open DOUBLE PRECISION,
    adj_high DOUBLE PRECISION,
    adj_low DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    adj_volume DOUBLE PRECISION,
    num_items INTEGER,
    PRIMARY KEY(ticker, time),
    FOREIGN KEY(ticker) REFERENCES tickers(ticker)
);

CREATE TABLE IF NOT EXISTS ticker_detail (
    ticker VARCHAR,
    logo VARCHAR,
    listdate DATE,
    cik INTEGER,
    bloomberg VARCHAR,
    figi VARCHAR,
    lei VARCHAR,
    sic INTEGER,
    country VARCHAR,
    industry VARCHAR,
    sector VARCHAR,
    marketcap BIGINT,
    employees INTEGER,
    phone VARCHAR,
    ceo VARCHAR,
    url VARCHAR,
    description VARCHAR,
    exchange VARCHAR,
    name VARCHAR,
    exchangeSymbo VARCHAR,
    hq_address VARCHAR,
    hq_state  VARCHAR,
    hq_country VARCHAR,
    type VARCHAR,
    updated DATE,
    PRIMARY KEY(ticker),
    FOREIGN KEY(ticker) REFERENCES tickers(ticker),
    FOREIGN KEY(industry) REFERENCES industries(industry),
    FOREIGN KEY(sector) REFERENCES sectors(sector),
    FOREIGN KEY(type) REFERENCES types(type)
);

CREATE TABLE IF NOT EXISTS financial (
    ticker VARCHAR,
    period VARCHAR,
    calendarDate DATE,
    reportPeriod DATE,
    updated DATE,
    dateKey DATE,
    accumulatedOtherComprehensiveIncome INTEGER,
    assets BIGINT,
    assetsCurrent BIGINT,
    assetsNonCurrent BIGINT,
    bookValuePerShare REAL,
    capitalExpenditure BIGINT,
    cashAndEquivalents BIGINT,
    cashAndEquivalentsUSD BIGINT,
    costOfRevenue BIGINT,
    consolidatedIncome BIGINT,
    currentRatio REAL,
    debtToEquityRatio REAL,
    debt BIGINT,
    debtCurrent BIGINT,
    debtNonCurrent BIGINT,
    debtUSD BIGINT,
    deferredRevenue BIGINT,
    depreciationAmortizationAndAccretion BIGINT,
    deposits INTEGER,
    dividendYield REAL,
    dividendsPerBasicCommonShare REAL,
    earningBeforeInterestTaxes BIGINT,
    earningsBeforeInterestTaxesDepreciationAmortization BIGINT,
    EBITDAMargin REAL,
    earningsBeforeInterestTaxesDepreciationAmortizationUSD BIGINT,
    earningBeforeInterestTaxesUSD BIGINT,
    earningsBeforeTax BIGINT,
    earningsPerBasicShare REAL,
    earningsPerDilutedShare REAL,
    earningsPerBasicShareUSD REAL,
    shareholdersEquity BIGINT,
    shareholdersEquityUSD BIGINT,
    enterpriseValue BIGINT,
    enterpriseValueOverEBIT INTEGER,
    enterpriseValueOverEBITDA REAL,
    freeCashFlow BIGINT,
    freeCashFlowPerShare REAL,
    foreignCurrencyUSDExchangeRate INTEGER,
    grossProfit BIGINT,
    grossMargin REAL,
    goodwillAndIntangibleAssets INTEGER,
    interestExpense INTEGER,
    investedCapital BIGINT,
    inventory BIGINT,
    investments BIGINT,
    investmentsCurrent BIGINT,
    investmentsNonCurrent BIGINT,
    totalLiabilities BIGINT,
    currentLiabilities BIGINT,
    liabilitiesNonCurrent BIGINT,
    marketCapitalization BIGINT,
    netCashFlow BIGINT,
    netCashFlowBusinessAcquisitionsDisposals BIGINT,
    issuanceEquityShares BIGINT,
    issuanceDebtSecurities BIGINT,
    paymentDividendsOtherCashDistributions BIGINT,
    netCashFlowFromFinancing BIGINT,
    netCashFlowFromInvesting BIGINT,
    netCashFlowInvestmentAcquisitionsDisposals BIGINT,
    netCashFlowFromOperations BIGINT,
    effectOfExchangeRateChangesOnCash INTEGER,
    netIncome BIGINT,
    netIncomeCommonStock BIGINT,
    netIncomeCommonStockUSD BIGINT,
    netLossIncomeFromDiscontinuedOperations INTEGER,
    netIncomeToNonControllingInterests INTEGER,
    profitMargin REAL,
    operatingExpenses BIGINT,
    operatingIncome BIGINT,
    tradeAndNonTradePayables BIGINT,
    payoutRatio REAL,
    priceToBookValue REAL,
    priceEarnings REAL,
    priceToEarningsRatio REAL,
    propertyPlantEquipmentNet BIGINT,
    preferredDividendsIncomeStatementImpact INTEGER,
    sharePriceAdjustedClose REAL,
    priceSales REAL,
    priceToSalesRatio REAL,
    tradeAndNonTradeReceivables BIGINT,
    accumulatedRetainedEarningsDeficit BIGINT,
    revenues BIGINT,
    revenuesUSD BIGINT,
    researchAndDevelopmentExpense BIGINT,
    shareBasedCompensation BIGINT,
    sellingGeneralAndAdministrativeExpense BIGINT,
    shareFactor INTEGER,
    shares BIGINT,
    weightedAverageShares BIGINT,
    weightedAverageSharesDiluted BIGINT,
    salesPerShare REAL,
    tangibleAssetValue BIGINT,
    taxAssets INTEGER,
    incomeTaxExpense BIGINT,
    taxLiabilities INTEGER,
    tangibleAssetsBookValuePerShare REAL,
    workingCapital BIGINT,
    PRIMARY KEY(ticker, calendarDate),
    FOREIGN KEY(ticker) REFERENCES tickers(ticker)
);