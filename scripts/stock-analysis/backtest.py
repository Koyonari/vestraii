#!/usr/bin/env python3
"""
Walk-forward backtest of the price prediction model.

For each ticker, repeatedly forecasts PREDICTION_DAYS ahead using only data
available at that point, then compares against what actually happened.
Historical news sentiment isn't available, so sentiment is held at 0.
Earnings dates are passed in full, since report dates are scheduled in advance.

Usage: python backtest.py [TICKER ...]
"""

import sys
import numpy as np
import pandas as pd
import yfinance as yf
from config import FALLBACK_TICKERS, PREDICTION_DAYS, MODEL_HISTORY_DAYS
from predict import predict_stock_trend
from webscrape import get_earnings_reaction_dates

STEP_DAYS = 10  # trading days between forecast origins
ALPHA = 0.05    # bands are 95% intervals


def legacy_predict(close, rng):
    """Previous model: noisy random walk on 90-day drift + momentum (kept for comparison)"""
    window = close[close.index >= close.index[-1] - pd.Timedelta(days=90)]
    last = window.iloc[-1]
    short_ma = window.rolling(min(10, len(window))).mean().iloc[-1]
    long_ma = window.rolling(min(30, len(window))).mean().iloc[-1]
    avg_change = window.pct_change().mean()
    vol = window.pct_change().std()
    momentum = short_ma / long_ma - 1
    price = last
    for _ in range(1, PREDICTION_DAYS):
        price = max(price * (1 + avg_change + momentum / 30) * (1 + rng.normal(0, vol * 0.5)), price * 0.95)
    band = vol * 1.96
    return price, price * (1 + band), price * (1 - band)


def backtest_ticker(ticker, rng):
    hist = yf.Ticker(ticker).history(period="5y")['Close'].dropna()
    hist.index = hist.index.tz_localize(None)
    earnings = get_earnings_reaction_dates(ticker)
    rows = []
    first_origin = hist.index[0] + pd.Timedelta(days=MODEL_HISTORY_DAYS)

    for i in range(0, len(hist), STEP_DAYS):
        origin = hist.index[i]
        target_date = origin + pd.Timedelta(days=PREDICTION_DAYS)
        if origin < first_origin or target_date > hist.index[-1]:
            continue

        train = hist[(hist.index <= origin) & (hist.index > origin - pd.Timedelta(days=MODEL_HISTORY_DAYS))]
        actual = hist[hist.index <= target_date].iloc[-1]
        last = train.iloc[-1]

        new = predict_stock_trend(ticker, train.to_frame('Close'), 0.0, earnings_dates=earnings)
        old_pred, old_hi, old_lo = legacy_predict(train, rng)

        rows.append({
            'actual': actual / last - 1,
            'new': new['predictions'][-1] / last - 1,
            'new_lo': new['lower_bound'][-1] / last - 1,
            'new_hi': new['upper_bound'][-1] / last - 1,
            'old': old_pred / last - 1,
            'old_lo': old_lo / last - 1,
            'old_hi': old_hi / last - 1,
            'naive': 0.0,  # baseline: price stays flat
        })
    return rows


def summarize(df, col):
    err = (df[col] - df['actual']) * 100
    result = {
        'MAE %': np.abs(err).mean(),
        'RMSE %': np.sqrt((err ** 2).mean()),
        'Direction hit %': ((df[col] > 0) == (df['actual'] > 0)).mean() * 100,
    }
    if f'{col}_lo' in df:
        lo, hi, y = df[f'{col}_lo'] * 100, df[f'{col}_hi'] * 100, df['actual'] * 100
        # Interval score: band width plus a penalty for each miss (lower is better)
        interval_score = (hi - lo) + (2 / ALPHA) * ((lo - y).clip(lower=0) + (y - hi).clip(lower=0))
        result['95% band coverage %'] = ((y >= lo) & (y <= hi)).mean() * 100
        result['Band width %'] = (hi - lo).mean()
        result['Interval score'] = interval_score.mean()
    return result


def main():
    tickers = sys.argv[1:] or FALLBACK_TICKERS
    rng = np.random.default_rng(0)
    rows = []
    for ticker in tickers:
        try:
            rows.extend(backtest_ticker(ticker, rng))
        except Exception as e:
            print(f"  ⚠ Skipping {ticker}: {e}")

    df = pd.DataFrame(rows)
    print(f"\nBacktest: {len(tickers)} tickers, {len(df)} forecasts, {PREDICTION_DAYS}-day horizon\n")
    result = pd.DataFrame({
        'flat baseline': summarize(df, 'naive'),
        'old model': summarize(df, 'old'),
        'new model': summarize(df, 'new'),
    })
    print(result.round(2).to_string())


if __name__ == "__main__":
    main()
