import pandas as pd
import numpy as np
import yfinance as yf
from joblib import load
from datetime import datetime, timedelta

try:
    linear_model = load("ProjOil/src/models/linear_model.joblib")
    rf_model = load("ProjOil/src/models/rf_model.joblib")
    gbr_model = load("ProjOil/src/models/gbr_model.joblib")
except Exception as e:
    raise RuntimeError(f"Failed to load saved models: {e}")

def fetch_heating_oil(days=14):
    try:
        oil = yf.Ticker("HO=F")
        df = oil.history(period=f"{days}d").reset_index()
        if df.empty:
            raise ValueError("No heating oil data returned")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to fetch heating oil data: {e}")

def fetch_crude_oil(days=14):
    try:
        crude = yf.Ticker("CL=F")
        df = crude.history(period=f"{days}d").reset_index()
        if df.empty:
            raise ValueError("No crude oil data returned")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to fetch crude oil data: {e}")
        
def fetch_weather():
    try:
        today = pd.Timestamp.today()  # keep as Timestamp
        start_date = (today - pd.Timedelta(days=8)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        url = f"https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USW00094728&startDate={start_date}&endDate={end_date}&dataTypes=TMAX,TMIN&format=csv&units=standard"
        df = pd.read_csv(url)
        if df.empty:
            raise ValueError("No weather data returned")
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to fetch weather data: {e}")

df_oil = fetch_heating_oil()
df_crude = fetch_crude_oil()
df_weather = fetch_weather()

df_weather["TAVG"] = (df_weather["TMAX"] + df_weather["TMIN"]) / 2

last_close = df_oil["Close"].iloc[-1]
close_lag1 = df_oil["Close"].iloc[-2]
close_roll7 = df_oil["Close"].iloc[-7:].mean()  # rolling 7-day mean

change_lag1 = (df_oil["Close"].iloc[-1] - df_oil["Close"].iloc[-2]) / df_oil["Close"].iloc[-2]
change_lag5 = (df_oil["Close"].iloc[-1] - df_oil["Close"].iloc[-6]) / df_oil["Close"].iloc[-6]

# Weather features
tavg_lag7 = df_weather["TAVG"].iloc[-7:].mean()

# Crude oil features
crude_close = df_crude["Close"].iloc[-1]
crude_lag1 = df_crude["Close"].iloc[-2]

X_today = pd.DataFrame([[
    last_close,
    tavg_lag7,
    crude_close,
    crude_lag1,
    close_lag1,
    close_roll7,
    change_lag1,
    change_lag5
]], columns=[
    "Close",
    "TAVG_lag7",
    "Crude_Close",
    "Crude_lag1",
    "Close_lag1",
    "Close_roll7",
    "Change_lag1",
    "Change_lag5"
])

try:
    pred_linear = linear_model.predict(X_today)[0]
    pred_rf = rf_model.predict(X_today)[0]
    pred_gbr = gbr_model.predict(X_today)[0]
except Exception as e:
    raise RuntimeError(f"Error making predictions: {e}")

print(f"Predicted next-day return:")
print(f"Linear Regression: {pred_linear:.4f}")
print(f"Random Forest:     {pred_rf:.4f}")
print(f"Gradient Boosting: {pred_gbr:.4f}")

preds = np.array([pred_linear, pred_rf, pred_gbr])
conf = np.abs(preds) / np.max(np.abs(preds))
position_size = np.sign(preds) * conf

output = pd.DataFrame({
    "Date": [datetime.today().strftime("%Y-%m-%d")],
    "Pred_Linear": [pred_linear],
    "Pred_RF": [pred_rf],
    "Pred_GBR": [pred_gbr],
    "Conf_Linear": [position_size[0]],
    "Conf_RF": [position_size[1]],
    "Conf_GBR": [position_size[2]]
})

import sys
from pathlib import Path

PROJECT_ROOT = Path().resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.utils.db import get_conn

def save_daily_prediction(date, model, predicted_change, confidence, direction, pnl=None):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO daily_predictions
        (date, model, predicted_change, confidence, direction, pnl)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        date,
        model,
        predicted_change,
        confidence,
        int(direction),
        pnl
    ))

    conn.commit()
    conn.close()

date = output.loc[0, "Date"]

model_rows = [
    ("Linear", output.loc[0, "Pred_Linear"], output.loc[0, "Conf_Linear"]),
    ("Random Forest", output.loc[0, "Pred_RF"], output.loc[0, "Conf_RF"]),
    ("Gradient Boosting", output.loc[0, "Pred_GBR"], output.loc[0, "Conf_GBR"]),
]

for model, pred, conf in model_rows:
    save_daily_prediction(
        date=date,
        model=model,
        predicted_change=float(pred),
        confidence=float(conf),
        direction=int(pred > 0),
        pnl=None
    )