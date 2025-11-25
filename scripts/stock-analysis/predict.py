import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import PREDICTION_DAYS
from webscrape import get_stock_price_data


def predict_stock_trend(ticker, price_data, sentiment_score):
    """Generate price predictions based on historical prices and sentiment"""
    if price_data is None or len(price_data) < 5:
        return None
    
    try:
        # Get the last closing price
        last_close = price_data['Close'].iloc[-1]
        
        # Calculate moving averages
        short_window = min(10, len(price_data))
        long_window = min(30, len(price_data))
        
        short_ma = price_data['Close'].rolling(window=short_window).mean().iloc[-1]
        long_ma = price_data['Close'].rolling(window=long_window).mean().iloc[-1]
        
        # Calculate average daily price change
        avg_daily_change = price_data['Close'].pct_change().mean()
        volatility = price_data['Close'].pct_change().std()
        
        # Convert sentiment to a price adjustment factor
        sentiment_factor = 1 + (sentiment_score * 0.05)
        
        # Calculate momentum
        momentum = (short_ma / long_ma - 1) if long_ma > 0 else 0
        
        # Generate predictions
        prediction_days = PREDICTION_DAYS
        dates = pd.date_range(
            start=price_data.index[-1] + pd.Timedelta(days=1), 
            periods=prediction_days
        )
        
        predicted_prices = [last_close]
        upper_bounds = [last_close]
        lower_bounds = [last_close]
        
        for i in range(1, prediction_days):
            # Blend of momentum, average change, and sentiment
            daily_change = (avg_daily_change + momentum/30) * sentiment_factor
            
            # Calculate next price
            next_price = predicted_prices[-1] * (1 + daily_change)
            
            # Add realistic noise based on historical volatility
            noise = np.random.normal(0, volatility * 0.5)
            next_price = next_price * (1 + noise)
            
            # Ensure price stays positive
            next_price = max(next_price, predicted_prices[-1] * 0.95)
            
            # Calculate confidence bounds
            confidence_interval = volatility * 1.96  # 95% confidence
            upper_bound = next_price * (1 + confidence_interval)
            lower_bound = next_price * (1 - confidence_interval)
            
            predicted_prices.append(next_price)
            upper_bounds.append(upper_bound)
            lower_bounds.append(lower_bound)
        
        # Calculate prediction metrics
        price_change_pct = ((predicted_prices[-1] - last_close) / last_close) * 100
        
        return {
            'predictions': predicted_prices,
            'upper_bound': upper_bounds,
            'lower_bound': lower_bounds,
            'current_price': round(last_close, 2),
            'predicted_price_30d': round(predicted_prices[-1], 2),
            'price_change_pct': round(price_change_pct, 2),
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
            abs_change = abs(pred['price_change_pct'])
            
            # Determine timeframe based on magnitude
            if abs_change > 20:
                timeframe = '30 days'
            elif abs_change > 10:
                timeframe = '14 days'
            else:
                timeframe = '7 days'
            
            shocking_predictions.append({
                'company': pred['name'],
                'symbol': pred['ticker'],
                'prediction': abs(pred['price_change_pct']),
                'direction': pred['prediction_direction'],
                'timeframe': timeframe,
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
