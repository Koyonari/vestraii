from supabase import create_client, Client
from datetime import datetime
import json
from config import SUPABASE_URL, SUPABASE_KEY


class DatabaseManager:
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment")
        
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    def upsert_stock_data(self, stock_data):
        """Insert or update stock data in database"""
        try:
            # Prepare data for stocks table
            stock_record = {
                'ticker': stock_data['ticker'],
                'name': stock_data['name'],
                'sector': stock_data.get('sector', 'Unknown'),
                'current_price': stock_data.get('current_price'),
                'investment_score': stock_data['investment_score'],
                'sentiment_score': stock_data['avg_sentiment'],
                'sentiment_category': stock_data['sentiment_category'],
                'news_count': stock_data['news_count'],
                'bullish_count': stock_data.get('bullish_count', 0),
                'neutral_count': stock_data.get('neutral_count', 0),
                'bearish_count': stock_data.get('bearish_count', 0),
                'updated_at': datetime.now().isoformat()
            }
            
            # Upsert to stocks table
            result = self.supabase.table('stocks').upsert(
                stock_record,
                on_conflict='ticker'
            ).execute()
            
            print(f"✓ Upserted stock data for {stock_data['ticker']}")
            return result
        
        except Exception as e:
            print(f"✗ Error upserting stock data for {stock_data['ticker']}: {e}")
            return None
    
    def upsert_price_history(self, ticker, historical_data):
        """Insert or update historical price data"""
        try:
            records = []
            for data_point in historical_data:
                records.append({
                    'ticker': ticker,
                    'date': data_point['date'],
                    'price': data_point['price'],
                    'volume': data_point.get('volume', 0)
                })
            
            # Batch upsert
            if records:
                result = self.supabase.table('price_history').upsert(
                    records,
                    on_conflict='ticker,date'
                ).execute()
                
                print(f"✓ Upserted {len(records)} price records for {ticker}")
                return result
        
        except Exception as e:
            print(f"✗ Error upserting price history for {ticker}: {e}")
            return None
    
    def upsert_predictions(self, ticker, prediction_data):
        """Insert or update prediction data"""
        try:
            records = []
            for pred_point in prediction_data['data']:
                records.append({
                    'ticker': ticker,
                    'prediction_date': pred_point['date'],
                    'predicted_price': pred_point['price'],
                    'generated_at': datetime.now().isoformat()
                })
            
            # Batch upsert
            if records:
                result = self.supabase.table('predictions').upsert(
                    records,
                    on_conflict='ticker,prediction_date'
                ).execute()
                
                print(f"✓ Upserted {len(records)} predictions for {ticker}")
                return result
        
        except Exception as e:
            print(f"✗ Error upserting predictions for {ticker}: {e}")
            return None
    
    def upsert_shocking_prediction(self, prediction):
        """Insert or update a shocking prediction"""
        try:
            record = {
                'ticker': prediction['symbol'],
                'company_name': prediction['company'],
                'prediction_pct': prediction['prediction'],
                'direction': prediction['direction'],
                'timeframe': prediction['timeframe'],
                'current_price': prediction.get('current_price'),
                'predicted_price': prediction.get('predicted_price'),
                'sentiment_score': prediction.get('sentiment_score'),
                'investment_score': prediction.get('investment_score'),
                'timestamp': prediction['timestamp'],
                'updated_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('shocking_predictions').upsert(
                record,
                on_conflict='ticker'
            ).execute()
            
            print(f"✓ Upserted shocking prediction for {prediction['symbol']}")
            return result
        
        except Exception as e:
            print(f"✗ Error upserting shocking prediction: {e}")
            return None
    
    def write_analysis_to_database(self, ranked_stocks, shocking_predictions):
        """Write complete analysis results to database"""
        print("\nWriting analysis results to database...")
        
        success_count = 0
        error_count = 0
        
        # Write stock data
        for _, stock in ranked_stocks.iterrows():
            result = self.upsert_stock_data(stock.to_dict())
            if result:
                success_count += 1
            else:
                error_count += 1
        
        # Write shocking predictions
        all_shocking = (
            shocking_predictions.get('top_increases', []) +
            shocking_predictions.get('top_decreases', [])
        )
        
        for prediction in all_shocking:
            result = self.upsert_shocking_prediction(prediction)
            if result:
                success_count += 1
            else:
                error_count += 1
        
        print(f"\n{'='*60}")
        print(f"Database Write Summary:")
        print(f"  ✓ Successful: {success_count}")
        print(f"  ✗ Failed: {error_count}")
        print(f"{'='*60}\n")
        
        return success_count, error_count
    
    def write_stock_json_to_database(self, json_file_path):
        """Read a stock JSON file and write to database"""
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            ticker = data['ticker']
            
            # Prepare stock data
            stock_data = {
                'ticker': ticker,
                'name': data['name'],
                'current_price': data.get('current_price'),
                'investment_score': data['sentiment']['investment_score'],
                'avg_sentiment': data['sentiment']['score'],
                'sentiment_category': data['sentiment']['category'],
                'news_count': data['sentiment']['news_count'],
                'bullish_count': data['sentiment'].get('bullish_count', 0),
                'neutral_count': data['sentiment'].get('neutral_count', 0),
                'bearish_count': data['sentiment'].get('bearish_count', 0)
            }
            
            # Write stock data
            self.upsert_stock_data(stock_data)
            
            # Write price history
            if 'historical_data' in data:
                self.upsert_price_history(ticker, data['historical_data'])
            
            # Write predictions
            if 'prediction' in data:
                self.upsert_predictions(ticker, data['prediction'])
            
            return True
        
        except Exception as e:
            print(f"Error writing JSON to database: {e}")
            return False
    
    def get_all_stocks(self, limit=100):
        """Retrieve all stocks from database"""
        try:
            result = self.supabase.table('stocks')\
                .select('*')\
                .order('investment_score', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
        
        except Exception as e:
            print(f"Error retrieving stocks: {e}")
            return []
    
    def get_stock_details(self, ticker):
        """Get detailed data for a specific stock"""
        try:
            # Get stock data
            stock = self.supabase.table('stocks')\
                .select('*')\
                .eq('ticker', ticker)\
                .execute()
            
            # Get price history
            prices = self.supabase.table('price_history')\
                .select('*')\
                .eq('ticker', ticker)\
                .order('date', desc=True)\
                .limit(90)\
                .execute()
            
            # Get predictions
            predictions = self.supabase.table('predictions')\
                .select('*')\
                .eq('ticker', ticker)\
                .order('prediction_date')\
                .execute()
            
            return {
                'stock': stock.data[0] if stock.data else None,
                'price_history': prices.data,
                'predictions': predictions.data
            }
        
        except Exception as e:
            print(f"Error retrieving stock details: {e}")
            return None
    
    def get_shocking_predictions(self, limit=10):
        """Get shocking predictions from database"""
        try:
            result = self.supabase.table('shocking_predictions')\
                .select('*')\
                .order('prediction_pct', desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
        
        except Exception as e:
            print(f"Error retrieving shocking predictions: {e}")
            return []


if __name__ == "__main__":
    # Test database operations
    try:
        db = DatabaseManager()
        print("✓ Connected to Supabase")
        
        # Test retrieving data
        stocks = db.get_all_stocks(limit=5)
        print(f"\nRetrieved {len(stocks)} stocks from database")
        
        if stocks:
            print("\nSample stock data:")
            print(f"  {stocks[0]['ticker']}: {stocks[0]['name']}")
            print(f"  Investment Score: {stocks[0]['investment_score']}")
        
    except Exception as e:
        print(f"Database connection error: {e}")
        print("\nMake sure SUPABASE_URL and SUPABASE_KEY are set in .env file")
