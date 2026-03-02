-- Daily model predictions
CREATE TABLE IF NOT EXISTS daily_predictions (
    date TEXT PRIMARY KEY,
    pred_linear REAL,
    pred_rf REAL,
    pred_gbr REAL,
    conf_linear REAL,
    conf_rf REAL,
    conf_gbr REAL,
    chosen_signal INTEGER,
    position_size REAL
);

-- Strategy performance
CREATE TABLE IF NOT EXISTS pnl (
    date TEXT PRIMARY KEY,
    daily_return REAL,
    strategy_return REAL,
    cum_pnl REAL
);

-- Data quality & pipeline checks
CREATE TABLE IF NOT EXISTS data_quality (
    date TEXT,
    check_name TEXT,
    passed INTEGER,
    message TEXT
);
