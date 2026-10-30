import pandas as pd
import numpy as np
from datetime import datetime
from config import PREDICTION_DAYS


# Model parameters (validated walk-forward on ~100 large caps; see backtest.py).
# Historical drift, momentum, technical indicators and post-earnings drift were all
# tested as return signals and none beat a constant drift out of sample, so the
# expected return is the long-run market drift plus a small news-sentiment tilt.
PRIOR_DAILY_DRIFT = 0.0003     # ~7.5%/yr long-run equity drift
SENTIMENT_DAILY_TILT = 0.0004  # max daily drift added by fully bullish news
EWMA_LAMBDA = 0.94             # RiskMetrics decay for recent volatility
LONG_VOL_DAYS = 250            # ~1 trading year for the long-run volatility
EARNINGS_LOOKBACK = 8          # past reports used to size the earnings-day move
CONFIDENCE_Z = 1.96            # 95% band


def _trading_days(index):
    """Normalize a DatetimeIndex to tz-naive dates for matching against earnings dates"""
    index = pd.DatetimeIndex(index)
    if index.tz is not None:
        index = index.tz_localize(None)
    return index.normalize()


def expected_daily_drift(sentiment_score=0.0, news_count=0):
    """Long-run drift tilted by news sentiment, scaled by how much news backs it up"""
    news_confidence = min(1.0, news_count / 20)
    return PRIOR_DAILY_DRIFT + SENTIMENT_DAILY_TILT * float(np.clip(sentiment_score, -1, 1)) * news_confidence


def estimate_volatility(close, earnings_dates=()):
    """
    Split volatility into ordinary trading days and earnings days.

    Returns the daily volatility on ordinary days (blend of recent EWMA and
    last trading year) and the mean squared log move on recent earnings days, or
    None when there's no earnings history to size it.
    """
    log_returns = np.log(close / close.shift(1))
    is_earnings = _trading_days(close.index).isin(earnings_dates)

    ordinary = log_returns[~is_earnings].dropna()
    ewma_vol = np.sqrt((ordinary ** 2).ewm(alpha=1 - EWMA_LAMBDA).mean().iloc[-1])
    sigma = 0.5 * ewma_vol + 0.5 * ordinary.tail(LONG_VOL_DAYS).std()

    earnings_moves = log_returns[is_earnings].dropna().tail(EARNINGS_LOOKBACK)
    jump_variance = float((earnings_moves ** 2).mean()) if len(earnings_moves) >= 2 else None

    return sigma, jump_variance


def predict_stock_trend(ticker, price_data, sentiment_score, news_count=0, earnings_dates=()):
    """Generate price predictions based on historical prices, sentiment and earnings dates"""
    if price_data is None or len(price_data) < 20:
        return None

    try:
        close = price_data['Close']
        last_close = float(close.iloc[-1])
        mu = expected_daily_drift(sentiment_score, news_count)
        sigma, jump_variance = estimate_volatility(close, earnings_dates)

        # Forecast over trading days only, covering PREDICTION_DAYS calendar days
        dates = pd.bdate_range(
            start=price_data.index[-1] + pd.Timedelta(days=1),
            end=price_data.index[-1] + pd.Timedelta(days=PREDICTION_DAYS),
        )
        t = np.arange(1, len(dates) + 1)

        # Variance grows by sigma^2 per ordinary day, plus the typical earnings move
        # on an upcoming earnings day, so bands widen when a report is due
        if jump_variance is None:
            earnings_days = np.zeros(len(t))
            jump_variance = 0.0
        else:
            earnings_days = np.cumsum(_trading_days(dates).isin(earnings_dates))
        variance = sigma ** 2 * (t - earnings_days) + jump_variance * earnings_days

        # Median of a lognormal random walk
        predicted_prices = last_close * np.exp(mu * t)
        spread = CONFIDENCE_Z * np.sqrt(variance)
        upper_bounds = predicted_prices * np.exp(spread)
        lower_bounds = predicted_prices * np.exp(-spread)

        price_change_pct = (predicted_prices[-1] / last_close - 1) * 100

        return {
            'dates': dates,
            'predictions': predicted_prices.tolist(),
            'upper_bound': upper_bounds.tolist(),
            'lower_bound': lower_bounds.tolist(),
            'current_price': round(last_close, 2),
            'predicted_price_30d': round(float(predicted_prices[-1]), 2),
            'price_change_pct': round(float(price_change_pct), 2),
            'prediction_direction': 'increase' if price_change_pct > 0 else 'decrease'
        }

    except Exception as e:
        print(f"Error generating prediction for {ticker}: {e}")
        return None


def generate_shocking_predictions(all_predictions, top_n=5):
    """
    Generate list of most shocking predictions (highest absolute % changes)
    Returns data in format for frontend consumption
    """
    shocking_predictions = []
    
    for pred in all_predictions:
        if pred and 'price_change_pct' in pred:
            shocking_predictions.append({
                'company': pred['name'],
                'symbol': pred['ticker'],
                'prediction': abs(pred['price_change_pct']),
                'direction': pred['prediction_direction'],
                'timeframe': f'{PREDICTION_DAYS} days',
                'timestamp': datetime.now().isoformat(),
                'current_price': pred['current_price'],
                'predicted_price': pred['predicted_price_30d'],
                'sentiment_score': pred.get('sentiment_score', 0),
                'investment_score': pred.get('investment_score', 50)
            })
    
    # Sort by absolute prediction magnitude
    shocking_predictions.sort(key=lambda x: x['prediction'], reverse=True)
    
    # Get top N increases and decreases
    increases = [p for p in shocking_predictions if p['direction'] == 'increase'][:top_n]
    decreases = [p for p in shocking_predictions if p['direction'] == 'decrease'][:top_n]
    
    return {
        'top_increases': increases,
        'top_decreases': decreases,
        'all_shocking': shocking_predictions[:top_n * 2]
    }
