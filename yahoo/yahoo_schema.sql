CREATE TABLE IF NOT EXISTS daily (
    ticker VARCHAR(10),
    date DATE,
    pct_returns DOUBLE PRECISION,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    $1,
    PRIMARY KEY(ticker, date)
);