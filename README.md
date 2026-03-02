# Heating-Oil-Price-Prediction-Pipeline

## Overview
The project is an complete end to end data and machine learning pipeline that predicts daily changes in Heating Oil price using a combination of variables such as:

- Weather data

- Comparative market data

- Time series and rolling features

The predictions can be generated daily then autoumatically logged to an SQLite databse.

## Data Sources
Weather Data: NOAA api daily summaries
Market Data: Yahoo Finance
The metric to measure the price of a given day was based on the closing price.
The data was chosen to span 2000-2006 and once fetched the data is aligned and merged by date. 

## Feature Engineering
Features were added to generate a more insightful model. The decision to add lagging and rolling average data was to incorporate context and historical data for models to train on. This was proven to be successful on the trained models as one achieved an RMSE of 0.0629%. This result aligns with our intuitive understanding of how underlying market trends can influence the future prices of heating oil.

To ensure that added features contributed meaningful signal rather than noise, a systematic evaulation was done on each feature's usefulness using permutation importance across all trained models. Results consistently showed that lagged heating oil prices and crude oil rolling averages were dominant drivers of performance, while weather derived variables often little impact. Objectively, a decision should have been made to omit all weather derived variables based on the permuation importance evaluation; however for the sake of preserving this projects integrity of predicting oil prices based off the weather - based off what Eduardo Saverin was claimed to have done in The Social Network - a decision was made to keep the best of the worst, weather feature.

## Key Results
- The results below are based off each model's prediction of percentage change in the following day's heating oil price.
### Regression Performance (Daily % Change)

|Model |RMSE|Directional Accuracy|Cumulative P&L|
|:------:|:--------:|:------:|:------:|
|Linear Regression|	0.024998|	47.8%|	-0.14
|Random Forest|	0.024157 |	52.2%|	+0.34
|Gradient Boosting|	0.024685|	49.8%|	+0.34
Strategy Simulation & Model Behavior Analysis

Although all models achieved similar regression performance in terms of RMSE, their behavior diverged significantly when evaluated in a directional trading and strategy simulation context. Tree-based models (Random Forest and Gradient Boosting) produced positive cumulative returns, while Linear Regression generated negative P&L despite strong regression metrics. This highlights an important distinction between minimizing prediction error and generating economically meaningful signals.

### Regression vs Directional Performance

Linear Regression optimized for minimising squared error produced smoother and more conservative predictions centered around the historical mean. While this resulted in stable RMSE values and robustness during extreme market events (such as the 2022 energy price spike), it also reduced sensitivity to smaller but frequent directional movements. 

In contrast, tree-based models captured nonlinear interactions and regime-dependent patterns, allowing them to better identify short-term directional biases even when absolute price changes were small. This explains why tree-based models achieved higher directional accuracy and superior cumulative returns despite comparable RMSE scores.

The model was also assessed on how the estimated generated profits based off simulated trades.
### Strategy Simulation (Cumulative P&L)
|Model|Cumulative P&L (%)|
|:----:|:----:|
|Linear Regression|	-0.14|
|Random Forest|	+0.34|
|Gradient Boosting|	+0.34|

### Strategy Simulation Mechanics

The trading strategy was implemented as a confidence-weighted directional strategy:

1. Each model predicted the next-day percentage price change

2. The direction of the trade (long or flat) was determined by the sign of the prediction

3. A confidence proxy was computed based on the magnitude of the predicted change relative to historical variability

4. Position size was scaled proportionally to model confidence

Daily P&L was calculated as: P&L = Position Size × Realized Price Change

This framework ensured that each model's correct and conversly incorrect opinions would be rewarded and penalised accordingly.

### Why Tree Models Performed Better in Trading

Several real-world factors likely contributed to the observed performance differences:

Nonlinear demand dynamics: Heating oil demand reacts asymmetrically to weather changes, inventory levels, and energy prices. Tree-based models naturally capture these threshold effects.

Market regime sensitivity: Energy markets often shift between volatility regimes. Tree models adapt better to such regime changes, while linear models assume stable relationships.

Directional signal amplification: Tree-based models tend to produce more polarized predictions, which—when combined with confidence-based sizing—translated into stronger trading signals.

Linear Regression, while effective at extrapolation and shock resilience, lacked the sensitivity required to exploit short-term directional opportunities consistently.


## Database Design
To support monitoring and future strategy evaluation, model predictions are persisted in a SQLite database rather than being stored only in-memory or as flat files.

The database was initialized using a defined schema and contains a normalized table structure, with one row per model per prediction date. Each record stores the prediction date, model identifier, predicted percentage price change, confidence estimate, directional signal, and optional realized P&L once the true market outcome is known. This design avoids wide, model-specific columns and allows new models to be added without schema changes.

SQLite was chosen because it is lightweight, easy to use, and well suited for single-machine analytical workflows. It works naturally with Python and pandas, making it ideal for local development, rapid prototyping, and building dashboards. At the same time, using SQL helps preserve patterns that easily transfer to larger relational databases.

The database logic is kept separate from the model training and inference code and is accessed through a small utility module. This mirrors how data pipelines are structured in production systems. Storing predictions in a database allows for backtesting, comparing model performance over time, and supporting live dashboards, while also leaving room to migrate to a cloud-based database in the future if the project scales.
