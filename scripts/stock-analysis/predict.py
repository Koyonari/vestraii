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
        # Sentiment ranges from -1 to 1, convert to multiplier 0.95 to 1.05
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
            
            predicted_prices.append(next_price)
        
        prediction_df = pd.DataFrame({
            'Date': dates,
            'Price': predicted_prices
        })
        prediction_df.set_index('Date', inplace=True)
        
        # Calculate prediction metrics
        price_change_pct = ((predicted_prices[-1] - last_close) / last_close) * 100
        
        return {
            'prediction_df': prediction_df,
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


def calculate_7day_30day_predictions(ticker, price_data, sentiment_score):
    """Calculate specific 7-day and 30-day predictions"""
    if price_data is None or len(price_data) < 5:
        return None
    
    try:
        last_close = price_data['Close'].iloc[-1]
        avg_daily_change = price_data['Close'].pct_change().mean()
        
        # Sentiment adjustment
        sentiment_factor = 1 + (sentiment_score * 0.05)
        
        # 7-day prediction
        predicted_7d = last_close * ((1 + avg_daily_change) ** 7) * sentiment_factor
        change_7d_pct = ((predicted_7d - last_close) / last_close) * 100
        
        # 30-day prediction
        predicted_30d = last_close * ((1 + avg_daily_change) ** 30) * sentiment_factor
        change_30d_pct = ((predicted_30d - last_close) / last_close) * 100
        
        return {
            'ticker': ticker,
            'current_price': round(last_close, 2),
            'predicted_7d': round(predicted_7d, 2),
            'change_7d_pct': round(change_7d_pct, 2),
            'predicted_30d': round(predicted_30d, 2),
            'change_30d_pct': round(change_30d_pct, 2)
        }
    
    except Exception as e:
        print(f"Error calculating predictions for {ticker}: {e}")
        return None


if __name__ == "__main__":
    # Test prediction functions
    print("Testing prediction functions...")
    
    test_ticker = 'AAPL'
    price_data = get_stock_price_data(test_ticker)
    
    if price_data is not None:
        # Test with neutral sentiment
        prediction_result = predict_stock_trend(test_ticker, price_data, 0.1)
        
        if prediction_result:
            print(f"\nPrediction for {test_ticker}:")
            print(f"Current Price: ${prediction_result['current_price']}")
            print(f"30-Day Predicted: ${prediction_result['predicted_price_30d']}")
            print(f"Change: {prediction_result['price_change_pct']}%")
            print(f"Direction: {prediction_result['prediction_direction']}")
        
        # Test shocking predictions
        mock_predictions = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'price_change_pct': 15.5,
                'prediction_direction': 'increase',
                'current_price': 150.0,
                'predicted_price_30d': 173.25,
                'sentiment_score': 0.5,
                'investment_score': 75
            }
        ]
        
        shocking = generate_shocking_predictions(mock_predictions)
        print("\nShocking Predictions:")
        print(f"Top increases: {len(shocking['top_increases'])}")
        print(f"Top decreases: {len(shocking['top_decreases'])}")
