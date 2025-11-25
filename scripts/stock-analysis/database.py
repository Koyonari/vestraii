from supabase import create_client, Client
from datetime import datetime
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY


class DatabaseManager:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def upsert_stock_data(self, stock_data):
        """Insert or update complete stock data in Supabase"""
        try:
            ticker = stock_data['ticker']
            
            # Prepare stock data matching existing schema
            stock = {
                'ticker': ticker,
                'name': stock_data['name'],
                'sentiment': {
                    'score': float(stock_data.get('sentiment_score', 0)),
                    'category': stock_data.get('sentiment_category', 'Neutral'),
                    'investment_score': float(stock_data.get('investment_score', 0))
                },
                'news_count': int(stock_data.get('news_count', 0)),
                'rank': int(stock_data.get('rank', 0)),
                'investment_score': float(stock_data.get('investment_score', 0)),
                'last_updated': datetime.now().isoformat()
            }
            
            # Upsert stock data (ticker is primary key)
            self.supabase.table('stocks').upsert(stock, on_conflict='ticker').execute()

            # Handle historical prices
            if stock_data.get('historical_data'):
                # Delete existing historical data
                self.supabase.table('stock_prices').delete().eq('ticker', ticker).execute()
                
                # Prepare historical data
                historical_data = [
                    {
                        'ticker': ticker,
                        'date': price['date'],
                        'price': float(price['price'])
                    }
                    for price in stock_data['historical_data']
                ]
                
                # Insert new historical data in chunks
                chunk_size = 100
                for i in range(0, len(historical_data), chunk_size):
                    chunk = historical_data[i:i + chunk_size]
                    self.supabase.table('stock_prices').insert(chunk).execute()

            # Handle predictions
            if stock_data.get('prediction') and stock_data['prediction'].get('data'):
                # Delete existing predictions
                self.supabase.table('stock_predictions').delete().eq('ticker', ticker).execute()
                
                predictions = []
                for i in range(len(stock_data['prediction']['data'])):
                    pred_data = stock_data['prediction']['data'][i]
                    upper = stock_data['prediction']['upper_bound'][i] if stock_data['prediction'].get('upper_bound') else None
                    lower = stock_data['prediction']['lower_bound'][i] if stock_data['prediction'].get('lower_bound') else None
                    
                    predictions.append({
                        'ticker': ticker,
                        'date': pred_data['date'],
                        'price': float(pred_data['price']),
                        'upper_bound': float(upper['price']) if upper else None,
                        'lower_bound': float(lower['price']) if lower else None
                    })
                
                # Insert new predictions in chunks
                chunk_size = 100
                for i in range(0, len(predictions), chunk_size):
                    chunk = predictions[i:i + chunk_size]
                    self.supabase.table('stock_predictions').insert(chunk).execute()

            return True

        except Exception as e:
            print(f"Error upserting stock data for {stock_data.get('ticker', 'unknown')}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def write_analysis_to_database(self, ranked_stocks, shocking_predictions=None):
        """Write complete analysis results to database"""
        success_count = 0
        error_count = 0
        
        for idx, stock in ranked_stocks.iterrows():
            try:
                # Prepare stock data
                stock_data = {
                    'ticker': stock['ticker'],
                    'name': stock['name'],
                    'sentiment_score': float(stock.get('avg_sentiment', 0)),
                    'sentiment_category': stock.get('sentiment_category', 'Neutral'),
                    'investment_score': float(stock.get('investment_score', 0)),
                    'news_count': int(stock.get('news_count', 0)),
                    'rank': idx + 1,  # 1-based ranking
                    'historical_data': stock.get('historical_data', []),
                    'prediction': stock.get('prediction', {
                        'data': [],
                        'upper_bound': [],
                        'lower_bound': []
                    })
                }
                
                if self.upsert_stock_data(stock_data):
                    success_count += 1
                else:
                    error_count += 1
                    
            except Exception as e:
                print(f"Error processing {stock.get('ticker', 'unknown')}: {str(e)}")
                import traceback
                traceback.print_exc()
                error_count += 1
                
        print(f"\nDatabase Write Summary:")
        print(f"✓ Successfully wrote {success_count} stocks")
        print(f"✗ Failed to write {error_count} stocks")
        
        return success_count, error_count
